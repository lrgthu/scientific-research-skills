---
name: literature-evidence-workflow
description: >
  Executes iterative multi-hop deep literature pursuit for fine-grained research
  questions hard to capture with keywords (Undermind pattern), unpacks candidate
  papers into a local arXiv LaTeX/full-text corpus, orchestrates parallel
  subagent screening and provenance-anchored structured evidence matrix
  extraction (Elicit pattern), and bridges evidence matrices directly into
  Schimel OCAR Funnels, taxonomic Related Work sections, and Booktabs tables.
---

# Iterative Deep Literature Pursuit & Parallel Evidence Matrix Skill

Replaces black-box literature RAG ("chat with PDFs") and paid tabular SaaS tools with a **transparent, source-code-level, provenance-anchored research pipeline**:

```text
Fine-Grained Question / Seed Papers
  ├─► Phase 1 (Undermind + ResearchRabbit): Multi-Framing Recall + Negative-Seed Snowballing
  ├─► Phase 2 (Elicit++): Local arXiv LaTeX / OA PDF Unpack + Parallel Subagent Evidence Matrix
  └─► Phase 3 (Schimel + Wilke Bridge): Concrete Knowledge Gap + Taxonomic Related Work + Booktabs `.tex`
```

Resolve `<WORKFLOW_DIR>` to the directory containing this `SKILL.md` file, and `<GRAPH_SCRIPTS>` to `../scholarly-graph-audit/scripts` relative to `<WORKFLOW_DIR>`:
```bash
WORKFLOW_DIR="<SKILL_DIR>"
GRAPH_SCRIPTS="<SKILL_DIR>/../scholarly-graph-audit/scripts"
```

---

## Phase 1: Iterative Deep Literature Pursuit (Undermind Protocol)

When a research question is too specific, cross-disciplinary, or mechanism-defined for single-shot keyword queries (where different communities invent different names for the same phenomenon):

1. **Pre-Register the Screening Rubric BEFORE Searching**:
   - Explicitly write down **Inclusion Criteria** (must-have problem setting, mathematical structure, or empirical regime) and **Exclusion Criteria** (superficially similar buzzwords that solve a different problem).
2. **Tri-Framing Query Expansion (Round 1 Broad Recall)**:
   - Decompose the question into **3 orthogonal terminological framings** (e.g., *ML/Deep Learning phrasing* vs. *Optimization/Control/Statistics phrasing* vs. *Phenomenon/Failure-mode phrasing*).
   - Run lightweight candidate recall across arXiv, OpenAlex, and `scholarly_graph.py resolve`.
3. **Positive + Negative Seed Graph Pursuit (Round 2+ Snowballing)**:
   - Screen Round 1 abstracts against the rubric:
     - Promote **true hits** to `--seeds` (`positivePaperIds`).
     - Promote **near-miss false positives** (wrong subfield sharing the same buzzwords!) to `--negatives` (`negativePaperIds`).
   - Run `uv run "$GRAPH_SCRIPTS/scholarly_graph.py" lineage --seeds ... --negatives ... --output round2_lineage.json` (see `scholarly-graph-audit` skill) to pull **Co-Cited Roots**, **Active Frontier**, and **SPECTER2 Semantic Siblings**.
4. **Explicit Saturation / Stopping Rule**:
   - Repeat snowball expansion on newly discovered high-relevance seeds until inspecting the top-20 newly surfaced graph neighbors yields **$<10\%$ ($\le 1\text{–}2$) new on-rubric papers**. Report the exact recall funnel (`Total Surfaced -> Abstract Screened -> Full-Text Included`) to the user.

---

## Phase 2: Local LaTeX/Full-Text Corpus & Parallel Evidence Matrix (Elicit++ Protocol)

Never extract comparison tables from chunked RAG snippets or memory. Always unpack full texts locally (preferring exact arXiv `.tex` source) and extract with explicit provenance anchors:

### Step 2.1 — Unpack Candidate Corpus (`unpack_paper_corpus.py`)

```bash
uv run "$WORKFLOW_DIR/scripts/unpack_paper_corpus.py" \
  --from-json /tmp/round2_lineage.json \
  --roles seed ancestor frontier semantic_sibling \
  --max-papers 20 \
  --out-dir ./literature/corpus
```
*(Or pass explicit IDs/local PDFs via `--papers "arXiv:2305.18290" "10.1038/..." "/path/to/local.pdf"`.)*

What this creates inside `<out-dir>/`:
- `corpus_manifest.json` summarizing provenance tiers (`latex_source`, `oa_pdf_fulltext`, `abstract_only`).
- Per-paper folders containing flattened, comment-stripped **`fulltext.tex` + `tables.tex`** (for arXiv papers) or page-stamped **`fulltext.txt` (`=== [Page N] ===`)** (for OA PDFs).

### Step 2.2 — Parallel Subagent Screening & Extraction

- For $\le 4$ papers, read `fulltext.tex` / `tables.tex` directly or via 1–2 subagents.
- For $5\text{–}30+$ papers:
  - **In Antigravity (`run_workflow`)**: Adapt [`./references/evidence_matrix_workflow_template.py`](./references/evidence_matrix_workflow_template.py) with the schemas in [`./references/ml_extraction_schemas.md`](./references/ml_extraction_schemas.md).
  - **In Claude Code / Codex / General Subagent Runtimes**: Fan out parallel subagents (one per entry in `corpus_manifest.json`) enforcing the JSON schema in [`./references/ml_extraction_schemas.md`](./references/ml_extraction_schemas.md), then merge their JSON objects into `extractions.json`.
  - **Human-in-the-Loop Standard**: The AI handles mechanical screening and structured extraction; always surface borderline exclusions and key assumptions so the researcher makes the final scientific judgment.

### Step 2.3 — Compile Multi-Format Matrix & Booktabs Table (`compile_evidence_matrix.py`)

```bash
uv run "$WORKFLOW_DIR/scripts/compile_evidence_matrix.py" \
  ./literature/extractions.json \
  --out-dir ./literature/matrix \
  --caption "Comparison of prior approaches across problem regimes, core mechanisms, and verified boundary conditions." \
  --label "tab:related_work"
```

Outputs:
1. `evidence_matrix.csv` — Spreadsheet/programmatic table.
2. `evidence_matrix.md` — Scannable Markdown table + Verbatim Provenance Audit + Exclusion Log.
3. `comparison_table.tex` — Publication-ready `booktabs` LaTeX table (`\toprule`/`\midrule`/`\bottomrule`, zero vertical bars, caption ABOVE).

---

## Phase 3: Downstream Synthesis Bridge to `scientific-writing`

When transitioning from Literature Matrix + Citation Audit (`scholarly-graph-audit`) to drafting manuscript prose, **load `scientific-writing` (`SKILL.md`)** and map the structured artifacts directly:

1. **`method_family` Clusters → Non-Author-Centric `Related Work`**:
   - Group rows by `method_family` (2–4 mechanistic camps) rather than writing chronological `"Author A (2022) proposed X. Author B (2023) proposed Y."` paragraphs.
   - Open each paragraph with the **shared mechanism and strength** of that camp (`Topic`), then pivot to its **structural `key_assumptions` / `verified_limitation`** in the `Stress` position.
2. **Intersection of `verified_limitation`s → Concrete `Introduction` Knowledge Gap**:
   - Contrast Camp A's limitation against Camp B's limitation to expose the exact unaddressed regime (`Challenge`: *"To determine/enable X without suffering Y, we..."* — zero vague `"little is known"` clichés).
3. **Final `.bib` Gate**:
   - Run `scholarly_graph.py bib-verify` on every cited paper to write verified, published-upgraded BibTeX entries into `references.bib`.
