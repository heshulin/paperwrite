# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

paperwrite is a CLI scaffolding tool for structured academic paper writing ("vibe writing"). The core principle is "think before you write" — users progress through three layers: sparks (free thinking in Markdown) → outline (paragraph-level outlines in Markdown) → paper (final LaTeX).

## Build & Run Commands

```bash
pip install -e .                # Install in development mode

# CLI commands (all run inside a paper project, except init/template)
paperwrite init <name>          # Create project (interactive template selection)
paperwrite init <name> -t acl_long  # Create with specific template
paperwrite build                # Compile PDF (requires tectonic)
paperwrite status               # Show writing progress per file
paperwrite count                # Word count per section
paperwrite doctor               # Check dependencies and project integrity
paperwrite section appendix     # Add a new section (outline + tex + main.tex update)
paperwrite ref add paper.pdf    # Add reference PDF + generate reading note
paperwrite ref list             # List references and note status
paperwrite ref note <name>      # Open/create reading note for a paper
paperwrite template import <path>  # Import custom conference template (ZIP or dir)
paperwrite template list        # List all available templates (built-in + custom)

make pdf                        # Alternative: build via Makefile
make clean                      # Clean build artifacts
```

No tests, no linting configured.

## Architecture

**The tool** (`cli/` package, entry point `cli.cli:main`):

- `cli/cli.py` — Click-based CLI with 8 top-level commands (`init`, `build`, `status`, `count`, `doctor`, `section`) and 2 command groups (`ref` with `add`/`list`/`note`, `template` with `import`/`list`). Project root is found by walking up from cwd looking for `paper/main.tex` (`_find_project_root()`). Template key is read from `.paperwrite` config first, then detected from existing sections (`_detect_template_key()`).

- `cli/templates.py` — Multi-template system. `TEMPLATES` dict for 6 built-in templates. Custom templates stored at `~/.paperwrite/templates/{key}/template.conf` (configparser format). `get_template(key)` looks up built-in first, then custom. `build_files_for_template(key)` assembles full file dict; for custom templates, also copies .sty/.cls/.bst resource files. Unknown sections get generic outline templates via `generic_outline_template()`.

- `cli/tex_parser.py` — LaTeX regex parser for importing custom templates. Extracts `\documentclass`, `\section{}` titles, `\bibliographystyle` from .tex files. `SECTION_TITLES` dict maps canonical keys to display titles (shared with templates.py to avoid circular imports). `find_main_tex()` locates the primary .tex file in a directory.

**Generated paper project** (output of `paperwrite init`):

- `sparks/` — 7 fixed Markdown files (motivation, innovations, experiments, results, related_work, writing_log, questions). Always the same regardless of template.
- `outline/` — `structure.md` + one `.md` per template section (varies by template, e.g. NeurIPS gets `broader_impact.md`, ACL gets `limitations.md`).
- `paper/` — `main.tex` pulls in `preamble.tex` + `sections/*.tex` via `\input`. `references.bib` for citations. Output goes to `paper/build/`.
- `refs/`, `scripts/` — for papers, notes, data, figure/table scripts.
- `.paperwrite` — configparser file storing the template key used at init.

Writing workflow is strictly upstream-first: sparks → outline → paper. Changes should always propagate from upstream to downstream.
