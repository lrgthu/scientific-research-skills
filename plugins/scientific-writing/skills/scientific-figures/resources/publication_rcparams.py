"""Publication & Slide Matplotlib Presets (Wilke 2019 + Rougier, Droettboom & Bourne 2014).

Provides:
- Colorblind-safe Okabe-Ito qualitative palette + paired light-fill / dark-text shades (Wilke Ch. 19-20)
- Exact physical journal column widths (Nature/Science, NeurIPS/ICML, IEEE/PLOS, 16:9 Slides)
- High-data-ink, despined Matplotlib rcParams with Type-42 TrueType vector PDF embedding (Wilke Ch. 23-27)
- Perpendicular context-grid, direct-label, and repeatable RNG helpers
"""

from __future__ import annotations
import matplotlib as mpl
import numpy as np

# Colorblind-safe Okabe-Ito palette (Wilke Table 19.1)
OKABE_ITO = {
    "orange": "#E69F00",
    "sky_blue": "#56B4E9",
    "bluish_green": "#009E73",
    "yellow": "#F0E442",
    "blue": "#0072B2",
    "vermilion": "#D55E00",
    "reddish_purple": "#CC79A7",
    "black": "#000000",
    "gray": "#7F7F7F",
    "light_gray": "#CCCCCC",
}

# Paired (light_fill, dark_stroke_or_text) hues so thin direct-label text stays crisp (Wilke Ch. 20)
OKABE_ITO_PAIRED_SHADES = {
    "blue": ("#A6CEE3", "#004C7A"),
    "vermilion": ("#F4B69C", "#9E3D00"),
    "bluish_green": ("#9FD8C7", "#006B4D"),
    "orange": ("#F9DFA2", "#A36E00"),
    "reddish_purple": ("#E8C4D8", "#8C436A"),
    "gray": ("#E0E0E0", "#4D4D4D"),
}

OKABE_ITO_CYCLE = [
    "#0072B2",  # blue
    "#D55E00",  # vermilion
    "#009E73",  # bluish green
    "#E69F00",  # orange
    "#CC79A7",  # reddish purple
    "#56B4E9",  # sky blue
    "#000000",  # black
]

# Solid filled marker cycle for redundant coding without noisy hollow line-drawings (Wilke Ch. 20 & 25)
SOLID_MARKERS = ["o", "s", "^", "D", "v", "P"]

# Exact physical column widths in inches (include in LaTeX at scale=1.0, Wilke Ch. 24 & Rougier Rule 3)
COLUMN_WIDTHS_IN = {
    "nature_1col": 3.50,      # 89 mm
    "nature_1.5col": 4.72,    # 120 mm
    "nature_2col": 7.20,      # 183 mm
    "neurips_half": 2.70,
    "neurips_full": 5.50,
    "icml_1col": 3.25,
    "icml_2col": 6.75,
    "ieee_1col": 3.45,
    "ieee_2col": 7.00,
    "slide_half": 6.00,
    "slide_full": 11.50,
}


def apply_publication_style(medium: str = "paper") -> None:
    """Apply clean, balanced rcParams adapted to 'paper' or 'slide' (Wilke Ch. 23-27, Rougier Rules 3 & 5)."""
    is_slide = medium.lower() == "slide"
    base_font = 16 if is_slide else 8.5
    line_width = 2.4 if is_slide else 1.3
    axes_lw = 1.2 if is_slide else 0.7

    mpl.rcParams.update({
        # Editable TrueType fonts in PDF/PS & preserved text in SVG (Wilke Ch. 27)
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "none",
        # Typography (Wilke Ch. 24: never tiny unreadable labels!)
        "font.family": "sans-serif",
        "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica", "Liberation Sans"],
        "font.size": base_font,
        "axes.titlesize": base_font + (2 if is_slide else 0.5),
        "axes.labelsize": base_font,
        "xtick.labelsize": base_font - (2 if is_slide else 1.0),
        "ytick.labelsize": base_font - (2 if is_slide else 1.0),
        "legend.fontsize": base_font - (2 if is_slide else 1.0),
        # Balanced data & context: despined top/right, clean outward ticks (Wilke Ch. 23)
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.linewidth": axes_lw,
        "axes.grid": False,
        "grid.color": "#E2E2E2",
        "grid.linewidth": 0.6,
        "axes.prop_cycle": mpl.cycler(color=OKABE_ITO_CYCLE),
        # Lines & Solid Markers (scaled proportionally with font size, Wilke Ch. 24-25)
        "lines.linewidth": line_width,
        "lines.markersize": 7.2 if is_slide else 4.5,
        "patch.edgecolor": "none",  # Solid fills without noisy outlines by default (Wilke Ch. 25)
        # Ticks
        "xtick.direction": "out",
        "ytick.direction": "out",
        "xtick.major.width": axes_lw,
        "ytick.major.width": axes_lw,
        "xtick.major.size": 5.0 if is_slide else 3.0,
        "ytick.major.size": 5.0 if is_slide else 3.0,
        # Clean legend without chartjunk box
        "legend.frameon": False,
        # Layout & lossless high-DPI PNG fallback (never JPEG! Wilke Ch. 27)
        "figure.constrained_layout.use": True,
        "savefig.dpi": 300 if is_slide else 600,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.03,
        # Monotonic perceptually uniform default colormap (never jet/rainbow, Wilke Ch. 4 & 19)
        "image.cmap": "viridis",
    })


def figsize_for(preset: str = "icml_1col", aspect: float = 0.68) -> tuple[float, float]:
    """Return (width_in, height_in) for a given venue preset and height/width aspect ratio."""
    w = COLUMN_WIDTHS_IN.get(preset, 3.45)
    return (w, round(w * aspect, 2))


def add_perpendicular_grid(ax: mpl.axes.Axes, vary_along: str = "y") -> None:
    """Add light-gray major gridlines perpendicular to the primary variable of interest (Wilke Ch. 23)."""
    grid_axis = "y" if vary_along == "y" else "x"
    ax.grid(axis=grid_axis, color="#E2E2E2", linewidth=0.6, zorder=0)
    ax.set_axisbelow(True)


def repeatable_rng(seed: int = 42) -> np.random.Generator:
    """Return a seeded Generator so jitter/bootstrap/draws are pixel-repeatable (Wilke Ch. 28)."""
    return np.random.default_rng(seed)
