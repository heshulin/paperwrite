"""Paperwrite CLI — academic paper vibe writing scaffolding tool."""

import re
import os
import configparser
import shutil
import subprocess
import sys
import tempfile
import zipfile
from datetime import date
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
    """Detect which template a project was created with."""
    # First check .paperwrite config (always accurate)
    config_path = root / ".paperwrite"
    if config_path.exists():
        config = configparser.ConfigParser()
        config.read(config_path)
        stored = config.get("paperwrite", "template", fallback=None)
        if stored and stored in templates.get_all_template_keys():
            return stored

    # Fall back to section matching
    sections_dir = root / "paper" / "sections"
    if not sections_dir.exists():
        return "default"

    existing = {f.stem for f in sections_dir.glob("*.tex")}

    # Check built-in templates
    for key, tpl in templates.TEMPLATES.items():
        if key == "default":
            continue
        tpl_sections = set(tpl["sections"])
        if tpl_sections.issubset(existing):
            return key

    # Check custom templates
    for key in templates.get_custom_template_keys():
        try:
            tpl = templates.load_custom_template(key)
            if set(tpl["sections"]).issubset(existing):
                return key
        except KeyError:
            continue

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


# ── ref 命令组 ──────────────────────────────────────────────────────────


@main.group()
def ref():
    """管理参考文献和精读笔记"""
    pass


@ref.command()
@click.argument("pdf_path", type=click.Path(exists=True))
@click.option("--move", "do_move", is_flag=True, default=False,
              help="移动文件而非复制")
@click.option("--no-spark", "update_spark", is_flag=True, flag_value=False,
              default=True, help="不更新 sparks/related_work.md")
def add(pdf_path, do_move, update_spark):
    """添加论文 PDF 并生成精读笔记"""
    root = _find_project_root()
    if not root:
        click.echo("Error: 不在 paperwrite 项目中 (paper/main.tex 未找到)。", err=True)
        sys.exit(1)

    src = Path(pdf_path)
    if src.suffix.lower() != ".pdf":
        click.echo("Error: 请提供 PDF 文件。", err=True)
        sys.exit(1)

    stem = src.stem
    name = src.name

    # Ensure directories exist
    papers_dir = root / "refs" / "papers"
    notes_dir = root / "refs" / "notes"
    papers_dir.mkdir(parents=True, exist_ok=True)
    notes_dir.mkdir(parents=True, exist_ok=True)

    paper_dest = papers_dir / name
    note_dest = notes_dir / f"{stem}.md"

    # Copy/move PDF
    if paper_dest.exists() and paper_dest.resolve() != src.resolve():
        click.echo(f"Warning: refs/papers/{name} 已存在，跳过。", err=True)
    elif not paper_dest.exists():
        if do_move:
            shutil.move(str(src), str(paper_dest))
            click.echo(f"已移动 PDF → refs/papers/{name}")
        else:
            shutil.copy2(str(src), str(paper_dest))
            click.echo(f"已复制 PDF → refs/papers/{name}")
    else:
        click.echo(f"PDF 已在 refs/papers/{name}，跳过。")

    # Generate note
    if note_dest.exists():
        click.echo(f"笔记已存在: refs/notes/{stem}.md，跳过。")
    else:
        content = templates.REF_NOTE_TEMPLATE.format(
            title=stem, date=date.today().isoformat()
        )
        note_dest.write_text(content, encoding="utf-8")
        click.echo(f"已创建笔记: refs/notes/{stem}.md")

    # Update sparks/related_work.md
    if update_spark:
        spark_path = root / "sparks" / "related_work.md"
        if spark_path.exists():
            link_target = f"refs/notes/{stem}.md)"
            spark_content = spark_path.read_text(encoding="utf-8")
            if link_target not in spark_content:
                entry = f"\n- [{stem}](../refs/notes/{stem}.md)\n"
                spark_path.write_text(spark_content.rstrip() + entry, encoding="utf-8")
                click.echo("已添加到 sparks/related_work.md")


@ref.command("list")
def ref_list():
    """列出所有参考文献及其笔记状态"""
    root = _find_project_root()
    if not root:
        click.echo("Error: 不在 paperwrite 项目中 (paper/main.tex 未找到)。", err=True)
        sys.exit(1)

    papers_dir = root / "refs" / "papers"
    if not papers_dir.exists():
        click.echo("refs/papers/ 目录为空。")
        return

    pdfs = sorted(papers_dir.glob("*.pdf"))
    if not pdfs:
        click.echo("refs/papers/ 目录为空。")
        return

    note_count = 0
    for pdf in pdfs:
        note_path = root / "refs" / "notes" / f"{pdf.stem}.md"
        has_note = note_path.exists()
        if has_note:
            note_count += 1
            symbol = click.style("  ✓", fg="green")
        else:
            symbol = click.style("  ✗", fg="red")
        click.echo(f"{symbol} {pdf.name}")

    click.echo(f"\n共 {len(pdfs)} 篇论文，{note_count} 篇有笔记")


@ref.command()
@click.argument("paper_name")
def note(paper_name):
    """打开/创建论文精读笔记"""
    root = _find_project_root()
    if not root:
        click.echo("Error: 不在 paperwrite 项目中 (paper/main.tex 未找到)。", err=True)
        sys.exit(1)

    # Resolve paper name (with or without .pdf suffix)
    stem = paper_name
    if stem.endswith(".pdf"):
        stem = stem[:-4]

    paper_file = root / "refs" / "papers" / f"{stem}.pdf"
    if not paper_file.exists():
        # Also try as literal filename (in case stem contains dots)
        paper_file = root / "refs" / "papers" / paper_name
        if not paper_file.exists():
            click.echo(f"Error: 未找到论文 '{paper_name}'。", err=True)
            click.echo("使用 paperwrite ref list 查看所有论文。", err=True)
            sys.exit(1)
        stem = paper_file.stem

    notes_dir = root / "refs" / "notes"
    notes_dir.mkdir(parents=True, exist_ok=True)
    note_path = notes_dir / f"{stem}.md"

    if not note_path.exists():
        content = templates.REF_NOTE_TEMPLATE.format(
            title=stem, date=date.today().isoformat()
        )
        note_path.write_text(content, encoding="utf-8")
        click.echo(f"已创建笔记: refs/notes/{stem}.md")

    click.echo(str(note_path))


# ── template 命令组 ─────────────────────────────────────────────────────


@main.group()
def template():
    """管理论文模板"""
    pass


@template.command("import")
@click.argument("path", type=click.Path(exists=True))
@click.option("--name", "-n", "tpl_name", default=None,
              help="模板名称 (默认从目录/文件名推断)")
@click.option("--description", "-d", "tpl_desc", default=None,
              help="模板描述")
def template_import(path, tpl_name, tpl_desc):
    """导入自定义会议模板 (ZIP 文件或目录)"""
    from . import tex_parser

    src = Path(path)

    # Handle ZIP files
    if src.is_file() and src.suffix.lower() == ".zip":
        tmp_dir = tempfile.mkdtemp(prefix="paperwrite_")
        try:
            with zipfile.ZipFile(src, 'r') as zf:
                zf.extractall(tmp_dir)
            # Find the actual content directory (ZIPs often have a nested dir)
            search_dir = Path(tmp_dir)
            tex_files = list(search_dir.rglob("*.tex"))
            if not tex_files:
                click.echo("Error: ZIP 中未找到 .tex 文件。", err=True)
                sys.exit(1)
            # Use the common parent of all tex files
            parents = set(f.parent for f in tex_files)
            if len(parents) == 1:
                search_dir = parents.pop()
            else:
                # Use the directory with the most tex files
                search_dir = max(parents, key=lambda d: len(list(d.glob("*.tex"))))
        except zipfile.BadZipFile:
            click.echo("Error: 无效的 ZIP 文件。", err=True)
            sys.exit(1)
    elif src.is_dir():
        search_dir = src
    else:
        click.echo("Error: 请提供 ZIP 文件或目录。", err=True)
        sys.exit(1)

    # Find main .tex file
    main_tex = tex_parser.find_main_tex(search_dir)
    if not main_tex:
        click.echo("Error: 未找到 .tex 文件。", err=True)
        sys.exit(1)

    click.echo(f"解析: {main_tex.name}")

    # Parse .tex file
    parsed = tex_parser.parse_tex_file(main_tex)

    if not parsed["section_keys"]:
        click.echo("Error: 无法自动解析章节结构。请检查 .tex 文件是否包含 \\section{} 命令。", err=True)
        sys.exit(1)

    # Derive template key
    if tpl_name:
        key = tpl_name.lower().replace(" ", "_").replace("-", "_")
    else:
        key = search_dir.name.lower().replace(" ", "_").replace("-", "_")
        # Clean up common suffixes
        for suffix in ("_template", "_tex", "_latex", "-main"):
            if key.endswith(suffix):
                key = key[:-len(suffix)]

    # Validate key
    if key in templates.TEMPLATES:
        click.echo(f"Error: 模板名 '{key}' 与内置模板冲突。请使用 --name 指定其他名称。", err=True)
        sys.exit(1)

    # Find resource files
    resource_files = tex_parser.find_resource_files(search_dir)

    # Create template directory
    tpl_dir = templates.CUSTOM_TEMPLATES_DIR / key
    tpl_dir.mkdir(parents=True, exist_ok=True)

    # Write template.conf
    config = configparser.ConfigParser()
    extra_preamble = "\n".join(parsed.get("usepackage_lines", []))
    config["template"] = {
        "name": tpl_name or key,
        "description": tpl_desc or f"自定义模板 (从 {main_tex.name} 导入)",
        "documentclass": parsed["documentclass"],
        "bibstyle": parsed["bibstyle"] or r"\bibliographystyle{plain}",
        "sections": ",".join(parsed["section_keys"]),
        "source_file": main_tex.name,
        "extra_preamble": extra_preamble,
    }

    # Copy resource files
    if resource_files:
        config["files"] = {}
        for res_file in resource_files:
            dest_name = res_file.name
            dest = f"paper/{dest_name}"
            config["files"][dest_name] = dest
            shutil.copy2(str(res_file), str(tpl_dir / dest_name))

    with open(tpl_dir / "template.conf", "w", encoding="utf-8") as f:
        config.write(f)

    # Copy original .tex for reference
    shutil.copy2(str(main_tex), str(tpl_dir / main_tex.name))

    # Print results
    click.echo(f"\n已导入模板 '{key}':")
    click.echo(f"  documentclass: {parsed['documentclass']}")
    click.echo(f"  sections: {', '.join(parsed['section_keys'])}")
    if parsed['bibstyle']:
        click.echo(f"  bibstyle: {parsed['bibstyle']}")
    if parsed.get("usepackage_lines"):
        click.echo(f"  宏包: {len(parsed['usepackage_lines'])} 个 \\usepackage 已提取")
    if resource_files:
        click.echo(f"  资源文件: {', '.join(f.name for f in resource_files)}")
    click.echo(f"\n使用: paperwrite init my-paper -t {key}")


@template.command("list")
def template_list():
    """列出所有可用模板 (内置 + 自定义)"""
    # Built-in templates
    click.echo(click.style("内置模板:", bold=True))
    for key, tpl in templates.TEMPLATES.items():
        sections_count = len(tpl["sections"])
        click.echo(f"  {key:<12} — {tpl['description']} ({sections_count} 节)")

    # Custom templates
    custom_keys = templates.get_custom_template_keys()
    if custom_keys:
        click.echo()
        click.echo(click.style("自定义模板:", bold=True))
        for key in custom_keys:
            try:
                tpl = templates.load_custom_template(key)
                sections_count = len(tpl["sections"])
                click.echo(f"  {key:<12} — {tpl['description']} ({sections_count} 节)")
            except KeyError:
                click.echo(f"  {key:<12} — (配置文件损坏)")


# ── init 命令 ──────────────────────────────────────────────────────────


@main.command()
@click.argument("name")
@click.option("--template", "-t", "template_key", default=None,
              help="指定模板 (内置或自定义模板名)")
def init(name, template_key):
    """创建论文项目 NAME/"""
    available = templates.get_all_template_keys()
    builtin_keys = list(templates.TEMPLATES.keys())

    # Interactive selection if no template specified
    if template_key is None:
        click.echo("请选择论文模板：\n")
        click.echo(click.style("内置模板:", bold=True))
        for i, key in enumerate(builtin_keys, 1):
            tpl = templates.TEMPLATES[key]
            click.echo(f"  {i}. {key:<12} — {tpl['description']}")

        custom_keys = templates.get_custom_template_keys()
        if custom_keys:
            click.echo()
            click.echo(click.style("自定义模板:", bold=True))
            for i, key in enumerate(custom_keys, len(builtin_keys) + 1):
                try:
                    tpl = templates.load_custom_template(key)
                    click.echo(f"  {i}. {key:<12} — {tpl['description']}")
                except KeyError:
                    click.echo(f"  {i}. {key:<12} — (配置文件损坏)")
        click.echo()

        while True:
            choice = click.prompt("请输入编号或模板名", type=str)
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

    tpl = templates.get_template(template_key)

    # Create directories
    for d in templates.SHARED_DIRS:
        (target / d).mkdir(parents=True, exist_ok=True)

    # Build files for this template
    files = templates.build_files_for_template(template_key)

    # Write template files
    for rel_path, content in files.items():
        file_path = target / rel_path
        if rel_path == "paper/main.tex" and isinstance(content, str):
            content = content.replace("__TITLE__", name)
        # Ensure parent directory exists (for resource files like paper/*.sty)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            file_path.write_bytes(content)
        else:
            file_path.write_text(content, encoding="utf-8")

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
    tpl = templates.get_template(template_key)

    sections = [
        ("Sparks (思考层)", "sparks/", [
            "motivation.md", "innovations.md", "experiments.md",
            "results.md", "related_work.md", "writing_log.md", "questions.md",
        ]),
        ("Outline (大纲层)", "outline/", [
            f"{sec}.md" for sec in tpl["sections"]
        ]),
        ("Paper (输出层)", "paper/sections/", [
            f"{sec}.tex" for sec in tpl["sections"]
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
    elif done <= 7 + len(tpl["sections"]):
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
