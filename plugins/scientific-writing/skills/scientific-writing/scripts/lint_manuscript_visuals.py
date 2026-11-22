#!/usr/bin/env python3
r"""Deterministic LaTeX Prose <-> Visual Symbiosis, Abstract Narrative & Cross-Artifact Consistency Linter.

Audits LaTeX manuscripts (flattening `\input{}` / `\include{}` across main text + appendix in reading order) for:
1. Orphan Visuals: Figures or tables never cited in prose (`\label{fig:...}` / `\label{tab:...}` with zero `\ref`/`\cref`).
2. Out-of-Order Callouts: Figures or tables cited out of sequence relative to their appearance order (e.g., citing Fig. 3 before Fig. 2).
3. Undefined Visual References: Prose `\ref{fig:...}` / `\cref{tab:...}` pointing to non-existent labels.
4. Pointer-Topic Sentences: Sentences wasting the Topic position on `"Figure \ref{...} shows"` / `"Table \ref{...} summarizes"` instead of leading with the scientific finding.
5. Descriptive vs. Declarative Figure Captions: Empirical figure captions starting with weak catalog/topic phrases (`"Relationship between..."`, `"Ablation study on..."`) instead of a takeaway claim.
6. Abstract Narrative Spectrum (`AAA` / `DHY` — Randy Olson): Flags bare Sentence-1 contradictions, zero-context `"We measured..."` openers, `DHY` contradiction zig-zags, and zero-conflict `AAA` abstracts.
7. Cross-Artifact Numeric & Protocol Consistency: Parses all LaTeX tables (`tabular`/`tabularx`/`\multicolumn`/`\multirow`) across main text and appendix to detect shared `(Dataset/Condition, Method, Metric)` cells that disagree beyond rounding without explicit `Protocol P1/P2` disambiguation, plus stale decimal metrics in the Abstract unmatched anywhere in the body/tables.
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

TABULAR_ENV_RE = re.compile(
    r"\\begin\{(tabular\*?|tabularx|tabulary)\}(.*?)\\end\{\1\}",
    flags=re.DOTALL,
)
PROTO_TAG_RE = re.compile(
    r"(?:\bProtocol\s+([A-Za-z0-9_-]+)|\b(P[1-9](?:-[A-Za-z0-9]+)?)\b)",
    flags=re.IGNORECASE,
)
METRIC_CELL_RE = re.compile(
    r"^\s*([+-]?\d+\.\d+)\s*(?:%|\\?%)?\s*(?:(?:\+-|\\pm|±)\s*[+-]?\d+(?:\.\d+)?\s*(?:%|\\?%)?|\(\s*[+-]?\d+(?:\.\d+)?\s*\))?\s*$"
)
GENERIC_ROLE_HEADERS = {
    "method", "methods", "model", "models", "baseline", "baselines", "approach", "approaches",
    "dataset", "datasets", "benchmark", "benchmarks", "cohort", "cohorts", "region", "regions",
    "task", "tasks", "setting", "settings", "condition", "conditions", "subset", "variant", "system",
}
SKIP_INDEX_HEADERS = {"rank", "#", "id", "idx", "index", "no", "row"}
METRIC_KEYWORDS = (
    ("r2", ("r 2", "r2", "rsq")),
    ("accuracy", ("acc", "accuracy", "top 1", "top 5")),
    ("perplexity", ("ppl", "perplexity")),
    ("latency", ("latency", "runtime", "wall clock", "ms token", "time")),
    ("throughput", ("throughput", "tok s", "tokens s", "samples s")),
    ("memory", ("memory", "vram", "hbm", "kv size", "footprint")),
    ("f1", ("f1", "f 1")),
    ("auc", ("auc", "auroc", "auprc")),
    ("recall", ("recall", "passkey")),
    ("precision", ("precision",)),
    ("loss", ("loss", "nll", "bpb")),
    ("rmse", ("rmse", "mse")),
    ("mae", ("mae",)),
    ("corr", ("pearson", "spearman", "corr")),
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


def _strip_leading_tabular_args(env_name: str, raw_body: str) -> str:
    i = 0
    n = len(raw_body)
    n_brace_args = 2 if env_name in {"tabular*", "tabularx", "tabulary"} else 1
    consumed = 0
    while i < n and consumed < n_brace_args:
        while i < n and raw_body[i].isspace():
            i += 1
        if i < n and raw_body[i] == "[":
            depth_b = 1
            i += 1
            while i < n and depth_b > 0:
                if raw_body[i] == "[":
                    depth_b += 1
                elif raw_body[i] == "]":
                    depth_b -= 1
                i += 1
            continue
        if i < n and raw_body[i] == "{":
            depth = 1
            i += 1
            while i < n and depth > 0:
                if raw_body[i] == "\\" and i + 1 < n:
                    i += 2
                    continue
                if raw_body[i] == "{":
                    depth += 1
                elif raw_body[i] == "}":
                    depth -= 1
                i += 1
            consumed += 1
        else:
            break
    return raw_body[i:]


def _clean_latex_cell(cell: str) -> str:
    s = re.sub(r"(\d)\{,\}(\d)", r"\1\2", cell)
    s = s.replace("$-$", "-").replace("$+$", "+").replace("--", "-").replace(r"\ ", " ")
    for _ in range(3):
        s_next = re.sub(
            r"\\(?:textbf|mathbf|textit|mathit|textrm|mathrm|texttt|emph|underline)\{([^{}]*)\}",
            r"\1",
            s,
        )
        if s_next == s:
            break
        s = s_next
    s = re.sub(r"\\(?:cellcolor|rowcolor|cite\w*|ref|cref|Cref|label)(?:\[[^\]]*\])*\{[^}]*\}", " ", s)
    s = re.sub(r"\\(?:dag|ddag|ast|star|uparrow|downarrow)\b", " ", s)
    s = s.replace("$", " ").replace(r"\,", " ").replace(r"\;", " ").replace(r"\!", "").replace("~", " ")
    return re.sub(r"\s+", " ", s).strip()


def _extract_proto_tag(text: str) -> str:
    tags = sorted(
        {
            (m.group(1) or m.group(2)).lower()
            for m in PROTO_TAG_RE.finditer(text)
            if (m.group(1) or m.group(2))
        }
    )
    return "+".join(tags) if tags else "canonical"


def _norm_descriptor(text: str) -> str:
    # Strip protocol annotations and benign sample-count tags `(N=8)` from entity labels
    t = PROTO_TAG_RE.sub(" ", text)
    t = re.sub(r"\(\s*[Nn]\s*=\s*\d+\s*\)", " ", t)
    t = re.sub(r"\\[a-zA-Z]+\*?", " ", t)
    t = re.sub(r"[^a-zA-Z0-9]+", " ", t).lower().strip()
    return re.sub(r"\s+", " ", t)


def _classify_metric_hint(norm_txt: str) -> str:
    padded = f" {norm_txt} "
    for canonical, aliases in METRIC_KEYWORDS:
        if any(f" {al} " in padded for al in aliases):
            return canonical
    return ""


def _split_tabular_rows(chunk: str) -> list[list[str]]:
    cleaned = re.sub(
        r"\\(?:toprule|bottomrule|cmidrule(?:\([^)]*\))?\{[^}]*\}|cline\{[^}]*\}|addlinespace(?:\[[^\]]*\])?)",
        " ",
        chunk,
    )
    cleaned = re.sub(r"\\(?:midrule|hline)\b", " ", cleaned)
    raw_rows = re.split(r"\\\\(?:\s*\[[^\]]*\])?", cleaned)
    rows: list[list[str]] = []
    for rr in raw_rows:
        if not rr.strip():
            continue
        cells = [c.strip() for c in re.split(r"(?<!\\)&", rr)]
        if any(c for c in cells):
            rows.append(cells)
    return rows


def _expand_header_row(cells: list[str]) -> list[str]:
    expanded: list[str] = []
    for c in cells:
        mc = re.search(r"\\multicolumn\{(\d+)\}\{[^}]*\}\{(.*)\}\s*$", c, flags=re.DOTALL)
        if mc:
            span = max(1, int(mc.group(1)))
            inner = _clean_latex_cell(mc.group(2))
            expanded.extend([inner] * span)
        else:
            expanded.append(_clean_latex_cell(c))
    return expanded


def _row_has_decimal_metric(row_cells: list[str]) -> bool:
    for rc in row_cells:
        if METRIC_CELL_RE.match(_clean_latex_cell(rc)):
            return True
    return False


def extract_table_metric_cells(table_rec: dict[str, Any]) -> list[dict[str, Any]]:
    body = table_rec.get("raw_body", "")
    caption = table_rec.get("caption_full", "")
    table_proto = _extract_proto_tag(caption)
    table_caption_metric = _classify_metric_hint(_norm_descriptor(_clean_latex_cell(caption)))
    out_cells: list[dict[str, Any]] = []

    for tm in TABULAR_ENV_RE.finditer(body):
        env_name = tm.group(1)
        tab_content = _strip_leading_tabular_args(env_name, tm.group(2))
        segments = re.split(r"\\(?:midrule|hline)\b", tab_content)

        active_col_headers: list[list[str]] = []
        pending_header_rows: list[list[str]] = []
        block_proto = "canonical"
        block_metric = ""

        for seg_idx, seg in enumerate(segments):
            seg_rows = _split_tabular_rows(seg)
            if not seg_rows:
                continue

            # When a table has no \midrule/\hline at all, row 0 is header and rows 1: are data
            if len(segments) == 1 and seg_idx == 0 and len(seg_rows) >= 2 and not _row_has_decimal_metric(seg_rows[0]):
                pending_header_rows.append(_expand_header_row(seg_rows[0]))
                seg_rows = seg_rows[1:]

            if not any(_row_has_decimal_metric(r) for r in seg_rows):
                for r in seg_rows:
                    if len(r) == 1 and r[0].lstrip().startswith(r"\multicolumn"):
                        mc = re.search(r"\\multicolumn\{\d+\}\{[^}]*\}\{(.*)\}\s*$", r[0], flags=re.DOTALL)
                        banner_txt = _clean_latex_cell(mc.group(1) if mc else r[0])
                        block_proto = _extract_proto_tag(banner_txt)
                        block_metric = _classify_metric_hint(_norm_descriptor(banner_txt))
                        pending_header_rows = []
                    else:
                        pending_header_rows.append(_expand_header_row(r))
                continue

            if pending_header_rows:
                max_h_cols = max(len(hr) for hr in pending_header_rows)
                active_col_headers = [[] for _ in range(max_h_cols)]
                for hr in pending_header_rows:
                    for c_idx, htxt in enumerate(hr):
                        if htxt and (not active_col_headers[c_idx] or active_col_headers[c_idx][-1] != htxt):
                            active_col_headers[c_idx].append(htxt)
                pending_header_rows = []

            max_cols = max([len(active_col_headers), *(len(r) for r in seg_rows)] or [0])
            while len(active_col_headers) < max_cols:
                active_col_headers.append([])

            leaf_counts: dict[str, int] = {}
            for ch_stack in active_col_headers:
                if ch_stack:
                    ln = _norm_descriptor(ch_stack[-1])
                    if ln:
                        leaf_counts[ln] = leaf_counts.get(ln, 0) + 1

            multirow_carry: dict[int, list[Any]] = {}
            for drow in seg_rows:
                if not _row_has_decimal_metric(drow):
                    if len(drow) == 1 and drow[0].lstrip().startswith(r"\multicolumn"):
                        mc = re.search(r"\\multicolumn\{\d+\}\{[^}]*\}\{(.*)\}\s*$", drow[0], flags=re.DOTALL)
                        banner_txt = _clean_latex_cell(mc.group(1) if mc else drow[0])
                        block_proto = _extract_proto_tag(banner_txt)
                    continue

                expanded_drow: list[str] = []
                for raw_c in drow:
                    mc = re.search(r"\\multicolumn\{(\d+)\}\{[^}]*\}\{(.*)\}\s*$", raw_c, flags=re.DOTALL)
                    if mc:
                        span = max(1, int(mc.group(1)))
                        expanded_drow.extend([mc.group(2)] * span)
                    else:
                        expanded_drow.append(raw_c)

                cleaned_row: list[str] = []
                for c_idx in range(max(len(expanded_drow), max_cols)):
                    raw_val = expanded_drow[c_idx] if c_idx < len(expanded_drow) else ""
                    mr = re.search(r"\\multirow\{(\d+)\}\{[^}]*\}\{(.*)\}\s*$", raw_val, flags=re.DOTALL)
                    if mr:
                        span_r = max(1, int(mr.group(1)))
                        txt_r = _clean_latex_cell(mr.group(2))
                        if span_r > 1:
                            multirow_carry[c_idx] = [span_r - 1, txt_r]
                        cleaned_row.append(txt_r)
                    else:
                        c_txt = _clean_latex_cell(raw_val)
                        if not c_txt and c_idx in multirow_carry and multirow_carry[c_idx][0] > 0:
                            c_txt = multirow_carry[c_idx][1]
                            multirow_carry[c_idx][0] -= 1
                        cleaned_row.append(c_txt)

                # Leading non-numeric columns before the first decimal metric are the row's entity descriptors
                first_metric_col = next((idx for idx, v in enumerate(cleaned_row) if METRIC_CELL_RE.match(v)), len(cleaned_row))
                row_descriptors: list[str] = []
                row_proto_parts: list[str] = []
                for c_idx in range(first_metric_col):
                    val_txt = cleaned_row[c_idx]
                    if not val_txt or re.match(r"^[+-]?\d+(?:\.\d+)?%?$", val_txt) or val_txt in {"-", "--", "—", "N/A", "n/a"}:
                        continue
                    hdr_norm = _norm_descriptor(" ".join(active_col_headers[c_idx])) if c_idx < len(active_col_headers) else ""
                    if hdr_norm in SKIP_INDEX_HEADERS or any(w in hdr_norm.split() for w in ("sites", "voxels", "samples", "params", "channels")):
                        continue
                    row_descriptors.append(val_txt)
                    p = _extract_proto_tag(val_txt)
                    if p != "canonical":
                        row_proto_parts.append(p)

                for c_idx, val_txt in enumerate(cleaned_row):
                    mm = METRIC_CELL_RE.match(val_txt)
                    if not mm:
                        continue
                    col_stack = active_col_headers[c_idx] if c_idx < len(active_col_headers) else []
                    hdr_raw = " ".join(col_stack)
                    hdr_norm_full = _norm_descriptor(hdr_raw)
                    if hdr_norm_full in SKIP_INDEX_HEADERS or any(w in hdr_norm_full.split() for w in ("sites", "voxels", "samples", "params")):
                        continue

                    num_str = mm.group(1)
                    val_float = float(num_str)
                    dec_places = len(num_str.split(".")[1]) if "." in num_str else 0

                    col_proto = _extract_proto_tag(hdr_raw)
                    proto_candidates = [p for p in [table_proto, block_proto, col_proto, *row_proto_parts] if p != "canonical"]
                    effective_proto = "+".join(sorted(set(proto_candidates))) if proto_candidates else "canonical"

                    # Use leaf column header unless the leaf header repeats across multiple columns in this block
                    if col_stack:
                        leaf_norm = _norm_descriptor(col_stack[-1])
                        chosen_col_pieces = col_stack if leaf_counts.get(leaf_norm, 0) > 1 else [col_stack[-1]]
                    else:
                        chosen_col_pieces = []

                    entities: set[str] = set()
                    metric_hints: list[str] = []
                    for raw_piece in [*row_descriptors, *chosen_col_pieces]:
                        nd = _norm_descriptor(raw_piece)
                        if not nd or nd in GENERIC_ROLE_HEADERS or nd in SKIP_INDEX_HEADERS:
                            continue
                        mh = _classify_metric_hint(nd)
                        if mh:
                            metric_hints.append(mh)
                            rem = re.sub(
                                r"\b(?:test|val|validation|train|mean|avg|average|pooled|score|scores|r\s*2|r2|rsq|acc|accuracy|top\s*1|top\s*5|ppl|perplexity|latency|runtime|time|ms|gb|mb|s|f1|auc|auroc|recall|precision|loss|nll|rmse|mse|mae|corr)\b",
                                " ",
                                nd,
                            )
                            rem = re.sub(r"\s+", " ", rem).strip()
                            if len(rem) >= 2 and rem not in GENERIC_ROLE_HEADERS:
                                entities.add(rem)
                        else:
                            entities.add(nd)

                    if len(entities) >= 2:
                        out_cells.append(
                            {
                                "table_label": table_rec["label"],
                                "proto": effective_proto,
                                "entities": frozenset(entities),
                                "metric_hint": metric_hints[-1] if metric_hints else (block_metric or table_caption_metric),
                                "value": val_float,
                                "decimals": dec_places,
                                "raw": num_str,
                            }
                        )
    return out_cells


def lint_cross_table_consistency(declared_tables: list[dict[str, Any]]) -> list[dict[str, Any]]:
    per_table_cells: list[list[dict[str, Any]]] = [extract_table_metric_cells(t) for t in declared_tables]
    # Count how many cells share `(proto, entities)` inside each table to know if metric_hint disambiguation is required
    entity_mult_per_table: list[dict[tuple[str, frozenset[str]], int]] = []
    for cells in per_table_cells:
        counts: dict[tuple[str, frozenset[str]], int] = {}
        for c in cells:
            k = (c["proto"], c["entities"])
            counts[k] = counts.get(k, 0) + 1
        entity_mult_per_table.append(counts)

    conflicts: list[dict[str, Any]] = []
    seen_pairs: set[tuple[str, str, tuple[str, ...], str]] = set()

    for i in range(len(per_table_cells)):
        for j in range(i + 1, len(per_table_cells)):
            for c1 in per_table_cells[i]:
                for c2 in per_table_cells[j]:
                    if c1["proto"] != c2["proto"] or c1["entities"] != c2["entities"]:
                        continue
                    m1, m2 = c1["metric_hint"], c2["metric_hint"]
                    if m1 and m2:
                        if m1 != m2:
                            continue
                    elif m1 or m2:
                        # One side lacks an explicit metric header; safe to match iff neither table has >1 metric column for these entities
                        if (
                            entity_mult_per_table[i][(c1["proto"], c1["entities"])] > 1
                            or entity_mult_per_table[j][(c2["proto"], c2["entities"])] > 1
                        ):
                            continue

                    min_dec = min(c1["decimals"], c2["decimals"])
                    tol = 0.500001 * (10.0 ** (-min_dec))
                    diff = abs(c1["value"] - c2["value"])
                    if diff > tol:
                        ent_tuple = tuple(sorted(c1["entities"]))
                        pair_sig = (c1["table_label"], c2["table_label"], ent_tuple, m1 or m2)
                        if pair_sig not in seen_pairs:
                            seen_pairs.add(pair_sig)
                            conflicts.append(
                                {
                                    "table_a": c1["table_label"],
                                    "table_b": c2["table_label"],
                                    "protocol": c1["proto"],
                                    "shared_entities": list(ent_tuple),
                                    "metric": m1 or m2 or "(implicit)",
                                    "value_a": c1["raw"],
                                    "value_b": c2["raw"],
                                    "abs_diff": round(diff, 6),
                                }
                            )
    return conflicts


def lint_abstract_body_numbers(clean_tex: str, has_body: bool) -> list[dict[str, str]]:
    if not has_body:
        return []
    m = ABSTRACT_ENV_RE.search(clean_tex)
    if m:
        raw_abs = m.group(1)
        body_rest = clean_tex[: m.start()] + " " + clean_tex[m.end() :]
    else:
        bm = re.search(r"\\abstract\s*\{", clean_tex)
        if not bm:
            return []
        raw_abs = extract_balanced_braces(clean_tex, r"\\abstract\s*\{")
        body_rest = clean_tex.replace(raw_abs, " ", 1)

    abs_clean = re.sub(r"\\(?:cite\w*|ref|cref|Cref|label)(?:\[[^\]]*\])*\{[^}]*\}", " ", raw_abs)
    # Mask common significance thresholds & version numbers (e.g. p < 0.05, v2.1)
    abs_clean = re.sub(r"\b(?:p|alpha|\\alpha)\s*[<=]\s*0\.0\d+\b", " ", abs_clean, flags=re.IGNORECASE)
    abs_clean = re.sub(r"\bv\d+\.\d+\b", " ", abs_clean, flags=re.IGNORECASE)

    abs_nums = re.findall(r"(?<![A-Za-z0-9_.])([+-]?\d+\.\d+)(?![A-Za-z0-9_.])", abs_clean)
    if not abs_nums:
        return []

    body_tokens = re.findall(r"(?<![A-Za-z0-9_])([+-]?\d+(?:\.\d+)?)(?![A-Za-z0-9_])", body_rest)
    body_parsed: list[tuple[float, int]] = []
    for bt in body_tokens:
        try:
            bv = float(bt)
            bd = len(bt.split(".")[1]) if "." in bt else 0
            body_parsed.append((bv, bd))
        except ValueError:
            continue

    unique_floats = sorted({bv for bv, _ in body_parsed})[:300]
    unmatched: list[dict[str, str]] = []
    seen_raw: set[str] = set()

    for raw_n in abs_nums:
        if raw_n in seen_raw:
            continue
        seen_raw.add(raw_n)
        av = float(raw_n)
        ad = len(raw_n.split(".")[1])
        tol_a = 0.55 * (10.0 ** (-ad))

        matched = False
        for bv, bd in body_parsed:
            tol_pair = 0.500001 * (10.0 ** (-min(ad, bd))) if bd > 0 else tol_a
            if (
                abs(av - bv) <= tol_pair
                or abs(abs(av) - abs(bv)) <= tol_pair
                or abs(av - 100.0 * bv) <= tol_a
                or abs(av / 100.0 - bv) <= tol_a / 100.0
            ):
                matched = True
                break

        if not matched and len(unique_floats) <= 300:
            for idx_a, x in enumerate(unique_floats):
                for y in unique_floats[idx_a + 1 :]:
                    if abs(abs(y - x) - abs(av)) <= tol_a:
                        matched = True
                        break
                    if abs(x) > 1e-9 and abs(abs(y / x) - abs(av)) <= tol_a:
                        matched = True
                        break
                    if abs(y) > 1e-9 and abs(abs(x / y) - abs(av)) <= tol_a:
                        matched = True
                        break
                if matched:
                    break

        if not matched:
            unmatched.append(
                {
                    "number": raw_n,
                    "message": f"Decimal metric '{raw_n}' in Abstract does not match any number (or pairwise diff/ratio) in manuscript body or tables (check for stale multi-round numbers).",
                }
            )
    return unmatched


def lint_tex_source(tex_text: str, check_abstract: bool = True, check_consistency: bool = True) -> dict[str, Any]:
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
            "raw_body": body,
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

    # 8. Cross-Artifact Numeric & Protocol Consistency
    has_body = bool(sections_index or declared_figures or declared_tables)
    cross_table_conflicts = lint_cross_table_consistency(declared_tables) if check_consistency else []
    abstract_unmatched_numbers = lint_abstract_body_numbers(clean_tex, has_body) if check_consistency else []

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
            "cross_table_conflicts": len(cross_table_conflicts),
            "abstract_unmatched_numbers": len(abstract_unmatched_numbers),
        },
        "clean": not (
            orphan_visuals
            or out_of_order
            or undefined_visual_refs
            or pointer_sentences
            or weak_captions
            or abstract_warnings
            or cross_table_conflicts
            or abstract_unmatched_numbers
        ),
        "visual_inventory": visual_inventory,
        "cross_table_conflicts": cross_table_conflicts,
        "abstract_unmatched_numbers": abstract_unmatched_numbers,
        "orphan_visuals": orphan_visuals,
        "out_of_order_callouts": out_of_order,
        "undefined_visual_refs": undefined_visual_refs,
        "pointer_topic_sentences": pointer_sentences[:25],
        "weak_descriptive_figure_captions": weak_captions,
        "abstract_narrative": abstract_info,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Audit LaTeX prose <-> figure/table callouts, ordering, captions, Abstract ABT/AAA/DHY narrative, and Cross-Table/Abstract numeric consistency."
    )
    parser.add_argument("target", help="Path to root main.tex file or manuscript directory")
    parser.add_argument("--no-abstract-lint", action="store_true", help="Skip Abstract AAA/DHY narrative spectrum checks")
    parser.add_argument("--no-consistency-lint", action="store_true", help="Skip cross-table and abstract-body numeric consistency checks")
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

    report = lint_tex_source(
        full_tex,
        check_abstract=not args.no_abstract_lint,
        check_consistency=not args.no_consistency_lint,
    )
    out_str = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        Path(args.output).expanduser().write_text(out_str, encoding="utf-8")
    else:
        sys.stdout.write(out_str)


if __name__ == "__main__":
    main()
