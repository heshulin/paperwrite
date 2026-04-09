# paperwrite

学术论文 vibe writing 脚手架工具——想清楚再动笔。

将论文写作拆解为三个层次、五个阶段，用目录结构强制你从思考到大纲再到成文，始终从上游改起。

## 安装

```bash
pip install git+https://github.com/heshulin/paperwrite.git
```

需要 Python >= 3.8。编译 PDF 还需要 [tectonic](https://tectonic-typesetting.github.io/)：

```bash
# macOS
brew install tectonic

# conda
conda install -c conda-forge tectonic
```

## 快速开始

```bash
# 1. 创建论文项目（交互式选择模板）
paperwrite init my-paper
cd my-paper

# 2. 或直接指定模板
paperwrite init my-paper --template acl_long

# 3. 检查环境和依赖
paperwrite doctor

# 4. 查看进度
paperwrite status

# 5. 在 sparks/ 里开始思考，在 outline/ 里规划大纲，最后在 paper/ 里写 LaTeX

# 6. 编译 PDF
paperwrite build
# 或
make pdf
```

## 支持的模板

| 模板 | 说明 | 特殊章节 |
|------|------|----------|
| `default` | 通用学术论文 | — |
| `acl_long` | ACL 长文 (8页) | Limitations |
| `acl_short` | ACL 短文 (4页) | Limitations |
| `neurips` | NeurIPS (9页) | Broader Impact |
| `cvpr` | CVPR (8页) | — |
| `ieee` | IEEE 会议论文 | IEEE 格式 |

## 工作流

核心原则：**想清楚再动笔**。`sparks` 里想、`outline` 里排、`paper` 里写，永远从上游改起。

### 三层目录结构

```
sparks/     思考层 — 动机、创新点、实验想法（Markdown）
outline/    桥梁层 — 各节段落级大纲（Markdown）
paper/      输出层 — LaTeX 源文件，可编译
refs/       参考层 — 文献、精读笔记、实验数据
scripts/    工具层 — 生成图表的脚本
```

### 五个阶段

| 阶段 | 做什么 | 在哪里 |
|------|--------|--------|
| **Spark** | 自由思考：研究动机、创新点、实验设计、相关工作笔记 | `sparks/` |
| **Outline** | 规划结构：先定骨架和页数预算，再按顺序填段落级大纲 | `outline/` |
| **Draft** | 转写 LaTeX：逐节把大纲转为论文 | `paper/sections/` |
| **Refine** | 三层迭代：发现问题回到上游修改 | 全部 |
| **Polish** | 定稿提交：选模板、检查引用、控制页数 | `paper/` |

## CLI 命令

```
paperwrite init <name>           创建论文项目
paperwrite init <name> -t <tpl>  指定模板创建
paperwrite build                 编译 PDF（需要 tectonic）
paperwrite status                显示写作进度
paperwrite doctor                检查依赖和项目完整性
paperwrite count                 统计各节字数
paperwrite section <name>        新增自定义小节
```

## 从源码安装

```bash
git clone https://github.com/heshulin/paperwrite.git
cd paperwrite
pip install -e .
```

## License

MIT
