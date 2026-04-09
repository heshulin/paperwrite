# paperwrite

学术论文 vibe writing 脚手架工具——**想清楚再动笔**。

写论文最怕什么？打开 LaTeX 就开始憋，憋了一下午写了两行还删了。paperwrite 的思路很简单：**先想、再排、最后写**，用三个文件夹把思考、大纲、成文强制分开。

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

## 30 秒上手

```bash
# 创建一个论文项目
paperwrite init my-paper
cd my-paper

# 检查一下环境是否 OK
paperwrite doctor

# 开始写！先在 sparks/motivation.md 写下你要解决什么问题
```

## 写论文的正确姿势

### 第一步：选模板

创建项目时选一个目标会议模板，不同模板会自动生成对应的章节结构：

```bash
paperwrite init my-paper              # 交互式选择
paperwrite init my-paper -t acl_long  # 直接指定
```

| 模板 | 适用场景 | 特殊章节 |
|------|---------|----------|
| `default` | 通用学术论文 | — |
| `acl_long` | ACL 长文 (8页) | Analysis, Limitations |
| `acl_short` | ACL 短文 (4页) | Limitations |
| `neurips` | NeurIPS (9页) | Broader Impact |
| `cvpr` | CVPR (8页) | — |
| `ieee` | IEEE 会议论文 | IEEE 双栏格式 |

### 第二步：在 sparks/ 里自由思考

别碰 LaTeX，别管格式，就在 Markdown 里把脑子里的东西倒出来：

```
sparks/
├── motivation.md     # 为什么要做这个？现有方案哪里不行？
├── innovations.md    # 我的核心贡献是什么？（2-3 点）
├── experiments.md    # 怎么验证？用什么数据集？和谁比？
├── results.md        # 实验结果说明了什么故事？
├── related_work.md   # 读过的论文笔记，随手扔这里
├── writing_log.md    # 写作日志，记录关键决策
└── questions.md      # 还有哪些问题没想清楚？
```

**这一步不需要写完整句子，关键词、碎片想法都可以。**

### 第三步：在 outline/ 里排大纲

想清楚之后，把碎片整理成段落级大纲。每段写清楚"这一段要说什么、用什么证据、引哪篇论文"。

推荐的填写顺序（不是论文顺序，是写作顺序）：

1. `outline/method.md` — 你最清楚的部分，先写
2. `outline/experiments.md` — 实验怎么做的
3. `outline/results.md` — 结果怎么解读
4. `outline/introduction.md` — 知道全貌后再写引言
5. `outline/related_work.md` — 把 sparks 里的笔记归类
6. `outline/discussion.md` — 局限性和讨论
7. `outline/conclusion.md` — 总结
8. `outline/abstract.md` — 最后写摘要

### 第四步：转写 LaTeX

大纲稳定后，逐节把 `outline/*.md` 翻译成 `paper/sections/*.tex`。

```bash
# 每写完一节，编译看看效果
paperwrite build
```

### 第五步：迭代修改

写着写着发现问题？**别直接改 LaTeX，回到上游去改**：

- 实验缺 baseline → 回 `sparks/experiments.md` 想 → 更新 `outline/` → 改 `paper/`
- 论证逻辑不对 → 回 `outline/` 重排段落
- 想到 reviewer 可能会问什么 → 记到 `sparks/questions.md`

### 日常使用的几个命令

```bash
paperwrite status          # 看看哪些文件写了、哪些还没动
paperwrite count           # 统计各节字数，控制页数
paperwrite section appendix  # 加一个新小节（自动创建 outline + tex + 更新 main.tex）
paperwrite doctor          # 检查环境和项目是否完整
paperwrite build           # 编译 PDF
```

## 核心理念

```
sparks（想）→ outline（排）→ paper（写）→ 发现问题 → 回到 sparks 改
```

**永远从上游改起。** 改实验设计不是去改 LaTeX 表格，而是回到 `sparks/experiments.md` 重新想清楚，然后顺着 outline 到 paper 传递下去。

## 目录结构总览

```
my-paper/
├── sparks/          随便写的思考碎片（Markdown）
├── outline/         段落级大纲（Markdown）
├── paper/
│   ├── main.tex     论文主文件
│   ├── preamble.tex 宏包配置
│   ├── references.bib
│   └── sections/    各节 LaTeX 源文件
├── refs/            参考文献和数据
└── scripts/         画图、生成表格的脚本
```

## 从源码安装

```bash
git clone https://github.com/heshulin/paperwrite.git
cd paperwrite
pip install -e .
```

## License

MIT
