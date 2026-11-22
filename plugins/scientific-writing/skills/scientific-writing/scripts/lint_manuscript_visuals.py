#!/usr/bin/env python3
r"""Deterministic LaTeX Prose <-> Figure/Table Symbiosis Linter.

Audits LaTeX manuscripts (flattening `\input{}` / `\include{}` in reading order) for:
1. Orphan Visuals: Figures or tables never cited in prose (`\label{fig:...}` / `\label{tab:...}` with zero `\ref`/`\cref`).
2. Out-of-Order Callouts: Figures or tables cited out of sequence relative to their appearance order (e.g., citing Fig. 3 before Fig. 2).
3. Undefined Visual References: Prose `\ref{fig:...}` / `\cref{tab:...}` pointing to non-existent labels.
4. Pointer-Topic Sentences: Sentences wasting the Topic position on `"Figure \ref{...} shows"` / `"Table \ref{...} summarizes"` instead of leading with the scientific finding.
5. Descriptive vs. Declarative Figure Captions: Empirical figure captions starting with weak catalog phrases (`"Relationship between..."`, `"Plot of..."`, `"This figure shows..."`) instead of a takeaway claim.
"""

# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any

INPUT_RE = re.compile(r"\\(?:input|include)\{([^}]+)\}")
FLOAT_ENV_RE = re.compile(
    r"\\begin\{(figure\*?|table\*?)\}(.*?)\\end\{\1\}",
    flags=re.DOTALL,
)
LABEL_RE = re.compile(r"\\label\{([^}]+)\}")
REF_RE = re.compile(
    r"\\(?:ref|cref|Cref|autoref|figureref|tableref)\*?\{([^}]+)\}"
)

POINTER_TOPIC_RE = re.compile(
    r"(?:^\s*|[.!?]\s+|\\(?:section|subsection|subsubsection|paragraph)\*?\{[^}]*\}\s*)"
    r"(?:As\s+(?:shown|illustrated|seen|reported|summarized|depicted)\s+in\s+(?:Fig(?:ure)?\.?|Tab(?:le)?\.?)\s*~?\s*\\(?:ref|cref|Cref|autoref)\{[^}]+\}\s*,|"
    r"(?:Fig(?:ure)?\.?|Tab(?:le)?\.?)\s*~?\s*\\(?:ref|cref|Cref|autoref)\{[^}]+\}\s+(?:shows?|presents?|illustrates?|depicts?|summarizes?|lists?|compares?|plots?|displays?)\b)",
    flags=re.IGNORECASE,
)

WEAK_CAPTION_START_RE = re.compile(
    r"^(?:This\s+figure\s+(?:shows|illustrates|depicts|presents)|"
    r"(?:A\s+|The\s+)?(?:plot|graph|chart|bar\s+chart|scatter\s+plot|histogram|comparison|summary|relationship|results?|illustration)\s+(?:of|between|showing|comparing)\b)",
    flags=re.IGNORECASE,
)


def strip_comments(tex: str) -> str:
    return "\n".join(re.sub(r"(?<!\\)%.*$", "", ln) for ln in tex.splitlines())


def flatten_manuscript(entry_path: Path, base_dir: Path | None = None, visited: set[Path] | None = None) -> str:
    if visited is None:
        visited = set()
    resolved = entry_path.resolve()
    if resolved in visited or not resolved.exists():
        return ""
    visited.add(resolved)
    bdir = base_dir or resolved.parent
    raw = strip_comments(resolved.read_text(encoding="utf-8", errors="ignore"))

    def _repl(m: re.Match[str]) -> str:
        rel = m.group(1).strip()
        for cand in (resolved.parent / rel, resolved.parent / f"{rel}.tex", bdir / rel, bdir / f"{rel}.tex"):
            if cand.exists() and cand.is_file():
                return "\n" + flatten_manuscript(cand, bdir, visited) + "\n"
        return m.group(0)

    return INPUT_RE.sub(_repl, raw)


def extract_balanced_caption(block: str) -> str:
    m = re.search(r"\\caption(?:\[[^\]]*\])?\s*\{", block)
    if not m:
        return ""
    i = m.end()
    depth = 1
    n = len(block)
    while i < n and depth > 0:
        if block[i] == "\\" and i + 1 < n:
            i += 2
            continue
        if block[i] == "{":
            depth += 1
        elif block[i] == "}":
            depth -= 1
        i += 1
    raw_cap = block[m.end() : max(m.end(), i - 1)]
    # Strip simple styling commands like \textbf{...} for clean inspection
    clean = re.sub(r"\\(?:textbf|textit|emph)\{([^{}]*)\}", r"\1", raw_cap)
    return re.sub(r"\s+", " ", clean).strip()


def lint_tex_source(tex_text: str) -> dict[str, Any]:
    clean_tex = strip_comments(tex_text)

    declared_figures: list[dict[str, Any]] = []
    declared_tables: list[dict[str, Any]] = []
    declared_set: set[str] = set()

    for m in FLOAT_ENV_RE.finditer(clean_tex):
        env_type = m.group(1).rstrip("*")
        body = m.group(2)
        caption = extract_balanced_caption(body)
        labels = [lb.strip() for lb in LABEL_RE.findall(body) if lb.strip()]
        if not labels:
            continue
        primary_label = labels[0]
        rec = {
            "kind": env_type,
            "label": primary_label,
            "all_labels": labels,
            "caption_preview": caption[:200],
        }
        for lb in labels:
            declared_set.add(lb)
        if env_type == "figure":
            declared_figures.append(rec)
        else:
            declared_tables.append(rec)

    # Remove float blocks before scanning prose callouts so self-references inside captions don't mask uncited floats
    prose_only = FLOAT_ENV_RE.sub(" ", clean_tex)

    first_seen_order: list[str] = []
    seen_refs: set[str] = set()
    for rm in REF_RE.finditer(prose_only):
        for raw_k in rm.group(1).split(","):
            k = raw_k.strip()
            if k and k not in seen_refs:
                seen_refs.add(k)
                first_seen_order.append(k)

    # 1. Orphan visuals (never cited in prose)
    orphan_visuals: list[dict[str, str]] = []
    for item in declared_figures + declared_tables:
        if not any(lb in seen_refs for lb in item["all_labels"]):
            orphan_visuals.append({"kind": item["kind"], "label": item["label"], "caption_preview": item["caption_preview"]})

    # 2. Sequential ordering check (separately for figures and tables)
    out_of_order: list[dict[str, Any]] = []
    for kind_name, decl_list in (("figure", declared_figures), ("table", declared_tables)):
        cited_decl_indices: list[tuple[int, str, int]] = []
        for decl_idx, item in enumerate(decl_list, start=1):
            positions = [first_seen_order.index(lb) for lb in item["all_labels"] if lb in seen_refs]
            if positions:
                cited_decl_indices.append((min(positions), item["label"], decl_idx))
        cited_decl_indices.sort(key=lambda t: t[0])
        max_decl_seen = 0
        max_label_seen = ""
        for _, label, decl_idx in cited_decl_indices:
            if decl_idx < max_decl_seen:
                out_of_order.append(
                    {
                        "kind": kind_name,
                        "label": label,
                        "declared_number": decl_idx,
                        "cited_after_label": max_label_seen,
                        "cited_after_number": max_decl_seen,
                    }
                )
            else:
                max_decl_seen = decl_idx
                max_label_seen = label

    # 3. Undefined fig:/tab: refs
    undefined_visual_refs = sorted(
        k
        for k in seen_refs
        if k not in declared_set and (k.lower().startswith("fig:") or k.lower().startswith("tab:"))
    )

    # 4. Pointer-Topic metadiscourse sentences in prose
    pointer_sentences: list[str] = []
    normalized_prose = re.sub(r"\s+", " ", prose_only)
    for pm in POINTER_TOPIC_RE.finditer(normalized_prose):
        start = pm.start()
        end = normalized_prose.find(".", pm.end())
        snippet = normalized_prose[start : (end + 1 if end != -1 else start + 180)].strip()
        pointer_sentences.append(snippet[:220])

    # 5. Weak descriptive figure captions
    weak_captions: list[dict[str, str]] = []
    for fig in declared_figures:
        cap = fig["caption_preview"]
        if cap and WEAK_CAPTION_START_RE.search(cap):
            weak_captions.append({"label": fig["label"], "caption_preview": cap})

    return {
        "counts": {
            "declared_figures": len(declared_figures),
            "declared_tables": len(declared_tables),
            "orphan_visuals": len(orphan_visuals),
            "out_of_order_callouts": len(out_of_order),
            "undefined_visual_refs": len(undefined_visual_refs),
            "pointer_topic_sentences": len(pointer_sentences),
            "weak_descriptive_figure_captions": len(weak_captions),
        },
        "clean": not (
            orphan_visuals
            or out_of_order
            or undefined_visual_refs
            or pointer_sentences
            or weak_captions
        ),
        "orphan_visuals": orphan_visuals,
        "out_of_order_callouts": out_of_order,
        "undefined_visual_refs": undefined_visual_refs,
        "pointer_topic_sentences": pointer_sentences[:25],
        "weak_descriptive_figure_captions": weak_captions,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit LaTeX prose <-> figure/table callouts, ordering, and captions.")
    parser.add_argument("target", help="Path to root main.tex file or manuscript directory")
    parser.add_argument("--output", "-o", help="Optional JSON report output path")
    args = parser.parse_args()

    p = Path(args.target).expanduser().resolve()
    if p.is_file():
        full_tex = flatten_manuscript(p)
    else:
        tex_files = sorted(p.rglob("*.tex"))
        roots = [t for t in tex_files if "\\documentclass" in t.read_text(encoding="utf-8", errors="ignore")]
        if roots:
            full_tex = flatten_manuscript(roots[0], p)
        else:
            full_tex = "\n".join(t.read_text(encoding="utf-8", errors="ignore") for t in tex_files)

    report = lint_tex_source(full_tex)
    out_str = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        Path(args.output).expanduser().write_text(out_str, encoding="utf-8")
    else:
        sys.stdout.write(out_str)


if __name__ == "__main__":
    main()
