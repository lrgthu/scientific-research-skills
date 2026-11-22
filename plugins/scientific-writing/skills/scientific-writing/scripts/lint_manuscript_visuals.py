#!/usr/bin/env python3
r"""Deterministic LaTeX Prose <-> Visual Symbiosis & Abstract Narrative Spectrum Linter.

Audits LaTeX manuscripts (flattening `\input{}` / `\include{}` in reading order) for:
1. Orphan Visuals: Figures or tables never cited in prose (`\label{fig:...}` / `\label{tab:...}` with zero `\ref`/`\cref`).
2. Out-of-Order Callouts: Figures or tables cited out of sequence relative to their appearance order (e.g., citing Fig. 3 before Fig. 2).
3. Undefined Visual References: Prose `\ref{fig:...}` / `\cref{tab:...}` pointing to non-existent labels.
4. Pointer-Topic Sentences: Sentences wasting the Topic position on `"Figure \ref{...} shows"` / `"Table \ref{...} summarizes"` instead of leading with the scientific finding.
5. Descriptive vs. Declarative Figure Captions: Empirical figure captions starting with weak catalog phrases (`"Relationship between..."`, `"Plot of..."`, `"This figure shows..."`) instead of a takeaway claim.
6. Abstract Narrative Spectrum (`AAA` / `DHY` — Randy Olson): Flags abstracts that (a) open Sentence 1 with a bare contradiction (`However, ...`) before context, (b) jump straight into uncontextualized action (`We measured ...` / Bizzwidget pitch) in Sentence 1, (c) fire `>=3` consecutive or `>=4` sentence-initial contradiction turns (`Despite... However... Yet...` DHY zig-zag), or (d) list `>=4` sentences with zero contradiction/problem/gap pivot (`AAA` fact dump).
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
ABSTRACT_ENV_RE = re.compile(
    r"\\begin\{abstract\}(.*?)\\end\{abstract\}",
    flags=re.DOTALL | re.IGNORECASE,
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
    r"(?:A\s+|The\s+)?(?:plot|graph|chart|bar\s+chart|scatter\s+plot|histogram|comparison|summary|relationship|results?|illustration)\s+(?:of|between|showing|comparing)\b|"
    r"(?:An?\s+|The\s+)?(?:ablation\s+(?:study|results?|analysis|experiments?)|experimental\s+(?:results?|evaluation|comparison|setup)|"
    r"(?:performance|accuracy|perplexity|latency|throughput|evaluation)\s+(?:comparison|results?|evaluation|study|analysis))\s+(?:of|on|for|across|between)\b)",
    flags=re.IGNORECASE,
)
SECTION_HEADING_RE = re.compile(r"\\(?:section|subsection)\*?\{([^{}]+)\}")
SUBPANEL_CAP_RE = re.compile(r"\(\s*([a-h])\s*\)")

# Olson Narrative Spectrum (AAA / ABT / DHY) patterns for abstracts
BARE_CONTRADICTION_S1_RE = re.compile(
    r"^(?:However|Yet|Nevertheless|Nonetheless|Conversely|Instead)\b",
    flags=re.IGNORECASE,
)
ZERO_CONTEXT_ACTION_S1_RE = re.compile(
    r"^(?:We\s+(?:examined|measured|investigated|tested|evaluated|conducted|collected|analyzed|performed|trained|sampled|probed|propose|present|introduce)\b|"
    r"In\s+this\s+(?:paper|study|work|article|letter)\s*,?\s*we\s+(?:examine|measure|investigate|test|evaluate|present|propose|introduce|analyze)\b)",
    flags=re.IGNORECASE,
)
SENT_CONTRADICTION_START_RE = re.compile(
    r"^(?:However|Yet|Despite|Although|Nevertheless|Nonetheless|Conversely|Whereas|Instead|Still|Unfortunately|In\s+contrast|On\s+the\s+other\s+hand)\b",
    flags=re.IGNORECASE,
)
ANY_CONTRADICTION_OR_GAP_RE = re.compile(
    r"\b(?:but|however|yet|despite|although|though|whereas|nevertheless|nonetheless|instead|conversely|while|unfortunately|unlike|rather\s+than|"
    r"challeng\w*|bottleneck\w*|limit\w*|fail\w*|degrad\w*|suffer\w*|lack\w*|unclear|unknown|unsolved|unresolved|poorly\s+understood|elusive|"
    r"inability|prohibitive\w*|intractable|unstabl\w*|instabilit\w*|collaps\w*|diverg\w*|unsatisfactor\w*|obstacl\w*|barrier\w*|trade-?off\w*|"
    r"dilemma\w*|paradox\w*|contradict\w*|conflict\w*|erases?|erasing|loses?|losing|miss(?:es|ing)?|overlook\w*|cannot|unable|stall\w*)\b",
    flags=re.IGNORECASE,
)
ABBREV_PROTECT_RE = re.compile(
    r"\b(?:e\.g|i\.e|et\s+al|Fig|Figs|Tab|Tabs|Sec|Secs|Eq|Eqs|vs|cf|approx|Dr|Prof)\.",
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


def extract_balanced_braces(text: str, macro_regex: str) -> str:
    m = re.search(macro_regex, text)
    if not m:
        return ""
    i = m.end()
    depth = 1
    n = len(text)
    while i < n and depth > 0:
        if text[i] == "\\" and i + 1 < n:
            i += 2
            continue
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
        i += 1
    return text[m.end() : max(m.end(), i - 1)]


def extract_balanced_caption(block: str) -> str:
    raw_cap = extract_balanced_braces(block, r"\\caption(?:\[[^\]]*\])?\s*\{")
    if not raw_cap:
        return ""
    clean = re.sub(r"\\(?:textbf|textit|emph)\{([^{}]*)\}", r"\1", raw_cap)
    return re.sub(r"\s+", " ", clean).strip()


def extract_abstract_sentences(clean_tex: str) -> list[str]:
    m = ABSTRACT_ENV_RE.search(clean_tex)
    raw_abs = m.group(1) if m else extract_balanced_braces(clean_tex, r"\\abstract\s*\{")
    if not raw_abs.strip():
        return []
    txt = re.sub(r"\$[^$]*\$", " MATH ", raw_abs)
    txt = re.sub(r"\\(?:cite\w*|ref|cref|Cref|autoref|label)\*?(?:\[[^\]]*\])*\{[^}]*\}", " ", txt)
    txt = re.sub(r"\\(?:textbf|textit|emph|textrm|texttt)\{([^{}]*)\}", r"\1", txt)
    txt = re.sub(r"\\[a-zA-Z]+\*?", " ", txt)
    txt = txt.replace("{", " ").replace("}", " ").replace("~", " ")
    txt = ABBREV_PROTECT_RE.sub(lambda am: am.group(0).replace(".", "<DOT>"), txt)
    txt = re.sub(r"(\d)\.(\d)", r"\1<DOT>\2", txt)
    txt = re.sub(r"\s+", " ", txt).strip()
    parts = [p.replace("<DOT>", ".").strip() for p in re.split(r"[.!?]+\s+", txt) if p.strip()]
    if parts:
        parts[-1] = parts[-1].rstrip(".!?").strip()
    return [s for s in parts if len(s.split()) >= 3]


def lint_abstract_narrative(clean_tex: str) -> dict[str, Any]:
    sentences = extract_abstract_sentences(clean_tex)
    if not sentences:
        return {"present": False, "sentence_count": 0, "warnings": []}

    warnings: list[dict[str, str]] = []
    s1 = sentences[0]

    if BARE_CONTRADICTION_S1_RE.search(s1):
        warnings.append(
            {
                "code": "PREMATURE_CONTRADICTION_OPENER",
                "message": "Abstract Sentence 1 starts with a bare contradiction connector before establishing shared 'AND' context (Olson DHY trap).",
                "excerpt": s1[:200],
            }
        )
    elif len(sentences) >= 2 and ZERO_CONTEXT_ACTION_S1_RE.search(s1):
        warnings.append(
            {
                "code": "ZERO_CONTEXT_ACTION_OPENER",
                "message": "Abstract Sentence 1 jumps straight into 'We measured/propose...' without establishing the motivating problem or 'AND/BUT' context first (Olson DHY / Schimel Bizzwidget trap).",
                "excerpt": s1[:200],
            }
        )

    flags = [bool(SENT_CONTRADICTION_START_RE.search(s)) for s in sentences]
    max_consec = 0
    cur_run = 0
    for fl in flags:
        cur_run = cur_run + 1 if fl else 0
        max_consec = max(max_consec, cur_run)
    total_turns = sum(flags)

    if max_consec >= 3 or total_turns >= 4:
        warnings.append(
            {
                "code": "CONSECUTIVE_CONTRADICTION_ZIGZAG",
                "message": f"Abstract fires {total_turns} sentence-initial contradiction turns (max consecutive={max_consec}), creating multi-directional 'DHY' (Despite, However, Yet) confusion instead of a singular 'BUT' pivot.",
                "excerpt": " | ".join(s[:80] for s, fl in zip(sentences, flags) if fl),
            }
        )

    joined = " ".join(sentences)
    if len(sentences) >= 4 and not ANY_CONTRADICTION_OR_GAP_RE.search(joined):
        warnings.append(
            {
                "code": "NO_CONTRADICTION_AAA_ABSTRACT",
                "message": f"Abstract ({len(sentences)} sentences) contains zero contradiction, bottleneck, or knowledge-gap pivot ('AAA: And, And, And' non-narrative fact dump).",
                "excerpt": joined[:220],
            }
        )

    return {
        "present": True,
        "sentence_count": len(sentences),
        "warnings": warnings,
    }


def extract_first_sentence(text: str) -> str:
    if not text:
        return ""
    protected = ABBREV_PROTECT_RE.sub(lambda am: am.group(0).replace(".", "<DOT>"), text)
    protected = re.sub(r"(\d)\.(\d)", r"\1<DOT>\2", protected)
    m = re.search(r"[.!?](?:\s+|$)", protected)
    first = protected[: m.start() + 1] if m else protected
    return first.replace("<DOT>", ".").strip()[:220]


def extract_subpanels_from_caption(caption: str) -> list[str]:
    found = sorted(set(ch.lower() for ch in SUBPANEL_CAP_RE.findall(caption)))
    if "a" in found and "b" in found:
        return found
    return []


def extract_cited_subpanels(prose_only: str, labels: list[str]) -> list[str]:
    cited: set[str] = set()
    for lb in labels:
        esc = re.escape(lb)
        for m in re.finditer(
            rf"\\(?:ref|cref|Cref|autoref|figureref)\*?\{{[^}}]*\b{esc}\b[^}}]*\}}\s*(?:\(\s*([a-h])\s*\)|([a-h])(?:\s*(?:--|-|,|\band\b)\s*([a-h]))?(?![a-zA-Z]))",
            prose_only,
        ):
            p1 = m.group(1) or m.group(2)
            p2 = m.group(3)
            if p1:
                cited.add(p1.lower())
            if p1 and p2 and ord(p1.lower()) <= ord(p2.lower()):
                for code in range(ord(p1.lower()), ord(p2.lower()) + 1):
                    cited.add(chr(code))
        # Also support \subref{fig:foo_a} or direct sub-label suffixes if defined
    return sorted(cited)


def extract_first_callout_sentence(prose_only: str, labels: list[str]) -> str:
    protected = ABBREV_PROTECT_RE.sub(lambda am: am.group(0).replace(".", "<DOT>"), prose_only)
    protected = re.sub(r"(\d)\.(\d)", r"\1<DOT>\2", protected)
    best_pos: int | None = None
    for lb in labels:
        esc = re.escape(lb)
        m = re.search(rf"\\(?:ref|cref|Cref|autoref|figureref|tableref)\*?\{{[^}}]*\b{esc}\b[^}}]*\}}", protected)
        if m and (best_pos is None or m.start() < best_pos):
            best_pos = m.start()
    if best_pos is None:
        return ""
    left = max(
        protected.rfind(".", 0, best_pos),
        protected.rfind("!", 0, best_pos),
        protected.rfind("?", 0, best_pos),
        protected.rfind("\n\n", 0, best_pos),
    )
    right_candidates = [idx for idx in (protected.find(".", best_pos), protected.find("!", best_pos), protected.find("?", best_pos)) if idx != -1]
    right = min(right_candidates) + 1 if right_candidates else min(len(protected), best_pos + 180)
    raw_sent = protected[(left + 1 if left != -1 else 0) : right].replace("<DOT>", ".")
    raw_sent = re.sub(r"\\(?:section|subsection|subsubsection|paragraph)\*?\{[^}]*\}", " ", raw_sent)
    return re.sub(r"\s+", " ", raw_sent).strip()[:240]


def lint_tex_source(tex_text: str, check_abstract: bool = True) -> dict[str, Any]:
    clean_tex = strip_comments(tex_text)

    sections_index = [(sm.start(), re.sub(r"\s+", " ", sm.group(1)).strip()) for sm in SECTION_HEADING_RE.finditer(clean_tex)]

    def _nearest_section(pos: int) -> str:
        sec = "(preamble/root)"
        for spos, stitle in sections_index:
            if spos <= pos:
                sec = stitle
            else:
                break
        return sec

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
            "section": _nearest_section(m.start()),
            "caption_full": caption,
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
    ref_counts: dict[str, int] = {}
    for rm in REF_RE.finditer(prose_only):
        for raw_k in rm.group(1).split(","):
            k = raw_k.strip()
            if k:
                ref_counts[k] = ref_counts.get(k, 0) + 1
                if k not in seen_refs:
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

    # 6. Abstract Narrative Spectrum (AAA / ABT / DHY)
    abstract_info = lint_abstract_narrative(clean_tex) if check_abstract else {"present": False, "sentence_count": 0, "warnings": []}
    abstract_warnings = abstract_info["warnings"]

    # 7. Structured Visual Inventory Scaffold (for 5-Gate Assertion-Evidence Auditing)
    visual_inventory: list[dict[str, Any]] = []
    for kind_name, decl_list in (("figure", declared_figures), ("table", declared_tables)):
        for idx, item in enumerate(decl_list, start=1):
            total_cites = sum(ref_counts.get(lb, 0) for lb in item["all_labels"])
            sub_decl = extract_subpanels_from_caption(item["caption_full"]) if kind_name == "figure" else []
            sub_cited = extract_cited_subpanels(prose_only, item["all_labels"]) if sub_decl else []
            uncited_sub = [sp for sp in sub_decl if sp not in sub_cited] if sub_decl else []
            visual_inventory.append(
                {
                    "id": f"{'Figure' if kind_name == 'figure' else 'Table'} {idx}",
                    "kind": kind_name,
                    "number": idx,
                    "label": item["label"],
                    "section": item["section"],
                    "callout_count": total_cites,
                    "first_callout_sentence": extract_first_callout_sentence(prose_only, item["all_labels"]),
                    "caption_first_sentence": extract_first_sentence(item["caption_full"]),
                    "subpanels_declared": sub_decl,
                    "subpanels_explicitly_cited": sub_cited,
                    "uncited_subpanels_hint": uncited_sub,
                }
            )

    return {
        "counts": {
            "declared_figures": len(declared_figures),
            "declared_tables": len(declared_tables),
            "orphan_visuals": len(orphan_visuals),
            "out_of_order_callouts": len(out_of_order),
            "undefined_visual_refs": len(undefined_visual_refs),
            "pointer_topic_sentences": len(pointer_sentences),
            "weak_descriptive_figure_captions": len(weak_captions),
            "abstract_narrative_warnings": len(abstract_warnings),
        },
        "clean": not (
            orphan_visuals
            or out_of_order
            or undefined_visual_refs
            or pointer_sentences
            or weak_captions
            or abstract_warnings
        ),
        "visual_inventory": visual_inventory,
        "orphan_visuals": orphan_visuals,
        "out_of_order_callouts": out_of_order,
        "undefined_visual_refs": undefined_visual_refs,
        "pointer_topic_sentences": pointer_sentences[:25],
        "weak_descriptive_figure_captions": weak_captions,
        "abstract_narrative": abstract_info,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Audit LaTeX prose <-> figure/table callouts, ordering, captions, and Abstract ABT/AAA/DHY narrative balance."
    )
    parser.add_argument("target", help="Path to root main.tex file or manuscript directory")
    parser.add_argument("--no-abstract-lint", action="store_true", help="Skip Abstract AAA/DHY narrative spectrum checks")
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

    report = lint_tex_source(full_tex, check_abstract=not args.no_abstract_lint)
    out_str = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        Path(args.output).expanduser().write_text(out_str, encoding="utf-8")
    else:
        sys.stdout.write(out_str)


if __name__ == "__main__":
    main()
