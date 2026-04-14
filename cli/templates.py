"""Multi-template system for paperwrite project scaffolding."""

import configparser
import re
from pathlib import Path

from .tex_parser import generic_outline_template, SECTION_TITLES

# ── Shared sparks templates (common to all paper types) ──────────────────

SPARKS_FILES = {
    "sparks/motivation.md": """\
# 研究动机

## 我们要解决什么问题？

## 为什么这个问题重要？

## 现有方案是什么？为什么不够好？

## 成功是什么样的？
""",
    "sparks/innovations.md": """\
# 核心贡献

1. ...
2. ...
3. ...

## 每个贡献为什么重要？

## 一句话版本：这篇论文做了什么？
""",
    "sparks/experiments.md": """\
# 实验设计

## 数据集

## Baselines

## 评估指标

## 消融实验设计

## 预期结果
""",
    "sparks/results.md": """\
# 结果解读

## 主实验结果

## 关键发现

## 意外发现

## 数据说明了什么故事？
""",
    "sparks/related_work.md": """\
# 相关工作笔记

<!-- 格式：论文名 — 做了什么 — 和我们的区别 -->
""",
    "sparks/writing_log.md": """\
# 写作日志

<!-- 记录写作过程中的决策和思考，方便跨 session 保持连续性 -->
""",
    "sparks/questions.md": """\
# 待解决问题

## 技术问题

## 写作问题

## 预判 Reviewer 会问什么？
""",
}

# ── Shared outline template generator ────────────────────────────────────

OUTLINE_TEMPLATES = {
    "structure": """\
# 论文结构

{page_budget}

## 各节之间的依赖关系

## 读者阅读顺序 vs 写作顺序
""",
    "abstract": """\
# Abstract 大纲

## 问题（1-2句）

## 方法（1-2句）

## 结果（1-2句）

## 意义（1句）
""",
    "introduction": """\
# Introduction 大纲

## Para 1: Hook — 用什么例子引入问题

## Para 2: 形式化问题定义

## Para 3: 现有方案为什么不行（引用 X, Y, Z）

## Para 4: 我们的方法一句话

## Para 5: 贡献列表
""",
    "related_work": """\
# Related Work 大纲

## 分类方式（按方法/按问题/按时间线）

## 类别 1:

## 类别 2:

## 类别 3:

## 和我们工作的关系总结
""",
    "method": """\
# Method 大纲

## 整体框架概述

## 模块 1:

## 模块 2:

## 模块 3:

## 训练/推理流程
""",
    "experiments": """\
# Experiments 大纲

## 实验设置
- 数据集
- Baselines
- 实现细节

## 主实验（对应哪个 Research Question）

## 消融实验

## 分析实验
""",
    "results": """\
# Results 大纲

## 主表结果分析

## 关键发现 1:

## 关键发现 2:

## 可视化说明了什么
""",
    "analysis": """\
# Analysis 大纲

## 深入分析

## 案例分析

## 定性分析
""",
    "discussion": """\
# Discussion 大纲

## 结果意味着什么

## 局限性

## 潜在的负面社会影响（如需要）
""",
    "limitations": """\
# Limitations 大纲

## 方法层面的局限性

## 数据层面的局限性

## 适用范围
""",
    "broader_impact": """\
# Broader Impact 大纲

## 正面社会影响

## 潜在风险和负面后果

## 缓解措施

## 公平性和伦理考量
""",
    "conclusion": """\
# Conclusion 大纲

## 总结（呼应 Introduction）

## Future Work
""",
}

# ── Shared LaTeX section template ────────────────────────────────────────

LATEX_SECTION_TEMPLATE = """\
\\section{{{title}}}
% TODO: 从 outline/{name}.md 转写
"""

LATEX_SUBSECTION_TEMPLATE = """\
\\section{{{title}}}
% TODO: 从 outline/{name}.md 转写
"""

# ── Template definitions ─────────────────────────────────────────────────

TEMPLATES = {
    "default": {
        "name": "默认模板",
        "description": "通用学术论文结构",
        "page_budget": "\n".join([
            "- Abstract (~150 words)",
            "- Introduction (~1.5 pages)",
            "- Related Work (~1.5 pages)",
            "- Method (~2 pages)",
            "- Experiments (~1 page)",
            "- Results (~1.5 pages)",
            "- Discussion (~0.5 pages)",
            "- Conclusion (~0.5 pages)",
        ]),
        "sections": [
            "abstract", "introduction", "related_work", "method",
            "experiments", "results", "discussion", "conclusion",
        ],
        "documentclass": r"\documentclass[11pt]{article}",
        "extra_preamble": "",
        "extra_bibstyle": r"\bibliographystyle{plain}",
    },
    "acl_long": {
        "name": "ACL Long Paper",
        "description": "ACL 长文，含 Limitations 节",
        "page_budget": "\n".join([
            "- Abstract (~150 words)",
            "- Introduction (~1.5 pages)",
            "- Related Work (~1 page)",
            "- Method (~2 pages)",
            "- Experiments (~1 page)",
            "- Results (~1 page)",
            "- Analysis (~0.5 pages)",
            "- Limitations (~0.5 pages)",
            "- Conclusion (~0.5 pages)",
            "总计: 最多 8 页正文 + 无限制参考文献",
        ]),
        "sections": [
            "abstract", "introduction", "related_work", "method",
            "experiments", "results", "analysis", "limitations", "conclusion",
        ],
        "documentclass": r"\documentclass[11pt]{article}",
        "extra_preamble": r"""
% ACL Rolling Review style
% \usepackage{acl}
% 如使用 acl style，请取消注释并删除下一行
""",
        "extra_bibstyle": r"\bibliographystyle{acl_natbib}",
    },
    "acl_short": {
        "name": "ACL Short Paper",
        "description": "ACL 短文，4 页正文，含 Limitations 节",
        "page_budget": "\n".join([
            "- Abstract (~100 words)",
            "- Introduction (~0.5 pages)",
            "- Method (~1 page)",
            "- Experiments & Results (~1.5 pages)",
            "- Limitations (~0.3 pages)",
            "- Conclusion (~0.2 pages)",
            "总计: 最多 4 页正文 + 无限制参考文献",
        ]),
        "sections": [
            "abstract", "introduction", "method",
            "experiments", "results", "limitations", "conclusion",
        ],
        "documentclass": r"\documentclass[11pt]{article}",
        "extra_preamble": r"""
% ACL Rolling Review style
% \usepackage{acl}
""",
        "extra_bibstyle": r"\bibliographystyle{acl_natbib}",
    },
    "neurips": {
        "name": "NeurIPS Paper",
        "description": "NeurIPS，含 Broader Impact 节",
        "page_budget": "\n".join([
            "- Abstract (~150 words)",
            "- Introduction (~1 page)",
            "- Related Work (~1 page)",
            "- Method (~2 pages)",
            "- Experiments (~1 page)",
            "- Results (~1.5 pages)",
            "- Broader Impact (~0.5 pages)",
            "- Conclusion (~0.5 pages)",
            "总计: 最多 9 页正文 + 无限制参考文献",
        ]),
        "sections": [
            "abstract", "introduction", "related_work", "method",
            "experiments", "results", "broader_impact", "conclusion",
        ],
        "documentclass": r"\documentclass{article}",
        "extra_preamble": r"""
% NeurIPS style
% \usepackage[final]{neurips_2025}
% 如使用 neurips style，请取消注释并下载对应 .sty 文件
""",
        "extra_bibstyle": r"\bibliographystyle{plain}",
    },
    "cvpr": {
        "name": "CVPR Paper",
        "description": "CVPR，8 页正文",
        "page_budget": "\n".join([
            "- Abstract (~150 words)",
            "- Introduction (~1 page)",
            "- Related Work (~1 page)",
            "- Method (~2 pages)",
            "- Experiments (~1.5 pages)",
            "- Results (~1 page)",
            "- Discussion (~0.5 pages)",
            "- Conclusion (~0.5 pages)",
            "总计: 最多 8 页正文 + 无限制参考文献",
        ]),
        "sections": [
            "abstract", "introduction", "related_work", "method",
            "experiments", "results", "discussion", "conclusion",
        ],
        "documentclass": r"\documentclass[10pt, twocolumn, letterpaper]{article}",
        "extra_preamble": r"""
% CVPR style
% \usepackage{cvpr}
% 如使用 cvpr style，请取消注释并下载对应 .sty 文件
""",
        "extra_bibstyle": r"\bibliographystyle{ieee_fullname}",
    },
    "ieee": {
        "name": "IEEE Conference",
        "description": "IEEE 会议论文，含关键词",
        "page_budget": "\n".join([
            "- Abstract (~150 words)",
            "- Introduction (~1 page)",
            "- Related Work (~1 page)",
            "- Methodology (~2 pages)",
            "- Results and Discussion (~1.5 pages)",
            "- Conclusion (~0.5 pages)",
            "总计: 通常 6 页",
        ]),
        "sections": [
            "abstract", "introduction", "related_work", "method",
            "experiments", "results", "discussion", "conclusion",
        ],
        "documentclass": r"\documentclass[conference]{IEEEtran}",
        "extra_preamble": r"""
% IEEE style - IEEEtran class handles most formatting
""",
        "extra_bibstyle": r"\bibliographystyle{IEEEtran}",
    },
}

# ── Directories (shared by all templates) ────────────────────────────────

SHARED_DIRS = [
    "sparks",
    "outline",
    "paper/sections",
    "paper/figures",
    "paper/tables",
    "paper/build",
    "refs/papers",
    "refs/notes",
    "refs/data",
    "scripts/figures",
    "scripts/tables",
]


REF_NOTE_TEMPLATE = """\
# {title}

> 添加日期: {date}

## 一句话总结

<!-- 用一句话描述这篇论文做了什么 -->

## 核心发现

-

## 方法要点

-

## 与我们工作的关系

<!-- 这篇论文对我们有什么启发？我们在哪些方面不同/更好？ -->

## 关键引用 / 摘抄

-

## 疑问 / 批判

-
"""


# ── Custom template storage ─────────────────────────────────────────────

CUSTOM_TEMPLATES_DIR = Path.home() / ".paperwrite" / "templates"


def get_custom_template_keys():
    """List keys of all imported custom templates."""
    if not CUSTOM_TEMPLATES_DIR.exists():
        return []
    return sorted(
        d.name for d in CUSTOM_TEMPLATES_DIR.iterdir()
        if d.is_dir() and (d / "template.conf").exists()
    )


def load_custom_template(key):
    """Load a custom template's metadata from template.conf.

    Returns a dict matching the TEMPLATES entry format.
    """
    conf_path = CUSTOM_TEMPLATES_DIR / key / "template.conf"
    if not conf_path.exists():
        raise KeyError(f"Custom template '{key}' not found")

    config = configparser.ConfigParser()
    config.read(conf_path)

    sections_str = config.get("template", "sections", fallback="")
    sections = [s.strip() for s in sections_str.split(",") if s.strip()]

    # Build page_budget from sections
    page_budget_lines = [f"- {s.replace('_', ' ').title()}" for s in sections]
    page_budget = "\n".join(page_budget_lines)

    return {
        "name": config.get("template", "name", fallback=key),
        "description": config.get("template", "description", fallback=""),
        "page_budget": page_budget,
        "sections": sections,
        "documentclass": config.get("template", "documentclass",
                                    fallback=r"\documentclass[11pt]{article}"),
        "extra_preamble": config.get("template", "extra_preamble", fallback=""),
        "extra_bibstyle": config.get("template", "bibstyle",
                                     fallback=r"\bibliographystyle{plain}"),
        "_custom": True,
        "_key": key,
    }


def get_all_template_keys():
    """Return built-in keys first, then custom keys."""
    return list(TEMPLATES.keys()) + get_custom_template_keys()


def get_template(key):
    """Get template dict by key — built-in first, then custom."""
    if key in TEMPLATES:
        return TEMPLATES[key]
    return load_custom_template(key)


# ── File generation ─────────────────────────────────────────────────────


def _escape_latex(text: str) -> str:
    """Escape LaTeX special characters in plain text (for \\title etc.)."""
    # Escape _ # $ % & { } ~ ^ in order — backslash first to avoid double-escaping
    text = text.replace('\\', '\\textbackslash{}')
    for ch in ('#', '$', '%', '&', '{', '}'):
        text = text.replace(ch, '\\' + ch)
    text = text.replace('~', '\\textasciitilde{}')
    text = text.replace('^', '\\textasciicircum{}')
    text = text.replace('_', '\\_')
    return text


def build_files_for_template(template_key: str) -> dict:
    """Build the complete FILES dict for a given template."""
    tpl = get_template(template_key)
    is_custom = tpl.get("_custom", False)
    files = {}

    # 1. sparks/ — always the same
    files.update(SPARKS_FILES)

    # 2. outline/ — generated from sections
    page_budget = tpl["page_budget"]
    files["outline/structure.md"] = OUTLINE_TEMPLATES["structure"].format(
        page_budget=page_budget
    )
    for sec in tpl["sections"]:
        if sec in OUTLINE_TEMPLATES:
            files[f"outline/{sec}.md"] = OUTLINE_TEMPLATES[sec]
        else:
            files[f"outline/{sec}.md"] = generic_outline_template(sec)

    # 3. paper/ — LaTeX files
    sections_input = "\n".join(
        rf"\input{{sections/{sec}}}" for sec in tpl["sections"]
    )

    # Handle abstract specially (it's \begin{abstract}, not \section)
    abstract_tex = r"\begin{abstract}" + "\n% TODO: 从 outline/abstract.md 转写\n\\end{abstract}\n"

    files["paper/main.tex"] = f"""{tpl['documentclass']}
\\input{{preamble}}

\\title{{__TITLE__}}
\\author{{Author Name}}
\\date{{\\today}}

\\begin{{document}}
\\maketitle

{sections_input}

{tpl['extra_bibstyle']}
\\bibliography{{references}}

\\end{{document}}
"""

    files["paper/preamble.tex"] = f"""% 基础宏包
\\usepackage[utf8]{{inputenc}}
\\usepackage{{amsmath,amssymb}}
\\usepackage{{graphicx}}
\\usepackage{{booktabs}}
\\usepackage{{hyperref}}
\\usepackage[numbers]{{natbib}}
{tpl['extra_preamble']}

% 图片路径
\\graphicspath{{{{figures/}}}}

% 自定义命令（按需添加）
"""

    # For custom templates with extracted packages, deduplicate and use only
    # the imported packages (they already include everything the template needs)
    if is_custom and tpl.get("extra_preamble"):
        files["paper/preamble.tex"] = f"""% 宏包（从模板提取）
{tpl['extra_preamble']}

% 图片路径
\\graphicspath{{{{figures/}}}}

% 自定义命令（按需添加）
"""

    files["paper/references.bib"] = """\
% 参考文献
% 示例:
% @article{example2024,
%   title={Example Paper Title},
%   author={Author, First and Author, Second},
%   journal={Journal Name},
%   year={2024}
% }
"""

    # 4. paper/sections/ — one .tex per section
    for sec in tpl["sections"]:
        path = f"paper/sections/{sec}.tex"
        if sec == "abstract":
            files[path] = abstract_tex
        else:
            title = SECTION_TITLES.get(sec, sec.replace("_", " ").title())
            files[path] = LATEX_SECTION_TEMPLATE.format(title=title, name=sec)

    # 5. Build tools
    files["Makefile"] = """\
.PHONY: pdf clean watch

pdf:
\tpaperwrite build

clean:
\trm -f paper/build/*

watch:
\t@echo "Use paperwrite build for on-demand compilation"
"""

    files[".gitignore"] = """\
paper/build/
*.aux
*.log
*.synctex.gz
*.fls
*.fdb_latexmk
*.bbl
*.blg
*.out
*.toc
refs/papers/*.pdf
"""

    # 6. For custom templates, copy resource files (.sty, .cls, .bst)
    if is_custom:
        tpl_dir = CUSTOM_TEMPLATES_DIR / tpl["_key"]
        config = configparser.ConfigParser()
        config.read(tpl_dir / "template.conf")
        if config.has_section("files"):
            for res_name, dest in config.items("files"):
                res_path = tpl_dir / res_name
                if res_path.exists():
                    files[dest] = res_path.read_bytes()

    return files


def build_template_signatures(template_key: str) -> dict:
    """Build content signatures for status detection."""
    files = build_files_for_template(template_key)
    sigs = {}
    for path, content in files.items():
        if path.endswith((".md", ".tex")) and path.startswith(
            ("sparks/", "outline/", "paper/sections/")
        ):
            sigs[path] = content.strip()
    return sigs


# ── README template (uses project name) ──────────────────────────────────

README_TEMPLATE = """\
# {title}

> 一句话描述

**状态**: Spark

## 目录结构

```
sparks/     思考层 — 动机、创新点、实验想法（Markdown）
outline/    桥梁层 — 各节详细大纲（Markdown）
paper/      输出层 — LaTeX 源文件，可编译
refs/       参考层 — 文献、精读笔记、实验数据
scripts/    工具层 — 生成图表的脚本
```

## 工作流

> 核心原则：想清楚再动笔。`sparks` 里想、`outline` 里排、`paper` 里写，永远从上游改起。

### Phase 1: Spark — 自由思考

全部在 `sparks/` 中进行，纯 Markdown，不碰 LaTeX，不操心格式。

1. **`sparks/motivation.md`** — 一切的起点。我要解决什么问题？为什么现有方案不行？我的方法凭什么更好？
2. **`sparks/innovations.md`** — 提炼 2-3 个核心贡献点，练习用一句话总结整篇论文
3. **`sparks/experiments.md`** — 怎么证明方法有效：数据集、对比方法、评估指标
4. **`sparks/related_work.md`** — 边读论文边扔笔记，格式："论文X做了Y，但没解决Z"

### Phase 2: Outline — 规划结构

先定 `outline/structure.md` 确认论文骨架和页数预算，然后**按写作顺序**逐个填大纲：

{outline_order}

每个大纲写到段落级别：每段说什么、用什么证据、引哪篇论文。

### Phase 3: Draft — 转写 LaTeX

大纲稳定后，逐节把 `outline/*.md` 转为 `paper/sections/*.tex`，顺序同上。每写完一节 `paperwrite build` 或 `make pdf` 看效果。图表脚本放 `scripts/`，生成的图放 `paper/figures/`。

### Phase 4: Refine — 三层迭代

写着写着发现问题时，回到上游修改：

- 实验缺 baseline → 回 `sparks/experiments.md` 想清楚 → 更新 `outline/` → 改 `paper/`
- 论证逻辑不通 → 回 `outline/` 重排段落顺序
- 想到 reviewer 会问什么 → 记到 `sparks/questions.md`

在 `sparks/writing_log.md` 里记录关键决策，方便下次接上。

### Phase 5: Polish — 定稿提交

- 选定会议模板，改 `paper/main.tex` 和 `paper/preamble.tex`
- 检查引用完整性（`references.bib`）
- 控制页数，`make pdf` 出最终版

## 构建

```bash
paperwrite build   # 编译 PDF
make pdf           # 同上（快捷方式）
make clean         # 清理编译产物
```

## 进度

```bash
paperwrite status   # 查看各文件写作进度
paperwrite count    # 统计各节字数
```
"""


def build_readme(title: str, template_key: str) -> str:
    """Build README with template-specific outline order."""
    tpl = get_template(template_key)
    items = []
    for i, sec in enumerate(tpl["sections"], 1):
        items.append(f"{i}. `outline/{sec}.md`")
    outline_order = "\n".join(items)
    return README_TEMPLATE.format(
        title=title,
        outline_order=outline_order,
    )
