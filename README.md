# Scientific Research Skills

**English** | [中文文档 (README_zh.md)](./README_zh.md)

[![CI](https://github.com/lrgthu/scientific-research-skills/actions/workflows/ci.yml/badge.svg)](https://github.com/lrgthu/scientific-research-skills/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B%20(uv)-3776AB.svg)](https://docs.astral.sh/uv/)
[![Agent Skills](https://img.shields.io/badge/Standard-SKILL.md%20%2B%20AGENTS.md-10B981.svg)](#installation)

An end-to-end, **zero-subscription open-stack research skill suite** for coding and research agents (**Google Antigravity**, **Claude Code**, **OpenAI Codex CLI**, **Gemini CLI**, and **Cursor**).

Most AI research workflows break in the middle: researchers juggle single-shot keyword search on one side, fragmented paid SaaS tabs (**Undermind**, **ResearchRabbit**, **Scite**, **Elicit**, **SciSpace**) in the middle, and patchwork LLM prose edits on the other. **`scientific-research-skills`** unifies the entire research lifecycle into **two decoupled, on-demand plugins** (`4` skills + `4` standalone `uv` Python CLIs + ironclad anti-hallucination & anti-patchwork rules):

```text
Seed Papers / Fine-Grained Research Question
 │
 ├──► [1. research-literature]  (100% Open Scholarly Stack — $0 SaaS Subscriptions)
 │     ├── scholarly-graph-audit:
 │     │    • Seed-to-Lineage Graph (Co-Cited Roots + Coupling Frontier + SPECTER2 Siblings)
 │     │    • Interactive HTML Citation Map (Timeline X=Year & Force Network, Offline-Ready)
 │     │    • Smart Citation Stance & Retraction Audit (S2 Contexts + arXiv .tex \cite{} + Crossref)
 │     │    • Zero-Hallucination .bib Verifier & Preprint-to-Published Venue Upgrader
 │     └── literature-evidence-workflow:
 │          • Iterative Multi-Hop Deep Recall with Positive/Negative Seeds (Undermind Pattern)
 │          • Local arXiv .tar.gz LaTeX / OA PDF Unpacker + Parallel Subagent Evidence Matrix (Elicit++)
 │
 └──► [2. scientific-writing]   (Manuscript Architecture & Publication Visuals — Bidirectional ⇄ Bridge)
       ├── scientific-writing:
       │    • Conditional Literature Bridge (Calls back to [1] for Intro/Related Work, H1->H2 Pivots & .bib Verify)
       │    • Anti-Patchwork Holistic Reconstruction Protocol (Zero Factual/LaTeX Regression)
       │    • Prose <-> Visual Symbiosis Laws & LaTeX Callout/Caption Linter (`lint_manuscript_visuals.py`)
       │    • Macro Storytelling (Schimel OCAR / Telegraphed OCAR / ABDCE / LDR / Hourglass / Rebuttals)
       │    • Reader-Expectation Mechanics (Gopen & Swan Topic -> Action Verb -> Stress + SCFL)
       └── scientific-figures:
            • Perceptual & Scale Laws (Wilke Ch. 1–29 + Rougier Ten Simple Rules)
            • Okabe–Ito CVD-Safe Palettes, Exact Journal Widths, & Clean Booktabs Tables
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
├── scripts/install.sh                   # Cross-agent installer (antigravity | claude | codex | cursor | all)
└── plugins/
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
    └── scientific-writing/              # Plugin 2: Scholarly Writing & Publication Figures
        ├── plugin.json
        ├── rules/AGENTS.md              # Scope gates + Anti-Patchwork & Proportional-Ink rules
        └── skills/
            ├── scientific-writing/
            │   ├── SKILL.md
            │   └── references/{macro-structure-and-sections.md, micro-style-flow-and-condensing.md, scfl-editing-and-examples.md}
            └── scientific-figures/
                ├── SKILL.md
                ├── references/{chart-directory-and-encodings.md, design-principles-tables-and-storytelling.md}
                └── resources/publication_rcparams.py
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

# Install for Google Antigravity (~/.gemini/config/plugins/)
./scripts/install.sh --target antigravity

# Install skills for Claude Code (~/.claude/skills/), Codex (~/.codex/skills/), or Cursor (~/.cursor/skills/)
./scripts/install.sh --target claude
./scripts/install.sh --target codex
./scripts/install.sh --target cursor

# Or install everywhere at once
./scripts/install.sh --target all
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

*(Optional Rate-Limit Keys)*: For heavy batch workloads, scripts automatically pick up `S2_API_KEY`, `OPENALEX_API_KEY`, and `CROSSREF_MAILTO` from `~/.env` if defined.

---

## Methodological Foundations & Credits

The rules, workflows, and presets in this repository are clean-room operationalizations inspired by foundational works in scientific communication, data visualization, and open bibliometrics:

- **Scientific Storytelling & Prose Architecture**:
  - Joshua Schimel, *Writing Science: How to Write Papers That Get Cited and Proposals That Get Funded* (Oxford University Press, 2012).
  - George D. Gopen & Judith A. Swan, *"The Science of Scientific Writing,"* *American Scientist* 78(6), 550–558 (1990).
- **Scientific Data Visualization & Publication Tables**:
  - Claus O. Wilke, *Fundamentals of Data Visualization* (O'Reilly Media, 2019).
  - Nicolas P. Rougier, Michael Droettboom & Philip E. Bourne, *"Ten Simple Rules for Better Figures,"* *PLOS Computational Biology* 10(9): e1003833 (2014, CC BY 4.0).
  - Masataka Okabe & Kei Ito, *Color Universal Design (CUD)* palette (2008).
- **Open Scholarly Infrastructure**:
  - [Semantic Scholar Academic Graph & Recommendations API](https://www.semanticscholar.org/product/api) (AI2 / SPECTER2), [OpenAlex](https://openalex.org/), [Crossref REST API & Retraction Watch](https://www.crossref.org/documentation/retrieve-metadata/rest-api/), and [arXiv](https://info.arxiv.org/help/api/index.html). Please respect each provider's API terms of service and individual paper licenses.

---

## License

Released under the [MIT License](./LICENSE).
