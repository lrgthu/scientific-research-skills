# Global Scientific Writing & Figure Rules (Schimel · Gopen & Swan · Wilke · Rougier et al.)

## 1. Dual-Skill Scope Gate (Research Only; Everyday & Ops Exempt)

- **GATE A — Scholarly Research Prose (`scientific-writing`)**:
  Whenever **any** research job, session, conversation, or subagent/swarm task involves **formal scientific, academic, or scholarly writing**—manuscripts (specialist journals, *Nature*/*Science*/*PNAS*, NeurIPS/ICML/ICLR/CVPR/ACL, arXiv/bioRxiv), paper sections (Title, Abstract, Intro, Related Work, Methods, Results, Discussion, Conclusion, Appendix prose), grant proposals (NSF, NIH, DOE, DARPA, Specific Aims), peer reviews, author rebuttals, theses, or formal science outreach articles:
  - You **MUST** read the `scientific-writing` skill (`skills/scientific-writing/SKILL.md`, using its path from your available skills list, plus relevant `references/*.md`) **before** outlining, drafting, or revising, and propagate this requirement to any delegated subagents/workflows/swarms.
  - **Conditional Literature Intelligence Bridge (`research-literature` ⇄ `scientific-writing`)**: When `scholarly-graph-audit` / `literature-evidence-workflow` are available, invoke them **selectively** during writing for (1) drafting/restructuring `Intro` Funnel, `Related Work`, Proposal `Background`, or `Rebuttal` literature comparisons without an existing verified evidence matrix, (2) `Tier-3` experimental thesis pivots ($H_1 \to H_2$) where the old `.bib` misses $H_2$'s lineage, and (3) verifying new/final `\cite{}` & `.bib` entries (`bib-verify`). **Exempt pure prose polishing, condensing, `SCFL` sentence edits, and `Methods`/`Results` internal flow edits** to keep non-literature writing zero-latency.

- **GATE B — Scientific Figures, Data Visualizations, Tables, & Captions (`scientific-figures`)**:
  Whenever **any** research job, session, conversation, or subagent/swarm task involves **designing, coding (Matplotlib/Seaborn/R/ggplot2/TikZ/PGFPlots/Vega/D3), styling, refactoring, critiquing, or captioning 2D scientific figures, benchmark/ablation plots, statistical charts, publication tables, schematics, poster visuals, or research presentation slides**:
  - You **MUST** read the `scientific-figures` skill (`skills/scientific-figures/SKILL.md`, using its path from your available skills list, plus relevant `references/*.md`) **before** writing plotting/table code or captions, **visually inspect rendered outputs** before delivery, and propagate this requirement to delegated subagents/workflows/swarms.
  - *(Note: Pure plotting/table tasks load `scientific-figures` only; pure prose tasks load `scientific-writing` only; tasks involving both figures/tables/captions and manuscript text load both.)*

- **EXPLICIT EXEMPTION (Do NOT Force-Invoke)**:
  Everyday chat Q&A, software `README.md`/docstrings/code comments/PRs/commits, non-scientific web/app UI styling, infrastructure/Grafana ops dashboards & runbooks, routine emails/messages, and 3D biomolecular structure visualization (where interactive sidecar viewers take priority) are **exempt** unless explicitly requested.

---

## 2. Anti-Patchwork Rule: Pre-Check & Holistic Reconstruction (反补丁写作铁律)

**Patchwork editing (*补丁式写作*—bolting new experimental rounds onto older drafts via incremental insertions/deletions) is strictly forbidden on full manuscripts and multi-section drafts:**

1. **Mandatory Pre-Write Diagnosis**: Before updating or expanding an existing paper/proposal (especially after new experiments, ablations, baselines, or negative/surprising findings), **inspect the full manuscript's `O–C–A–R` alignment, Hourglass symmetry, figure-to-story mapping, and story arcs**.
2. **Strict 3-Tier Triage**:
   - **Minor Fix (In-Place Allowed)**: *Only* typos, grammar, `\cite`/`\ref` fixes, or pure numeric sync where *zero* claims, rankings, mechanisms, or arcs change.
   - **Bounded Module Addition (Section-Level Arc Rewrite)**: New experiment purely reinforces an existing claim without shifting `Opening`, `Challenge`, or `Resolution` → audit whole-paper consistency and **rewrite the target subsection/section arc cleanly** (never append `"Moreover / It is worth noting..."` bolt-on paragraphs).
   - **Thesis/Mechanism/Boundary Shift OR Patchwork Debt (Full-Paper Retrospective & Holistic Rewrite — Default Principle)**:
     1. **Lock Hard Assets**: Freeze all verified numbers/stats, equations/notation, `\cite{}` keys, and `\label{}`/`\ref{}` anchors (zero factual regression).
     2. **Re-Distill Bottom-Up**: Pool *old + new* results without chronological bias; demote superseded experiments/figures to Appendix (*"murder your darlings"*); recalibrate `OCAR` and Hourglass width (`Opening == Resolution`).
     3. **Rewrite Top-Down**: Reconstruct prose seamlessly from `Opening → Funnel → Challenge → Action → Resolution` with unbroken serial arcs and continuous `Stress → Topic` flow.

---

## 3. Core Prose Principles (Schimel + Gopen & Swan)

- **Reader-Expectation North Star**: **Make the reader's job easy** (Schimel). Readers interpret substance from **structural location clues**—strive for **clarification without oversimplification** (Gopen & Swan). When a rule conflicts with reader comprehension, break the rule deliberately.
- **Structure Debugs Science**: When aligning `Old → New` exposes a missing logical step or unstated hypothesis between sentences/experiments, **explicitly supply the missing scientific connection**.
- **Macro Storytelling (`Data → Information → Knowledge → Understanding` & `SUCCES`)**:
  - Discover the story **bottom-up** from data/outliers; tell it **top-down**. Match structure to audience patience: **`OCAR`** (specialist journals), **Telegraphed `OCAR`** (ML/AI conferences & biomedical), **`ABDCE`/`LDR`** (proposals—win pages 1–2 and **always** end with a synthesis Resolution), **`LDR`** (*Nature*/*Science*, abstracts, public), **`LD`** (Methods, Results paragraphs, right-opening sentences).
  - Match `Resolution` width to `Opening` width. Frame the Introduction as a **Funnel** around a concrete **Knowledge Gap** (ban `"little is known"`, ban `"Smith (2003) found X"` author-subject lists unless contrasting rival camps, ban **Bizzwidget** solution-before-problem pitches). State Challenge as **`"To learn/determine X, we did Y"`**. Separate **Data** (first) → **Inference** → **Interpretation**; lead with **effect sizes and fit ($R^2$, fold-change, $\Delta$)** over binary $p$-values. Handle caveats early via **`"But, yes"`**—**NEVER** end with `"more research is needed"`, vague `"may provide insights"`, or surprise topics.
- **Sentence & Flow Mechanics**:
  - One function per unit in complete serial arcs (`TS-D`/`LD` point-first or `LDR`/`OCAR` point-last; zero point-nowhere paragraphs).
  - **Topic (`Subject`)** = whose story + backward-linking **old information** (`Janus` `Stress → Topic` relay) → **Immediate Action Verb** (zero long Subject–Verb interruptions; replace static/fuzzy verbs & zombie nominalizations; use passive *only* to keep the continuing character in Topic or omit irrelevant actors) → **Stress (`Syntactic Closure`)** = **new, emphasis-worthy information** (use `;`, `:`, `both...and`, or lists for secondary Stress; *a sentence is too long iff Stress candidates > Stress positions*). Revise iteratively via **`SCFL`**.

---

## 4. Core Visualization & Table Principles (Claus O. Wilke + Rougier, Droettboom & Bourne)

- **Repeatable Pipeline, Story Role, & Medium (Wilke Ch. 1, 24, 28–29 · Rougier Rules 1–3, 9–10)**:
  - Eliminate **Wrong** (math/unit/`>100%` pie/negative KDE errors) → **Bad** (misleading/confusing encodings) → **Ugly** (imbalanced styling). Generate plots programmatically from raw data with **seeded RNGs** (separating content from theme).
  - **"Make a figure for the generals"**: Strip tangential variables; order panels left-to-right (`Context/Input → Discovery`); progress from **raw-data views → derived metrics** across **`3–6` diverse, non-repetitive figures** per storyline. **Never copy-paste paper figures into slides**: build paper figures at exact column width (`scale=1.0`, `7–9 pt` fonts, TrueType `.pdf` `pdf.fonttype=42` or lossless `.png`, **never `.jpeg`**) and rebuild slides with thicker lines and $\ge 14\text{–}18\text{ pt}$ horizontal text.
- **Proportional Ink, Scales, Chart Choice, & Uncertainty (Wilke Ch. 3, 6–18 · Rougier Rule 7)**:
  - **Proportional Ink**: Linear bars/shaded areas **must start at `0`** (use **Cleveland dot plots** or $\Delta$-from-baseline for tight non-zero ranges); **plot all ratios/fold-changes on a log scale** with bars anchored at **`1`** (never draw raw-amount bars on log scales; label log axes with the variable name itself or explicit `log₁₀`/`log₂`). Scale bubble **area** (`s`), never radius; swap to **horizontal bars** instead of rotated tick labels; sort unordered categories by value while preserving natural order on ordered factors.
  - **Distributions & Uncertainty**: **Ban `Mean ± 2·SD` error bars** for population spread and **ban stacked/overlapping histograms** (use filled KDEs, ECDF/Q–Q, shaded boxplots, violins, **sina plots**, or **ridgelines**). State exact error-bar definitions (`SE`, `80%/95%/99%` graded CI, posterior half-eyes), and **never eyeball overlapping CIs for significance**—plot **contrast CIs directly against $\Delta = 0$**. Handle overplotting via `alpha + jitter` → `hexbin` → contours/facets; **ban gratuitous & static 3D**.
- **Color, Direct Labeling, Multi-Panel, Captions, & Clean Tables (Wilke Ch. 4, 19–25, 27 · Rougier Rules 4–6, 8)**:
  - Keep context gray and reserve accent color for focal series; **ban `jet`/`rainbow`**; use monotonic **Sequential** (`viridis`), zero-centered **Diverging** (`TwoSlopeNorm(vcenter=0)`), and **Okabe–Ito Qualitative** (`≤8` groups, paired with **solid shapes** over hollow line drawings, mindful that thin lines lose CVD contrast). **Eliminate legends via direct labeling** where possible (or match legend order to visual data rank).
  - Lock shared scales across **Small Multiples**; keep a **unified visual language** (consistent colors & left-to-right category order) and discreet `a, b` labels across **Compound Figures**; use light **perpendicular grids** (or `x = y` diagonal without grid on paired scatters).
  - **Titles, Captions & Tables**: Omit top canvas titles on paper figures—start the **caption below** with the declarative title + full encoding/uncertainty key; format **Publication Tables** with **zero vertical lines**, **zero inter-row horizontal lines**, left-aligned text, right-aligned uniform-decimal numbers (headers aligned to data!), and **captions ABOVE**. **Always visually inspect rendered figures via `read_file`**.
