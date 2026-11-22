# Encodings, Scales, Color Theory & Complete Chart Directory (Wilke Ch. 2–16)

Distilled from **Claus O. Wilke's *Fundamentals of Data Visualization*** (Part I: *From Data to Visualization*, Chapters 2–16), integrated with **Rougier, Droettboom & Bourne (2014)**. Use this reference whenever mapping variables onto visual channels, choosing coordinate transformations, selecting colormaps, or picking the optimal chart type for your scientific message.

---

## 1. Aesthetic Mappings, Data Types, & Scale Laws (Ch. 2)

Every visualization maps data variables onto **aesthetics** via invertible 1-to-1 **scales**:

| Data Type | Examples | Compatible Aesthetics | Critical Constraints |
| :--- | :--- | :--- | :--- |
| **Quantitative continuous** | `1.3`, `57.84`, temperature, loss, concentration | Position (`x`, `y`), size (area), continuous/binned sequential or diverging color, line width | **NEVER** map continuous values to marker shape or line dash pattern. Human vision perceives **position** far more accurately than size or color hue. |
| **Quantitative discrete** | Counts, integer epochs, number of layers | Position, size (area), discrete/binned sequential color | Treat as continuous on axes when range is large, or discrete ticks when small. |
| **Ordered factor (ordinal)** | `Low < Med < High`, age brackets, `Stage I–IV` | Position (in natural order!), sequential lightness/color, line width | **NEVER** sort ordered factors by bar height—preserve their natural order! |
| **Unordered factor (nominal)** | Model architectures, species, countries, genes | Position (**sorted by data value!**), qualitative color (3–5 ideal, max 8), solid marker shape, line type | **NEVER** leave unordered categories in arbitrary/alphabetical order—sort by ascending/descending metric or meaningful grouping! |
| **Dates & times** | `2026-11-21`, hours, post-stimulus ms | Position (`x` axis by convention), progressive color shade along paths | Spacing on axis must match true temporal intervals. |
| **Text / Identifiers** | Gene symbols, state codes, outlier IDs | Direct annotations (`ax.text` / `ggrepel`), axis tick labels, table cells | Label a representative/salient subset rather than overcrowding every point. |

---

## 2. Coordinate Systems & Nonlinear Axes (Ch. 3)

1. **Cartesian Aspect Ratio & Linear Invariance**:
   - Standard Cartesian plots (`x` and `y` carry unrelated units) remain valid under linear unit transformations (`°C` ↔ `°F`) and should have their **aspect ratio tuned so trends are neither crushed flat nor spiked vertically** (~`0.6–0.75` height/width typical; wide `0.25–0.35` for long multi-decade oscillatory time series).
   - **Equal-Unit Lock (`ax.set_aspect('equal')`)**: Mandatory **only** when `x` and `y` measure the exact same physical quantity in identical units (e.g., paired wild-type vs. mutant expression, PCA space if unscaled, spatial coordinates).
2. **Logarithmic Scales & The Ratio Law**:
   - Log scales convert multiplication/division into uniform spatial steps and have a **natural midpoint at `1`**.
   - **Mandatory Ratio Rule**: **ALWAYS plot ratios, fold-changes, speedups, and odds ratios on a logarithmic scale**, NEVER on a linear scale! On a linear scale, `0.2x` (`1/5`) is squashed into `(0, 1)` while `5x` stretches to `5`, creating severe visual asymmetry; on a log scale, `1/5` and `5` sit symmetrically around `1`.
   - **Log Axis Labeling Law**:
     - Prefer placing **original untransformed values on a logarithmic axis** (`1, 3.16, 10, 31.6, 100`) titled with the **variable name itself** (e.g., `Population`, **NOT** `log(Population)`!).
     - If you plot log-transformed numbers on a linear scale (`0, 0.5, 1, 1.5, 2`), you **MUST** state the explicit logarithm base in the axis title (`log₁₀(Population)` or `log₂(Fold change)`—never ambiguous bare `log(x)`!).
3. **Square-Root Scales**:
   - Useful when skewed non-negative counts/areas **contain `0`** (where `log(0)` is undefined) or when mapping 2D geographic surface areas back to 1D linear extent (`√Area`). Note that unlike log scales, square-root steps lack constant multiplicative meaning away from `0`.
4. **Polar Coordinates**:
   - Reserve strictly for **genuinely periodic cyclical data** (24-hour circadian cycles, 365-day seasonal normals where Dec 31 connects smoothly to Jan 1) or simple part-to-whole pie charts. Never coil non-periodic bar or line charts into polar coordinates!

---

## 3. Functional Color Theory: Distinguish, Represent, Highlight (Ch. 4)

Every color choice must serve **one** of three functional jobs:

1. **Qualitative Scales (Distinguish Unordered Groups)**:
   - Use distinct hues of **comparable perceptual salience/lightness** so no group accidentally dominates (`Okabe–Ito`, ColorBrewer `Dark2` / `Set2`). Never imply a false ordering.
2. **Sequential & Diverging Scales (Represent Data Values)**:
   - **Sequential** (`viridis`, `inferno`, `cividis`, `YlGnBu`, ColorBrewer `Blues`/`Purples`): Strictly **monotonic lightness** from low to high; multi-hue scales must follow natural brightness progressions (e.g., dark red → orange → light yellow, never rainbow!).
   - **Diverging** (`RdBu_r`, `PiYG`, `PRGn`, `Blue-Red`, `Earth`): Two sequential scales stitched at a **bright/neutral midpoint** representing a meaningful reference (`0`, `50%`, `1.0x`, baseline). Extremes must have balanced darkness (`TwoSlopeNorm(vmin=-M, vcenter=0, vmax=+M)`). Render missing (`NaN`) regions in distinct neutral gray.
3. **Accent Scales (Highlight Focal Elements)**:
   - Pair 1–2 vivid, saturated **accent colors** for focal series/outliers with **drab, desaturated tones or neutral grays** (`#B0B0B0` / `#CCCCCC`) for baseline/context elements so context never competes visually with the takeaway.

---

## 4. Complete Message-Driven Chart Directory & Pitfalls (Ch. 5–16)

### 4.1 Visualizing Amounts (Ch. 6)
- **Single Categorical Variable**:
  - **Vertical Bars**: Standard when category labels are short; **must start at `0`**.
  - **Horizontal Bars**: **Preferred whenever category labels are long**—swap `x` and `y` so all text reads horizontally (**never** use 45°/90° rotated tick labels!).
  - **Cleveland Dot Plot**: **Use instead of bars** when values cluster tightly far from zero (e.g., accuracies in `86%–92%` or life expectancies in `60–81 yr`), where zero-anchored bars become long nearly-equal columns that draw the eye to bar middles rather than endpoints. **Still sort categories by value!**
- **Two+ Categorical Variables**:
  - **Faceted Regular Bar Plots (Small Multiples)** > **Grouped (Dodged) Bars**: Grouped bars force slow mental legend-to-color matching; faceting encodes both categories by spatial position!
  - **Stacked Bars**: Valid **only** when the sum of stacked segments is physically meaningful (e.g., counts of male + female = total passengers; never stack medians or averages!). For small tables of counts, print exact numbers inside bars and omit the explicit `y` axis.
  - **Heatmap**: Best for dense `M × N` amount grids (e.g., `20 countries × 25 years`). Order categorical rows deliberately to match your story (e.g., sort by final-year rank *or* by year first crossing a `20%` adoption threshold).

### 4.2 Visualizing Single & Multiple Distributions (Ch. 7–9)
- **1–2 Distributions (Ch. 7–8)**:
  - **Histogram** (equal bin widths mandatory; **always test 3–4 bin widths** so peaks aren't noisy or smoothed away) & **Kernel Density Estimate (KDE)** (**always test multiple bandwidths** and **clip/verify boundaries** so Gaussian tails never predict impossible values like negative ages or accuracies `>100%`!).
  - **Comparing 2–4 Distributions**: **STRICTLY BAN stacked histograms and overlapping semi-transparent histograms** (stacked bars have unreadable shifting baselines; overlapping alpha bars create false third-color illusions!). Instead use:
    1. **Overlapping Semi-Transparent Filled KDEs** (optionally scaled so area = group count `n`),
    2. **Faceted Partial/Fractional Densities** (colored subgroup density overlaid on light-gray total population density), or
    3. **Age Pyramid** (back-to-back horizontal histograms—valid for **exact 2 groups only**).
  - **Parameter-Free Exact Distributions (Ch. 8)**:
    - **Ascending ECDF**: Zero binning/bandwidth arbitrariness; directly reveals medians (`0.5`), quartiles, plateaus, and natural cutoffs.
    - **Descending ECDF on Log–Log Axes**: Gold-standard test for heavy right-tailed / scale-free **power laws** (true power law = straight line; log-normal curves downward).
    - **Q–Q Plot (`Observed` vs. `Theoretical` on `x = y` line)**: Tests normality, log-normality (Q–Q on `log(x)`), and ceiling/floor truncation.
- **Many Distributions at Once (`5–100+` groups, Ch. 9)**:
  - **STRICTLY BAN `Mean ± 2·SD` Point-and-Error-Bar Plots** for population distributions (hides skew/bimodality and misleads readers who read error bars as SE/CI of the mean).
  - **Boxplot** (shaded interior box = middle 50% IQR, center line = median, whiskers = max data within `1.5 × IQR` fences, dots = outliers): Compact, shows skew clearly, **hides bimodality**.
  - **Violin Plot** (mirrored KDE): Reveals bimodality/multimodality; **only use when per-group `N` is large enough** to justify smooth curves.
  - **Jittered Strip Chart**: Use when per-group `N` is sparse (never plot unjittered overlapping strips!).
  - **Sina Plot** (points jittered horizontally in proportion to local violin density, optionally overlaid inside a light violin): **Best-of-both-worlds default**—shows every raw observation *and* true bimodal/skewed density shape!
  - **Ridgeline Plot** (horizontally staggered KDEs along a vertical grouping/time axis; never use ridgeline histograms!): Scales cleanly to **10–100 temporal distributions** or **2-group polarization trajectories** over time.

### 4.3 Visualizing Proportions & Nested Proportions (Ch. 10–11)
- **Simple Proportions Decision Matrix (Ch. 10, Table 10.1)**:
  - **Pie Chart**: Acceptable **only** for a single small dataset (`2–4` slices) emphasizing simple fractions (`1/2`, `1/3`, `1/4`, or whether a 2-party coalition exceeds `50%`). Fails across multiple conditions/timepoints or many similar-sized slices (`~20%` each).
  - **Side-by-Side Bars**: Best whenever comparing `≥4` categories or tracking shifts across conditions/years; obscures part-to-whole visual unity.
  - **Stacked Bars / Stacked Densities**: Avoid across `≥3` categories (middle segments shift baselines unpredictably!). **Valid exceptions**: (a) **2-category stacked bars** over time (add a thin dashed line at `50%`!), or (b) **Faceted Partial Densities** showing each category's count or `%` share in color against the gray total/remainder.
- **Nested / Multi-Variable Proportions (Ch. 11)**:
  - **STRICTLY BAN `>100%` Double-Counting Pies** (mixing overlapping categories like material + era in one pie) and avoid double-counting concentric nested pies.
  - **Mosaic Plot**: Subdivides `x` width by Variable A and `y` height within each column by Variable B (`Area ∝ Count`). Requires **orthogonal categorical variables that each partition 100% of observations**. Always print counts/`%` inside tiles when possible because differing rectangle aspect ratios hinder eye-ball area comparison.
  - **Treemap**: Recursively nested rectangles (`Area ∝ Value`, optionally colored by a second metric). Best for **non-orthogonal hierarchies** (e.g., Region → State, Architecture Family → Variant); utilizes rectangular canvas far better than thin-wedged nested pies and supports clean inside labeling.
  - **Parallel Sets (Alluvial Plot)**: Best for **`3–5` categorical dimensions**. Place the **color-defining category on the far left** (matching left-to-right reading) and **reorder column axes + category blocks to minimize band criss-crossing**.

### 4.4 Visualizing Associations, Time Series, & Trends (Ch. 12–14)
- **Multivariate Quantitative Associations (Ch. 12)**:
  - **Scatter Plot** (`y` plotted *against* `x`, color/shape for group).
  - **Scatter Plot Matrix (SPLOM)** > **Bubble Chart**: Bubble size has low perceptual resolution; pairwise 2D position panels reveal 3–4 variable correlations far more clearly.
  - **Correlogram** (`≥5` variables): Diverging colormap centered at `r = 0` (`TwoSlopeNorm(-1, 0, 1)`) + **circle area scaled by `|r|`** so weak/zero correlations shrink away and strong correlations pop out.
  - **Dimension Reduction (PCA)**: Pair the **score projection plot** (`PC2` vs. `PC1`, colored/shaped by class) with a **loadings/rotation arrow biplot** so axes remain physically interpretable.
  - **Paired Measurements** (`before/after`, `WT/mutant`, `twin A/B`):
    - Large `N`: **Scatter plot overlaid on an `x = y` diagonal line** (omit competing rectangular grids!).
    - Small `N` (`≤15` named entities) or `≥3` timepoints: **Slopegraph** connecting paired values across vertical columns with direct labels.
- **Time Series & Dose–Response Curves (Ch. 13)**:
  - Connect points with lines whenever `x` imposes strict order (time, dose, hyperparameter sweep). Omit dots on dense series to emphasize trajectory; keep dots + `"lines serve as guide to the eye"` on sparse series.
  - **Shaded Area Under Curve**: Valid **only** when `y` starts at `0`!
  - **Multiple Response Variables Over Time**: Stacked aligned line panels (easy reading) vs. **Connected Scatter Plot / Phase Portrait** (reveals cyclic hysteresis/spirals, including in PCA space)—**MUST** indicate temporal direction and speed via **progressive color darkening or arrows + date callouts**!
- **Smoothing, Functional Trends, & Decomposition (Ch. 14)**:
  - Plot moving averages at the **center** of the window (not trailing end) to avoid phase lag; prefer **LOESS** over raw moving averages for smooth full-range curves, and **test multiple spline/GAM knot specs** to check boundary sensitivity.
  - **Prefer Explicit Analytical Functional Forms** (`y = A - B exp(-mx)`) with interpretable parameters over black-box smoothers whenever theory exists.
  - **Linearize Before Fitting Law**: **Fit straight lines to log-transformed data** (`log-linear` for exponential `y = A e^{mx}`, `log-log` for power laws `y ~ x^α`, `linear-log` for `y ~ log x`) rather than fitting nonlinear exponentials directly to untransformed data (where largest `y` values dominate squared residuals and distort low-end fit!).
  - **Detrending & STL Decomposition**: Divide time series by long-term exponential trends to expose bubbles/anomalies, or decompose via **STL** into `Long-Term Trend + Seasonal Cycle + Remainder (noise/shocks)`.

### 4.5 Visualizing Geospatial Data (Ch. 15)
- **Projections**: Curved Earth cannot be flattened without distorting either angles (**Conformal**: Mercator—severely inflates polar areas!) or areas (**Equal-Area**: Interrupted Goode homolosine for global maps; Albers for continental maps). **Never rescale inset regions** (e.g., shrinking Alaska to 12% true area) unless intentionally building a cartogram!
- **Map Layers**: Keep only task-relevant layers (drop distracting terrain on electoral maps) and include a **scale bar and north arrow** on physical maps.
- **Choropleths vs. Cartograms**:
  - Choropleths are most honest when coloring **densities (`quantity / area`)** or small, roughly uniform units (counties), using **4–6 discrete color bins** for readable legend lookup.
  - When large, sparsely populated territories visually dominate non-density choropleths, switch to a **population-scaled Cartogram**, an **equal-square Cartogram Heatmap (`statebins`)**, or **Geofaceted Mini-Plots**.

### 4.6 Visualizing Uncertainty (Ch. 16)
- **Intuitive Frequency Framing**: Humans misjudge continuous probabilities/areas; use **waffle grids** (`10 × 10` random squares) or **Quantile Dotplots** (`10–20` countable stacked dots, e.g., `1 dot = 5%` or `10%` chance) when communicating risk/probability intuitively.
- **Point Estimate Uncertainty**:
  - **NEVER confuse Standard Deviation (`SD`, population spread) with Standard Error / Confidence Interval (`SE` / `CI`, precision of parameter estimate)**.
  - **Mandatory Specification**: Every caption/label **must** state the exact error-bar metric and level (`"mean ± SEM"`, `"95% bootstrap CI"`, `"80%/95%/99% posterior credible intervals"`).
  - **Graded Error Bars** (nested `80%, 95%, 99%` intervals with thicker/darker inner bars, capped or uncapped) combat **deterministic construal error** (readers mistaking CI endpoints for hard min/max bounds) far better than hard-to-integrate faded confidence strips.
  - **Significance of Differences Law**: **NEVER eyeball whether two group error bars overlap to judge significance!** Compute and plot the **Confidence Intervals of the Contrasts / Differences (`Δ vs. baseline`)** directly against a vertical `Δ = 0` reference line (with multiple-comparison correction such as Dunnett/Tukey).
  - **Bayesian Posteriors**: Credible intervals answer *"where the parameter likely lies"*; visualize full posteriors via **half-eyes** (ridgeline + interval bar), **eye plots** (violin + interval bar), or **quantile-shaded ridgelines** (`80%/95%/99%` fill bands).
- **Curve-Fit Uncertainty & HOPs**:
  - Pair or replace smooth **graded confidence bands** with **10–20 random posterior fitted draws** (`spaghetti draws`) on nonlinear splines/GAMs—revealing that fit uncertainty means *increased curve wiggliness*, not merely shifting the smooth mean curve up and down!
  - For web/slides, **Hypothetical Outcome Plots (HOPs)** cycle across representative random draws using crisp cuts/fast fades (avoid slow morphing deformations, and verify sampled frames match true outcome proportions!).
