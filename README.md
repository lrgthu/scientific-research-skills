# Scientific Research Skills

**English** | [中文文档 (README_zh.md)](./README_zh.md)

[![CI](https://github.com/lrgthu/scientific-research-skills/actions/workflows/ci.yml/badge.svg)](https://github.com/lrgthu/scientific-research-skills/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B%20(uv)-3776AB.svg)](https://docs.astral.sh/uv/)
[![Agent Skills](https://img.shields.io/badge/Standard-SKILL.md%20%2B%20AGENTS.md-10B981.svg)](#installation)

An end-to-end, **zero-subscription open-stack research skill suite** for coding and research agents (**Google Antigravity**, **Claude Code**, **OpenAI Codex CLI**, **Gemini CLI**, and **Cursor**).

Most AI research workflows break in the middle: researchers juggle naive LLM armchair "brainstorming" at the start, fragmented paid SaaS tabs (**Undermind**, **ResearchRabbit**, **Scite**, **Elicit**, **SciSpace**) in literature review, ad-hoc unseeded experiment scripts in coding, patchwork LLM prose edits, and unfiltered multi-round AI referee critiques that sand off a paper's soul into defensive disclaimers. **`scientific-research-skills`** unifies the **Stage 0 → Stage 3** scientific method plus a **standalone on-demand AI-review filter** into **five decoupled plugins** (`7` skills + `9` standalone `uv` Python CLIs):

```text
Raw Curiosity / Seed Papers / Observed Anomaly
 │
 ├──► [0. scientific-ideation]   (Stage 0: Problem Taste, Strong Inference & Rapid Falsification)
 │     └── scientific-ideation:
 │          • Hamming Attack Vector ("Why Now?") & Alon 2D `Feasibility × Knowledge Gain` Pareto Frontier
 │          • Platt Competing Hypotheses (H1 vs. H2/H0) & Anti-LLM-Slop Guardrails (Si et al. ICLR 2025)
 │          • Exact Operator + Iso-Compute Baseline + <=4h Crucial Kill Test + Cloud Pivot (`lint_research_ideas.py`)
 │
 ├──► [1. research-literature]   (Stage 1: 100% Open Scholarly Graph & Full-Text Evidence — $0 SaaS)
 │     ├── scholarly-graph-audit:
 │     │    • Seed-to-Lineage Graph (Co-Cited Roots + Coupling Frontier + SPECTER2 Siblings)
 │     │    • Interactive HTML Citation Map (Timeline X=Year & Force Network, Offline-Ready)
 │     │    • Smart Citation Stance & Retraction Audit (S2 Contexts + arXiv .tex \cite{} + Crossref)
 │     │    • Zero-Hallucination .bib Verifier & Preprint-to-Published Venue Upgrader
 │     └── literature-evidence-workflow:
 │          • Iterative Multi-Hop Deep Recall with Positive/Negative Seeds (Undermind Pattern)
 │          • Local arXiv .tar.gz LaTeX / OA PDF Unpacker + Parallel Subagent Evidence Matrix (Elicit++)
 │
 ├──► [2. scientific-computing]  (Stage 2: Reproducible Engineering & Google-Style Scientific Python)
 │     └── scientific-computing:
 │          • Canonical Layout (`data/raw/` Read-Only -> `src/` Guts -> `scripts/` Drivers -> `results/`)
 │          • Tidy Data, Semantic Artifact Naming, & Provenance JSON Sidecars (`scaffold_research_project.py`)
 │          • Google Python Style Adapted for NumPy/SciPy/PyTorch/JAX (`NaN`-Safe Guards, `.size` Truthiness, §3.16.5 Math)
 │          • Analytical/Conservation Oracles, Isolated `default_rng`, & AST Static Auditor (`audit_scientific_python.py`)
 │
 └──► [3. scientific-writing]    (Stage 3: Manuscript Architecture & Publication Visuals — Bidirectional ⇄ Bridge)
       ├── scientific-writing:   (Automatically co-invokes `scientific-figures` on every writing/revision task)
       │    • Conditional Literature Bridge (Calls back to [1] for Intro/Related Work, H1->H2 Pivots & .bib Verify)
       │    • Anti-Patchwork Holistic Reconstruction Protocol (Zero Factual/LaTeX Regression)
       │    • Narrative Spectrum (`AAA/ABT/DHY`), Dobzhansky Theme, `iABT->cABT->kABT`, Null-Result Reframing & Talks
       │    • Cross-Artifact Numeric/Protocol Consistency (`P1/P2` Lock) & LaTeX Linter (`lint_manuscript_visuals.py`)
       │    • Macro Storytelling (Schimel OCAR / Telegraphed OCAR / ABDCE / LDR / Hourglass / Rebuttals)
       │    • Reader-Expectation Mechanics (Gopen & Swan Topic -> Action Verb -> Stress + SCFL)
       └── scientific-figures:
            • 5-Gate Figure/Table Assertion-Evidence Audit (Doumont + Alley + Frankel & DePace + Cargill/Schimel)
            • Perceptual & Scale Laws (Wilke Ch. 1–29 + Rougier Ten Simple Rules)
            • Okabe–Ito CVD-Safe Palettes, Exact Journal Widths, & Clean Booktabs Tables

 [Standalone On-Demand: llm-review-triage]  (0 Always-On Rules — Invoked ONLY on External AI Reviews / `/llm-review-triage`)
  └── llm-review-triage:
       • Soul Lock + Limitation-Boomerang Immunity + Test-Time Overthinking / Confounder-Inflation Filter
       • Round <= 2 Contractive Drift Hard-Stop & Anti-Defensive-Writing Diff Auditor (`audit_review_and_hedging.py`)
```

---

## Why Native Open-Stack Skills Over Fragmented SaaS?

| Capability | Typical Commercial SaaS | How `scientific-research-skills` Solves It Openly |
| :--- | :--- | :--- |
| **Deep Iterative Discovery** | *Undermind* | Multi-framing query expansion + strict pre-registered screening rubric + positive/negative SPECTER2 seed snowballing until $<10\%$ marginal hit saturation. |
| **Seed Lineage & Visual Maps** | *ResearchRabbit 2.0 / Litmaps* | `scholarly_graph.py lineage` + `render_citation_map.py`: computes specificity-weighted co-cited roots, active citing frontier, and SPECTER2 siblings, compiling an interactive Timeline/Force HTML map. |
| **Citation Stance & Retractions** | *Scite* | `scholarly_graph.py citation-audit` & `tex-context`: pulls S2 verbatim citing `contexts`/`intents`, **automatically extracts exact `\cite{}` sentences from citing arXiv `.tex` sources**, and checks OpenAlex + Crossref (Retraction Watch). |
| **Structured Evidence Tables** | *Elicit* | `unpack_paper_corpus.py` flattens arXiv `.tar.gz` LaTeX (`fulltext.tex` + `tables.tex` — zero PDF chunking loss!) for parallel subagent extraction into `CSV`, `Markdown`, and Booktabs `.tex`. |
| **Library RAG & Drafting** | *SciSpace* | Replaces lossy PDF-chunk RAG and generic gap-spotting clichés with local LaTeX/full-text inspection bridged directly into Schimel `OCAR` Funnels and taxonomic `Related Work`. |

---

## Repository Structure

```text
scientific-research-skills/
├── .claude-plugin/marketplace.json      # Claude Code plugin marketplace manifest
├── rules/GLOBAL_RESEARCH_ROUTER.md      # Optional Always-On Stage 0–3 global research router (--pin-global)
├── scripts/install.sh                   # Cross-agent installer (antigravity | claude | codex | cursor | all)
└── plugins/
    ├── scientific-ideation/             # Plugin 0: Problem Taste, Strong Inference & Pareto Ideation
    │   ├── plugin.json
    │   ├── rules/AGENTS.md              # Anti-armchair-slop, competing hypotheses & 1–4h kill-test rules
    │   └── skills/
    │       └── scientific-ideation/
    │           ├── SKILL.md
    │           ├── references/{problem-taste-and-pareto-selection.md, strong-inference-and-anti-slop-audit.md, crucial-experiment-and-murder-board.md}
    │           └── scripts/lint_research_ideas.py
    ├── research-literature/             # Plugin 1: Literature Graph, Audit & Evidence Matrices
    │   ├── plugin.json
    │   ├── rules/AGENTS.md              # Zero-hallucination .bib, retraction & provenance guardrails
    │   └── skills/
    │       ├── scholarly-graph-audit/
    │       │   ├── SKILL.md
    │       │   └── scripts/{scholarly_graph.py, render_citation_map.py}
    │       └── literature-evidence-workflow/
    │           ├── SKILL.md
    │           ├── references/{ml_extraction_schemas.md, evidence_matrix_workflow_template.py}
    │           └── scripts/{unpack_paper_corpus.py, compile_evidence_matrix.py}
    ├── scientific-computing/            # Plugin 2: Reproducible Scientific Python & Google Style
    │   ├── plugin.json
    │   ├── rules/AGENTS.md              # Read-only raw data, NaN-safe guards, RNG & Google Style rules
    │   └── skills/
    │       └── scientific-computing/
    │           ├── SKILL.md
    │           ├── references/{project-data-and-reproducibility.md, google-python-scientific-style.md, testing-profiling-and-numerical-rigor.md}
    │           └── scripts/{scaffold_research_project.py, audit_scientific_python.py}
    └── scientific-writing/              # Plugin 3: Scholarly Writing & Publication Figures
        ├── plugin.json
        ├── rules/AGENTS.md              # Scope gates + Anti-Patchwork & Proportional-Ink rules
        └── skills/
            ├── scientific-writing/
            │   ├── SKILL.md
            │   ├── scripts/lint_manuscript_visuals.py
            │   └── references/{macro-structure-and-sections.md, micro-style-flow-and-condensing.md, scfl-editing-and-examples.md, cross-artifact-consistency-audit.md}
            └── scientific-figures/
                ├── SKILL.md
                ├── references/{figure-table-assertion-evidence-audit.md, chart-directory-and-encodings.md, design-principles-tables-and-storytelling.md}
                └── resources/publication_rcparams.py
    └── llm-review-triage/               # Standalone On-Demand Plugin: Area-Chair Filter for AI Reviews
        ├── plugin.json                  # (Intentionally NO rules/AGENTS.md -> 0 Always-On overhead)
        └── skills/
            └── llm-review-triage/
                ├── SKILL.md
                ├── references/{lrm-critic-pathologies-and-ac-triage.md, anti-hedging-and-soul-preservation.md}
                └── scripts/audit_review_and_hedging.py
```

---

## Installation

### Prerequisite: `uv` (for Python CLI tools)
All CLI scripts use inline [PEP 723](https://peps.python.org/pep-0723/) metadata and manage isolated environments automatically via `uv`—no manual `pip install` or virtual environment setup required:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Quick Install Across Agents

Clone this repository and run `scripts/install.sh`:
```bash
git clone https://github.com/lrgthu/scientific-research-skills.git
cd scientific-research-skills

# Install for Google Antigravity (~/.gemini/config/plugins/) and pin global default research router
./scripts/install.sh --target antigravity --pin-global

# Install skills for Claude Code (~/.claude/skills/), Codex (~/.codex/skills/), or Cursor (~/.cursor/skills/)
./scripts/install.sh --target claude --pin-global
./scripts/install.sh --target codex
./scripts/install.sh --target cursor

# Or install everywhere at once and pin global Always-On research routing
./scripts/install.sh --target all --pin-global
```

For **Claude Code Plugin Marketplace** users, you can also register the repository directly:
```text
/plugin marketplace add lrgthu/scientific-research-skills
```

---

## Standalone CLI Quickstart (Zero API Keys Required)

Every script in `research-literature` works out of the box **without API keys**—caching responses locally in `~/.cache/research-literature/http_cache.sqlite3` and automatically falling back across **Semantic Scholar → OpenAlex → Crossref → arXiv LaTeX source** whenever public rate limits are encountered.

### 1. Map Citation Lineage & Render an Interactive Graph (ResearchRabbit + Litmaps)
```bash
GRAPH_CLI="plugins/research-literature/skills/scholarly-graph-audit/scripts"

uv run "$GRAPH_CLI/scholarly_graph.py" lineage \
  --seeds "arXiv:2305.18290" "arXiv:2203.02155" \
  --max-per-group 12 \
  --output /tmp/dpo_lineage.json

uv run "$GRAPH_CLI/render_citation_map.py" /tmp/dpo_lineage.json \
  --mode standalone \
  --title "RLHF & DPO Citation Lineage" \
  --output /tmp/dpo_citation_map.html
```

### 2. Audit In-Text Citation Stance, LaTeX `\cite{}` Sentences & Retractions (Scite Pattern)
```bash
# Corpus-wide citation context + Crossref Retraction Watch audit
uv run "$GRAPH_CLI/scholarly_graph.py" citation-audit "arXiv:2305.18290" \
  --max-citing 50 \
  --output /tmp/dpo_audit.json

# Extract verbatim \cite{} sentences + resolved bibliography keys directly from any arXiv .tar.gz source
uv run "$GRAPH_CLI/scholarly_graph.py" tex-context \
  --arxiv "2305.18290" \
  --query "ouyang" \
  --output /tmp/dpo_tex_cites.json
```

### 3. Verify `.bib` Files, Lint `.tex` Citations, Catch Hallucinations & Upgrade Stale Preprints
```bash
uv run "$GRAPH_CLI/scholarly_graph.py" bib-verify \
  --bib references.bib \
  --tex-dir ./manuscript \
  --output-bib references_verified.bib \
  --report /tmp/bib_audit_report.json
```
- Flags fabricated/unresolvable entries as `UNVERIFIED_HALLUCINATION_RISK` and author collisions as `METADATA_AUTHOR_MISMATCH`.
- Flags retracted/withdrawn works via OpenAlex `is_retracted`, Crossref Retraction Watch, and OpenReview (`RETRACTED_OR_WITHDRAWN`).
- Upgrades stale `arXiv` `@misc` entries to peer-reviewed venue records across Crossref, OpenAlex, and **OpenReview** (`UPGRADE_AVAILABLE_TO_PUBLISHED`, e.g., NeurIPS/ICLR/ICML/TMLR) while preserving your existing BibTeX citation keys.
- Audits `.tex` manuscripts for undefined `[?]` citations (`undefined_cite_keys_in_tex`), duplicate papers under multiple keys (`duplicate_work_keys`), and unused `.bib` entries.

### 4. Unpack arXiv LaTeX Corpus & Compile Booktabs Evidence Matrices (Elicit++)
```bash
WF_CLI="plugins/research-literature/skills/literature-evidence-workflow/scripts"

uv run "$WF_CLI/unpack_paper_corpus.py" \
  --from-json /tmp/dpo_lineage.json \
  --max-papers 15 \
  --out-dir ./literature/corpus

uv run "$WF_CLI/compile_evidence_matrix.py" \
  ./literature/extractions.json \
  --out-dir ./literature/matrix
```

### 5. Scaffold a Reproducible Scientific Python Repo & Run Static Scientific/Google-Style Audits
```bash
SCICOMP_CLI="plugins/scientific-computing/skills/scientific-computing/scripts"

# Scaffold src/ + read-only data/raw/ + Google-docstring Ruff + pytest + provenance sidecar runner
uv run "$SCICOMP_CLI/scaffold_research_project.py" ./my-experiment --author "Your Lab"

# Audit any research codebase for NaN range traps, global RNGs, mutable defaults, array truthiness, & Google Style
uv run "$SCICOMP_CLI/audit_scientific_python.py" --strict ./my-experiment
```

### 6. Validate & Pareto-Rank Candidate Research Ideas (Stage-0 Strong Inference & Murder Board)
```bash
IDEATION_CLI="plugins/scientific-ideation/skills/scientific-ideation/scripts/lint_research_ideas.py"

# Generate a structured candidate-portfolio JSON template
uv run "$IDEATION_CLI" --init-template /tmp/candidate_ideas.json

# Validate competing hypotheses, anti-slop terminology, & kill conditions, and render an Alon Pareto Murder-Board brief
uv run "$IDEATION_CLI" /tmp/candidate_ideas.json \
  --markdown-out ./ideation_murder_board.md \
  --strict
```

### 7. Triage External Reasoning-Model Reviews & Guard Diffs Against Defensive Hedging (`/llm-review-triage`)
```bash
TRIAGE_CLI="plugins/llm-review-triage/skills/llm-review-triage/scripts/audit_review_and_hedging.py"

# Scaffold & summarize an Area-Chair review triage ledger (separating 20% high-ROI substance from overthinking noise)
uv run "$TRIAGE_CLI" init-ledger /tmp/triage_ledger.json
uv run "$TRIAGE_CLI" summarize-ledger /tmp/triage_ledger.json --markdown-out ./review_triage_brief.md --strict

# Audit a manuscript diff before/after review edits to block stacked hedge chains & apologetic scar tissue
uv run "$TRIAGE_CLI" diff-audit ./manuscript/before.tex ./manuscript/after.tex --strict
```

*(Optional Rate-Limit Keys)*: For heavy batch workloads, literature scripts automatically pick up `S2_API_KEY`, `OPENALEX_API_KEY`, and `CROSSREF_MAILTO` from `~/.env` if defined.

---

## Methodological Foundations & Credits

The rules, workflows, and presets in this repository are clean-room operationalizations inspired by foundational works in scientific inquiry, scientific computing, scientific communication, data visualization, and open bibliometrics:

- **Problem Selection, Strong Inference & Research Ideation**:
  - John R. Platt, *"Strong Inference,"* *Science* 146(3642), 347–353 (1964, `10.1126/science.146.3642.347`).
  - Richard W. Hamming, *"You and Your Research,"* Bell Communications Research Colloquium Seminar (March 7, 1986).
  - Uri Alon, *"How To Choose a Good Scientific Problem,"* *Molecular Cell* 35(6), 726–728 (2009, `10.1016/j.molcel.2009.09.013`).
  - Zachary C. Lipton & Jacob Steinhardt, *"Troubling Trends in Machine Learning Scholarship,"* *ACM Queue* 17(1), 45–77 (2019, `arXiv:1807.03341`).
  - Chenglei Si, Diyi Yang & Tatsunori Hashimoto, *"Can LLMs Generate Novel Research Ideas? A Large-Scale Human Study with 100+ NLP Researchers,"* *ICLR* (2025, `arXiv:2409.04109`).

- **Scientific Computing, Reproducibility & Python Engineering**:
  - Greg Wilson, D. A. Aruliah, C. Titus Brown, Neil P. Chue Hong, Matt Davis, Richard T. Guy, Steven H. D. Haddock, Kathryn D. Huff, Ian M. Mitchell, Mark D. Plumbley, Ben Waugh, Ethan P. White & Paul Wilson, *"Best Practices for Scientific Computing,"* *PLOS Biology* 12(1): e1001745 (2014, `arXiv:1210.0530`, CC BY).
  - Greg Wilson, Jennifer Bryan, Karen Cranston, Justin Kitzes, Lex Nederbragt & Tracy K. Teal, *"Good Enough Practices in Scientific Computing,"* *PLOS Computational Biology* 13(6): e1005510 (2017, `arXiv:1609.00037`, CC BY).
  - Google, *[Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)* (CC BY 3.0).

- **Scientific Storytelling & Prose Architecture**:
  - Joshua Schimel, *Writing Science: How to Write Papers That Get Cited and Proposals That Get Funded* (Oxford University Press, 2012).
  - Margaret Cargill & Patrick O'Connor, *Writing Scientific Research Articles: Strategy and Steps* (3rd ed., Wiley-Blackwell, 2021).
  - Randy Olson, *Houston, We Have a Narrative: Why Science Needs Story* (University of Chicago Press, 2015).
  - George D. Gopen & Judith A. Swan, *"The Science of Scientific Writing,"* *American Scientist* 78(6), 550–558 (1990).
- **Assertion-Evidence Visual Auditing, Data Visualization & Publication Tables**:
  - Jean-luc Doumont, *Trees, Maps, and Theorems: Effective Communication for Rational Minds* (Principiae, 2009).
  - Michael Alley, *The Craft of Scientific Writing* (4th ed., Springer, 2018) & *The Craft of Scientific Presentations* (2nd ed., Springer, 2013).
  - Felice C. Frankel & Angela H. DePace, *Visual Strategies: A Practical Guide to Graphics for Scientists and Engineers* (Yale University Press, 2012).
  - Claus O. Wilke, *Fundamentals of Data Visualization* (O'Reilly Media, 2019).
  - Nicolas P. Rougier, Michael Droettboom & Philip E. Bourne, *"Ten Simple Rules for Better Figures,"* *PLOS Computational Biology* 10(9): e1003833 (2014, CC BY 4.0).
  - Masataka Okabe & Kei Ito, *Color Universal Design (CUD)* palette (2008).
- **Open Scholarly Infrastructure**:
  - [Semantic Scholar Academic Graph & Recommendations API](https://www.semanticscholar.org/product/api) (AI2 / SPECTER2), [OpenAlex](https://openalex.org/), [Crossref REST API & Retraction Watch](https://www.crossref.org/documentation/retrieve-metadata/rest-api/), and [arXiv](https://info.arxiv.org/help/api/index.html). Please respect each provider's API terms of service and individual paper licenses.

---

## License

Released under the [MIT License](./LICENSE).
