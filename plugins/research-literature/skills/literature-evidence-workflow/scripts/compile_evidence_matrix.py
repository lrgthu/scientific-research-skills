#!/usr/bin/env python3
r"""Compiles structured per-paper extraction JSON into CSV, Markdown, and Booktabs LaTeX tables.

Enforces `scientific-figures` Booktabs publication table formatting:
- Caption ABOVE the table
- `\toprule`, `\midrule`, `\bottomrule` only (ZERO vertical bars `|`, ZERO inter-row `\hline`s)
- Left-aligned text columns (`l` / `p{...}`), right-aligned numeric columns (`r`)
- Preserves provenance anchors in Markdown synthesis notes
"""

# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import re
from typing import Any


LATEX_ESCAPE_MAP = {
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}


def latex_escape(val: Any) -> str:
    s = re.sub(r"\s+", " ", str(val if val is not None else "—")).strip()
    return "".join(LATEX_ESCAPE_MAP.get(ch, ch) for ch in s)


def md_escape(val: Any) -> str:
    s = re.sub(r"\s+", " ", str(val if val is not None else "—")).strip()
    return s.replace("|", r"\|")


def is_numeric_column(rows: list[dict[str, Any]], col: str) -> bool:
    vals = [str(r.get(col, "")).strip() for r in rows if r.get(col) not in (None, "", "—", "N/A")]
    if not vals:
        return False
    num_re = re.compile(r"^[+-]?\d+(?:\.\d+)?(?:\s*[±%×xkMGB]+)?$")
    return sum(1 for v in vals if num_re.match(v)) >= max(1, int(0.75 * len(vals)))


DEFAULT_COLUMNS = [
    ("citation_label", "Study"),
    ("method_family", "Method Family"),
    ("problem_regime", "Regime / Setting"),
    ("core_mechanism", "Core Mechanism"),
    ("datasets_and_scale", "Datasets & Scale"),
    ("primary_metric_delta", "Reported Effect / Δ"),
    ("verified_limitation", "Key Assumption / Limitation"),
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Compile JSON paper extractions into CSV, Markdown, and Booktabs LaTeX.")
    parser.add_argument("extractions_json", help="Input JSON array (or {'rows': [...]}) of extracted paper records")
    parser.add_argument("--out-dir", required=True, help="Output directory for evidence_matrix.{csv,md,tex}")
    parser.add_argument(
        "--columns",
        help="Optional comma-separated field:Header pairs (e.g. 'citation_label:Study,core_mechanism:Mechanism')",
    )
    parser.add_argument("--caption", default="Structured comparison of prior methods, assumptions, empirical regimes, and verified limitations.", help="Booktabs table caption (placed ABOVE table)")
    parser.add_argument("--label", default="tab:literature_comparison", help="LaTeX table label")
    args = parser.parse_args()

    raw = json.loads(Path(args.extractions_json).expanduser().read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = raw["rows"] if isinstance(raw, dict) and "rows" in raw else raw
    # Filter to included papers if `included` boolean exists
    included_rows = [r for r in rows if r.get("included", True) is not False]

    if args.columns:
        cols = []
        for pair in args.columns.split(","):
            if ":" in pair:
                k, h = pair.split(":", 1)
                cols.append((k.strip(), h.strip()))
            else:
                cols.append((pair.strip(), pair.strip()))
    else:
        present_keys = {k for r in included_rows for k in r.keys()}
        cols = [(k, h) for k, h in DEFAULT_COLUMNS if k in present_keys]
        if not cols and included_rows:
            cols = [(k, k.replace("_", " ").title()) for k in list(included_rows[0].keys())[:7] if k != "provenance"]

    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Write CSV
    csv_path = out_dir / "evidence_matrix.csv"
    all_keys = list(dict.fromkeys([k for k, _ in cols] + ["provenance_tier", "provenance_anchor", "verbatim_quote"]))
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=all_keys, extrasaction="ignore")
        writer.writeheader()
        for r in included_rows:
            writer.writerow(r)

    # 2. Write Markdown Evidence Summary + Provenance Log
    md_lines = [
        "# Literature Evidence Matrix & Provenance Audit",
        "",
        f"- **Included Studies**: {len(included_rows)} (screened from {len(rows)} candidates)",
        "",
        "| " + " | ".join(h for _, h in cols) + " | Provenance |",
        "| " + " | ".join("---:" if is_numeric_column(included_rows, k) else ":---" for k, _ in cols) + " | :--- |",
    ]
    for r in included_rows:
        prov_badge = f"`{r.get('provenance_tier', 'unspecified')}` {r.get('provenance_anchor', '')}".strip()
        cells = [md_escape(r.get(k, "—")) for k, _ in cols] + [md_escape(prov_badge)]
        md_lines.append("| " + " | ".join(cells) + " |")

    md_lines.extend(["", "## Verbatim Evidence & Provenance Anchors", ""])
    for r in included_rows:
        label = r.get("citation_label") or r.get("title") or "Study"
        tier = r.get("provenance_tier", "unspecified")
        anchor = r.get("provenance_anchor", "N/A")
        quote = r.get("verbatim_quote", "")
        md_lines.append(f"- **{label}** (`{tier}`, {anchor}): {quote}")

    excluded = [r for r in rows if r.get("included", True) is False]
    if excluded:
        md_lines.extend(["", "## Screened-Out Candidates (Exclusion Log)", ""])
        for ex in excluded:
            md_lines.append(f"- **{ex.get('citation_label') or ex.get('title')}**: Excluded — {ex.get('exclusion_reason', 'Outside scope rubric')}")

    md_path = out_dir / "evidence_matrix.md"
    md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    # 3. Write Booktabs LaTeX Table (`comparison_table.tex`)
    col_specs = ["r" if is_numeric_column(included_rows, k) else "l" for k, _ in cols]
    tex_lines = [
        "% Requires \\usepackage{booktabs} in preamble",
        "% Formatted per Wilke Ch. 25 / Rougier Rule 8: zero vertical lines, zero inter-row lines, caption ABOVE",
        "\\begin{table*}[t]",
        "  \\centering",
        f"  \\caption{{{latex_escape(args.caption)}}}",
        f"  \\label{{{args.label}}}",
        f"  \\begin{{tabular}}{{@{{\\extracolsep{{\\fill}}}}{''.join(col_specs)}@{{}}}}",
        "    \\toprule",
        "    " + " & ".join(latex_escape(h) for _, h in cols) + " \\\\",
        "    \\midrule",
    ]
    for r in included_rows:
        tex_lines.append("    " + " & ".join(latex_escape(r.get(k, "—")) for k, _ in cols) + " \\\\")
    tex_lines.extend(
        [
            "    \\bottomrule",
            "  \\end{tabular}",
            "\\end{table*}",
        ]
    )
    tex_path = out_dir / "comparison_table.tex"
    tex_path.write_text("\n".join(tex_lines) + "\n", encoding="utf-8")

    print(f"Compiled {len(included_rows)} rows -> {csv_path}, {md_path}, {tex_path}")


if __name__ == "__main__":
    main()
