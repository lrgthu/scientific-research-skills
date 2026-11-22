# Scientific Research Skills（全流程开源科研技能套件）

[English Documentation (README.md)](./README.md) | **中文文档**

[![CI](https://github.com/lrgthu/scientific-research-skills/actions/workflows/ci.yml/badge.svg)](https://github.com/lrgthu/scientific-research-skills/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B%20(uv)-3776AB.svg)](https://docs.astral.sh/uv/)
[![Agent Skills](https://img.shields.io/badge/Standard-SKILL.md%20%2B%20AGENTS.md-10B981.svg)](#安装方式)

面向 **Google Antigravity**、**Claude Code**、**OpenAI Codex CLI**、**Gemini CLI** 与 **Cursor** 的**零订阅费、端到端科研智能体技能套件（Skill Suite）**。

当前大多数 AI 辅助科研工具存在明显的“中间层断层”：上游只有单次关键词检索脚本，中间层被迫依赖多个割裂且昂贵的商业 SaaS（**Undermind**、**ResearchRabbit**、**Scite**、**Elicit**、**SciSpace**），下游则是“打补丁式”的碎片化 AI 润色。本项目将完整科研闭环沉淀为 **2 个按需加载的解耦插件**（共 `4` 个核心 Skill、`4` 个基于 `uv` 的零配置 Python CLI，以及反幻觉引文与反补丁写作全局护栏规则）：

```text
种子论文 / 细粒度研究问题
 │
 ├──► [1. research-literature]  （100% 开源学术图谱与源码级证据层 —— 零商业订阅）
 │     ├── scholarly-graph-audit:
 │     │    • 种子演进主线测绘（共引奠基祖先 + 耦合活跃前沿 + SPECTER2 正负样本语义近邻）
 │     │    • 交互式引文图谱编译（Timeline 年份轴 / Force 力导向双视图，支持离线浏览器直开）
 │     │    • 施引褒贬语境与撤稿审计（S2 施引原句 + arXiv .tex 源码 \cite{} 抽取 + Crossref 撤稿库）
 │     │    • 零幻觉 .bib 核验器（拦截伪造引用、预警撤稿论文、预印本自动升级正式发表版）
 │     └── literature-evidence-workflow:
 │          • 多视角迭代深挖检索与正/负种子滚雪球收敛协议（吸收 Undermind 方法论）
 │          • 本地 arXiv .tar.gz LaTeX 源码解包 + 并行子智能体结构化证据矩阵（吸收 Elicit）
 │
 └──► [2. scientific-writing]   （学术论文架构重构与出版级图表工程 —— 与 [1] 双向按需联动 ⇄）
       ├── scientific-writing:
       │    • 反向文献按需联动（写 Intro/Related Work、H1->H2 主线转向及定稿 .bib 核验时自动拉起 [1]，纯润色走零延迟快车道）
       │    • 反补丁全局复盘重写协议（新实验迭代后零数据/公式/引文退化的整体重构）
       │    • 图文表互文八律与 LaTeX 顺序/孤儿图表/结论式图注静态检查器（`lint_manuscript_visuals.py`）
       │    • 宏观叙事结构（Schimel OCAR / 预示型 OCAR / 基金 ABDCE / Nature LDR / 沙漏对称 / Rebuttal 回复）
       │    • 读者预期句法力学（Gopen & Swan Topic -> 强动作动词 -> Stress 闭合 + SCFL 审校）
       └── scientific-figures:
            • 视觉感知与标度铁律（Wilke 第 1–29 章 + Rougier 等《更佳科研图表十诫》）
            • Okabe–Ito 色觉安全配色、期刊精确栏宽预设与无竖线 Booktabs 三线表规范
```

---

## 核心能力与商业工具对照

| 科研痛点环节 | 常见商业 SaaS | 本套件的开源原生解法 |
| :--- | :--- | :--- |
| **细粒度防漏检追踪** | *Undermind* | 检索前锁定纳入/排除准则 → 三正交术语扩展 → 将易混错分论文作为 `--negatives` 负样本喂入 SPECTER2 滚雪球，直至边际命中率 $<10\%$ 收敛。 |
| **新课题找学术主线** | *ResearchRabbit 2.0 / Litmaps* | `scholarly_graph.py lineage` + `render_citation_map.py`：计算特异性加权的共引祖先与活跃前沿，一键生成带时间轴与力导向切换的交互式图谱 HTML。 |
| **施引褒贬与撤稿核查** | *Scite* | `citation-audit` 与 `tex-context`：获取 S2 施引原句/意图，**并支持直接从施引 arXiv 论文的 `.tex` 源码中精准提取 `\cite{}` 原句与章节名**，联查 OpenAlex + Crossref (Retraction Watch) 撤稿状态。 |
| **批量精读与对比矩阵** | *Elicit* | `unpack_paper_corpus.py` 优先拉取 arXiv LaTeX 源码展开为 `fulltext.tex` 与独立 `tables.tex`（零 PDF 切片丢失），由并行子智能体抽取带原文锚点的 `CSV`、`Markdown` 与 Booktabs `.tex` 对比表。 |
| **文献库问答与找 Gap** | *SciSpace* | 摒弃容易丢失数学符号与跨表脚注的 PDF 切片 RAG，直接从结构化证据矩阵的“各流派隐含假设与失效边界”映射为 Schimel 漏斗式具体未知问题（Knowledge Gap）与流派化 `Related Work`。 |

---

## 安装方式

### 前置依赖：`uv`
所有 Python 脚本均采用 [PEP 723](https://peps.python.org/pep-0723/) 内联依赖声明，通过 `uv` 自动隔离运行，无需手动建虚拟环境或 `pip install`：
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 一键安装到主流 Agent

```bash
git clone https://github.com/lrgthu/scientific-research-skills.git
cd scientific-research-skills

# 安装到 Google Antigravity (~/.gemini/config/plugins/)
./scripts/install.sh --target antigravity

# 安装到 Claude Code (~/.claude/skills/)、Codex (~/.codex/skills/) 或 Cursor (~/.cursor/skills/)
./scripts/install.sh --target claude
./scripts/install.sh --target codex
./scripts/install.sh --target cursor

# 或一次性同步到全部环境
./scripts/install.sh --target all
```

**Claude Code 插件市场**用户也可直接添加：
```text
/plugin marketplace add lrgthu/scientific-research-skills
```

---

## 命令行快速上手（无需任何 API Key）

`research-literature` 内置 `~/.cache/research-literature/http_cache.sqlite3` 本地持久化缓存；当 Semantic Scholar 公共匿名池触发限流时，会自动无缝回退至 **OpenAlex + Crossref + arXiv LaTeX 源码引擎**。

```bash
GRAPH_CLI="plugins/research-literature/skills/scholarly-graph-audit/scripts"
WF_CLI="plugins/research-literature/skills/literature-evidence-workflow/scripts"

# 1. 从种子论文构建演进图谱并生成可交互 HTML 视图
uv run "$GRAPH_CLI/scholarly_graph.py" lineage \
  --seeds "arXiv:2305.18290" "arXiv:2203.02155" \
  --max-per-group 12 \
  --output /tmp/dpo_lineage.json

uv run "$GRAPH_CLI/render_citation_map.py" /tmp/dpo_lineage.json \
  --mode standalone \
  --output /tmp/dpo_citation_map.html

# 2. 审计论文被后续文献如何引用（含自动 arXiv .tex 源码 \cite{} 回退）及撤稿检查
uv run "$GRAPH_CLI/scholarly_graph.py" citation-audit "arXiv:2305.18290" \
  --output /tmp/dpo_audit.json

# 3. 核验 references.bib 与 LaTeX 稿件：拦截幻觉/错配、检查撤稿、扫除 [?] 漏引、升级 arXiv/OpenReview 正式版
uv run "$GRAPH_CLI/scholarly_graph.py" bib-verify \
  --bib references.bib \
  --tex-dir ./manuscript \
  --output-bib references_verified.bib \
  --report /tmp/bib_report.json

# 4. 批量解包候选论文 arXiv LaTeX 源码并编译出版级 Booktabs 对比表
uv run "$WF_CLI/unpack_paper_corpus.py" --from-json /tmp/dpo_lineage.json --out-dir ./literature/corpus
uv run "$WF_CLI/compile_evidence_matrix.py" ./literature/extractions.json --out-dir ./literature/matrix
```

*（可选提速配置：如需在超大规模批处理下获得更高专属配额，可在 `~/.env` 中按需配置免费的 `S2_API_KEY`、`OPENALEX_API_KEY` 与 `CROSSREF_MAILTO`，脚本会自动静默读取。）*

---

## 方法论致谢与开源协议

本套件中的规则、工作流与代码均为 Clean-Room 原创工程实现，方法论体系致谢以下经典著作与开放学术基础设施：
- **学术叙事与句法结构**：Joshua Schimel, *Writing Science* (2012)；George D. Gopen & Judith A. Swan, *"The Science of Scientific Writing"* (1990)。
- **科研可视化与制表规范**：Claus O. Wilke, *Fundamentals of Data Visualization* (2019)；Nicolas P. Rougier, Michael Droettboom & Philip E. Bourne, *"Ten Simple Rules for Better Figures"* (*PLOS Computational Biology*, 2014, CC BY 4.0)；Okabe & Ito 色觉安全调色板。
- **开放学术数据源**：Semantic Scholar (AI2 / SPECTER2)、OpenAlex、Crossref (Retraction Watch) 与 arXiv（请遵守各平台 API 服务条款及所检索论文自身的版权许可）。

本项目基于 [MIT License](./LICENSE) 开源发布。
