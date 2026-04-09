"""Paperwrite CLI — academic paper vibe writing scaffolding tool."""

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


@click.group()
@click.version_option(version="0.1.0")
def main():
    """Paperwrite — 学术论文 vibe writing 脚手架工具"""
    pass


@main.command()
@click.argument("name")
def init(name):
    """创建论文项目 NAME/"""
    target = Path.cwd() / name
    if target.exists():
        click.echo(f"Error: '{name}' already exists.", err=True)
        sys.exit(1)

    # Create directories
    for d in templates.DIRS:
        (target / d).mkdir(parents=True, exist_ok=True)

    # Write template files
    for rel_path, content in templates.FILES.items():
        file_path = target / rel_path
        file_content = content
        if rel_path == "paper/main.tex":
            file_content = content.replace("__TITLE__", name)
        file_path.write_text(file_content, encoding="utf-8")

    # Write README
    readme_content = templates.README_TEMPLATE.format(title=name)
    (target / "README.md").write_text(readme_content, encoding="utf-8")

    # git init
    subprocess.run(["git", "init"], cwd=target, capture_output=True)
    subprocess.run(["git", "add", "-A"], cwd=target, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", f"init: {name} paperwrite project"],
        cwd=target,
        capture_output=True,
    )

    click.echo(f"Created '{name}/' with paperwrite structure.")
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

    sections = [
        ("Sparks (思考层)", "sparks/", [
            "motivation.md", "innovations.md", "experiments.md",
            "results.md", "related_work.md", "writing_log.md", "questions.md",
        ]),
        ("Outline (大纲层)", "outline/", [
            "structure.md", "abstract.md", "introduction.md", "related_work.md",
            "method.md", "experiments.md", "results.md", "discussion.md", "conclusion.md",
        ]),
        ("Paper (输出层)", "paper/sections/", [
            "abstract.tex", "introduction.tex", "related_work.tex", "method.tex",
            "experiments.tex", "results.tex", "discussion.tex", "conclusion.tex",
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
                content = full_path.read_text(encoding="utf-8").strip()
                template_key = rel_path
                template_content = templates.TEMPLATE_SIGNATURES.get(template_key, "")
                if content == template_content:
                    symbol = click.style("  x", fg="red")
                    label = "not started"
                else:
                    symbol = click.style("  +", fg="green")
                    label = "written"
                    done += 1
            click.echo(f"{symbol} {fname:<25} {label}")

    click.echo()
    click.echo(f"Progress: {done}/{total} files written")

    if done == 0:
        phase = "Spark — start with sparks/motivation.md"
    elif done <= 7:
        phase = "Spark"
    elif done <= 16:
        phase = "Outline"
    elif done < total:
        phase = "Draft"
    else:
        phase = "Polish"
    click.echo(f"Phase: {phase}")
