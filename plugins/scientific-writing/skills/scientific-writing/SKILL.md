---
name: scientific-writing
description: >-
  Authoritative scientific, academic, ML/computational, and scholarly research writing skill synthesizing Joshua Schimel's Writing Science and Gopen & Swan's The Science of Scientific Writing, with a strict Anti-Patchwork Holistic Reconstruction workflow. Use whenever outlining, drafting, integrating new experimental rounds into, revising, condensing, reviewing, or critiquing scholarly manuscripts (specialist journals, Nature/Science, NeurIPS/ICML/ICLR/CVPR/ACL, arXiv/bioRxiv), abstracts, introductions, related work, methods, experiments/results, discussions, grant proposals (NSF/NIH/DARPA), peer reviews, author rebuttals, theses, or formal science outreach articles. Don't use for everyday casual chat, code comments/docstrings/READMEs/PRs, homelab/ops runbooks, or routine emails unless explicitly requested.
---

# Scientific Writing Skill (Schimel + Gopen & Swan)

> **Core Premise**: Readers interpret scientific substance from **structural location clues** rather than absorbing facts passively. Making the reader's job effortless—achieving **structural clarification without technical oversimplification**—is the author's primary responsibility *(synthesizing Joshua Schimel, Writing Science, 2012; George D. Gopen & Judith A. Swan, "The Science of Scientific Writing," American Scientist, 1990)*.

This skill operationalizes two foundational pillars of scientific prose—**Joshua Schimel's macro-storytelling & rewriting craft** (`OCAR`, `SUCCES`, Hourglass, `"But, yes"`, `SCFL`) and **Gopen & Swan's cognitive reader-expectation theory** (Syntactic Resolution, `Old → New` Topic/Stress architecture, Medial Syntactic Closure, and Structural Logic Debugging)—together with a mandatory **Anti-Patchwork Holistic Reconstruction Protocol** for iterative research papers.

## Reference Modules (Progressive Disclosure)

Load the reference module(s) matching your task:

1. **[Macro Structure, Sections, Proposals, Limitations & Public Framing](./references/macro-structure-and-sections.md)** — **Read when planning, outlining, or drafting**: `Data → Information → Knowledge → Understanding`, `SUCCES`, `OCAR` / Telegraphed `OCAR` / `ABDCE` / `LDR` / `LD` selection, Hourglass symmetry, Two-Step Openings, Pawn-Push vs. Queen-Launch, Funnel vs. Literature Review, Bizzwidget trap, Challenge formulas, Methods/Results/Effect-Size Stats/Discussion, Tabular Left-to-Right layout, Resolution spirals, `"But, yes"` limitations, and Nancy Baron's Message Box.
2. **[Micro-Architecture, Reader Expectations, Janus Flow, Verbs & Condensing](./references/micro-style-flow-and-condensing.md)** — **Read when drafting prose, fixing transitions, debugging opaque passages, or cutting length**: Nested serial arcs, Point-First (`TS-D`/`LD`) vs. Point-Last (`LDR`/`OCAR`) paragraphs, Gopen & Swan's 7 Reader-Expectation Principles, Syntactic Resolution (Subject–Verb gap pathology), Syntactic Closure (`;`/`:`/lists secondary Stress & Gopen–Swan sentence-length law), `Old → New` Janus relay, Topic-String & Verb-List diagnostics, uncovering hidden logical gaps, Active vs. Strategic Passive voice, Denominalization, Noun-train breaking, and 5 Delete-Key condensing targets.
3. **[Anti-Patchwork Reconstruction, SCFL Editing Protocol & Worked Examples](./references/scfl-editing-and-examples.md)** — **Read when updating an existing manuscript after new experiments, running full-paper revisions, or reviewing/critiquing drafts**: Anti-Patchwork Audit & 4-Step Holistic Rewrite Protocol, iterative `SCFL` checklist, 7-dimension review scorecard, and canonical Before → After rewrites (Schimel + Gopen & Swan + ML/computational research).

---

## Mandatory 5-Phase Execution Workflow

### Phase 0: Scope & Anti-Patchwork Pre-Check (Mandatory Gate for Existing Drafts)

Whenever modifying, expanding, or revising an existing manuscript or proposal (especially after completing a new round of experiments, ablations, or baselines), **STOP and audit the whole manuscript BEFORE editing any paragraph**:

1. **Check for the 5 Patchwork Pathologies (*补丁式写作症状*)**:
   - **Hourglass / `OCAR` Drift**: Does the Opening/Funnel still pitch an older hypothesis while new experiments shifted the real story, mechanism, or scope?
   - **Bolt-On Scars**: Are paragraphs stitched together with defensive addenda (`"Moreover, we also tested..."`, `"It is worth noting that..."`, `"Furthermore, an additional experiment..."`)?
   - **Chronological Lab-Log Ordering**: Are experiments ordered by when they were run rather than intellectual hierarchy (`primary claim → mechanism → boundary/ablation`)?
   - **Sunk-Cost Bloat**: Are superseded early exploratory experiments still cluttering the main text instead of being collapsed or moved to the Appendix?
   - **Broken `Old → New` Chains & Hidden Logical Gaps**: Did prior insertions sever `Stress → Topic` transitions or overload single sentences with multiple competing Stress candidates?

2. **Execute Strict 3-Tier Triage**:
   - **Tier 1 — Minor Fix (微小修复 → In-Place Edit Allowed)**: Pure typo/grammar polish, fixing `\cite`/`\ref`, or updating exact table/text numbers where *zero* claims, rankings, mechanisms, or story arcs change. (Verify local `Topic → Stress` continuity.)
   - **Tier 2 — Bounded Module Reinforcement (单点补强 → Section/Subsection Arc Rewrite)**: New experiment purely strengthens an existing claim without altering `Opening`, `Challenge`, or `Resolution`. Audit whole-paper consistency, then **rewrite the entire affected subsection/section arc cleanly** (never wedge a patch paragraph!).
   - **Tier 3 — Story/Mechanism/Scope Shift OR Existing Patchwork Debt (全篇复盘重写 → Default for Full-Paper Iterations)**: Read [scfl-editing-and-examples.md](./references/scfl-editing-and-examples.md) Section 1 and execute the **4-Step Holistic Reconstruction Protocol**:
     1. **Lock Hard Assets**: Freeze an explicit inventory of verified metrics, equations/notation, `\cite{}` keys, `\label{}`/`\ref{}` tags, and co-author factual constraints (guaranteeing **zero factual or LaTeX regression**).
     2. **Bottom-Up Re-Distillation**: Pool *old + new* experimental results together without chronological bias. Re-run `"Elaborate and Slash"` to find the unified core story; demote superseded experiments to Appendix/Supplement (*"murder your darlings"*).
     3. **Blueprint Alignment**: Formulate the updated `OCAR` + Hourglass blueprint (if the narrative pivot is major, show the brief `Old vs. New OCAR` comparison to align with the user, or proceed directly when instructed to rewrite).
     4. **Clean-Slate Top-Down Rewrite**: Rewrite from `Opening → Funnel → Challenge → Action → Resolution` as one seamless organism.

---

### Phase 1: Diagnose Genre, Audience Schemas, & Macro Structure

1. **Clarification, Not Oversimplification**: Distinguish peer/specialist writing (preserve exact technical terms that carry established schemas; clarify via **structural placement**) from broad/public writing (replace specialist terms with everyday schemas).
2. **Select Macro Structure by Audience Patience**:
   - **Specialist Journal**: **`OCAR`** (Opening → Challenge → Action → Resolution).
   - **ML/CS Conference (NeurIPS/ICML/ICLR/CVPR/ACL) & Biomedical Paper**: **Telegraphed `OCAR`** (full `O → C` funnel ending with `"In this paper, we show..."` contributions preview; closes with full `R`).
   - **Grant Proposal (NSF/NIH/DOE/DARPA)**: **`ABDCE`** (Action/Hook → Background → Development → Climax → Ending) or **`LDR`**—win the reviewer's irrevocable `"no/maybe"` cut in pages 1–2, and **always** end with a synthesis Resolution paragraph.
   - **Generalist High-Impact (*Nature*/*Science*/*PNAS*), Abstract, Executive/Public Piece**: **`LDR`** (Lead → Development → Resolution).
   - **Methods Subsection, Results Paragraph, Right-Opening Sentence, 5-Min Policy Brief**: **`LD`** (Point-first Lead → Development).
3. **Cross-Language Discipline**: `OCAR`, `SUCCES`, Hourglass symmetry, Nested Serial Arcs, and Gopen & Swan's `Old (Topic) → Action Verb → New (Stress)` reader expectations apply equally to **English** and **Chinese/bilingual** scholarly writing (in Chinese, eliminate bureaucratic nominalized constructions such as `进行了…的分析 / 实现了…的改善`).

---

### Phase 2: Distill the Story Bottom-Up (`Data → Understanding` + Blueprint)

1. **Push Rightward Along `Data → Information → Knowledge → Understanding` (`→ Application`)**:
   - Listen objectively to data and outliers (*never* jam data into a preconceived `PLOT`). Remember: old question + new dataset/tool = *Information*; high-impact papers ask a **new question** yielding *Knowledge* and *Understanding*.
2. **Draft the 4-Point `OCAR` + Message Box Blueprint**:
   - **Opening (`O`) & "So What?"**: Central characters + broad problem + target audience hook.
   - **Knowledge Gap & Challenge (`C`)**: Concrete hole in the wall of knowledge (`Unexpected` + `Curiosity`), framed as **`"To learn/determine X [Question / falsifiable Hypothesis], we did Y [Approach]"`**.
   - **Action (`A` — 2–3 Core Pillars)**: Essential evidence only; archive secondary/covarying data.
   - **Resolution (`R`)**: How `A` answers `C` and shifts understanding of `O` at the **exact same Hourglass width as `O`**.

---

### Phase 3: Draft Top-Down by Section & Reader-Expectation Mechanics

Consult [macro-structure-and-sections.md](./references/macro-structure-and-sections.md) and [micro-style-flow-and-condensing.md](./references/micro-style-flow-and-condensing.md):

1. **Opening & Funnel (Introduction / Related Work)**:
   - Open with a deliberate **Pawn-Push** or bold **Queen-Launch** (use a quick **Two-Step Opening** for interdisciplinary readers). Eliminate **Misdirection** and textbook **No-Direction**.
   - Frame the **hole in the wall** (Knowledge Gap), never a literature-dump wall: ban `"little is known"`, ban **Bizzwidget** solution-before-problem pitches, and ban `"Smith (2003) found X"` researcher-subject sentences (make phenomena the subject unless contrasting rival camps).
2. **Challenge**:
   - State **`"To determine X [Question/Hypothesis], we evaluated Y [Approach]"`** with primary intellectual questions first and method validation second. Make hypotheses crisp and falsifiable.
3. **Action — Methods, Tables/Figures, Results, Statistics, & Discussion**:
   - **Methods**: Use `LD` + named method schemas (`"To measure X, we modified protocol Y..."`).
   - **Tables & Figures (Gopen & Swan Left-to-Right + `scientific-figures` Sibling Skill)**: Put familiar context / independent variables / baselines on the **left** (creating a regular pattern of expectation) and new, discovery-worthy results on the **right**. Whenever designing/coding plots or writing **Rule 4 self-contained Figure Captions**, also load [`../scientific-figures/SKILL.md`](../scientific-figures/SKILL.md).
   - **Results & Statistics**: Lead every paragraph point-first (`LD`/`TS-D`). Present **Data before Inference**, separated cleanly from **Interpretation**. Tell the story through **effect sizes, magnitudes, and fit ($R^2$, fold-change, $\Delta$)**—never through bare `"significantly increased (p < 0.05)"` or Type-II-blind `"no significant effect (p > 0.05)"`.
   - **Discussion & `"But, Yes"` Limitations**: Build complete serial story arcs (`LDR` or `OCAR`). Air methodological/scope limitations **early and unapologetically** (in Intro scope, Methods/*Potential Pitfalls*, or middle `3`-position of Discussion), constrain claims honestly, and **end on `"Yes"`**.
4. **Resolution**:
   - Walk backward through `OCAR` (`A → C → O`) to close the spiral. Never end with `"more research is needed"`, hollow `"may provide new insights"`, or surprise characters.
5. **Gopen & Swan's 7 Reader-Expectation Sentence Rules**:
   - **One unit, one function**: Every paragraph and clause serves a single clear point.
   - **Topic Position (`Subject`)**: Put **(a) whose story the sentence tells** and **(b) backward-linking "old information"** up front—always provide context before asking the reader to process anything new.
   - **Immediate Subject–Verb Resolution**: Follow every Subject **immediately** with its Verb (never trap crucial info inside a 15–25 word Subject–Verb interruption!).
   - **Action in the Verb**: Put the true scientific action (*limit, inhibit, accelerate, prune*) in the verb—not in static `is/has` verbs, fuzzy verbs, or zombie nominalizations. Use passive voice *only* when needed to keep the continuing character/old info in the Topic position (`"Pollen is dispersed by bees"` in a paragraph about pollen).
   - **Stress Position (`Syntactic Closure`)**: Place the **new, emphasis-worthy information** at points of syntactic closure (end of sentence, or medial closure created via `;`, `:`, `both...and`, or announced lists). Never let imposter filler occupy the Stress, and obey the **Gopen–Swan Length Law**: *never pack more viable Stress candidates into a sentence than there are Stress positions available*.

---

### Phase 4: Multi-Pass `SCFL` + Structural Logic-Gap Audit

Run the iterative **`SCFL`** loop (see [scfl-editing-and-examples.md](./references/scfl-editing-and-examples.md)):
1. **`S` — Structure**: Verify macro structure, Hourglass `O == R` width, serial story-arc completeness, and paragraph `TS-D`/`LD`/`LDR`/`OCAR` integrity.
2. **`C` — Clarity & Hidden Logic Debugging**: Check Subject–Verb proximity, Stress syntactic closure, and concrete magnitudes. **Crucial Gopen–Swan Step**: When aligning `Old (Topic) → New (Stress)` reveals an unstated leap between two sentences or between an experiment and its conclusion, **explicitly supply the missing logical/mechanistic bridge**!
3. **`F` — Flow (Topic-String & Janus Check)**: Extract the vertical list of sentence Topics in each paragraph to verify a consistent controlling perspective and unbroken `Stress → Topic` relay.
4. **`L` — Language & Condensing (Verb-List & Delete-Key Sweep)**: Extract the vertical list of verbs to replace static/fuzzy/nominalized verbs with concrete actions; break up 3–4+ word **noun trains**; prefer crisp Anglo-Saxon words over ponderous Latinate bloat; cut redundancies, obvious statements, empty amplifiers, and metadiscourse (targeting 10–20% tightening without making prose barren); finish with a mental **read-out-loud** check.
