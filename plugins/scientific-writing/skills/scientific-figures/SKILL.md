---
name: scientific-figures
description: >-
  Authoritative scientific figure design, data visualization, publication table formatting, and visual storytelling skill synthesizing Claus O. Wilke's "Fundamentals of Data Visualization" (Ch. 1–29) and Rougier, Droettboom & Bourne's "Ten Simple Rules for Better Figures" (PLOS Computational Biology, 2014). Use whenever designing, coding (Matplotlib/Seaborn/R/ggplot2/TikZ/PGFPlots/Vega/D3), styling, refactoring, critiquing, or captioning 2D research figures, benchmark/ablation plots, statistical charts, publication tables, conceptual schematics, poster graphics, or oral presentation slides. Don't use for 3D biomolecular structure viewing (use interactive sidecar viewers first) or non-scientific web/app UI styling and infrastructure ops dashboards.
---

# Scientific Figures & Data Visualization Skill (Wilke + Rougier et al.)

> **Core Premise**: Scientific visualizations must accurately reflect quantitative magnitudes, honor human visual perception, and communicate a clear message before pursuing decorative polish *(synthesizing Claus O. Wilke, Fundamentals of Data Visualization, 2019; Nicolas P. Rougier, Michael Droettboom & Philip E. Bourne, "Ten Simple Rules for Better Figures," PLOS Computational Biology, 2014, `10.1371/journal.pcbi.1003833`, CC BY 4.0)*.

This skill unifies **Claus O. Wilke's complete *Fundamentals of Data Visualization* (Chapters 1–29)** with **Rougier, Droettboom & Bourne's *Ten Simple Rules for Better Figures* (2014)**, Tufte's balanced data-ink principles, and Schimel / Gopen & Swan's narrative flow to engineer accurate, repeatable, publication-grade figures, tables, and visual storylines.

## Bundled Resources (Progressive Disclosure — Read Before Coding!)

1. **[Encodings, Scales, Color Theory & Complete Chart Directory (Wilke Ch. 2–16)](./references/chart-directory-and-encodings.md)** — **Read when choosing *what* chart to plot or *how* to transform/encode data**: Aesthetic mappings, Cartesian aspect ratios, Log/Ratio & Sqrt laws, Functional color theory (Distinguish / Represent / Highlight), and full decision rules + banned anti-patterns across **Amounts**, **Single & Multi-Group Distributions** (KDE, ECDF, Q–Q, Boxplot, Violin, Sina, Ridgeline), **Proportions & Nested Proportions** (Pie vs. Side-by-Side vs. Mosaic vs. Treemap vs. Parallel Sets), **Associations & Paired Data** (SPLOM, Correlogram, PCA, `x = y` scatter, Slopegraph), **Time Series & Trends** (Connected Scatterplots, LOESS/GAM, Log-Linearized Fits, Detrending/STL), **Geospatial Maps/Cartograms**, and **Uncertainty** (Frequency Framing, Quantile Dotplots, Graded CIs, Contrast CIs vs. `0`, Bayesian Half-Eyes, Posterior Fitted Draws, HOPs).
2. **[Perceptual Laws, Clean Tables, Visual Storytelling & Matplotlib Recipes (Wilke Ch. 1, 17–29 + Rougier Ten Rules)](./references/design-principles-tables-and-storytelling.md)** — **Read when styling plots, formatting tables, assembling multi-panel figures, or writing code**: `Ugly vs. Bad vs. Wrong` triage, Principle of Proportional Ink, Overplotting ladder, CVD + Thin-Element Size laws, Redundant Coding & Direct Labeling (legend-free design), Small Multiples vs. Compound Alignment, **Wilke's 6 Rules for Clean Tables**, Perpendicular Context Grids, Larger Axis Labels, Solid Shapes over Line Drawings, Banning Gratuitous/Static 3D, Vector/Lossless File Formats (`PDF`/`SVG`/`PNG` vs. `JPEG`), Programmatic Repeatability, Ch. 29 Visual Storytelling, and ready-to-adapt Python/Matplotlib recipes.
3. **[Publication Matplotlib Helper (`publication_rcparams.py`)](./resources/publication_rcparams.py)** — **Import or inspect when writing Python scripts**: Okabe–Ito hex/paired-shade palettes, exact journal column widths (`scale=1.0`), Type-42 TrueType PDF settings, perpendicular grid helper, and seeded repeatable RNG.
4. **Sibling Prose Skill (`scientific-writing`)**: When aligning figures/tables with manuscript `OCAR` arcs or executing post-experiment paper rewrites, cross-check [`../scientific-writing/SKILL.md`](../scientific-writing/SKILL.md).

---

## Mandatory 5-Phase Visualization Workflow

### Phase 1: Triage, Audience, Story Role, & Repeatable Pipeline (Wilke Ch. 1, 28–29 · Rougier Rules 1–3, 9–10)

1. **`Ugly` vs. `Bad` vs. `Wrong` Gate (Ch. 1)**:
   - Eliminate **Wrong** errors first (broken math, missing units, `>100%` double-counted pies, KDE tails predicting negative ages/impossible values), then **Bad** perceptual traps (truncated bars, spaghetti curves, `jet`/`rainbow`, unmatched legends), then **Ugly** imbalances (tiny fonts, rotated tick labels, misaligned panels).
2. **Programmatic Repeatability & Content/Design Separation (Preface, Ch. 28)**:
   - Generate figures directly from raw data via **automated scripts** with **fixed RNG seeds** (`np.random.default_rng(42)`) so jitter, bootstrap intervals, and posterior draws are pixel-repeatable across revisions. Avoid unlogged interactive GUI tweaks or brittle manual Illustrator/Excel post-processing in iterative research pipelines. Separate **content** (data, transforms, plot type) from **design** (`rcParams` / themes).
3. **"Make a Figure for the Generals" & Story Sequence (Ch. 29, Rules 1–2, 9)**:
   - State the **single core visual takeaway** in one sentence before coding; strip tangential dimensions (*"when you try to show too much data at once, you may end up not showing anything"*).
   - Order panels left-to-right (`Context/Input/Baseline on Left → Mechanism/Result on Right`).
   - Across a paper or talk: **build up toward complex small multiples** (show 1 representative panel first in talks), progress from **raw-data views → derived summary metrics**, **vary chart types across distinct analyses** (consistent visual language, *never* repetitive bar-after-bar), and target **`3–6` core figures per storyline** (demoting excess plots to Supplement).
4. **Adapt Strictly to Medium — NEVER Copy-Paste Paper Figures Into Slides (Rule 3, Ch. 24)**:
   - **Journal / Conference Paper**: Design at **exact physical column width** (`3.25–3.5 in` single-col, `6.75–7.2 in` double-col) with **`7–9 pt` fonts** so LaTeX includes at `scale=1.0` without shrinking text!
   - **Oral Presentation Slides (`16:9`)**: Rebuild from scratch—strip secondary curves/ticks, thicken lines (`2.0–3.0 pt`), enlarge horizontal text (`≥14–18 pt`), and add bold visual callouts (`yellow box`, `dashed threshold`).

---

### Phase 2: Message-Driven Chart & Scale Selection Router (Wilke Ch. 2–16)

Consult [chart-directory-and-encodings.md](./references/chart-directory-and-encodings.md) and apply these hard selection rules:

| Primary Message | Preferred Encodings | Strictly Banned / Pitfall to Avoid |
| :--- | :--- | :--- |
| **Amounts** (Ch. 6) | **Horizontal bars** for long labels; **vertical bars** (`start=0`); **Cleveland dot plots** for tight non-zero ranges (`85%–92%`) or log amounts; **faceted bars** or **ordered heatmaps** for 2-way tables. | Rotated 45°/90° tick labels; alphabetical unordered bars; reordering naturally ordered factors (age brackets); bars starting away from `0` (linear) or on log scales for raw amounts. |
| **Distributions** (Ch. 7–9) | **1–4 groups**: Filled histogram (test multiple binwidths!), clipped KDE, **ECDF** (descending log–log for power laws), **Q–Q** (`x=y`), **fractional KDE vs. gray total**, **age pyramid** (exact 2 groups). **Many groups**: Light-shaded **boxplot**, **violin** (large `N`), **sina plot** (raw points + density!), **ridgeline KDE** (time trends). | **`Mean ± 2·SD` error bars** for population spread; **stacked or overlapping histograms**; KDE curves bleeding into impossible negative/`>100%` regions; ridgeline histograms. |
| **Proportions** (Ch. 10–11) | **Side-by-side bars** (many slices / multi-year); **2-group stacked bars** (`50%` dashed line); **faceted partial densities**; **pie chart** (*only* 1 snapshot of 2–4 simple fractions like `1/2`, `1/4`). **Nested**: **Mosaic plot** (orthogonal 100% partitions + printed counts), **Treemap** (hierarchies + inside labels), **Parallel sets** (`3+` vars, color origin on **far left**, minimize crossings). | Multi-year pies; `≥3`-category stacked bar series (shifting middle baselines); **`>100%` overlapping pies**; double-counting concentric pies. |
| **$x$–$y$ Associations & Trends** (Ch. 12–14) | **Scatter plot** / **SPLOM** (beats bubble charts!); **Correlogram** with circle area $\propto |r|$; **PCA** score + loadings biplot; **`x = y` diagonal scatter** (paired large `N`) or **Slopegraph** (paired small `N` / `3+` times); **Direct-labeled line graph**; **Connected scatterplot** (with progressive color/arrows + dates); **LOESS** / analytical fit / **linear fit on log-transformed data** / **STL decomposition**. | Unannotated connected scatterplots; nonlinear exponential least-squares on untransformed `y`; shaded area under lines when `y` does not start at `0`. |
| **Geospatial** (Ch. 15) | **Equal-area projections** (Goode homolosine, Albers); **binned (4–6 levels) density choropleths** (`qty / area`) + scale bar & north arrow; **population cartograms**, **equal-square statebins**, or **geofacets**. | Mercator world area comparisons; shrinking inset Alaska arbitrarily; unnormalized raw-count choropleths dominated by giant sparse regions. |
| **Uncertainty** (Ch. 16) | **Graded error bars** (`80%/95%/99%`), **Contrast CIs plotted directly against `Δ = 0`**, **Quantile dotplots** (`10–20` dots) / waffle frequency grids, Bayesian **half-eyes / eyes**, **graded confidence bands + posterior fitted draws**, **HOPs** (crisp cuts). | Confusing **SD** with **SE / CI**; unstated error-bar meaning; **eyeballing overlapping group error bars for significance**. |

- **Critical Ratio & Log-Scale Law (Ch. 3 & 17)**: **ALWAYS plot ratios / fold-changes on a log scale**, with bars/references anchored at **`1`** (never on a linear scale!). Label log-scale axes with the **original variable name** (`1, 10, 100`), or specify the explicit base if plotting log-transformed numbers (`log₁₀(x)` / `log₂(x)`).

---

### Phase 3: Perceptual Integrity, Color, Direct Labeling, & Multi-Panel Design (Wilke Ch. 17–26 · Rougier Rules 5–8)

1. **Proportional Ink & Solid Shapes (Ch. 17 & 25)**:
   - Linear bars and shaded curve areas **must start at `0`**; log-scale ratio bars **must start at `1`**; bubble **`area` (`s`) $\propto$ value** (never radius!).
   - **Prefer solid colored/gray shapes over hollow line drawings** (fill histogram bars, shade boxplot interiors lightly, use semi-transparent filled KDEs, and use solid scatter markers `o, s, ^, D` rather than noisy hollow symbols/cross-hatching).
2. **Overplotting Ladder (Ch. 18)**: `alpha + subtle jitter` (moderate `N`) → **`hexbin` / 2D histogram** (large `N`) → **2D contours** (`≤3` separated groups) or **faceted small multiples** (`≥4` overlapping groups).
3. **Color Discipline, CVD Safety, & Redundant Coding (Ch. 4, 19–20, Rule 6)**:
   - Default context/baselines to neutral gray; reserve vivid accent color to highlight the focal finding.
   - Cap qualitative palettes at **`3–5` categories** (hard max **`8`**, **Okabe–Ito**); for `>8` items, color by parent group and **direct-label** focal items. Ban `jet`/`rainbow` and neon oversaturated large fills; center diverging scales strictly at the neutral reference (`TwoSlopeNorm(vcenter=0)`).
   - **Thin-Element CVD Law**: Colors collapse on thin lines and tiny dots (especially under CVD)—thicken lines, pair color with solid shapes, **order legend entries to match the visual data rank** (never alphabetical!), and **eliminate legends via direct labeling** whenever possible (using a slightly darker hue shade for thin text labels than for area fills).
4. **Balanced Context Grids & Multi-Panel Alignment (Ch. 21, 23, 26)**:
   - Draw light-gray major gridlines **perpendicular to the variable of interest** (horizontal for time series/vertical bars; vertical for horizontal bars/dot plots; **`x = y` diagonal ONLY without rectangular grid** for paired scatters). Never strip context so far that bars/facets float in space.
   - **Small Multiples**: Enforce identical axis ranges across facets and logical panel ordering. **Compound Figures**: Enforce one **unified visual language** (identical category colors and left-to-right order across all panels), aligned spines/baselines, and discreet page-number-style `a, b` / `A, B` labels.
   - **Ban Gratuitous & Static 3D** (Ch. 26): Replace 3D pies/bars/scatters with 2D Trellis/facets or multi-encoding 2D plots (use interactive sidecar viewers for 3D biomolecules).

---

### Phase 4: Titles, Self-Contained Captions, Clean Tables, & File Formats (Wilke Ch. 22, 27 · Rougier Rule 4)

1. **One-Title Rule, Declarative Takeaway Captions, & Prose Symbiosis (Ch. 22.1–22.2, Rule 4)**:
   - **Manuscripts / Books (Caption Below Figure)**: **Omit top titles inside the figure canvas**; open the caption with a **bold declarative takeaway sentence stating the finding** (`"Figure 3. Spectral gating preserves constant loss up to 128k tokens."` — **never** a descriptive catalog phrase like `"This figure shows..."` or `"Relationship between X and Y"`, except concise functional titles on conceptual architecture schematics). Follow immediately with complete panel `(a)–(c)` / axis / unit / encoding keys, sample size $n$, and exact error-bar definition (`mean ± SEM`, `95% CI`) so the visual is **100% self-contained** without reading the main text.
   - **Prose ⇄ Visual Lock**: Ensure every figure/sub-panel and table is cited in sequential order in prose, never duplicate the exact same data in both a main-text table and a main-text figure, and lock 100% identical method names, acronyms, and math symbols ($\beta$, $\lambda$) between figure labels/legends and manuscript prose (ban leaked run IDs like `Ours-v2`).
   - Always include **units** on quantitative axis/legend titles (`Latency (ms)`); omit obvious redundant titles (`2020, 2022` needs no `Time (years AD)`).
2. **Wilke's 6 Rules for Publication Tables (Ch. 22.3)**:
   - **(1) Zero vertical lines**; **(2) Zero horizontal lines between data rows** (top/header/bottom rules or subtle row tint only); **(3) Left-align text, right-align numbers with uniform decimals**, center single chars; **(4) Align column headers identically with their data** (right-align headers over number columns!); **(5) Sort rows/columns purposefully**; **(6) Place Table Captions ABOVE the table** (and Figure Captions BELOW).
3. **File Format Discipline (Ch. 27)**:
   - Export **`PDF` (`pdf.fonttype=42`)** for print/LaTeX (set `rasterized=True` on multi-hundred-thousand-point scatter layers so PDF viewers stay instant!) or **`SVG`** for web/schematics; use lossless **`PNG` (`≥300–600 DPI`) / `TIFF`** for bitmaps; **STRICTLY BAN `JPEG`** for any plot, schematic, line art, or text.

---

### Phase 5: Mandatory Post-Render Visual Inspection Gate

After executing any figure generation script, **ALWAYS call `read_file` on the rendered `.png` (or rasterized `.pdf` preview)** and pass all 10 checks before delivering:
- [ ] **Zero `Wrong` / `Bad` defects**: No negative KDE tails, `>100%` pies, truncated linear bars, log-scale amount bars, radius-scaled bubbles, or overlapping-CI significance guesses?
- [ ] **Proportional & Balanced Typography**: Text (`7–9 pt` paper / `14–18 pt` slide) and markers balanced and legible when viewed at true `3.5 in` / `7.0 in` physical width; zero rotated category labels?
- [ ] **Zero Collisions / Clipping**: No cut-off labels, colliding direct annotations, or legends occluding data?
- [ ] **Color & CVD Integrity**: Gray context + purposeful accent; `≤8` Okabe–Ito categories; zero `jet`/`rainbow`; zero-centered diverging norm; thin text darker than fill?
- [ ] **Legend-Free or Rank-Matched**: Direct-labeled where feasible, or legend entries ordered to match visual data rank?
- [ ] **Solid Shapes & Clean Context**: Filled bars/shaded boxes/solid markers; light perpendicular grid (or `x = y` diagonal on paired scatters)?
- [ ] **Multi-Panel Coherence**: Shared facet scales; aligned compound axes; unified category colors & left-to-right ordering across panels; discreet consistent `a, b` labels?
- [ ] **Title, Caption & Table Compliance**: No duplicate top title on paper figures; self-contained Rule 4 caption below figure (or Booktabs caption above table with zero vertical/inter-row lines and right-aligned numeric headers)?
- [ ] **Lossless Format & Repeatability**: Saved as TrueType vector `.pdf`/`.svg` + lossless `.png` (never `.jpeg`), generated from a seeded repeatable script?
- [ ] **Iterated Until Clean**: Re-run and re-inspect if *any* visual flaw appears.
