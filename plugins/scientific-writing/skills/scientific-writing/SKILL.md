---
name: scientific-writing
description: >-
  Authoritative scientific, academic, ML/computational, and scholarly research writing & storytelling skill synthesizing Joshua Schimel's Writing Science, Randy Olson's Houston, We Have a Narrative (ABT / Narrative Spectrum / Dobzhansky Template), and Gopen & Swan's The Science of Scientific Writing, with a strict Anti-Patchwork Holistic Reconstruction workflow. Activating scientific-writing (/scientific-writing) ALWAYS automatically loads and co-activates the sibling scientific-figures skill. Use whenever outlining, drafting, integrating new experimental rounds into, revising, condensing, reviewing, or critiquing scholarly manuscripts (specialist journals, Nature/Science, NeurIPS/ICML/ICLR/CVPR/ACL, arXiv/bioRxiv), abstracts, introductions, related work, methods, experiments/results, discussions, grant proposals (NSF/NIH/DARPA), peer reviews, author rebuttals, theses, research talks/keynotes/elevator pitches, or formal science outreach articles. Don't use for everyday casual chat, code comments/docstrings/READMEs/PRs, homelab/ops runbooks, or routine emails unless explicitly requested.
---

# Scientific Writing & Storytelling Skill (Schimel + Olson + Gopen & Swan)

> **Core Premise**: Science advances via hypothetico-deductive problem solving (`AND → BUT → THEREFORE`), and readers interpret substance from **structural location clues** rather than absorbing disconnected facts (`AAA`). Making the reader's job effortless—unifying evidence around a singular theme and achieving **structural clarification without technical oversimplification or hype**—is the author's primary responsibility *(synthesizing Joshua Schimel, Writing Science, 2012; Randy Olson, Houston, We Have a Narrative, 2015; George D. Gopen & Judith A. Swan, "The Science of Scientific Writing," American Scientist, 1990)*.

This skill operationalizes three complementary scales of scientific communication—**Joshua Schimel's macro-architecture** (`OCAR`, `SUCCES`, Hourglass, `"But, yes"`, `SCFL`), **Randy Olson's narrative-spectrum & compression tools** (`WSP`, Dobzhansky Template, `AAA ↔ ABT ↔ DHY`, `iABT → cABT → kABT`, `Agon` null-result reframing, and oral talk storytelling), and **Gopen & Swan's sentence-level reader-expectation theory** (Syntactic Resolution, `Old → New` Topic/Stress architecture, Medial Closure, and Structural Logic Debugging)—backed by a mandatory **Anti-Patchwork Holistic Reconstruction Protocol**.

## Mandatory Automatic Co-Invocation (`/scientific-writing` $\implies$ `/scientific-figures`)

> **REQUIRED ON EVERY INVOCATION**: Whenever `scientific-writing` (or `/scientific-writing`) is activated—whether via user slash command, automatic global routing, or subagent delegation—you **MUST immediately read [`../scientific-figures/SKILL.md`](../scientific-figures/SKILL.md)** (plus [`../scientific-figures/references/figure-table-assertion-evidence-audit.md`](../scientific-figures/references/figure-table-assertion-evidence-audit.md) when storyboarding, auditing, or revising drafts/slides) **before** outlining, drafting, or editing. Figures, sub-panels, and tables form the deductive spine of scientific storytelling; prose and visuals are never planned or revised in isolation. Always pass **both** `scientific-writing/SKILL.md` and `scientific-figures/SKILL.md` to any delegated subagents, `run_workflow` nodes, or `swarm` workers.

## Reference Modules (Progressive Disclosure)

Load the reference module(s) matching your task:

1. **[Macro Structure, ABT Narrative Spectrum, Sections, Proposals, Rebuttals & Talks](./references/macro-structure-and-sections.md)** — **Read when planning, outlining, pitching, or drafting**: `Data → Understanding`, Dobzhansky Core-Theme Test, `Agon` & Null/Boundary (`Miniplot`) Reframing, `SUCCES`, `OCAR` / Telegraphed `OCAR` / `ABDCE` / `LDR` / `LD`, Fractal `ABT` Engine & Narrative Spectrum (`AAA` vs. `ABT` vs. `DHY`), Goldilocks `iABT → cABT → kABT` calibration, Hourglass symmetry, Openings/Funnel/Challenge/Methods/Results/Discussion/Resolution, 8 Prose ⇄ Visual Symbiosis Laws, `"But, yes"` limitations, Message Box, **Author Rebuttals**, and **Oral Research Talks / Elevator Pitches**.
2. **[Micro-Architecture, Reader Expectations, Janus Flow, Verbs & Condensing](./references/micro-style-flow-and-condensing.md)** — **Read when drafting prose, fixing transitions, debugging opaque passages, or cutting length**: Nested serial arcs, Point-First (`TS-D`/`LD`) vs. Point-Last (`LDR`/`OCAR`) paragraphs, Gopen & Swan's 7 Reader-Expectation Principles, Syntactic Resolution (Subject–Verb gap pathology), Syntactic Closure (`;`/`:`/lists secondary Stress & Gopen–Swan sentence-length law), `Old → New` Janus relay, Topic-String & Verb-List diagnostics, uncovering hidden logical gaps, Active vs. Strategic Passive voice, Denominalization, Noun-train breaking, and 5 Delete-Key condensing targets.
3. **[Anti-Patchwork Reconstruction, SCFL Editing Protocol & Worked Examples](./references/scfl-editing-and-examples.md)** — **Read when updating an existing manuscript after new experiments, running full-paper revisions, or reviewing/critiquing drafts**: Anti-Patchwork Audit & Holistic Rewrite Protocol, iterative `SCFL` + Story-Circle checklist, 10-dimension review scorecard, and clean-room Before → After rewrites (`Old → New` gaps, `DHY/AAA → ABT` abstracts, null-result reframing, visual callouts).
4. **[Figure & Table Assertion-Evidence Audit Protocol](../scientific-figures/references/figure-table-assertion-evidence-audit.md)** — **Read when storyboarding a paper's visuals from results, reviewing/critiquing manuscript figures & tables, or executing Anti-Patchwork `Tier-3` visual pruning**: Synthesizes Doumont (*1-sentence Message*), Alley (*Assertion–Evidence–Explanation*), Frankel & DePace (*Visual Inference Chains*), and Schimel / Cargill & O'Connor (*Figure-First Storyboarding & Deletion Counterfactual*) into a **5-Gate Visual-by-Visual Audit Ledger** (`KEEP` / `REFACTOR` / `SPLIT` / `MERGE` / `INLINE TO PROSE` / `DEMOTE OR DELETE`).
5. **[Cross-Artifact Numeric, Protocol & Directional Consistency Audit](./references/cross-artifact-consistency-audit.md)** — **Read when auditing, finalizing, revising, or writing rebuttals for empirical manuscripts**: Eliminates silent macro-vs-micro aggregation drift, unbadged protocol/rank/mask shifts (`P1` vs. `P2`), pooled-vs-stratified directional sign inversions, stale multi-round cache skew, and `pp` vs. `%` arithmetic mismatches via an **8-Tuple Protocol Identity Registry**, **Single-Source Generation**, and a **5-Matrix Consistency Gate**.
6. **Conditional Literature Intelligence Bridge (`scholarly-graph-audit` & `literature-evidence-workflow`, when installed)** — **Load selectively on literature-touching writing tasks**:
   - **Trigger**: (a) Drafting/restructuring `Introduction` Funnel, `Related Work`, Proposal `Background`, or `Rebuttal` literature positioning without an existing verified evidence matrix; (b) `Tier-3` narrative pivots ($H_1 \to H_2$) where existing `.bib` citations no longer cover the new core mechanism; (c) Adding new `\cite{}` entries or finalizing `.bib` (`bib-verify`).
   - **Fast-Path Exemption (Do NOT Trigger)**: Pure `SCFL` prose polishing, condensing, `Topic → Verb → Stress` flow tightening, `Methods` / `Results` internal narrative edits, or `Tier-1` minor fixes where citations and literature scope are already locked.

---

## Mandatory 5-Phase Execution Workflow

### Phase 0: Scope & Anti-Patchwork Pre-Check (Mandatory Gate for Existing Drafts)

Whenever modifying, expanding, or revising an existing manuscript or proposal (especially after completing a new round of experiments, ablations, or baselines), **STOP and audit the whole manuscript BEFORE editing any paragraph**:

1. **Check for the 5 Patchwork Pathologies (*补丁式写作症状*)**:
   - **Hourglass / `OCAR` Drift**: Does the Opening/Funnel still pitch an older hypothesis while new experiments shifted the real story, mechanism, or scope?
   - **Bolt-On Scars (`AAA` / `DHY` Accumulation)**: Are paragraphs stitched together with `"Moreover, we also tested..."` (`AAA` brick-piling) or zig-zagging `"However... Yet... Despite..."` caveats (`DHY` multi-directional confusion)?
   - **Chronological Lab-Log Ordering**: Are experiments ordered by when they were run rather than intellectual hierarchy (`primary claim → mechanism → boundary/ablation`)?
   - **Sunk-Cost Bloat**: Are superseded early exploratory experiments still cluttering the main text instead of being collapsed or moved to the Appendix?
   - **Broken `Old → New` Chains & Hidden Logical Gaps**: Did prior insertions sever `Stress → Topic` transitions or overload single sentences with multiple competing Stress candidates?

2. **Execute Strict 3-Tier Triage**:
   - **Tier 1 — Minor Fix (微小修复 → In-Place Edit Allowed)**: Pure typo/grammar polish, fixing `\cite`/`\ref`, or updating exact table/text numbers where *zero* claims, rankings, mechanisms, or story arcs change. (Verify local `Topic → Stress` continuity.)
   - **Tier 2 — Bounded Module Reinforcement (单点补强 → Section/Subsection Arc Rewrite)**: New experiment purely strengthens an existing claim without altering `Opening`, `Challenge`, or `Resolution`. Audit whole-paper consistency, then **rewrite the entire affected subsection/section cleanly as a nested `ABT` arc** (never wedge a patch paragraph!).
   - **Tier 3 — Story/Mechanism/Scope Shift OR Existing Patchwork Debt (全篇复盘重写 → Default for Full-Paper Iterations)**: Read [scfl-editing-and-examples.md](./references/scfl-editing-and-examples.md) Section 1 and execute the **4-Step Holistic Reconstruction Protocol**:
     1. **Lock Hard Assets**: Freeze an explicit inventory of verified metrics, equations/notation, `\cite{}` keys, `\label{}`/`\ref{}` tags, and co-author factual constraints (guaranteeing **zero factual or LaTeX regression**).
     2. **Bottom-Up Re-Distillation, Dobzhansky Test, 5-Gate Visual Audit, & Literature Pivot Check**: Pool *old + new* experimental results without chronological bias. Run `"Elaborate and Slash"` + Olson's **Dobzhansky Core-Theme Test** (`"Nothing in [these findings] makes sense except in the light of [unifying mechanism]"`) to lock **one singular Master `kABT`** (reframing null/boundary surprises via **Assumption-Refutation `ABT`** rather than defensive patching or false-positive hype). Execute the **5-Gate Assertion-Evidence Audit** ([figure-table-assertion-evidence-audit.md](../scientific-figures/references/figure-table-assertion-evidence-audit.md)) across every old and new figure, sub-panel, and table—inlining sparse/flat numbers into prose, merging duplicate table+plot pairs, and demoting superseded visuals to Appendix (*"murder your darlings"*). **Crucial Pivot Gate**: If the story shifted from $H_1 \to H_2$, check whether the existing `.bib` and `Related Work` cover $H_2$—if not, invoke `scholarly-graph-audit` (`lineage`) / `literature-evidence-workflow` (when available) on $H_2$!
     3. **Blueprint Alignment**: Formulate the updated `OCAR` + `kABT` + Hourglass blueprint (show a brief `Old vs. New OCAR/ABT` comparison when major thesis pivots warrant user sign-off, or proceed directly when instructed).
     4. **Clean-Slate Top-Down Rewrite**: Rewrite from `Opening → Funnel → Challenge → Action → Resolution` as one seamless organism.

---

### Phase 1: Diagnose Genre, Audience Schemas, & Macro Structure

1. **Clarification, Not Oversimplification**: Distinguish peer/specialist writing (preserve exact technical terms carrying established schemas; clarify via **structural placement**) from broad/interdisciplinary communication (lead with **Narrative Relatability `cABT`** and shared schemas before specialist terms).
2. **Select Macro Structure by Audience Patience**:
   - **Specialist Journal**: **`OCAR`** (Opening → Challenge → Action → Resolution).
   - **ML/CS Conference (NeurIPS/ICML/ICLR/CVPR/ACL) & Biomedical Paper**: **Telegraphed `OCAR`** (full `O → C` funnel ending with `"In this paper, we show..."` preview; closes with full `R`).
   - **Grant Proposal (NSF/NIH/DOE/DARPA)**: **`ABDCE`** or **`LDR`**—establish the Dobzhansky `"Why care?"` stakes and `kABT` hook to win pages 1–2, and **always** end with a synthesis Resolution paragraph.
   - **Generalist High-Impact (*Nature*/*Science*/*PNAS*), Abstract, Executive/Public Piece**: **`LDR` / `ABT`** (`1–2` `AND` setup beats → **single** `BUT` contradiction → `THEREFORE` consequence & resolution).
   - **Methods Subsection, Results Paragraph, Right-Opening Sentence, 5-Min Policy Brief**: **`LD`** (Point-first Lead → Development).
   - **Oral Research Talk, Keynote, or Elevator Pitch**: **`Arouse & Fulfill` + Nested `ABT`s** (arouse curiosity with one ultra-specific anomaly/moment + `kABT`, then fulfill across `2–3` nested `Setup [AND] → Bottleneck [BUT] → Breakthrough [THEREFORE]` slide modules; never deliver a chronological `"and then"` slide dump).
3. **Cross-Language Discipline**: `OCAR`, `ABT`, Hourglass symmetry, and Gopen & Swan's `Old (Topic) → Action Verb → New (Stress)` mechanics apply equally to **English** and **Chinese/bilingual** scholarly work (in Chinese, eliminate bureaucratic nominalizations like `进行了…的分析 / 实现了…的改善` and `However/Yet` multi-turn zig-zags).

---

### Phase 2: Distill the Singular Story Bottom-Up (`WSP` + `Data → Understanding`)

1. **Push Rightward Along `Data → Information → Knowledge → Understanding` (`→ Application`) & Honor `Agon`**:
   - Listen objectively to data and outliers (*never* bend science or cherry-pick to manufacture a false-positive `Archplot`). When findings are **null, negative, or conditional (`Miniplot`)**, reframe them honestly as an **Assumption-Refutation `ABT`** exposing why a prevailing belief breaks down.
2. **Run Olson's `WSP` Compression (`Word → Sentence → Paragraph`)**:
   - **Word (Dobzhansky Unifying Theme)**: `"Nothing in [system/phenomenon] makes sense except in the light of [core mechanism/variable]."` (Eliminates Forscher's *"Chaos in the Brickyard"*).
   - **Sentence (Goldilocks `iABT → cABT → kABT`)**:
     1. Draft the unconstrained **`iABT`** (all technical facts in `AND / BUT / THEREFORE`).
     2. Strip 100% of jargon to test the **`cABT`** (bare conversational logic—if the `cABT` is incoherent, the paper's core argument is still unfocused!).
     3. Re-inject only high-leverage specifics into the **`kABT`** (your crisp elevator pitch & abstract spine).
   - **Paragraph (`OCAR` + Message Box Blueprint)**: Lock **Opening (`O`)**, **Knowledge Gap & Challenge (`C`: `"To determine X, we did Y"`)**, **Action (`A`: `2–3` nested `ABT` pillars)**, and **Resolution (`R`: matching `O` Hourglass width)**.
3. **Sequence the Figure-First Assertion-Evidence Storyboard BEFORE Drafting Prose (Cargill & O'Connor · Schimel · Doumont · Alley)**:
   - Lay out candidate Figures and Tables in reading order (`Visual 1 → Visual K`) and write **one verb-driven Assertion sentence** per visual ([figure-table-assertion-evidence-audit.md](../scientific-figures/references/figure-table-assertion-evidence-audit.md)). Verify that reading *only* those 1-sentence assertions reconstructs the entire `BUT → HOW → THEREFORE → WHY → SCOPE` argument, and ruthlessly cut, inline, or demote any visual that fails the **Deletion Counterfactual** or **One-Sentence Message** test.

---

### Phase 3: Draft Top-Down by Section, Narrative Spectrum & Reader Mechanics

Consult [macro-structure-and-sections.md](./references/macro-structure-and-sections.md) and [micro-style-flow-and-condensing.md](./references/micro-style-flow-and-condensing.md):

1. **Abstracts, Opening & Funnel (Narrative Spectrum `AAA ↔ ABT ↔ DHY`)**:
   - **Upstream Literature Grounding Gate (Conditional)**: When drafting from scratch or restructuring `Introduction`, `Related Work`, Proposal `Background`, or `Rebuttal` baseline comparisons—and no verified Evidence Matrix / Citation Lineage exists in the workspace—first invoke `scholarly-graph-audit` (`lineage` + `citation-audit`) and/or `literature-evidence-workflow` (when installed).
   - **Hit Optimal `ABT`, Ban `AAA` & `DHY`**: Lay down `1–2` clean `AND` exposition statements, pivot on **one decisive `BUT` contradiction/gap**, and advance via `THEREFORE` (`"To resolve X, we..."`). Treat literal *and/but/therefore* as removable scaffolding. **Never** open Sentence 1 of an abstract with a bare contradiction (`"However,..."`) or uncontextualized action (`"We measured..."`), **never** string together `AAA` fact lists without conflict, and **never** zig-zag across `3+` consecutive `Despite... However... Yet...` turns (`DHY`).
   - Frame the **hole in the wall** (Knowledge Gap): ban `"little is known"`, ban **Bizzwidget** solution-before-problem pitches, and ban `"Smith (2003) found X"` researcher-subject lists.
2. **Challenge**:
   - State **`"To determine X [Question/Hypothesis], we evaluated Y [Approach]"`** with primary intellectual questions first and method validation second.
3. **Action — Methods, Tables/Figures, Results, Statistics, & Discussion**:
   - **Methods**: Use `LD` + named method schemas (`"To measure X, we modified protocol Y..."`).
   - **Prose ⇄ Figure/Table Symbiosis (`scientific-figures` Sibling Skill + 8 Interaction Laws)**:
     - **Visuals as Story Spine, Zero Table-Echoing**: Each figure/table answers **one** distinct question (ban triple-reporting identical data in both table and figure). Prose states **synthesized conclusions and key effect sizes ($\Delta$, fold-change, anomalies)**—**never** recite table cells row-by-row in text!
     - **Phenomenon in Topic, Sequential 100% Callout Coverage, & Symbol Lock**: Put the scientific finding in the Topic and the callout at closure (`"Error spiked 4.8-fold above 32k tokens (Fig. 2b)"` — **ban `"Figure 2 shows..."` / `"Table 1 summarizes..."`**). Cite **every** figure, table, and sub-panel **strictly in appearance order**, keep 100% identical method names/math symbols across prose and legends, write **self-contained declarative takeaway captions** (`"X increases Y..."`, never `"Relationship between X and Y"`), and apply the co-loaded [`../scientific-figures/SKILL.md`](../scientific-figures/SKILL.md) workflow across every visual, Booktabs table, caption, and slide.
   - **Results & Statistics**: Lead every paragraph point-first (`LD`/`TS-D`), threading subsections as **nested `ABT`s** that advance the master theme (inculcation from orthogonal angles, never monotonous repetition). Present **Data before Inference**, separated from **Interpretation**, and tell the story via **effect sizes and fit ($R^2$, fold-change, $\Delta$)** over bare $p$-values.
   - **Discussion & `"But, Yes"` Limitations**: Air methodological/scope limitations **early and unapologetically**, constrain claims honestly, and **end on `"Yes"`**.
4. **Resolution**:
   - Walk backward through `OCAR` (`A → C → O`) to close the spiral. Never end with `"more research is needed"`, hollow `"may provide new insights"`, or surprise characters.
5. **Gopen & Swan's 7 Reader-Expectation Sentence Rules**:
   - **One unit, one function** · **Topic (`Subject`)** = continuing character + backward-linking **old info** · **Immediate Subject–Verb resolution** (zero 15–25 word interruptions) · **Concrete Action in the Verb** (strategic passive *only* to protect Topic alignment) · **Stress (`Syntactic Closure`)** = **new emphasis-worthy info** (`;`, `:`, `both...and` for secondary Stress; *Stress candidates $\le$ Stress positions*).

---

### Phase 4: Multi-Pass `SCFL` + Story-Circle & Linter Gate

Run the iterative **`SCFL`** loop (see [scfl-editing-and-examples.md](./references/scfl-editing-and-examples.md)):
1. **`S` — Structure & Narrative Spectrum**: Verify macro structure, Hourglass `O == R` width, Dobzhansky core theme, `cABT` jargon-free clarity, and **`ABT` balance** (zero `AAA` monotony or `DHY` multi-turn confusion).
2. **`C` — Clarity & Hidden Logic Debugging**: Check Subject–Verb proximity, Stress closure, concrete specifics/magnitudes, and **explicitly supply any missing logical/mechanistic bridge** exposed when aligning `Old (Topic) → New (Stress)`.
3. **`F` — Flow (Topic-String & Janus Check)**: Verify consistent paragraph Topic strings and unbroken `Stress → Topic` relay.
4. **`L` — Language & Condensing (Verb-List & Delete-Key Sweep)**: Replace static/fuzzy/nominalized verbs with concrete actions; break 3–4+ word noun trains; prune redundancies, empty amplifiers, and metadiscourse (targeting 10–20% tightening); finish with a mental **read-out-loud** check.
5. **Visual Callout, Cross-Artifact Consistency, Abstract Narrative & `.bib` Integrity Gate (Final Pass)**:
   - On LaTeX manuscripts, run `uv run "<SKILL_DIR>/scripts/lint_manuscript_visuals.py" path/to/main.tex` (which flattens `main.tex` + `appendix.tex` + `tables/*.tex`) to verify **zero orphan figures/tables**, **strict sequential callouts**, **zero `"Figure X shows..."` pointer-topics**, **declarative figure captions**, **clean Abstract `ABT` structure**, **zero `cross_table_conflicts`**, and **zero `abstract_unmatched_numbers`**.
   - Execute the **5-Matrix Consistency Audit** ([cross-artifact-consistency-audit.md](./references/cross-artifact-consistency-audit.md)): verify identical canonical aggregation across main & appendix tables, explicit `Protocol P1/P2` badges for modified ranks/masks, and **zero directional sign inversions** between captions/prose and stratified panels/tables.
   - Whenever new `\cite{}` entries were introduced or before finalizing a manuscript/proposal/rebuttal, invoke `scholarly-graph-audit` (`scholarly_graph.py bib-verify --tex-dir ...`, when installed) to upgrade stale preprints, screen for retractions, and block hallucinated BibTeX entries. *(Skip network `.bib` queries during pure prose-polishing passes where citations are unchanged.)*
