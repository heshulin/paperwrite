"""All template file contents for paperwrite project scaffolding."""

DIRS = [
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

# {relative_path: content}
FILES = {
    # ── sparks/ ──
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
    # ── outline/ ──
    "outline/structure.md": """\
# 论文结构

- Abstract (~150 words)
- Introduction (~1.5 pages)
- Related Work (~1.5 pages)
- Method (~2 pages)
- Experiments (~1 page)
- Results (~1.5 pages)
- Discussion (~0.5 pages)
- Conclusion (~0.5 pages)

## 各节之间的依赖关系

## 读者阅读顺序 vs 写作顺序
""",
    "outline/abstract.md": """\
# Abstract 大纲

## 问题（1-2句）

## 方法（1-2句）

## 结果（1-2句）

## 意义（1句）
""",
    "outline/introduction.md": """\
# Introduction 大纲

## Para 1: Hook — 用什么例子引入问题

## Para 2: 形式化问题定义

## Para 3: 现有方案为什么不行（引用 X, Y, Z）

## Para 4: 我们的方法一句话

## Para 5: 贡献列表
""",
    "outline/related_work.md": """\
# Related Work 大纲

## 分类方式（按方法/按问题/按时间线）

## 类别 1:

## 类别 2:

## 类别 3:

## 和我们工作的关系总结
""",
    "outline/method.md": """\
# Method 大纲

## 整体框架概述

## 模块 1:

## 模块 2:

## 模块 3:

## 训练/推理流程
""",
    "outline/experiments.md": """\
# Experiments 大纲

## 实验设置
- 数据集
- Baselines
- 实现细节

## 主实验（对应哪个 Research Question）

## 消融实验

## 分析实验
""",
    "outline/results.md": """\
# Results 大纲

## 主表结果分析

## 关键发现 1:

## 关键发现 2:

## 可视化说明了什么
""",
    "outline/discussion.md": """\
# Discussion 大纲

## 结果意味着什么

## 局限性

## 潜在的负面社会影响（如需要）
""",
    "outline/conclusion.md": """\
# Conclusion 大纲

## 总结（呼应 Introduction）

## Future Work
""",
    # ── paper/ ──
    "paper/main.tex": """\
\\documentclass[11pt]{article}
\\input{preamble}

\\title{__TITLE__}
\\author{Author Name}
\\date{\\today}

\\begin{document}
\\maketitle

\\input{sections/abstract}
\\input{sections/introduction}
\\input{sections/related_work}
\\input{sections/method}
\\input{sections/experiments}
\\input{sections/results}
\\input{sections/discussion}
\\input{sections/conclusion}

\\bibliographystyle{plain}
\\bibliography{references}

\\end{document}
""",
    "paper/preamble.tex": """\
% 基础宏包
\\usepackage[utf8]{inputenc}
\\usepackage{amsmath,amssymb}
\\usepackage{graphicx}
\\usepackage{booktabs}
\\usepackage{hyperref}
\\usepackage[numbers]{natbib}

% 图片路径
\\graphicspath{{figures/}}

% 自定义命令（按需添加）
""",
    "paper/references.bib": """\
% 参考文献
% 示例:
% @article{example2024,
%   title={Example Paper Title},
%   author={Author, First and Author, Second},
%   journal={Journal Name},
%   year={2024}
% }
""",
    "paper/sections/abstract.tex": """\
\\begin{abstract}
% TODO: 从 outline/abstract.md 转写
\\end{abstract}
""",
    "paper/sections/introduction.tex": """\
\\section{Introduction}
% TODO: 从 outline/introduction.md 转写
""",
    "paper/sections/related_work.tex": """\
\\section{Related Work}
% TODO: 从 outline/related_work.md 转写
""",
    "paper/sections/method.tex": """\
\\section{Method}
% TODO: 从 outline/method.md 转写
""",
    "paper/sections/experiments.tex": """\
\\section{Experiments}
% TODO: 从 outline/experiments.md 转写
""",
    "paper/sections/results.tex": """\
\\section{Results}
% TODO: 从 outline/results.md 转写
""",
    "paper/sections/discussion.tex": """\
\\section{Discussion}
% TODO: 从 outline/discussion.md 转写
""",
    "paper/sections/conclusion.tex": """\
\\section{Conclusion}
% TODO: 从 outline/conclusion.md 转写
""",
    # ── build tools ──
    "Makefile": """\
.PHONY: pdf clean watch

pdf:
\tcd paper && tectonic -o build main.tex

clean:
\trm -f paper/build/*

watch:
\tcd paper && tectonic -o build --watch main.tex
""",
    ".gitignore": """\
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
""",
}

# README is separate because it uses the project name
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

1. `outline/method.md` — 先写方法，这是你最清楚的部分
2. `outline/experiments.md` — 实验设置紧跟方法
3. `outline/results.md` — 有了实验才有结果
4. `outline/introduction.md` — 知道全貌后再写引言
5. `outline/related_work.md` — 从 sparks 笔记整理分类
6. `outline/discussion.md` — 讨论局限性
7. `outline/conclusion.md` — 总结
8. `outline/abstract.md` — 最后写摘要

每个大纲写到段落级别：每段说什么、用什么证据、引哪篇论文。

### Phase 3: Draft — 转写 LaTeX

大纲稳定后，逐节把 `outline/*.md` 转为 `paper/sections/*.tex`，顺序同上。每写完一节 `make pdf` 看效果。图表脚本放 `scripts/`，生成的图放 `paper/figures/`。

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
make pdf     # 编译 PDF
make clean   # 清理编译产物
make watch   # 持续编译（保存即编译）
```
"""

# Template content signatures for status detection.
# If a file's content stripped of whitespace matches its template, it's "not started".
TEMPLATE_SIGNATURES = {}
for path, content in FILES.items():
    if path.endswith((".md", ".tex")) and path.startswith(("sparks/", "outline/", "paper/sections/")):
        TEMPLATE_SIGNATURES[path] = content.strip()
