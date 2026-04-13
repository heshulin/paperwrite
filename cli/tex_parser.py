"""LaTeX template parser — extract document structure via regex."""

import re
from pathlib import Path


# ── Section title mapping (shared with templates.py) ────────────────────

SECTION_TITLES = {
    "abstract": "Abstract",
    "introduction": "Introduction",
    "related_work": "Related Work",
    "method": "Method",
    "experiments": "Experiments",
    "results": "Results",
    "analysis": "Analysis",
    "discussion": "Discussion",
    "limitations": "Limitations",
    "broader_impact": "Broader Impact",
    "conclusion": "Conclusion",
}

# ── Regex patterns ───────────────────────────────────────────────────────

DOCCLASS_RE = re.compile(
    r'\\documentclass\s*(?:\[([^\]]*)\])?\s*\{([^}]+)\}'
)

# Supports one level of nested braces: \section{Results on \textbf{XYZ}}
SECTION_RE = re.compile(
    r'\\section\*?\{((?:[^{}]|\{[^}]*\})*)\}'
)

SUBSECTION_RE = re.compile(
    r'\\subsection\*?\{((?:[^{}]|\{[^}]*\})*)\}'
)

BIBSTYLE_RE = re.compile(
    r'\\bibliographystyle\{([^}]+)\}'
)

INPUT_RE = re.compile(
    r'\\input\{([^}]+)\}'
)

ABSTRACT_RE = re.compile(
    r'\\begin\{abstract\}'
)

USEPACKAGE_RE = re.compile(
    r'\\usepackage\s*(?:\[([^\]]*)\])?\s*\{([^}]+)\}'
)

# ── Section key derivation ───────────────────────────────────────────────

# Reverse lookup: "introduction" -> "introduction", "related work" -> "related_work"
_REVERSE_SECTION_TITLES = {v.lower(): k for k, v in SECTION_TITLES.items()}


def title_to_key(title: str) -> str:
    """Convert a section title to a canonical key.

    >>> title_to_key("Related Work")
    'related_work'
    >>> title_to_key("Broader Impact")
    'broader_impact'
    """
    lower = title.strip().lower()

    # Check if it matches a known section title
    if lower in _REVERSE_SECTION_TITLES:
        return _REVERSE_SECTION_TITLES[lower]

    # Derive key: lowercase, replace non-alphanumeric with underscore
    key = re.sub(r'[^a-z0-9]+', '_', lower).strip('_')

    # Fallback for non-ASCII or empty results
    if not key or key == '_':
        return None

    return key


# ── Generic outline template for unknown sections ────────────────────────

def generic_outline_template(section_key: str) -> str:
    """Generate a generic outline template for sections not in OUTLINE_TEMPLATES."""
    title = section_key.replace("_", " ").title()
    return f"""\
# {title} 大纲

## 核心要点

## 关键论据

## 与其他节的关系
"""


# ── Main parser ──────────────────────────────────────────────────────────

def parse_tex_file(path: Path) -> dict:
    """Parse a .tex file and extract document structure.

    Returns dict with keys:
        documentclass: str, e.g. r'\\documentclass[conference]{IEEEtran}'
        sections: list[str]  — raw section titles
        section_keys: list[str]  — canonical keys
        bibstyle: str or None, e.g. r'\\bibliographystyle{IEEEtran}'
        has_abstract: bool
        usepackage_lines: list[str]  -- raw usepackage lines from preamble
    """
    text = path.read_text(encoding="utf-8", errors="replace")

    # Strip comment lines
    lines = []
    for line in text.split("\n"):
        stripped = line.lstrip()
        if stripped.startswith("%"):
            continue
        # Remove inline comments (but not escaped \%)
        line_clean = re.sub(r'(?<!\\)%.*$', '', line)
        lines.append(line_clean)
    clean_text = "\n".join(lines)

    # Extract documentclass
    docclass_match = DOCCLASS_RE.search(clean_text)
    if docclass_match:
        opts = docclass_match.group(1) or ""
        cls = docclass_match.group(2)
        if opts:
            documentclass = f"\\documentclass[{opts}]{{{cls}}}"
        else:
            documentclass = f"\\documentclass{{{cls}}}"
    else:
        documentclass = "\\documentclass[11pt]{article}"

    # Extract \usepackage lines (only from preamble, i.e. before \begin{document})
    usepackage_lines = []
    begin_doc_match = re.search(r'\\begin\{document\}', clean_text)
    preamble_text = clean_text[:begin_doc_match.start()] if begin_doc_match else clean_text
    for match in USEPACKAGE_RE.finditer(preamble_text):
        opts = match.group(1) or ""
        pkgs = match.group(2)
        if opts:
            usepackage_lines.append(f"\\usepackage[{opts}]{{{pkgs}}}")
        else:
            usepackage_lines.append(f"\\usepackage{{{pkgs}}}")

    # Extract sections
    section_titles = SECTION_RE.findall(clean_text)
    section_keys = []
    for title in section_titles:
        key = title_to_key(title)
        if key:
            section_keys.append(key)

    # If no \section found, try \subsection
    if not section_keys:
        subsection_titles = SUBSECTION_RE.findall(clean_text)
        for title in subsection_titles:
            key = title_to_key(title)
            if key:
                section_keys.append(key)

    # If still nothing, try \input to infer section names
    if not section_keys:
        inputs = INPUT_RE.findall(clean_text)
        for inp in inputs:
            name = Path(inp).stem
            # Skip common non-section inputs
            if name in ("preamble", "macros", "commands", "packages"):
                continue
            key = title_to_key(name) or name.lower().replace(" ", "_")
            if key:
                section_keys.append(key)

    # Detect abstract
    has_abstract = bool(ABSTRACT_RE.search(clean_text))
    if has_abstract and "abstract" not in section_keys:
        section_keys.insert(0, "abstract")

    # Extract bibliography style
    bibstyle_match = BIBSTYLE_RE.search(clean_text)
    bibstyle = None
    if bibstyle_match:
        bibstyle = f"\\bibliographystyle{{{bibstyle_match.group(1)}}}"

    return {
        "documentclass": documentclass,
        "sections": section_titles,
        "section_keys": section_keys,
        "bibstyle": bibstyle,
        "has_abstract": has_abstract,
        "usepackage_lines": usepackage_lines,
    }


def find_resource_files(directory: Path) -> list:
    """Find .sty, .cls, .bst files in a directory (recursive)."""
    files = []
    for pattern in ("*.sty", "*.cls", "*.bst"):
        files.extend(directory.rglob(pattern))
    return sorted(files)


def find_main_tex(directory: Path) -> Path:
    """Find the main .tex file in a directory.

    Priority: main.tex > paper.tex > sample.tex > template.tex > largest .tex
    """
    tex_files = list(directory.rglob("*.tex"))
    if not tex_files:
        return None

    # Prefer specific names
    for name in ("main.tex", "paper.tex", "sample.tex", "template.tex"):
        for f in tex_files:
            if f.name.lower() == name:
                return f

    # Fall back to largest file
    return max(tex_files, key=lambda f: f.stat().st_size)
