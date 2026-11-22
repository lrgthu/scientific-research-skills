---
name: scholarly-graph-audit
description: >
  Maps seed-based scholarly citation lineages (co-cited foundational roots,
  bibliographic-coupling active frontier, SPECTER2 positive/negative embedding
  neighbors, and recurring authors — ResearchRabbit / Litmaps pattern), renders
  interactive HTML citation network/timeline maps, audits verbatim in-text
  citing contexts, functional intents, arXiv LaTeX \cite{} sentences, and
  Crossref/OpenAlex retraction notices (Scite pattern), and verifies/upgrades
  canonical .bib bibliographies with zero hallucinated citations.
---

# Scholarly Graph, Citation Stance Audit & `.bib` Verification Skill

Bridges single-paper search and manuscript writing (`scientific-writing`) using a **100% open scholarly graph stack**:
- **Semantic Scholar Academic Graph + SPECTER2 Recommendations API** (`TLDR`, `isInfluential`, verbatim citing `contexts`, `intents`, positive/negative seed embeddings)
- **OpenAlex Graph** (`referenced_works`, `cites`, `is_retracted`, published-venue deduplication, automatic fallback if the Semantic Scholar anonymous pool throttles)
- **Crossref REST API + Retraction Watch** (`update-to` / `updated-by` retractions, expressions of concern, errata)
- **arXiv `.tar.gz` LaTeX Source Parser** (verbatim `\cite{}` sentence extraction even on brand-new preprints not yet parsed by citation indexers)

All HTTP responses are cached locally in `~/.cache/research-literature/http_cache.sqlite3` (7-day TTL).

---

## Prerequisites & Optional Rate-Limit Keys

1. **`uv`**: Ensure `uv` is installed and on `PATH` (`uv --version`, or `curl -LsSf https://astral.sh/uv/install.sh | sh`).
2. **Works Keyless Out of the Box**: Do **NOT** block execution if API keys are unset. Both scripts automatically load `~/.env` via `python-dotenv` and fall back across providers seamlessly.
3. **Optional Keys (`S2_API_KEY`, `OPENALEX_API_KEY`, `CROSSREF_MAILTO`)**:
   - Only if the user requests high-volume batch runs or dedicated rate limits, verify presence safely (`grep -sq "^S2_API_KEY=" ~/.env`; **never** `cat` or `echo` secret values into chat logs) and provide a local hidden-input `read -s` terminal snippet for the user to add their key.

Resolve `<SKILL_DIR>` to the directory containing this `SKILL.md` file:
```bash
SCRIPT_DIR="<SKILL_DIR>/scripts"
```

---

## Core Workflows & CLI Reference

### 1. Seed-to-Lineage Mapping (`lineage` — ResearchRabbit / Litmaps Engine)

Given 1–6 seed papers (DOIs, `arXiv:xxxx.xxxxx`, OpenAlex `W...`, S2 IDs, or exact titles) and optional `--negatives` (off-topic papers to steer SPECTER2 away from adjacent subfields):

```bash
uv run "$SCRIPT_DIR/scholarly_graph.py" lineage \
  --seeds "arXiv:1706.03762" "arXiv:2005.14165" \
  --negatives "arXiv:2010.11929" \
  --max-per-group 15 \
  --output /tmp/lineage_graph.json
```

**What it computes:**
- **`foundational_ancestors` (Co-Citation Roots)**: Papers cited by multiple seeds, ranked by specificity-adjusted co-citation ($\text{seed\_count}^{2.2} / \ln(12 + \text{global\_citations})$) so subfield-defining roots surface above generic utilities.
- **`active_frontier` (Bibliographic Coupling / Descendants)**: Recent & influential works citing multiple seeds.
- **`semantic_siblings` (SPECTER2 Recommendations)**: Embedding-nearest papers (catching concurrent preprints that use different terminology and do not yet cite the seeds).
- **`key_authors`**: Researchers recurring across $\ge 2$ nodes in the discovered subgraph.

---

### 2. Interactive Citation Map Visualization (`render_citation_map.py`)

Whenever exploring a new research topic from seed papers or asked to visualize citation relationships, compile a self-contained, theme-aware interactive HTML map (supports **Timeline `X = Year`** and **Force Network** layouts, role filters, search, pan/zoom, and click-to-inspect drawer):

```bash
uv run "$SCRIPT_DIR/render_citation_map.py" /tmp/lineage_graph.json \
  --mode standalone \
  --title "Topic Citation Lineage Map" \
  --output citation_map.html
```
- **Standard Browser / CLI Agents (Claude Code, Codex, Cursor)**: Save `citation_map.html` in the workspace/output directory so the user can open it directly in any browser (works offline with built-in fallback styles).
- **Antigravity IDE Inline / Artifact View**: Render with `--mode inline` ($\le 395\text{px}$ height) or `--mode standalone`, write the resulting HTML into `<Artifact Directory Path>/citation_map.html` via native `write_file` with `ArtifactMetadata: {UserFacing: true, RequestFeedback: false}`, and embed inline via `<agent-embed src="file:///<Artifact Directory Path>/citation_map.html"></agent-embed>` when using `inline` mode.

---

### 3. Smart Citation Stance & Integrity Audit (`citation-audit` & `tex-context` — Scite Pattern)

Before relying on a prior paper's claim, choosing baselines, or framing `Related Work`, audit **how** subsequent papers actually cite it and verify its retraction/correction status:

```bash
# A. Corpus-wide in-text citation contexts, S2 intents, influential citers & Crossref Retraction Watch check
#    (Automatically falls back to extracting verbatim \cite{} sentences from top citing arXiv .tex sources if S2 throttles!)
uv run "$SCRIPT_DIR/scholarly_graph.py" citation-audit "arXiv:2305.18290" \
  --max-citing 80 \
  --output /tmp/citation_audit.json

# B. Direct LaTeX-source \cite{} sentence extraction (works even on brand-new arXiv preprints!)
uv run "$SCRIPT_DIR/scholarly_graph.py" tex-context \
  --arxiv "2402.03300" \
  --query "rafailov" \
  --output /tmp/tex_cite_contexts.json
```

**Agent Interpretation Protocol (Beyond Raw Tallies):**
- Do **NOT** blindly trust lexical cue counts alone: read the verbatim `contexts` in `contrasting_or_limitation_contexts`, `method_adoption_contexts`, and `supporting_or_result_contexts`.
- Distinguish four scholarly roles when summarizing for the user:
  1. **Empirical Reproduction / Support**: Independent work confirms the claim holds.
  2. **Boundary / Failure Mode Exposed**: Later work shows the method degrades under specific regimes (e.g., OOD shift, length extrapolation, high noise)—*prime material for `Introduction` Knowledge Gaps!*
  3. **Methodological Adoption**: Used directly as a backbone, loss, or evaluation protocol (`methodology` intent).
  4. **Superficial Background Mention**: Cited only in passing (`background` intent).
- **Retraction Alert**: If `integrity_status.is_retracted` is `true` or `crossref_updates` contains a retraction/expression of concern, warn the user prominently at the top of your response.

---

### 4. Zero-Hallucination `.bib` Verifier, Manuscript Linter & Preprint Upgrader (`bib-verify`)

Whenever auditing an existing `.bib` file, checking a LaTeX manuscript before submission, or generating verified BibTeX entries:

```bash
# Audit an existing .bib + cross-check a LaTeX manuscript directory for undefined [?], unused, or duplicate keys
uv run "$SCRIPT_DIR/scholarly_graph.py" bib-verify \
  --bib path/to/references.bib \
  --tex-dir path/to/manuscript_tex_dir \
  --output-bib path/to/references_verified.bib \
  --report /tmp/bib_audit_report.json

# Or resolve & generate verified BibTeX from DOIs / arXiv IDs / OpenReview URLs / titles
uv run "$SCRIPT_DIR/scholarly_graph.py" bib-verify \
  --ids "arXiv:2305.18290" "https://openreview.net/forum?id=ljNZyrAlaa" "10.1038/s41586-021-03819-2" \
  --output-bib /tmp/new_refs.bib \
  --report /tmp/new_refs_report.json
```

**Status Codes & Pre-Submission Checks:**
- `VERIFIED_PUBLISHED` / `VERIFIED_PREPRINT`: Safe to cite; list canonical URLs/DOIs.
- `UPGRADE_AVAILABLE_TO_PUBLISHED`: The `.bib` cited an `arXiv`/`bioRxiv` preprint that now has a peer-reviewed conference/journal publication (checked across OpenAlex, Semantic Scholar, Crossref, and **OpenReview** for recent ICLR/ICML/NeurIPS/TMLR acceptances)—adopt the upgraded `@inproceedings`/`@article` entry while preserving the user's original BibTeX key.
- `METADATA_YEAR_MISMATCH` / `METADATA_AUTHOR_MISMATCH`: Flags year drift or author-list mismatch (preventing generic-title false collisions!).
- `RETRACTED_OR_WITHDRAWN`: **Block silent citation**—surfaces Crossref/OpenAlex retractions and OpenReview `Withdrawn` notices immediately.
- `UNVERIFIED_HALLUCINATION_RISK`: Could not be verified across any scholarly index—flag explicitly to the user and **never** include in a final `.bib`.
- `manuscript_cross_check` (when `--tex-dir` is passed): Reports `undefined_cite_keys_in_tex` (preventing `[?]` in compiled PDFs), `duplicate_work_keys` (same paper cited under two different `.bib` keys), and `unused_bib_keys`.
