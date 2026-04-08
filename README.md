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

1. **Spark** — 在 `sparks/` 中自由思考
2. **Outline** — 在 `outline/` 中规划每节
3. **Draft** — 从 outline 转写到 `paper/sections/`
4. **Refine** — 三层之间迭代
5. **Polish** — 排版、加模板、提交

## 构建

```bash
make pdf     # 编译 PDF
make clean   # 清理编译产物
make watch   # 持续编译（保存即编译）
```
