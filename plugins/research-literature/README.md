# Research Literature Intelligence (`v1.0.0`)

Global Antigravity plugin (`isGlobal: true`) bridging raw scholarly database APIs (`science` plugin) and downstream manuscript/figure synthesis (`scientific-writing` plugin) using a **100% open, zero-subscription scholarly stack** (Semantic Scholar Academic Graph & SPECTER2 Recommendations + OpenAlex + arXiv LaTeX/HTML + Crossref / Retraction Watch):

1. **`scholarly-graph-audit` Skill** (`skills/scholarly-graph-audit/SKILL.md` + `scripts/`):
   - **Seed-to-Lineage Mapping (`lineage`)**: Absorbs **ResearchRabbit 2.0 & Litmaps**—computes co-cited foundational ancestors, bibliographic-coupling frontier descendants, SPECTER2 positive/negative embedding neighbors, and recurring key authors across Semantic Scholar + OpenAlex.
   - **Interactive Citation Map (`render_citation_map.py`)**: Compiles CSP-compliant, theme-aware interactive HTML visualizations (dual Timeline / Force-Graph toggle, role filters, search, and inspector drawer).
   - **Smart Citation Context & Integrity Audit (`citation-audit` & `tex-context`)**: Absorbs **Scite**—retrieves verbatim citing sentences (`contexts`), functional `intents` (`background` / `methodology` / `result`), `isInfluential` flags, direct arXiv `.tex` `\cite{}` sentence extraction, and Crossref/OpenAlex retraction & correction checks.
   - **Zero-Hallucination `.bib` Verifier (`bib-verify`)**: Cross-validates `.bib` files or paper IDs, flags hallucinated or retracted works, and automatically upgrades stale arXiv preprints to peer-reviewed venue publications (NeurIPS/ICLR/ICML/JMLR/etc.).

2. **`literature-evidence-workflow` Skill** (`skills/literature-evidence-workflow/SKILL.md` + `scripts/` + `references/`):
   - **Iterative Deep Literature Pursuit**: Absorbs **Undermind**—multi-framing query expansion, strict pre-registered inclusion/exclusion rubrics, SPECTER2 negative-seed refinement, and citation-snowball saturation checks.
   - **Parallel Full-Text / arXiv LaTeX Evidence Matrix**: Absorbs **Elicit** and replaces **SciSpace**—unpacks arXiv `.tar.gz` LaTeX sources (`fulltext.tex` + `tables.tex` + `.bib`/`.bbl`) or OA full texts locally and fans out parallel subagents (`run_workflow`) to extract provenance-anchored structured comparison matrices (`JSON` / `CSV` / `Markdown` / Booktabs `.tex`) ready for `scientific-writing` (`OCAR` Funnel & Taxonomic Related Work).

3. **Always-On Citation Integrity & Workflow Guardrail (`rules/AGENTS.md`)**:
   - Enforces verified `.bib` citations, preprint-to-published venue upgrades, retraction screening, and provenance-anchored evidence extraction whenever drafting scholarly `Related Work`, citation tables, or bibliographies.
