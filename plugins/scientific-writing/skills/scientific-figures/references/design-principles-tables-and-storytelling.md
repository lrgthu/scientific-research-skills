# Perceptual Design Laws, Clean Tables, Visual Storytelling & Matplotlib Recipes (Wilke Ch. 1, 17–29 + Rougier Ten Rules)

Synthesizes **Claus O. Wilke's *Fundamentals of Data Visualization*** (Chapters 1, 17–29) and **Nicolas P. Rougier, Michael Droettboom & Philip E. Bourne's *"Ten Simple Rules for Better Figures"*** (*PLOS Computational Biology*, 2014, `10.1371/journal.pcbi.1003833`), together with ready-to-adapt Python/Matplotlib code recipes.

---

## 1. Diagnostic Triage: Ugly vs. Bad vs. Wrong (Wilke Ch. 1)

Evaluate every draft figure against Wilke's three orthogonal failure modes:
- **WRONG (Objective / Mathematical Error — Must Fix First)**: Broken math, unstated or contradictory units, >100% double-counted pie slices, KDE curves predicting negative ages or probabilities `>1`, mislabeled axes, or rescaled data that contradicts raw numbers.
- **BAD (Perceptual / Cognitive Defect — Misleads or Obscures)**: Truncated bar-chart baselines (`ylim=(50, 70)`), radius-scaled bubbles, stacked/overlapping histograms, `jet`/`rainbow` colormaps, 7 tangled spaghetti lines, alphabetical unordered bars, unmatched legend order, static 3D scatter/bar charts, or multi-panel facets with unannounced mismatched `y`-scales.
- **UGLY (Aesthetic Imbalance — Distracts or Looks Amateurish)**: Tiny unreadably scaled axis labels, rotated 45°/90° category labels, hollow line-drawn histogram bars, garish oversaturated fills, misaligned compound panels, mismatched/oversized panel letters (`A`, `B`), or JPEG compression halos around text.

---

## 2. Eleven Non-Negotiable Perceptual & Design Laws (Wilke Ch. 17–28 + Rougier Rules 1–10)

### Law 1: The Principle of Proportional Ink (Ch. 17, Rougier Rule 7)
> *"The sizes of shaded areas in a visualization need to be proportional to the data values they represent."* (Bergstrom & West 2016)
- **Linear Axes**: Bars and shaded areas under curves **MUST start at `0`**. To show small changes around a high baseline (`$110..$135`), either use unshaded lines / Cleveland dot plots, **or** explicitly plot `Δ (Change / Loss relative to baseline)` with bars/shading anchored at `Δ = 0`.
- **Logarithmic Axes**:
  - **NEVER draw bar charts of raw amounts on a log scale** (`0` lies at `-∞`, so any bar origin like `0.3` or `10⁻⁹` makes bar lengths completely arbitrary!). Use **dot plots** with labels adjacent to dots instead.
  - **Bars on a log scale ARE ideal for ratios / fold-changes**, and **MUST start at `1`** (extending right/up for `>1` and left/down for `<1`).
- **2D Area Encodings**: Scale circle/bubble **`area` (`s` in `pts²`) $\propto$ value**, never radius/diameter! Remember humans judge 1D bar length more accurately than 2D pie/treemap areas.

### Law 2: Overplotting Escalation Ladder (Ch. 18)
Never leave opaque overlapping points (`N > 50` or rounded values) hiding subgroup frequencies:
1. **Moderate `N` (`50–1,000`)**: Partial transparency (`alpha=0.5–0.7`) + **subtle controlled jitter** (never over-jitter beyond rounding resolution!).
2. **Large `N` (`1,000–1,000,000+`)**: **2D Hexagonal Binning (`ax.hexbin`)** or 2D rectangular histogram (hexagons keep points closer to bin centers than equal-area squares, Carr et al. 1987).
3. **Smooth Continuous Point Clouds**: **2D KDE Contour Lines / Shaded Contours** (`1–3` well-separated groups max). If `≥4` groups overlap, **facet into Small Multiples** over a shared background grid!

### Law 3: Color Pitfalls, CVD Safety, & Element Size (Ch. 19, Rougier Rule 6)
- **Category Cap**: Qualitative color works best for **`3–5` groups** (hard cap **`8`**, **Okabe–Ito** palette). For `>8` items, color by broader parent group and **direct-label** focal items!
- **Saturation Discipline**: Never fill large bars/maps with neon, 100%-saturated colors; use muted/light fills so text and gridlines stay comfortable to inspect.
- **Ban Non-Monotonic Scales**: Never use `rainbow` or `jet` (circular dark-red ends + erratic luminance jumps fabricate false boundaries).
- **CVD + Element-Size Interaction (Stone et al. 2014)**: ~8% of males have red–green CVD (deuteranomaly/protanomaly) and others have blue–yellow CVD (tritanomaly). Colors that look distinct on large swatches **collapse into indistinguishable grays/browns on thin lines and tiny scatter dots**! Thicken colored lines, enlarge markers, use CVD-safe palettes (`Okabe–Ito`, `PiYG`, `viridis`, `cividis`), and verify grayscale/CVD legibility.

### Law 4: Redundant Coding & Eliminating Legends (Ch. 20, Rougier Rule 8)
- **Redundant Coding**: Pair color with distinct **solid marker shapes** (circles, squares, triangles) and swap palette assignments so perceptually close hues (blue & green) never sit intermingled.
- **Legend Order = Perceived Visual Order**: Whenever a legend is kept and curves/stacks have a clear vertical/horizontal data ranking, **manually order legend entries to match the visual order of the data** (never leave default alphabetical sorting!).
- **Design Without Legends (Direct Labeling First)**: Eliminate legends whenever possible:
  - Place series names directly at the **right end of lines**, adjacent to **KDE peaks**, on **group ellipses**, on **marginal density plots**, or integrate colorbars directly into an axis when double-encoding.
  - **Two-Shade Text Legibility Trick**: Thin colored text looks lighter than adjacent filled areas—fill areas/points with a **lighter shade** (or `alpha`) and draw **outlines + direct text labels in a darker shade of the same hue**!

### Law 5: Multi-Panel Figures — Small Multiples vs. Compound Alignment (Ch. 21)
- **Small Multiples (Facets / Trellis)**:
  - **Lock Identical Axis Limits/Scales** across all panels (readers assume equal scales; if varying `ylim` is strictly unavoidable, explicitly warn in the caption!).
  - Order panels by a **meaningful data dimension** (time, rank, magnitude—never arbitrary/alphabetical). Omit `(a), (b)` letters since facet strip headers identify slices.
- **Compound Multi-Panel Figures**:
  - **Subdued Consistent Panel Labels**: Format `(a), (b)` or `a, b` / `A, B` like discreet page numbers—matching font family, modest size (`8–9 pt` bold), top-left aligned, consistent case across every figure in the manuscript (never huge mismatched slapped-on letters!).
  - **Unified Visual Language**: If `Female = Orange (Left)` and `Male = Blue (Right)` in Panel `a`, **every panel (`b`, `c`, ...) across the entire paper MUST keep that exact color and left-to-right order**, enabling a single shared legend!
  - **Strict Axis & Baseline Alignment**: Align plot spines and baselines across rows/columns programmatically (`GridSpec` / `subfigures` / `patchwork` / `cowplot`—never eyeball drag-and-drop).

### Law 6: Single-Title Placement, Axis Units, & Clean Research Tables (Ch. 22, Rougier Rule 4)
- **One-Title Placement Law**:
  - **Papers, Proposals, Theses, Books (Caption Below Figure)**: Do **NOT** draw a title above the figure canvas! Place the declarative/topical figure title as the **first element of the caption block** (never open captions with `"This figure shows..."`).
  - **Standalone Slides, Web Posts, Posters (No Separate Caption Block)**: Integrate a concise declarative title, subtitle, and data-source line directly onto the figure canvas.
- **Axis & Legend Titles**: State explicit **units** for every quantitative axis (`Body mass (g)`, `Latency (ms)`). Omit redundant titles *only* when labels are 100% self-explanatory (`2018, 2020, 2022` or `Female / Male`); **never** omit `y`-axis titles when numbers require interpretation, and avoid awkward over-labeling (`Time (years AD)`).
- **Wilke's 6 Rules for Publication Tables (Ch. 22.3 — Booktabs Discipline)**:
  1. **NO vertical lines** anywhere in the table.
  2. **NO horizontal lines between data rows** (only top rule, header-separator rule, and bottom rule—or very subtle alternating row tint `#F7F7F7` for wide tables).
  3. **Left-align text columns**; **right-align number columns** with **uniform decimal digits** throughout each column; **center single-character columns**.
  4. **Align column headers identically with their data** (left-aligned header over text; right-aligned header over numbers!).
  5. Order rows/columns purposefully (left-to-right context → result; rows sorted by magnitude or logical grouping).
  6. **Place Table Captions ABOVE the table** (tables are read top-down) and **Figure Captions BELOW the figure**!

### Law 7: Balance Data Ink and Context Grids (Ch. 23, Rougier Rule 8)
- *"Maximize the data–ink ratio, **within reason**."* Strip double frames, legend boxes, and heavy minor grids (`ggplot2` default white-on-gray can overpower thin data lines), **but never strip context so aggressively that points or facet bars float unanchored in empty space**!
- **Perpendicular Grid Rule**: Draw thin, light-gray (`#E0E0E0`) major gridlines **perpendicular to the primary variable of interest**:
  - Horizontal gridlines only → Vertical bars, time series, boxplots/violins.
  - Vertical gridlines only → Horizontal bars, Cleveland dot plots, ridgelines.
  - Light 2D grid → Unpaired scatter plots (no axis spines needed if grid frames the area, or use crisp `left`/`bottom` spines).
  - **`x = y` Diagonal Reference Line ONLY (No Rectangular Grid!)** → Paired `WT vs. Mutant` / `Before vs. After` scatter plots!
- Never place value labels just outside bar tips where they visually elongate bar length—place labels cleanly inside bars or use a dot plot.

### Law 8: Use Larger Axis Labels & Inspect at Print Scale (Ch. 24, Rougier Rule 3)
- Zoomed-in high-DPI monitors trick authors into shipping tiny `4–5 pt` text. **Design at exact physical column width** (`3.25–3.5 in` single-col, `6.75–7.2 in` double-col) with **`7–9 pt` paper fonts** (`14–20 pt` on slides) so LaTeX includes at `scale=1.0`.
- When enlarging text for small-scale reproduction, **scale marker sizes and line widths proportionally** so symbols never look puny next to large labels! Always zoom out to true `3.5 in` physical width (or `1.5 in` thumbnail test) to verify balance.

### Law 9: Prefer Solid Filled Shapes Over Line Drawings (Ch. 25)
- **Solid colored/gray fills** form coherent perceptual objects and avoid figure-ground optical illusions caused by hollow outlines, cross-hatching, and stippling:
  - **Histograms & Bar Plots**: Fill bars with solid muted color or gray (hollow outlined bars make gaps indistinguishable from bars!).
  - **Density Plots**: Use semi-transparent shaded areas (`fill_between(..., alpha=0.35)`) + crisp darker outline rather than porous dashed black-and-white lines.
  - **Scatter Plots**: Use **solid filled shapes** (`o`, `s`, `^`, `D`) rather than noisy open circles/crosses (`+`, `x`, hollow `o`); handle overlap via `alpha`/jitter/hexbin.
  - **Boxplots**: Give boxes a light interior fill (`#E5E5E5` or pastel tint) so adjacent boxes separate cleanly from whitespace.

### Law 10: Don't Go 3D (Ch. 26, Rougier Rule 7)
- **Strictly Ban Gratuitous 3D**: 3D tilted pies exaggerate front wedges; 3D perspective bars read shorter than true height against back-wall grids.
- **Avoid Static 3D Position Scales (`x, y, z` scatter/bars)**: Projecting 3D coordinates onto a 2D page is **non-invertible**—readers cannot recover true point positions! Replace with **2D Trellis / Small Multiples** or 2D position + color/size encodings.
- **Valid 3D Exceptions**: Interactive rotatable viewers (e.g., Biomolecular Structure Viewer sidecar for proteins!), slowly rotating video/GIF animations, or genuine physical 3D surfaces/topography.

### Law 11: File Formats, Programmatic Repeatability, & Content/Design Separation (Ch. 27–28)
- **Master File Format Matrix**:
  - **`PDF` (Vector, `pdf.fonttype=42`)**: Primary format for LaTeX/print publications (resolution-independent, sharp typography; embed fonts to prevent font-substitution breakage; supersedes outdated `EPS`). *Caveat*: If plotting `>100,000` points/polygons stalls PDF rendering, set `rasterized=True` on the dense artist (`ax.scatter(..., rasterized=True)`) at `600 DPI` while keeping axes/text crisp vector, or export `600 DPI PNG`.
  - **`SVG` (Vector)**: Primary vector format for web/HTML and Inkscape schematic assembly.
  - **`PNG` / `TIFF` (Lossless Bitmap)**: Required for online docs, screenshots, line drawings, or mixed photo+text panels.
  - **`JPEG` (Lossy Bitmap)**: **PURE PHOTOGRAPHS ONLY. STRICTLY BAN `JPEG` for plots, schematics, text, or composite figures** (introduces irreversible sharp-edge ringing artifacts; converting `JPEG → PDF/PNG` never restores lost sharpness!).
- **Programmatic Repeatability**: Generate figures from raw data via code scripts with **explicitly fixed RNG seeds** (`np.random.default_rng(42)`) so jitter, bootstrap bands, and posterior draws are pixel-repeatable across paper revisions—avoiding unrecorded interactive GUI tweaks or brittle manual Illustrator redraws. Separate **content** (data, transforms, encodings) from **design** (reusable theme / `rcParams`).

---

## 3. Visual Storytelling in Manuscripts & Talks (Wilke Ch. 29 + Schimel `OCAR`)

1. **Figures Inside the Story Arc (`OCAR` / `LDR`)**:
   - A single static figure rarely carries a complete `Opening → Challenge → Action → Resolution` arc unless condensed into a tight `Challenge + Resolution` lead graphic. Sequence figures deliberately across the narrative (e.g., `Fig. 1` establishes the **Challenge/Anomaly**, `Fig. 2` delivers the **Mechanistic Resolution**).
2. **"Make a Figure for the Generals"**:
   - Busy reviewers, editors, and program managers will not spend 20 minutes decoding a 6-dimensional hyper-plot. *"When you try to show too much data at once, you may end up not showing anything."* Strip tangential variables to spotlight the primary comparison, or split into two clean figures.
3. **Build Up Toward Complex Figures**:
   - Before presenting a dense `30`-panel Small Multiples grid (especially in talks or complex multi-factor papers), **first show a single representative panel** so the audience learns the axes and visual encoding effortlessly.
4. **Memorability Without Chartjunk**:
   - When communicating to broad audiences where 10 generic bar charts blur together, consider **Isotype Plots** where repeated scaled icons *directly represent data units* (never paste decorative clip-art onto axes or backgrounds, which distracts comprehension, Haroz et al. 2015).
5. **Be Consistent, NEVER Repetitive (`3–6` Core Figures Rule)**:
   - Maintain one unified visual palette/ordering across the whole paper, **but vary the chart type across distinct analyses** (e.g., raw trajectory line plot → summary % bar/dot plot → distribution sina/boxplot) so readers immediately see where one analysis ends and the next begins.
   - **Raw → Derived Progression**: Show figures closest to the **raw data first**, then progress to **derived summary quantities** (contrasts, slopes, fitted parameters).
   - **Target `3–6` Core Figures per Paper / Storyline**: Demote excess repetitive figures to the Appendix/Supplement (*aligns with the Anti-Patchwork "murder your darlings" rule*).

---

## 4. Production Matplotlib Recipes

### Recipe 1: Direct-Labeled Multi-Series Plot with Perpendicular Grid & Two-Shade Accents (Wilke Ch. 20 & 23)
```python
import matplotlib.pyplot as plt

def plot_direct_labeled_series(x, series_map, focal_key, ylabel, width_in=3.5):
    """series_map: dict[name, y_array] — eliminates legend box via right-hand direct labels."""
    fig, ax = plt.subplots(figsize=(width_in, width_in * 0.65), constrained_layout=True)
    ax.grid(axis="y", color="#E2E2E2", linewidth=0.6, zorder=0)  # Perpendicular to y-values!
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    ax.tick_params(axis="y", length=0)

    for name, y in series_map.items():
        is_focal = (name == focal_key)
        line_col = "#0072B2" if is_focal else "#8C8C8C"
        text_col = "#004C7A" if is_focal else "#595959"  # Darker shade for crisp thin text!
        lw = 1.8 if is_focal else 1.1
        ax.plot(x, y, color=line_col, lw=lw, zorder=3 if is_focal else 2)
        ax.text(
            x[-1], y[-1], f"  {name}", color=text_col,
            va="center", ha="left", fontsize=7.5,
            fontweight="bold" if is_focal else "normal",
        )
    ax.set_xlim(x[0], x[-1] + 0.22 * (x[-1] - x[0]))  # Room for direct labels
    ax.set_ylabel(ylabel)
    return fig, ax
```

### Recipe 2: Graded Error Bars / Contrast CIs Against Zero (Wilke Ch. 16)
```python
import numpy as np
import matplotlib.pyplot as plt

def plot_graded_contrasts(labels, mean_diff, ci80, ci95, ci99, xlabel, width_in=3.45):
    """Plot differences vs. baseline with 80/95/99% graded CIs against zero (never eyeball overlap!)."""
    order = np.argsort(mean_diff)
    fig, ax = plt.subplots(figsize=(width_in, 0.38 * len(labels) + 0.6), constrained_layout=True)
    ax.axvline(0.0, color="#666666", linestyle="--", lw=0.9, zorder=1)
    ax.grid(axis="x", color="#EAEAEA", lw=0.6, zorder=0)

    for pos, idx in enumerate(order):
        m = mean_diff[idx]
        # 99% (lightest/thinnest) -> 95% -> 80% (darkest/thickest) + point estimate
        ax.plot([m - ci99[idx], m + ci99[idx]], [pos, pos], color="#A6CEE3", lw=1.2, zorder=2)
        ax.plot([m - ci95[idx], m + ci95[idx]], [pos, pos], color="#56B4E9", lw=2.4, zorder=3)
        ax.plot([m - ci80[idx], m + ci80[idx]], [pos, pos], color="#0072B2", lw=3.8, zorder=4)
        ax.plot(m, pos, marker="o", color="#D55E00", markersize=4.8, zorder=5)

    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels([labels[i] for i in order])
    ax.set_xlabel(xlabel)
    for sp in ("top", "right", "left"):
        ax.spines[sp].set_visible(False)
    ax.tick_params(axis="y", length=0)
    return fig, ax
```

### Recipe 3: Small Multiples Refactor with Ghost Context Curves (Rougier Fig. 7 + Wilke Ch. 21)
```python
def plot_small_multiples_ghost(x, series_dict, ref_band=None, width_in=3.5):
    names = list(series_dict.keys())
    n = len(names)
    fig, axes = plt.subplots(
        n, 1, figsize=(width_in, 0.55 * n + 0.4),
        sharex=True, sharey=True, constrained_layout=True,
    )
    for idx, (ax, focal_name) in enumerate(zip(axes, names)):
        if ref_band is not None:
            ax.axhspan(ref_band[0], ref_band[1], color="#F0F0F0", zorder=0)
        for other_name, y_other in series_dict.items():
            if other_name != focal_name:
                ax.plot(x, y_other, color="#D0D0D0", lw=0.7, zorder=1)
        ax.plot(x, series_dict[focal_name], color="#0072B2", lw=1.5, zorder=3)
        ax.text(-0.03, 0.5, focal_name, transform=ax.transAxes, ha="right", va="center", fontsize=7.5)
        for sp in ("top", "right", "left", "bottom"):
            ax.spines[sp].set_visible(False)
        ax.set_yticks([])
        ax.tick_params(axis="x", length=0 if idx < n - 1 else 3)
    axes[-1].spines["bottom"].set_visible(True)
    return fig, axes
```

### Recipe 4: Diverging Colormap Centered at Zero + Area-Scaled Bubbles (Wilke Ch. 4 & 17)
```python
import matplotlib.colors as mcolors

# 1. Zero-centered diverging norm (never let asymmetric min/max shift white midpoint!)
vmax = float(np.nanmax(np.abs(matrix)))
norm = mcolors.TwoSlopeNorm(vmin=-vmax, vcenter=0.0, vmax=vmax)
cmap = plt.get_cmap("RdBu_r").copy()
cmap.set_bad("#CCCCCC")  # Explicit neutral gray for missing values

# 2. Honest area-proportional bubbles (s is already points^2!)
areas_pts2 = 160.0 * (magnitudes / np.max(magnitudes))
```

### Recipe 5: Sina + Shaded Violin Hybrid Distribution Plot (Wilke Ch. 9 & 25)
```python
from scipy.stats import gaussian_kde

def plot_sina_violin(groups_dict, ylabel, seed=42, width_in=3.5):
    """Repeatable sina + light-filled violin plot (solid shapes, zero SD-bar deception)."""
    rng = np.random.default_rng(seed)  # Repeatable jitter!
    fig, ax = plt.subplots(figsize=(width_in, width_in * 0.68), constrained_layout=True)
    ax.grid(axis="y", color="#E5E5E5", lw=0.6, zorder=0)
    names = list(groups_dict.keys())
    for pos, name in enumerate(names):
        vals = np.asarray(groups_dict[name], dtype=float)
        kde = gaussian_kde(vals)
        grid = np.linspace(vals.min(), vals.max(), 120)
        dens = kde(grid)
        half_w = 0.36 * (dens / dens.max())
        ax.fill_betweenx(grid, pos - half_w, pos + half_w, color="#DCEAF7", edgecolor="#56B4E9", lw=0.8, zorder=2)
        local_w = 0.30 * (kde(vals) / dens.max())
        x_jit = pos + rng.uniform(-1.0, 1.0, size=len(vals)) * local_w
        ax.scatter(x_jit, vals, s=9, color="#004C7A", alpha=0.65, edgecolors="none", zorder=3)
    ax.set_xticks(range(len(names)))
    ax.set_xticklabels(names)
    ax.set_ylabel(ylabel)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    return fig, ax
```
