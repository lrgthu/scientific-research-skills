# Figure & Table Assertion-Evidence Audit Protocol (逐图逐表论证检视)

Synthesizes **Jean-luc Doumont** (*Trees, Maps, and Theorems*, 2009), **Michael Alley** (*The Craft of Scientific Writing*, 4th ed., 2018; *The Craft of Scientific Presentations*, 2nd ed., 2013), **Felice C. Frankel & Angela H. DePace** (*Visual Strategies: A Practical Guide to Graphics for Scientists and Engineers*, 2012), **Joshua Schimel** (*Writing Science*, 2012), and **Margaret Cargill & Patrick O'Connor** (*Writing Scientific Research Articles: Strategy and Steps*, 3rd ed., 2021), integrated with **Claus O. Wilke** (2019) and **Nicolas P. Rougier et al.** (2014).

---

## 1. Core Philosophy: Every Visual Is an Argument, Never a Lab Trophy

Researchers routinely treat figures and tables as **chronological proof-of-labor** (*"we ran six experiments, so here are six figures and four tables"*). Readers, reviewers, and grant panelists experience visuals differently: **visuals are the structural spine of the scientific argument**, scanned *before*—and often *instead of*—the continuous body text.

> **The Iron Guillotine Rule**: Every single **Figure**, **Compound Sub-Panel (`a, b, c...`)**, and **Table** in a manuscript, proposal, or presentation must pass **Four Existential Questions + One Encoding Audit (Gates 1–5)**. Any visual that cannot cleanly answer Gates 1–4 has **no reason to remain in the main text**—refactor it around a clear governing variable, merge it, inline its numbers into one prose sentence, demote it to the Appendix, or delete it.

| Source Pillar | Central Visual Law | Failure Mode Eliminated |
| :--- | :--- | :--- |
| **Jean-luc Doumont** (*Trees, Maps, and Theorems*) | **One-Sentence Message First**: Every visual must be preceded in design—and anchored in its caption—by **one complete conclusion sentence** (*what it proves*), never a topic label (*what it plots*). Maximize signal-to-noise so viewer attention locks instantly onto that message. | Ambiguous data dumps where even the authors cannot state the takeaway in one verb-driven sentence. |
| **Michael Alley** (*Craft of Scientific Writing / Presentations*) | **Assertion–Evidence–Explanation Triad**: Pair an explicit **Assertion** (full-sentence slide headline / bold caption opener / point-first paragraph lead) with **Visual Evidence** (chart/diagram/table, zero bullet walls) and a concise **Prose Bridge** explaining *how* the evidence proves the claim. | Topic headers (`"Results"`, `"Ablation Study"`) paired with unexplained plots or row-by-row table recitation. |
| **Felice Frankel & Angela DePace** (*Visual Strategies*) | **Visual as Inference Chain**: Define **Audience × Purpose** (**Explanatory** proof vs. **Exploratory** inspection) and verify every visual link across **Compare & Contrast**, **Process & Time**, or **Form & Structure** so the viewer's eye never hits a missing deductive step. | Broken visual arguments (missing baselines, unaligned scales, spaghetti mechanism arrows, or claims stronger than error bars). |
| **Joshua Schimel** & **Cargill & O'Connor** | **Figure-First Storyboarding**: Sequence visuals + their 1-sentence messages *before* drafting text so every visual occupies one irreplaceable step in `OCAR` / `ABT`. Apply the **Deletion Counterfactual**: if cutting it leaves the story unbroken, cut it. | Redundant tables + plots, chronological lab-log ordering, and sunk-cost bloat after multi-round revisions. |

---

## 2. Level 1 Audit: Whole-Manuscript Storyboard Continuity Test (Cargill & O'Connor + Schimel)

Before inspecting individual tick marks or colors, audit the **collective set of visuals as a standalone storyboard**:

1. **Extract the Bare Assertion Sequence**:
   - List `Visual 1 → Visual 2 → ... → Visual K` in exact manuscript appearance order (run `lint_manuscript_visuals.py` on LaTeX projects to extract `visual_inventory` automatically).
   - Write **only** the 1-sentence Assertion of each visual—hiding all body text.
2. **Run Four Storyboard Continuity Checks**:
   - **Completeness (`Missing Visual Bridge` Check)**: Reading `Assertion 1 → Assertion K` aloud, can an informed peer follow `Motivating Bottleneck [BUT] → Core Mechanism [HOW] → Headline Breakthrough [THEREFORE] → Why It Works [MECHANISM] → Regime Boundaries [SCOPE]` without a logical leap? If a pivotal claim in the Abstract/Introduction lacks visual backing, **create the missing figure**.
   - **Uniqueness (`Slot Collision` Check)**: Do two visuals occupy the exact same argumentative slot (e.g., two separate benchmark tables proving *"we beat baselines"*, or both a table and a bar chart plotting the same numbers)? **Merge or demote one.**
   - **Intellectual vs. Chronological Order**: Are visuals ordered by argumentative priority (`Headline Claim → Mechanistic Cause → Boundary/Ablation`) rather than the calendar order in which scripts ran?
   - **Cognitive Budget (`3–6` Core Figures + `1–3` Focused Tables)**: Does the main text respect reader attention, moving exhaustive sweeps, hyperparameter sensitivity grids, and per-dataset breakdowns to the Appendix/Supplement?

---

## 3. Level 2 Audit: The 5-Gate Visual-by-Visual Inspection Protocol

Inspect **every Figure, every Sub-Panel (`a, b, c...`), and every Table** individually against Gates 1–5 (calling `read_file` on rendered `.png`/`.pdf` images whenever available):

### Gate 1: Existence & Medium Necessity (`有没有必要存在？删掉故事会不会断？`)
- **The Deletion Counterfactual Test (Schimel; Cargill & O'Connor)**:
  - Ask: *"If we delete this visual completely, which exact inference in `OCAR` / `ABT` collapses?"*
  - If the honest answer is *"none—it just shows an extra variant we tried"* or *"the numbers are flat around 0.2% as expected"*, it fails Gate 1.
- **The Medium Triage Law (Prose vs. Table vs. Figure)**:
  - **$\le 3\text{–}4$ numbers or trivial insensitivity check** (*"Accuracy varied by `<0.4%` across $\lambda \in [0.1, 10]$"*) $\rightarrow$ **Inline into 1 prose sentence**; delete the figure/table!
  - **Exact multi-metric decimal lookup** across heterogeneous benchmarks where readers compare precise digits $\rightarrow$ **Publication Table** (never a cluttered 10-bar grouped bar chart).
  - **Functional relationships, scaling laws, distributions, spatial patterns, or Pareto trade-offs** $\rightarrow$ **Figure** (never a 50-cell wall of digits hiding the curve shape).
  - **Strict Non-Duplication**: Never present the same experimental series in both a main-text Table and a main-text Figure.

### Gate 2: Singular Declarative Claim / Message (`它支撑什么具体 Claim？一句话结论是什么？`)
- **Doumont's One-Sentence Message Law + Alley's Assertion Headline**:
  - Formulate **one declarative sentence with an active finite verb** stating what the reader must conclude (`Subject + Action Verb + Quantitative/Directional Relationship`).
  - **Topic Label (`FAIL` — Noun Phrase)** vs. **Assertion (`PASS` — Falsifiable Claim)**:

    | Visual Kind | Topic Label (`FAIL` — States *What Is Plotted*) | Assertion / Message (`PASS` — States *What It Proves*) |
    | :--- | :--- | :--- |
    | **Empirical Plot** | `"Validation loss versus context length for four methods."` | `"Spectral key sketching holds validation loss constant up to 128k tokens while eviction baselines diverge past 32k."` |
    | **Ablation Visual** | `"Ablation study on routing temperature and Sinkhorn steps."` | `"Three Sinkhorn iterations suffice to eliminate expert collapse across all temperature regimes."` |
    | **Slide Headline** | `"Experimental Results: Latency"` | `"Warp-tiled sparse attention cuts batch-1 decoding latency 3.1-fold without accuracy loss."` |
    | **Architecture `Fig. 1`** *(Functional Exception)* | `"System overview."` *(too vague)* | `"Overview of Spectral Anchor Routing: (a) dense eviction drops dormant cues, whereas (b) low-rank sketching preserves high-frequency keys."` *(Contrasts problem `[BUT]` vs. mechanism `[THEREFORE]`!)* |
    | **Lookup Table** | `"Results."` *(too vague)* | `"End-to-end retrieval recall and wall-clock latency across six long-context benchmarks (mean ± 95% CI, n = 5 seeds)."` *(Clear scope above table + point-first assertion in citing prose!)* |

- **Doumont's Guillotine**: If attempting to write the 1-sentence claim yields a muddled compound sentence (`"Method A wins on X, although B wins on Y, and Z is noisy"`), the visual lacks a message—either **re-parameterize the axes** to expose the true governing variable (e.g., plot $\Delta$ accuracy vs. task compression ratio!) or cut it.

### Gate 3: Storyline Slot & Sub-Panel Unity (`它在全篇 Story 里的唯一定位是什么？`)
- **Assign Exactly One `OCAR` / `ABT` Role**:
  1. **`[Problem / Gap Motivation — BUT]`**: Empirically demonstrates *why* existing assumptions/baselines fail (often paired as `Fig. 1a` alongside the proposed conceptual overview `Fig. 1b`—eliminating the *Bizzwidget* fallacy of showing a complex architecture diagram before proving a problem exists!).
  2. **`[Conceptual Mechanism — HOW]`**: Explains the physical, mathematical, or algorithmic structure enabling the solution.
  3. **`[Headline Validation — Primary THEREFORE]`**: Proves the central thesis on primary benchmarks/systems.
  4. **`[Mechanistic Verification — WHY IT WORKS]`**: Isolates internal representations, invariants, or scaling laws proving the gain comes from the claimed mechanism rather than confounding capacity/tuning.
  5. **`[Boundary / Trade-Off / Essential Ablation — "BUT, YES"]`**: Maps Pareto compute–quality frontiers, failure regimes, or component necessity.
- **Anti-Chimera Sub-Panel Audit (`Fig. Xa–f` Bloat Gate)**:
  - Authors frequently staple 4–6 unrelated mini-plots into one compound figure to bypass page/figure caps.
  - **Rule**: Every sub-panel (`a, b, c...`) must **(1) be explicitly cited in prose**, **(2) pass Gate 1 individually**, and **(3) combine with sibling panels to prove ONE shared umbrella assertion** for that figure. Evict unrelated side-experiments from compound figures!

### Gate 4: Visual-to-Claim Inference Bridge (`它是怎么一步步支撑 Claim 的？缺了哪一步读者推不过去？`)
Apply **Frankel & DePace's *Visual Strategies*** + **Alley's Triad** to verify that a skeptical reviewer can visually deduce the claim **without leaps of faith**:

1. **Explanatory vs. Exploratory Alignment (Frankel & DePace)**:
   - **Main-Text Figures = Explanatory**: Their job is to make a known conclusion *transparent and inescapable*. Strip raw exploratory clutter (unused auxiliary metrics, ungrouped 15-line rainbows) that forces the reader to do data mining.
   - **Exploratory Richness** (full phase-space heatmaps, dense taxonomy matrices) is valid *only* when annotated with clear guideposts (decision boundaries, highlighted regimes) so the main claim still pops out first.
2. **Audit by Visual Argument Archetype (Check for Broken Inference Bridges)**:
   - **Archetype A — Compare & Contrast** (*"A outperforms/differs from B"*):
     - *Required Visual Evidence*: Explicit control/baseline on the same frame, locked axis scales across panels, direct representation of **uncertainty / variance** (`95% CI`, `SEM`, or raw `sina` points), and direct visual access to the **contrast $\Delta$**.
     - *Broken Bridge Traps*: Unaligned `y`-axes across side-by-side panels; comparing two conditions without showing variance; forcing readers to mentally subtract stacked bar segments or flip between pages.
   - **Archetype B — Process, Mechanism & Time** (*"System transitions via ① → ② → ③"*):
     - *Required Visual Evidence*: Unambiguous reading vector (`left → right` or `top → bottom`), numbered stage anchors (`①, ②, ③`), and concrete input-to-output tensor/state shapes or physical transformations (showing *what changes* at each arrow, not just boxes labeled `"Module A → Module B"`!).
     - *Broken Bridge Traps*: Circular arrow tangles with no visual entry point; black-box module names that copy code class names without illustrating the mathematical operation.
   - **Archetype C — Form, Structure & Spatial Hierarchy** (*"Component X localizes to / governs structure Y"*):
     - *Required Visual Evidence*: High foreground/background contrast (focal structure in saturated accent; context in muted gray), consistent orientation/cropping, and explicit scale bars/units.
3. **Claim ⇄ Evidence Calibration Check (Zero Overclaiming)**:
   - Does the visual *honestly* support the strength of the assertion?
   - Flag immediately if: **(a)** prose claims *"exponential/linear scaling"* from 3 points over a narrow range, **(b)** prose claims *"consistent superiority"* when error bars overlap across half the regimes, or **(c)** outlier failures visible in the plot are ignored in text (apply Schimel's **`"But, yes"`** rule to bound the claim explicitly!).
4. **Prose Explanation Bridge (Alley + Gopen & Swan)**:
   - Citing prose must **never** say `"Figure 3 shows the results of X"` (zero assertion) nor recite every coordinate. It must state **Claim (`Topic/Stress`) + Quantitative Effect Size ($\Delta$, fold-change, slope) + Mechanistic Meaning + `(Fig. 3b)`**.

### Gate 5: Encoding, Signal-to-Noise, & Perceptual Execution (`画法与表式是否最合理？`)
Apply **Doumont's Signal-to-Noise Law** + **Wilke & Rougier's Perceptual Rules**:

- **2-Second Squint / Attention Test (Doumont)**: Looking at the visual for 2 seconds, does the eye land immediately on the **exact contrast that proves Gate 2's claim**? If heavy gridlines, 8 competing neon baselines, or giant legends hijack attention first, mute baselines to gray (`#8C8C8C` / `#D0D0D0`) and highlight **only the focal series/regime** in Okabe–Ito accent color.
- **High-Leverage Encoding Refactor Patterns (Common Research Upgrades)**:

  | Weak Default Choice (`BAD` for the Claim) | Why It Fails the Claim | Optimal Assertion-Evidence Refactor (`GOOD`) |
  | :--- | :--- | :--- |
  | **Tall linear bars** comparing `91.2%` vs. `92.8%` (`ylim=[0, 100]`) | Bars look 98% identical; truncating `ylim=[90, 94]` violates Proportional Ink. | **Cleveland dot plot** on `[88%, 94%]` **or** horizontal **$\Delta$ gain over baseline** bars anchored at `Δ = 0` with `95% CI`! |
  | **Two separate tables** (`Table 1: Accuracy`, `Table 2: Runtime/Memory`) | Forces reviewer to cross-index 20 numbers mentally to judge efficiency trade-offs. | **2D Pareto Frontier Plot** (`Latency/Memory` on `x` vs. `Accuracy` on `y`, ideal corner annotated, Pareto envelope shaded)! |
  | **`Mean ± SD` bar chart** for skewed latency or biological response | Hides tail spikes, multimodality, and sample size; `Mean - SD` may cross `< 0`. | **Sina + light violin plot**, **ECDF** (for tail SLAs like `p99`), or **Quantile dotplot**! |
  | **15-row × 10-column " Kitchen-Sink" Leaderboard Table** with bold numbers | Overwhelms working memory; mixes 3 mechanism families in arbitrary order. | Keep **top representative baselines grouped by mechanism family** in main text (Booktabs, uniform right-aligned decimals, $\Delta$ column); move exhaustive archive to Appendix. |
  | **Pure "Boxes-and-Arrows" `Fig. 1` Architecture Diagram** | Commits Bizzwidget fallacy—shows *how* your code is wired before showing *why* prior methods fail. | **Two-Part `ABT` `Fig. 1`**: **Left `(a)`** concrete failure/bottleneck of prior method `[BUT]` $\rightarrow$ **Right `(b)`** how your core operation resolves that exact bottleneck `[THEREFORE]`! |

---

## 4. Mandatory Audit Output Format: The Visual Audit Ledger

Whenever asked to **audit/critique figures and tables**, **plan a paper's visual spine**, or execute **Phase 0 Anti-Patchwork `Tier-3` reconstruction**, produce a structured **Visual-by-Visual Assertion-Evidence Ledger** assigning every visual one of **6 explicit Disposition Verdicts**:

- **`KEEP`** — Passes Gates 1–5; retain with minor caption/typography polish.
- **`REFACTOR`** — Valid Gate 1–3 slot & claim, but fails Gate 4 or Gate 5 (specify exact new chart encoding, missing baseline/CI, or `Fig. 1` `ABT` redesign).
- **`SPLIT / PRUNE PANELS`** — Compound figure mixes distinct claims or carries dead sub-panels; keep core panels and split/demote extras.
- **`MERGE`** — Collides with another visual's slot; combine into small multiples, a unified Pareto plot, or one compact table.
- **`INLINE TO PROSE`** — Too sparse/flat to justify float space ($\le 3\text{–}4$ numbers); replace with 1 quantitative sentence in text.
- **`DEMOTE TO APPENDIX` / `DELETE`** — Fails Gate 1 (deletion leaves story intact) or Gate 2 (no coherent takeaway); cut from main text.

### Template: Visual-by-Visual Audit Table + Action Plan

```markdown
### 1. Storyboard Continuity Diagnosis (`Visual 1 → Visual K`)
- **Master `kABT` Thesis**: ...
- **Assertion Sequence Read-Through**: [Pass / Gap at X / Redundancy between Fig. A & Table B]
- **Main-Text Visual Budget**: Before: `X` figs, `Y` tables → Recommended After: `X'` figs, `Y'` tables

### 2. Visual-by-Visual 5-Gate Audit Ledger
| Visual ( & Panels) | Current Caption / Heading | Gate 2: Required 1-Sentence Assertion (Doumont / Alley) | Gate 3: `OCAR` / `ABT` Story Slot | Gate 1, 4 & 5 Diagnosis (Necessity · Inference Bridge · Encoding) | Verdict & Concrete Action |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Fig. 1 (a–b)** | *"Overview of our framework."* | ... | `[BUT → THEREFORE]` Motivation + Mechanism | ... | **`REFACTOR`** — Add Panel (a) empirical bottleneck before Panel (b) pipeline |
| **Table 1** | ... | ... | `[Primary THEREFORE]` Headline Benchmark | ... | **`KEEP`** — Fix Booktabs right-alignment & add 95% CI |
| **Fig. 4** | *"Sensitivity to λ."* | *(Flat: `<0.3%` Δ across 5 values)* | Redundant minor ablation | Fails Gate 1: deleting it breaks zero links | **`INLINE TO PROSE`** + **`DEMOTE TO APPENDIX`** |
```

---

## 5. Clean-Room Worked Audit Example (ML Systems Manuscript)

**Scenario**: A draft paper on **Spectral Anchor Routing (`SAR`)** for long-context LLM inference currently contains **5 Figures and 3 Tables** accumulated across two rebuttal rounds:
- `Fig. 1`: Block diagram of `SAR` modules (`Tokenizer → QKV → Spectral Sketch → Output`).
- `Table 1`: Perplexity across 4 context lengths (`4k, 16k, 64k, 128k`) for 5 methods.
- `Fig. 2`: Line plot of the **exact same** perplexity numbers from `Table 1`.
- `Table 2`: Passkey retrieval accuracy across 6 tasks.
- `Table 3`: Decoding latency (ms/token) and peak KV memory (GB) for the same 5 methods.
- `Fig. 3 (a–d)`: `(a)` Attention recall vs. token distance; `(b)` Singular-value spectrum decay; `(c)` Training loss curve of router warmup; `(d)` Sensitivity bar chart to sketch rank $r \in \{8, 16, 32, 64\}$ showing flat `98.9%–99.2%` accuracy at $r \ge 16$.
- `Fig. 4`: Bar chart (`ylim=[0, 100]`) of MMLU 5-shot accuracy (`68.1%` vs. `68.3%`).
- `Fig. 5`: GPU kernel roofline utilization plot.

### Audit Execution & Reconstructed Spine (`8 Visuals → 4 Sharp Figures + 1 Lookup Table`)

1. **`Fig. 1` (`REFACTOR`)**: Fails Gate 4 (*Bizzwidget* pure code wiring—never shows *why* standard eviction fails). **Fix**: Rebuild as **`Fig. 1a [BUT]`** (attention heatmap showing a dormant token at pos `2k` reactivating at `96k`, which standard eviction deletes) $\rightarrow$ **`Fig. 1b [THEREFORE]`** (how `SAR`'s low-rank spectral sketch retains that high-frequency key signature).
2. **`Table 1` + `Fig. 2` (`DELETE Table 1`, `KEEP Fig. 2`)**: Fails Gate 1 (100% duplicate reporting of identical perplexity scaling data). Scaling divergence across `4k → 128k` is a continuous trend—keep **`Fig. 2`** (log-$x$ context scaling curve with `95% CI` bands and direct right-hand method labels; move exact lookup digits to Appendix).
3. **`Table 2` (`KEEP` as `Table 1`)**: Valid `[Primary THEREFORE]` multi-benchmark exact retrieval lookup table. Format with Booktabs, mechanism-grouped baselines, and uniform 1-decimal right-alignment.
4. **`Table 3` + `Fig. 5` (`MERGE & REFACTOR` into `Fig. 4` Systems Efficiency)**: `Table 3` forces readers to cross-compare memory, latency, and recall mentally across `Table 2` and `Table 3`. **Fix**: Replace `Table 3` + `Fig. 5` with a two-panel **`Fig. 4 [Boundary & Pareto Efficiency]`**: `(a)` **Peak KV Memory vs. 128k Recall Pareto Frontier** (showing `SAR` in the upper-left optimal corner at $4.2\times$ lower memory) and `(b)` **Batch-1 Latency Scaling + Roofline Saturation**.
5. **`Fig. 3 (a–d)` (`SPLIT / PRUNE PANELS` $\rightarrow$ `Fig. 3a–b`)**: Chimera figure! Panels `(a)` (dormant-anchor recall vs. distance) and `(b)` (rapid singular-value decay explaining *why* rank-16 sketches suffice) form a tight **`[Mechanistic WHY]`** pair. Panel `(c)` (routine warmup curve) fails Gate 1 $\rightarrow$ **Appendix**; Panel `(d)` (rank threshold plateau above $r=16$) can be added as an inset threshold callout on `(b)` or compact 4-row ablation in Appendix.
6. **`Fig. 4` MMLU Sanity Bar Chart (`INLINE TO PROSE` + `DELETE`)**: Fails Gate 1 & Gate 5 (two nearly identical `68%`-tall bars proving zero degradation on short-context tasks). **Fix**: Replace the entire figure with one sentence in Sec. 4.2: *"Preserving spectral anchors left short-context reasoning unchanged on 5-shot MMLU (68.3% vs. 68.1% dense baseline; Appendix Table 5)."*

**Resulting Storyboard Read-Through (4 Figures + 1 Table — Zero Fat, 100% Unbroken Chain)**:
- **`Fig. 1 [BUT → HOW]`**: *Standard eviction permanently deletes dormant retrieval anchors, whereas `SAR` compresses keys into a rank-16 spectral sketch.*
- **`Fig. 2 [Primary THEREFORE — Scaling]`**: *`SAR` preserves constant validation perplexity up to 128k tokens while eviction baselines diverge past 32k.*
- **`Table 1 [Primary THEREFORE — Breadth]`**: *Across six long-context retrieval and reasoning benchmarks, `SAR` matches full-cache accuracy within 0.3 percentage points.*
- **`Fig. 3 [Mechanism — WHY]`**: *Rapid singular-value decay in key matrices allows rank-16 sketches to recover 99.1% of long-range dormant-head recall.*
- **`Fig. 4 [Efficiency & Boundary — Pareto]`**: *Warp-tiled `SAR` shifts the memory–recall Pareto frontier 4.2-fold downward and accelerates 128k decoding 3.1-fold.*
