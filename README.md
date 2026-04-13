# paperwrite

学术论文 vibe writing 脚手架工具 —— **想清楚再动笔**。

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-green.svg)](https://www.python.org/)

写论文最怕什么？打开 LaTeX 就开始憋，憋了一下午写了两行还删了。

paperwrite 的思路很简单：**先想、再排、最后写**，用三层目录（sparks → outline → paper）把思考、大纲、成文强制分开。

---

## 安装

```bash
pip install git+https://github.com/heshulin/paperwrite.git
```

需要 Python >= 3.8。编译 PDF 还需要安装 [tectonic](https://tectonic-typesetting.github.io/)：

```bash
# macOS
brew install tectonic

# conda
conda install -c conda-forge tectonic
```

---

## 快速开始

```bash
# 1. 创建论文项目（交互式选择模板）
paperwrite init my-paper
cd my-paper

# 2. 在 sparks/ 里自由思考（纯 Markdown，不碰 LaTeX）
#    编辑 sparks/motivation.md → 写下你要解决什么问题

# 3. 在 outline/ 里规划结构
#    每个文件写到段落级别：每段说什么、用什么证据、引哪篇论文

# 4. 逐节把 outline/*.md 转写为 paper/sections/*.tex

# 5. 编译 PDF
paperwrite build

# 6. 随时查看进度
paperwrite status   # 哪些文件写了、哪些还没动
```

---

## 核心理念

```
sparks（想）→ outline（排）→ paper（写）
    ↑                                    │
    └────── 发现问题？回到上游改 ──────────┘
```

**永远从上游改起。** 改实验设计不是去改 LaTeX 表格，而是回到 `sparks/experiments.md` 重新想清楚，然后顺着 outline → paper 传递下去。

---

## 内置模板

| 模板 | 适用场景 | 特殊章节 |
|------|---------|----------|
| `default` | 通用学术论文 | — |
| `acl_long` | ACL 长文 (8页) | Analysis, Limitations |
| `acl_short` | ACL 短文 (4页) | Limitations |
| `neurips` | NeurIPS (9页) | Broader Impact |
| `cvpr` | CVPR (8页) | — |
| `ieee` | IEEE 会议论文 | IEEE 双栏格式 |

```bash
paperwrite init my-paper -t neurips   # 直接指定模板
```

---

## 自定义模板

内置不支持的会议？导入你自己的模板。从会议官网下载 LaTeX 模板包（通常是 ZIP，包含 `.tex` + `.sty/.cls` 文件），一条命令导入：

```bash
# 从目录导入
paperwrite template import /path/to/icassp-template --name icassp

# 从 ZIP 导入
paperwrite template import icassp-template.zip --name icassp

# 查看所有可用模板
paperwrite template list

# 用自定义模板创建项目
paperwrite init my-paper -t icassp
```

工具会自动从 `.tex` 文件中解析出 `\documentclass`、`\section{}` 结构、`\bibliographystyle`，以及 `.sty/.cls/.bst` 等资源文件，生成完整的 vibe writing 项目。

---

## 命令参考

### `paperwrite init` — 创建论文项目

在当前目录下创建一个完整的论文项目文件夹，包含 sparks / outline / paper 等目录结构。

```bash
paperwrite init my-paper              # 交互式选择模板
paperwrite init my-paper -t acl_long  # 直接指定模板
```

### `paperwrite build` — 编译 PDF

调用 tectonic 将 `paper/main.tex` 编译为 PDF，输出到 `paper/build/main.pdf`。

```bash
paperwrite build
```

### `paperwrite status` — 查看写作进度

逐文件检查 sparks / outline / paper 各层中哪些已经写过了、哪些还是初始模板，并判断当前处于哪个写作阶段。

```bash
paperwrite status
```

### `paperwrite count` — 统计字数

按层（sparks / outline / paper）统计每个文件的字数，帮助控制论文篇幅。

```bash
paperwrite count
```

### `paperwrite doctor` — 环境检查

检查 tectonic 是否安装、项目结构是否完整、关键文件是否存在。

```bash
paperwrite doctor
```

### `paperwrite section` — 新增章节

在 outline/ 和 paper/sections/ 中同时创建一个新章节文件，并自动把 `\input{sections/xxx}` 添加到 main.tex。

```bash
paperwrite section appendix           # 新增 appendix 章节
paperwrite section future_work        # 新增 future_work 章节
```

### `paperwrite ref add` — 添加参考文献

将一篇 PDF 复制到 `refs/papers/`，同时在 `refs/notes/` 中生成精读笔记模板，并自动在 `sparks/related_work.md` 中添加链接。

```bash
paperwrite ref add attention-is-all-you-need.pdf
paperwrite ref add ~/Downloads/bert.pdf --move   # 移动而非复制
```

### `paperwrite ref list` — 列出参考文献

显示 `refs/papers/` 中所有 PDF，并标记哪些已经有精读笔记。

```bash
paperwrite ref list
```

### `paperwrite ref note` — 打开精读笔记

打开或创建指定论文的精读笔记（Markdown 格式），输出笔记文件路径。

```bash
paperwrite ref note attention-is-all-you-need
paperwrite ref note bert.pdf          # 带 .pdf 后缀也可以
```

### `paperwrite template import` — 导入会议模板

从 ZIP 文件或目录中解析 LaTeX 模板，自动提取 documentclass、章节结构、参考文献样式，以及 .sty/.cls/.bst 资源文件，保存为可复用的自定义模板。

```bash
paperwrite template import ./icassp-template --name icassp
paperwrite template import interspeech-template.zip --name interspeech
paperwrite template import ./template --name my_conf --description "My Conference 2025"
```

### `paperwrite template list` — 列出所有模板

分两组显示所有可用模板：内置模板 + 用户导入的自定义模板。

```bash
paperwrite template list
```

---

## 写作工作流

### Phase 1: Spark — 自由思考

全部在 `sparks/` 中进行，纯 Markdown，不碰 LaTeX，不操心格式。

1. **`sparks/motivation.md`** — 一切的起点。我要解决什么问题？为什么现有方案不行？
2. **`sparks/innovations.md`** — 提炼 2-3 个核心贡献点
3. **`sparks/experiments.md`** — 数据集、对比方法、评估指标
4. **`sparks/related_work.md`** — 边读论文边扔笔记（也可用 `paperwrite ref add` 直接管理 PDF）

### Phase 2: Outline — 规划结构

先定 `outline/structure.md` 确认论文骨架和页数预算，然后按**写作顺序**（不是论文阅读顺序）逐个填大纲：

1. `outline/method.md` — 你最清楚的部分，先写
2. `outline/experiments.md` — 实验怎么做的
3. `outline/results.md` — 结果怎么解读
4. `outline/introduction.md` — 知道全貌后再写引言
5. `outline/related_work.md` — 把 sparks 里的笔记归类
6. `outline/discussion.md` — 局限性和讨论
7. `outline/conclusion.md` — 总结
8. `outline/abstract.md` — 最后写摘要

每个大纲写到段落级别：每段说什么、用什么证据、引哪篇论文。

### Phase 3: Draft — 转写 LaTeX

大纲稳定后，逐节把 `outline/*.md` 转为 `paper/sections/*.tex`。每写完一节编译看看效果：

```bash
paperwrite build
```

### Phase 4: Refine — 三层迭代

写着写着发现问题？**别直接改 LaTeX，回到上游去改**：

- 实验缺 baseline → 回 `sparks/experiments.md` 重新想 → 更新 `outline/` → 改 `paper/`
- 论证逻辑不对 → 回 `outline/` 重排段落
- 想到 reviewer 可能会问什么 → 记到 `sparks/questions.md`

### Phase 5: Polish — 定稿提交

- 检查引用完整性（`paper/references.bib`）
- 控制页数，`paperwrite count` 看字数
- `paperwrite build` 出最终版

---

## 目录结构

```
my-paper/
├── sparks/              自由思考（Markdown）
│   ├── motivation.md    研究动机
│   ├── innovations.md   核心贡献
│   ├── experiments.md   实验设计
│   ├── results.md       结果解读
│   ├── related_work.md  相关工作笔记
│   ├── writing_log.md   写作日志
│   └── questions.md     待解决问题
├── outline/             段落级大纲（Markdown）
│   ├── structure.md     论文骨架与页数预算
│   └── *.md             各节大纲（因模板而异）
├── paper/
│   ├── main.tex         论文主文件
│   ├── preamble.tex     宏包配置
│   ├── references.bib   参考文献
│   ├── sections/        各节 LaTeX 源文件
│   └── build/           编译输出（PDF）
├── refs/
│   ├── papers/          参考文献 PDF
│   └── notes/           精读笔记（Markdown）
├── scripts/             画图、生成表格的脚本
└── .paperwrite          项目配置（记录所用模板）
```

---

## 从源码安装

```bash
git clone https://github.com/heshulin/paperwrite.git
cd paperwrite
pip install -e .
```

## License

MIT
