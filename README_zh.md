# Scientific Research Skills（全流程开源科研技能套件）

[English Documentation (README.md)](./README.md) | **中文文档**

[![CI](https://github.com/lrgthu/scientific-research-skills/actions/workflows/ci.yml/badge.svg)](https://github.com/lrgthu/scientific-research-skills/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B%20(uv)-3776AB.svg)](https://docs.astral.sh/uv/)
[![Agent Skills](https://img.shields.io/badge/Standard-SKILL.md%20%2B%20AGENTS.md-10B981.svg)](#安装方式)

面向 **Google Antigravity**、**Claude Code**、**OpenAI Codex CLI**、**Gemini CLI** 与 **Cursor** 的**零订阅费、端到端科研智能体技能套件（Skill Suite）**。

当前大多数 AI 辅助科研工具存在明显的链路断层：起点依赖大模型凭空“拍脑袋”拼凑热词，文献层被迫依赖多个割裂且昂贵的商业 SaaS（**Undermind**、**ResearchRabbit**、**Scite**、**Elicit**、**SciSpace**），实验代码缺乏可复现性与数值防错规范，终点则是“打补丁式”润色，且在引入外部推理大模型模拟审稿时极易陷入“诚实局限被当靶子打、为找茬而找茬、多轮防御性加限定词导致文章不像人话”的陷阱。本项目将**「Stage 0 选题与强推论 → Stage 1 文献图谱与源码证据 → Stage 2 可复现科学计算 → Stage 3 论文重构与出版级图表」**四段闭环外加**「独立按需插件 `/llm-review-triage`（外审意见分诊与护魂盾）」**沉淀为 **5 个解耦插件**（共 `7` 个核心 Skill、`9` 个基于 `uv` 的零配置 Python CLI）：

```text
原始好奇心 / 种子论文 / 实验反常现象
 │
 ├──► [0. scientific-ideation]   （Stage 0：选题品味、强推论竞争假说与快速证伪预检）
 │     └── scientific-ideation:
 │          • Hamming 破局抓手（Attack Vector）与 Alon 二维「可行性 × 知识增量」帕累托前沿筛选
 │          • Platt 强推论双竞争假说（H1 vs. H2/H0）与 AI 选题七大翻车防御（Si et al. ICLR 2025）
 │          • 精确算子 + 等算力极简基线 + <=4h 关键证伪实验（Kill Condition）+ 迷雾转向预案（`lint_research_ideas.py`）
 │
 ├──► [1. research-literature]   （Stage 1：100% 开源学术图谱与源码级证据层 —— 零商业订阅）
 │     ├── scholarly-graph-audit:
 │     │    • 种子演进主线测绘（共引奠基祖先 + 耦合活跃前沿 + SPECTER2 正负样本语义近邻）
 │     │    • 交互式引文图谱编译（Timeline 年份轴 / Force 力导向双视图，支持离线浏览器直开）
 │     │    • 施引褒贬语境与撤稿审计（S2 施引原句 + arXiv .tex 源码 \cite{} 抽取 + Crossref 撤稿库）
 │     │    • 零幻觉 .bib 核验器（拦截伪造引用、预警撤稿论文、预印本自动升级正式发表版）
 │     └── literature-evidence-workflow:
 │          • 多视角迭代深挖检索与正/负种子滚雪球收敛协议（吸收 Undermind 方法论）
 │          • 本地 arXiv .tar.gz LaTeX 源码解包 + 并行子智能体结构化证据矩阵（吸收 Elicit）
 │
 ├──► [2. scientific-computing]  （Stage 2：可复现科学计算工程与 Google 规范科研 Python）
 │     └── scientific-computing:
 │          • 标准目录与数据洁癖（`data/raw/` 严格只读 -> `src/` 核心算法库 -> `scripts/` 驱动脚本 -> `results/`）
 │          • Tidy Data 规范、语义化文件命名（禁 `fig3a.png`/`result1.csv`）与实验溯源 JSON（`scaffold_research_project.py`）
 │          • 面向 NumPy/SciPy/PyTorch/JAX 适配的 Google Python Style（防 `NaN` 漏检区间校验、`.size` 判空、§3.16.5 论文公式命名豁免）
 │          • 解析极限/守恒律测试预言机、独立 `default_rng(seed)` 随机流与 AST 静态审计器（`audit_scientific_python.py`）
 │
 └──► [3. scientific-writing]    （Stage 3：学术论文架构重构与出版级图表工程 —— 与上游双向联动 ⇄）
       ├── scientific-writing:   （每次激活自动级联调用 `scientific-figures`，实现图文一体同步重构与检视）
       │    • 反向文献按需联动（写 Intro/Related Work、H1->H2 主线转向及定稿 .bib 核验时自动拉起 [1]，纯润色走零延迟快车道）
       │    • 反补丁全局复盘重写协议（新实验迭代后零数据/公式/引文退化的整体重构）
       │    • 叙事光谱诊断（Olson `AAA/ABT/DHY`）、Dobzhansky 核心母题、`iABT->cABT->kABT` 浓缩、阴性结果重构与学术报告编排
       │    • 全文—跨图—跨表数字/聚合口径/协议（`P1/P2`）/结论方向一致性锁死协议与 LaTeX 静态审计器（`lint_manuscript_visuals.py`）
       │    • 宏观叙事结构（Schimel OCAR / 预示型 OCAR / 基金 ABDCE / Nature LDR / 沙漏对称 / Rebuttal 回复）
       │    • 读者预期句法力学（Gopen & Swan Topic -> 强动作动词 -> Stress 闭合 + SCFL 审校）
       └── scientific-figures:
            • 逐图逐表五门论证检视协议（Doumont 一句话结论 + Alley Assertion-Evidence + Frankel & DePace 视觉推演链 + Cargill 图先行）
            • 视觉感知与标度铁律（Wilke 第 1–29 章 + Rougier 等《更佳科研图表十诫》）
            • Okabe–Ito 色觉安全配色、期刊精确栏宽预设与无竖线 Booktabs 三线表规范

 [独立按需插件: llm-review-triage] （零常驻规则开销 —— 仅在面对外部大模型审稿意见或调用 `/llm-review-triage` 时激活）
  └── llm-review-triage:
       • 灵魂锚点锁死 + 诚实局限回旋镖免疫 + 推理模型过度推演（Overthinking）找茬过滤
       • 多轮收敛硬停损（Round <= 2）+ 中英双语防御性限定词与补丁疤痕 Diff 审计（`audit_review_and_hedging.py`）
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

# 安装到 Google Antigravity (~/.gemini/config/plugins/) 并全局钉死（Pin）科研默认路由规则
./scripts/install.sh --target antigravity --pin-global

# 安装到 Claude Code (~/.claude/skills/)、Codex (~/.codex/skills/) 或 Cursor (~/.cursor/skills/)
./scripts/install.sh --target claude --pin-global
./scripts/install.sh --target codex
./scripts/install.sh --target cursor

# 或一次性同步到全部环境并开启全局科研默认调度
./scripts/install.sh --target all --pin-global
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

# 5. 一键初始化可复现科研 Python 仓库 + 静态审计数值隐患与 Google 风格违规
SCICOMP_CLI="plugins/scientific-computing/skills/scientific-computing/scripts"
uv run "$SCICOMP_CLI/scaffold_research_project.py" ./my-experiment --author "Your Lab"
uv run "$SCICOMP_CLI/audit_scientific_python.py" --strict ./my-experiment

# 6. 第 0 环候选 Idea 强推论完整性校验、反黑话扫描与 Alon 帕累托决策表生成
IDEATION_CLI="plugins/scientific-ideation/skills/scientific-ideation/scripts/lint_research_ideas.py"
uv run "$IDEATION_CLI" --init-template /tmp/candidate_ideas.json
uv run "$IDEATION_CLI" /tmp/candidate_ideas.json --markdown-out ./ideation_murder_board.md --strict

# 7. 独立外审意见 Area-Chair 分诊与改稿前后“防免责声明体”中英双语 Diff 审计
TRIAGE_CLI="plugins/llm-review-triage/skills/llm-review-triage/scripts/audit_review_and_hedging.py"
uv run "$TRIAGE_CLI" init-ledger /tmp/triage_ledger.json
uv run "$TRIAGE_CLI" summarize-ledger /tmp/triage_ledger.json --markdown-out ./review_triage_brief.md --strict
uv run "$TRIAGE_CLI" diff-audit ./manuscript/before.tex ./manuscript/after.tex --strict
```

*（可选提速配置：如需在超大规模批处理下获得更高专属配额，可在 `~/.env` 中按需配置免费的 `S2_API_KEY`、`OPENALEX_API_KEY` 与 `CROSSREF_MAILTO`，脚本会自动静默读取。）*

---

## 方法论致谢与开源协议

本套件中的规则、工作流与代码均为 Clean-Room 原创工程实现，方法论体系致谢以下经典著作与开放学术基础设施：
- **选题品味、强推论与科研构思（Stage 0）**：John R. Platt, *"Strong Inference"* (*Science*, 1964)；Richard W. Hamming, *"You and Your Research"* (1986)；Uri Alon, *"How To Choose a Good Scientific Problem"* (*Molecular Cell*, 2009)；Zachary C. Lipton & Jacob Steinhardt, *"Troubling Trends in Machine Learning Scholarship"* (*ACM Queue*, 2019, `arXiv:1807.03341`)；Chenglei Si, Diyi Yang & Tatsunori Hashimoto, *"Can LLMs Generate Novel Research Ideas?"* (*ICLR*, 2025, `arXiv:2409.04109`)。
- **科学计算工程与 Python 编码规范**：Greg Wilson et al., *"Best Practices for Scientific Computing"* (*PLOS Biology*, 2014, `arXiv:1210.0530`, CC BY)；Greg Wilson et al., *"Good Enough Practices in Scientific Computing"* (*PLOS Computational Biology*, 2017, `arXiv:1609.00037`, CC BY)；Google, *[Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)* (CC BY 3.0)。
- **学术叙事与句法结构**：Joshua Schimel, *Writing Science* (2012)；Margaret Cargill & Patrick O'Connor, *Writing Scientific Research Articles* (3rd ed., 2021)；Randy Olson, *Houston, We Have a Narrative: Why Science Needs Story* (2015)；George D. Gopen & Judith A. Swan, *"The Science of Scientific Writing"* (1990)。
- **图表论证检视、可视化与制表规范**：Jean-luc Doumont, *Trees, Maps, and Theorems* (2009)；Michael Alley, *The Craft of Scientific Writing* / *Presentations* (Assertion-Evidence)；Felice C. Frankel & Angela H. DePace, *Visual Strategies* (2012)；Claus O. Wilke, *Fundamentals of Data Visualization* (2019)；Nicolas P. Rougier et al., *"Ten Simple Rules for Better Figures"* (*PLOS Computational Biology*, 2014, CC BY 4.0)；Okabe & Ito 色觉安全调色板。
- **开放学术数据源**：Semantic Scholar (AI2 / SPECTER2)、OpenAlex、Crossref (Retraction Watch) 与 arXiv（请遵守各平台 API 服务条款及所检索论文自身的版权许可）。

本项目基于 [MIT License](./LICENSE) 开源发布。
