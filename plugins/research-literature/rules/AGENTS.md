# Global Research Literature Intelligence & Citation Integrity Rules

## 1. Dual-Skill Literature Scope Gate (Research Only; Everyday Coding & Ops Exempt)

- **GATE L1 — Citation Graph Lineage, Stance/Retraction Auditing, Interactive Maps, & `.bib` Verification (`scholarly-graph-audit`)**:
  Whenever **any** research session or subagent/workflow task involves **exploring a topic from seed papers, mapping research lineages (foundational ancestors / active frontier / concurrent preprints), rendering interactive citation network maps, auditing how a paper or baseline is cited by later work (supporting vs. contrasting/limitation vs. method adoption), checking retractions/corrections, or generating/auditing `.bib` bibliographies**:
  - You **MUST** read the `scholarly-graph-audit` skill (`skills/scholarly-graph-audit/SKILL.md`, using its path from your available skills list) before running ad-hoc web searches or writing `.bib` entries, and propagate this requirement to delegated subagents/workflows.

- **GATE L2 — Deep Literature Pursuit, Systematic Screening, & Multi-Paper Evidence Matrices (`literature-evidence-workflow`)**:
  Whenever **any** research session or subagent/workflow task involves **exhaustively tracking fine-grained research questions hard to express with keywords, batch-screening candidate papers, extracting structured multi-paper comparison matrices (methods, datasets, metrics, compute, failure modes), building a local project paper corpus, or synthesizing literature prior to drafting `Introduction` / `Related Work` / baseline comparison tables**:
  - You **MUST** read the `literature-evidence-workflow` skill (`skills/literature-evidence-workflow/SKILL.md`, using its path from your available skills list), coordinating downstream prose with `scientific-writing` and tables with `scientific-figures`.

- **EXPLICIT EXEMPTION**:
  Everyday coding, debugging, software docs (`README.md`/PRs/commits), infrastructure/ops tasks, and math/algorithm derivations that make no empirical literature or bibliography claims are **exempt**.

---

## 2. Ironclad Citation & Evidence Integrity Guardrails

1. **Zero Unverified `\cite{}` or `.bib` Entries**:
   - **Never** invent, guess, or emit a BibTeX entry, DOI, arXiv ID, author list, publication year, venue, or baseline metric from parametric memory.
   - Before adding new entries to a `.bib` file or finalizing references in a manuscript/rebuttal/proposal, **verify every citation** via `scholarly_graph.py bib-verify` (or verified scholarly database CLIs). Unresolvable citations must be flagged `[UNVERIFIED — DO NOT CITE]` for user review rather than silently fabricated.
2. **Preprint-to-Published Upgrade & Retraction Gate**:
   - When curating `.bib` files or citing core baselines/foundational claims, check:
     - **Published Venue Upgrade**: If an arXiv/bioRxiv preprint has since been published in a peer-reviewed venue (e.g., NeurIPS, ICLR, ICML, CVPR, ACL, JMLR, *Nature*), prefer the canonical peer-reviewed venue record (retaining the `eprint` ID if helpful).
     - **Retraction & Contrasting-Citation Audit**: Verify `is_retracted == false` (OpenAlex) and Crossref `update-to` / Retraction Watch notices. Before resting a paper's core motivation or baseline choice on a prior claim, check incoming citation contexts (`citation-audit`) for known reproductions, caveats, or refutations.
3. **Provenance-Anchored Evidence Matrices (Full-Text / LaTeX First)**:
   - Never treat chunked RAG summaries or abstract-only skims as ground truth for experimental settings, equations, or ablation numbers.
   - Prefer unpacking **arXiv `.tar.gz` LaTeX source** (`fulltext.tex` + `tables.tex`) or full OA text (`unpack_paper_corpus.py`), and require every extracted matrix row to record an explicit provenance anchor (`section_or_table` + brief verbatim evidence); label any paper where full text was unavailable as `[abstract-only]`.
