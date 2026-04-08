# Paper Title

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
