"""Paperwrite CLI — academic paper vibe writing scaffolding tool."""

import re
import os
import shutil
import subprocess
import sys
from pathlib import Path

import click

from . import templates


def _find_project_root():
    """Walk up from cwd to find a paperwrite project (has paper/main.tex)."""
    p = Path.cwd()
    while p != p.parent:
        if (p / "paper" / "main.tex").exists():
            return p
        p = p.parent
    return None


def _detect_template_key(root: Path) -> str:
    """Detect which template a project was created with by checking sections."""
    sections_dir = root / "paper" / "sections"
    if not sections_dir.exists():
        return "default"

    existing = {f.stem for f in sections_dir.glob("*.tex")}

    for key, tpl in templates.TEMPLATES.items():
        if key == "default":
            continue
        tpl_sections = set(tpl["sections"])
        # If all template-specific sections exist, it's likely this template
        if tpl_sections.issubset(existing):
            return key

    return "default"


def _normalize(text: str) -> str:
    """Normalize text for comparison: strip trailing whitespace per line, remove blank lines."""
    lines = [line.rstrip() for line in text.split("\n")]
    return "\n".join(line for line in lines if line.strip())


@click.group()
@click.version_option(version="0.1.0")
def main():
    """Paperwrite — 学术论文 vibe writing 脚手架工具"""
    pass


@main.command()
@click.argument("name")
@click.option("--template", "-t", "template_key", default=None,
              help="指定模板 (default/acl_long/acl_short/neurips/cvpr/ieee)")
def init(name, template_key):
    """创建论文项目 NAME/"""
    available = list(templates.TEMPLATES.keys())

    # Interactive selection if no template specified
    if template_key is None:
        click.echo("请选择论文模板：\n")
        for i, key in enumerate(available, 1):
            tpl = templates.TEMPLATES[key]
            click.echo(f"  {i}. {key:<12} — {tpl['description']}")
        click.echo()

        while True:
            choice = click.prompt("请输入编号或模板名", type=str)
            # Accept number or name
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(available):
                    template_key = available[idx]
                    break
            elif choice in available:
                template_key = choice
                break
            click.echo(f"无效选择，请输入 1-{len(available)} 或模板名")
    elif template_key not in available:
        click.echo(f"Error: unknown template '{template_key}'.", err=True)
        click.echo(f"Available: {', '.join(available)}", err=True)
        sys.exit(1)

    target = Path.cwd() / name
    if target.exists():
        click.echo(f"Error: '{name}' already exists.", err=True)
        sys.exit(1)

    tpl = templates.TEMPLATES[template_key]

    # Create directories
    for d in templates.SHARED_DIRS:
        (target / d).mkdir(parents=True, exist_ok=True)

    # Build files for this template
    files = templates.build_files_for_template(template_key)

    # Write template files
    for rel_path, content in files.items():
        file_path = target / rel_path
        file_content = content
        if rel_path == "paper/main.tex":
            file_content = content.replace("__TITLE__", name)
        file_path.write_text(file_content, encoding="utf-8")

    # Write README
    readme_content = templates.build_readme(name, template_key)
    (target / "README.md").write_text(readme_content, encoding="utf-8")

    # Write .paperwrite config to remember the template
    config_content = f"[paperwrite]\ntemplate = {template_key}\n"
    (target / ".paperwrite").write_text(config_content, encoding="utf-8")

    # git init
    subprocess.run(["git", "init"], cwd=target, capture_output=True)
    subprocess.run(["git", "add", "-A"], cwd=target, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", f"init: {name} paperwrite project ({template_key})"],
        cwd=target,
        capture_output=True,
    )

    click.echo(f"Created '{name}/' with template '{tpl['name']}'.")
    click.echo()
    click.echo("Next steps:")
    click.echo(f"  cd {name}")
    click.echo("  # Start writing in sparks/motivation.md")
    click.echo("  # Check progress with: paperwrite status")
    click.echo("  # Build PDF with: paperwrite build")


@main.command()
def build():
    """编译 PDF（需要 tectonic）"""
    root = _find_project_root()
    if not root:
        click.echo("Error: not in a paperwrite project (paper/main.tex not found).", err=True)
        sys.exit(1)

    paper_dir = root / "paper"
    build_dir = paper_dir / "build"
    build_dir.mkdir(exist_ok=True)

    tectonic = shutil.which("tectonic")
    if not tectonic:
        click.echo("Error: tectonic not found. Install it with:", err=True)
        click.echo("  brew install tectonic", err=True)
        click.echo("  conda install -c conda-forge tectonic", err=True)
        sys.exit(1)

    click.echo("Building PDF...")
    result = subprocess.run(
        [tectonic, "-o", "build", "main.tex"],
        cwd=paper_dir,
    )

    if result.returncode == 0:
        pdf_path = build_dir / "main.pdf"
        click.echo(f"Done: {pdf_path}")
    else:
        sys.exit(result.returncode)


@main.command()
def status():
    """显示写作进度"""
    root = _find_project_root()
    if not root:
        click.echo("Error: not in a paperwrite project (paper/main.tex not found).", err=True)
        sys.exit(1)

    template_key = _detect_template_key(root)
    template_sigs = templates.build_template_signatures(template_key)

    sections = [
        ("Sparks (思考层)", "sparks/", [
            "motivation.md", "innovations.md", "experiments.md",
            "results.md", "related_work.md", "writing_log.md", "questions.md",
        ]),
        ("Outline (大纲层)", "outline/", [
            f"{sec}.md" for sec in templates.TEMPLATES[template_key]["sections"]
        ]),
        ("Paper (输出层)", "paper/sections/", [
            f"{sec}.tex" for sec in templates.TEMPLATES[template_key]["sections"]
        ]),
    ]

    done = 0
    total = 0

    for section_name, prefix, files in sections:
        click.echo()
        click.echo(click.style(section_name, bold=True))
        for fname in files:
            total += 1
            rel_path = prefix + fname
            full_path = root / rel_path
            if not full_path.exists():
                symbol = click.style("  -", fg="yellow")
                label = "missing"
            else:
                content = full_path.read_text(encoding="utf-8")
                template_content = template_sigs.get(rel_path, "")
                if template_content and _normalize(content) == _normalize(template_content):
                    symbol = click.style("  ✗", fg="red")
                    label = "not started"
                else:
                    symbol = click.style("  ✓", fg="green")
                    label = "written"
                    done += 1
            click.echo(f"{symbol} {fname:<25} {label}")

    click.echo()
    click.echo(f"Progress: {done}/{total} files written")

    if done == 0:
        phase = "Spark — start with sparks/motivation.md"
    elif done <= 7:
        phase = "Spark"
    elif done <= 7 + len(templates.TEMPLATES[template_key]["sections"]):
        phase = "Outline"
    elif done < total:
        phase = "Draft"
    else:
        phase = "Polish"
    click.echo(f"Phase: {phase}")


@main.command()
def doctor():
    """检查项目依赖和完整性"""
    issues = []

    # Check tectonic
    tectonic = shutil.which("tectonic")
    if tectonic:
        click.echo(click.style("✓", fg="green") + f" tectonic: {tectonic}")
    else:
        click.echo(click.style("✗", fg="red") + " tectonic: not found")
        issues.append("Install tectonic: brew install tectonic")

    # Check project root
    root = _find_project_root()
    if root:
        click.echo(click.style("✓", fg="green") + f" project root: {root}")
    else:
        click.echo(click.style("✗", fg="red") + " not in a paperwrite project")
        issues.append("Run this command inside a paperwrite project")
        click.echo()
        for issue in issues:
            click.echo(click.style(f"  → {issue}", fg="yellow"))
        sys.exit(1)

    # Check key files
    key_files = [
        "paper/main.tex",
        "paper/preamble.tex",
        "paper/references.bib",
    ]
    for rel in key_files:
        if (root / rel).exists():
            click.echo(click.style("✓", fg="green") + f" {rel}")
        else:
            click.echo(click.style("✗", fg="red") + f" {rel} missing")
            issues.append(f"Missing {rel}")

    # Check template config
    config_path = root / ".paperwrite"
    if config_path.exists():
        import configparser
        config = configparser.ConfigParser()
        config.read(config_path)
        tpl = config.get("paperwrite", "template", fallback="unknown")
        click.echo(click.style("✓", fg="green") + f" template: {tpl}")
    else:
        click.echo(click.style("-", fg="yellow") + " .paperwrite config not found")

    # Check sparks/ outline/ directories
    for dirname in ["sparks", "outline", "paper/sections"]:
        if (root / dirname).exists():
            count = len(list((root / dirname).glob("*")))
            click.echo(click.style("✓", fg="green") + f" {dirname}/ ({count} files)")
        else:
            click.echo(click.style("✗", fg="red") + f" {dirname}/ missing")
            issues.append(f"Missing {dirname}/ directory")

    click.echo()
    if issues:
        click.echo(click.style(f"Found {len(issues)} issue(s):", fg="yellow"))
        for issue in issues:
            click.echo(click.style(f"  → {issue}", fg="yellow"))
    else:
        click.echo(click.style("All checks passed!", fg="green"))


@main.command()
def count():
    """统计各节字数"""
    root = _find_project_root()
    if not root:
        click.echo("Error: not in a paperwrite project (paper/main.tex not found).", err=True)
        sys.exit(1)

    def word_count(text: str) -> int:
        """Count words, ignoring LaTeX commands and comments."""
        # Remove comments
        text = re.sub(r'%.*$', '', text, flags=re.MULTILINE)
        # Remove LaTeX commands
        text = re.sub(r'\\[a-zA-Z]+(\{[^}]*\})*', '', text)
        # Remove braces and special chars
        text = re.sub(r'[{}\\]', ' ', text)
        return len(text.split())

    layers = [
        ("Sparks", "sparks/", ".md"),
        ("Outline", "outline/", ".md"),
        ("Paper", "paper/sections/", ".tex"),
    ]

    total_words = 0
    for layer_name, prefix, ext in layers:
        layer_dir = root / prefix
        if not layer_dir.exists():
            continue
        files = sorted(layer_dir.glob(f"*{ext}"))
        if not files:
            continue

        click.echo(click.style(f"\n{layer_name}", bold=True))
        layer_total = 0
        for f in files:
            content = f.read_text(encoding="utf-8")
            wc = word_count(content)
            layer_total += wc
            click.echo(f"  {f.name:<30} {wc:>5} words")
        click.echo(f"  {'':<30} {layer_total:>5} words")
        total_words += layer_total

    click.echo()
    click.echo(f"Total: {total_words} words")


@main.command()
@click.argument("name")
def section(name):
    """新增小节 NAME（在 outline/ 和 paper/sections/ 中创建）"""
    root = _find_project_root()
    if not root:
        click.echo("Error: not in a paperwrite project (paper/main.tex not found).", err=True)
        sys.exit(1)

    # Create outline file
    outline_path = root / "outline" / f"{name}.md"
    if outline_path.exists():
        click.echo(f"Warning: {outline_path} already exists, skipping.", err=True)
    else:
        title = name.replace("_", " ").title()
        outline_path.write_text(
            f"# {title} 大纲\n\n## 要点\n",
            encoding="utf-8",
        )
        click.echo(f"Created: outline/{name}.md")

    # Create tex file
    tex_path = root / "paper" / "sections" / f"{name}.tex"
    if tex_path.exists():
        click.echo(f"Warning: {tex_path} already exists, skipping.", err=True)
    else:
        title = name.replace("_", " ").title()
        tex_path.write_text(
            f"\\section{{{title}}}\n% TODO: 从 outline/{name}.md 转写\n",
            encoding="utf-8",
        )
        click.echo(f"Created: paper/sections/{name}.tex")

    # Add \input to main.tex
    main_tex = root / "paper" / "main.tex"
    if main_tex.exists():
        content = main_tex.read_text(encoding="utf-8")
        input_line = f"\\input{{sections/{name}}}"
        if input_line in content:
            click.echo(f"Already in main.tex: {input_line}")
        else:
            # Insert before \end{document}
            content = content.replace(
                "\\end{document}",
                f"{input_line}\n\n\\end{{document}}",
            )
            main_tex.write_text(content, encoding="utf-8")
            click.echo(f"Added to main.tex: {input_line}")

    click.echo()
    click.echo("Done! Write your outline in outline/%s.md first." % name)
