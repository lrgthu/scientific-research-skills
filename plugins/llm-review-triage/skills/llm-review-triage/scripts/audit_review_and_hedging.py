#!/usr/bin/env python3
r"""Audits LLM-review triage ledgers and guards manuscript diffs against defensive hedging.

Provides two deterministic, zero-dependency subcommands:
1. `init-ledger` / `summarize-ledger`: Validates Area-Chair review triage ledgers,
   flags multi-round contractive drift and unfiltered appeasement, and renders a
   Markdown decision brief.
2. `diff-audit`: Compares `before` and `after` manuscript drafts (.tex / .md,
   English & Chinese) to catch stacked qualifier chains, reviewer-appeasement scar
   tissue, Abstract hook dilution, and word-count bloat.
"""

# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

from __future__ import annotations

import argparse
from collections.abc import Mapping, Sequence
import difflib
import json
import pathlib
import re
import sys
from typing import Any

VALID_BUCKETS = frozenset({
    "DO_NOW_SUBSTANCE",
    "CLARIFY_STRUCTURALLY",
    "IGNORE_LIMITATION_BOOMERANG",
    "IGNORE_OVERTHINKING_OR_HEDGE",
})

ACCEPTED_BUCKETS = frozenset({"DO_NOW_SUBSTANCE", "CLARIFY_STRUCTURALLY"})

EN_HEDGE_RE = re.compile(
    r"\b(?:may|might|could|perhaps|possibly|potentially|somewhat|preliminar(?:y|ily)|"
    r"arguably|tentatively|modestly|conceivably|appear(?:s)?\s+to|seem(?:s)?\s+to|"
    r"tend(?:s)?\s+to|to\s+(?:some|a\s+certain)\s+extent|"
    r"under\s+certain\s+(?:specific\s+|constrained\s+)?(?:conditions|settings|regimes|configurations))\b",
    re.IGNORECASE,
)

ZH_HEDGE_RE = re.compile(
    r"(?:在(?:一定|某种)(?:程度|意义|范围)上|在(?:部分)?特定(?:受限)?(?:实验)?(?:条件|设定|配置|场景)下|"
    r"或许|可能|似乎|有望|初步(?:暗示|表明|显示)?|较为有效)"
)

SCAR_TISSUE_RE = re.compile(
    r"(?:\bit\s+(?:is\s+worth\s+noting|should\s+be\s+noted|is\s+important\s+to\s+note)\s+that\b|"
    r"\bto\s+address\s+potential\s+concerns\b|"
    r"\bnot\s+a\s+(?:silver\s+bullet|panacea)\b|"
    r"\bdo\s+not\s+claim\s+universal\s+superiority\b|"
    r"值得注意的是|需要指出的是|应当指出的是|为了回应潜在的(?:顾虑|质疑)|并非万能)",
    re.IGNORECASE,
)

DEFENSIVE_PLAN_RE = re.compile(
    r"(?:\b(?:soften|tone\s+down|water\s+down|add\s+qualifiers|add\s+hedges)\b|"
    r"弱化(?:表述|结论)|加(?:上|入)?限定词|降低调门)",
    re.IGNORECASE,
)

ABSTRACT_TEX_RE = re.compile(
    r"\\begin\{abstract\}(.*?)\\end\{abstract\}", re.DOTALL | re.IGNORECASE
)
ABSTRACT_MD_RE = re.compile(
    r"(?:^|\n)#+\s*(?:Abstract|摘要)\s*\n(.*?)(?=\n#+\s|\Z)",
    re.DOTALL | re.IGNORECASE,
)

_STARTER_LEDGER: dict[str, Any] = {
    "manuscript_title": "Replace with your manuscript title",
    "soul_anchor": {
        "core_thesis_kabt": (
            "Score-accumulating KV eviction drops dormant multi-hop bridge keys [BUT]; "
            "streaming rank-r residual sketching recovers 99% recall at fixed memory [THEREFORE]."
        ),
        "paper_archetype": "algorithmic_mechanism",
        "disclosed_limitations": [
            "Section 6 (Limitations): Evaluated on 7B-14B causal decoders up to 128k tokens; multimodal vision-language KV caches are left to future work."
        ],
        "round_index": 1,
    },
    "comments": [
        {
            "id": "C1",
            "source_model": "Frontier-LRM-A",
            "summary": "Compare against an iso-byte INT4 KV quantization baseline at matched 20% memory budget.",
            "bucket": "DO_NOW_SUBSTANCE",
            "pathology_tag": "NONE",
            "objective_bug": False,
            "rationale": "High-ROI control ruling out rival hypothesis H2 (uniform precision compression vs. subspace sketching).",
            "planned_action": "Run INT4 KV baseline on the 200-sample 2-hop RULER slice (~1.5 GPU-hours) and add row to Table 1.",
        },
        {
            "id": "C2",
            "source_model": "Frontier-LRM-A",
            "summary": "The paper fails to evaluate 70B+ models or multimodal video-LLM caches.",
            "bucket": "IGNORE_LIMITATION_BOOMERANG",
            "pathology_tag": "LIMITATION_BOOMERANG",
            "objective_bug": False,
            "rationale": "Already explicitly bounded in Section 6; claims in Abstract/Intro are scoped to 7B-14B text decoders.",
            "planned_action": "None (0 edits).",
        },
        {
            "id": "C3",
            "source_model": "Frontier-LRM-B",
            "summary": "Claims in the Abstract are too strong; replace 'recovers 99.1% recall' with 'may preliminarily help mitigate recall loss under certain configurations'.",
            "bucket": "IGNORE_OVERTHINKING_OR_HEDGE",
            "pathology_tag": "DEFENSIVE_HEDGING_TRAP",
            "objective_bug": False,
            "rationale": "99.1% is an exact empirical measurement on the stated benchmark; adding stacked hedges destroys clarity.",
            "planned_action": "Keep exact numeric claim scoped by 'Across 7B-14B decoders up to 128k tokens'.",
        },
    ],
}


def strip_comments(text: str) -> str:
    """Strips unescaped LaTeX `%` comments for prose measurement."""
    lines: list[str] = []
    for raw in text.splitlines():
        cleaned = re.sub(r"(?<!\\)%.*$", "", raw)
        lines.append(cleaned)
    return "\n".join(lines)


def count_units(text: str) -> int:
    """Counts English words plus CJK characters for bilingual density metrics."""
    en_words = len(re.findall(r"[A-Za-z0-9_]+", text))
    cjk_chars = len(re.findall(r"[\u4e00-\u9fff]", text))
    return max(1, en_words + cjk_chars)


def count_hedges(text: str) -> int:
    """Counts total English and Chinese epistemic hedge matches in text."""
    return len(EN_HEDGE_RE.findall(text)) + len(ZH_HEDGE_RE.findall(text))


def extract_abstract(text: str) -> str:
    """Extracts LaTeX or Markdown abstract text if present."""
    tex_match = ABSTRACT_TEX_RE.search(text)
    if tex_match:
        return tex_match.group(1)
    md_match = ABSTRACT_MD_RE.search(text)
    return md_match.group(1) if md_match else ""


def split_clauses(line: str) -> list[str]:
    """Splits a line into sentence/clause spans for stacked-hedge detection."""
    return [seg.strip() for seg in re.split(r"[.!?;。！？；\n]+", line) if seg.strip()]


def audit_added_lines(added_lines: Sequence[tuple[int, str]]) -> list[dict[str, Any]]:
    """Scans newly added/modified lines in `after` for stacked hedges and scar tissue."""
    findings: list[dict[str, Any]] = []
    for lineno, line in added_lines:
        for clause in split_clauses(line):
            en_hits = [m.group(0) for m in EN_HEDGE_RE.finditer(clause)]
            zh_hits = [m.group(0) for m in ZH_HEDGE_RE.finditer(clause)]
            hits = en_hits + zh_hits
            if len(hits) >= 2:
                findings.append({
                    "line": lineno,
                    "severity": "ERROR",
                    "code": "STACKED_HEDGE_CHAIN",
                    "matches": hits,
                    "excerpt": clause[:160],
                    "message": (
                        f"Clause stacks {len(hits)} epistemic hedges ({', '.join(hits)}); "
                        "replace qualifier soup with an exact domain/numeric scope."
                    ),
                })
        scar = SCAR_TISSUE_RE.search(line)
        if scar:
            findings.append({
                "line": lineno,
                "severity": "WARNING",
                "code": "APOLOGETIC_SCAR_TISSUE",
                "matches": [scar.group(0)],
                "excerpt": line.strip()[:160],
                "message": (
                    f"Reviewer-appeasement meta-discourse `{scar.group(0)}` disrupts "
                    "reader flow; state facts directly or confine boundaries to Limitations."
                ),
            })
    return findings


def _macro_diff_warnings(
    clean_before: str,
    clean_after: str,
    units_before: int,
    units_after: int,
    density_before: float,
    density_after: float,
) -> list[dict[str, Any]]:
    """Checks document-level hedge surges, abstract dilution, and prose bloat."""
    warnings: list[dict[str, Any]] = []
    density_delta = round(density_after - density_before, 3)
    length_growth_pct = round(100.0 * (units_after - units_before) / units_before, 2)

    if units_after >= 80 and density_delta > 0.40:
        warnings.append({
            "line": 1,
            "severity": "WARNING",
            "code": "HEDGE_DENSITY_SURGE",
            "matches": [],
            "excerpt": "",
            "message": (
                f"Overall hedge density jumped by +{density_delta:.2f} per 100 units "
                f"({density_before:.2f} -> {density_after:.2f}); check for defensive over-editing."
            ),
        })

    abs_before = extract_abstract(clean_before)
    abs_after = extract_abstract(clean_after)
    if abs_after and count_hedges(abs_after) > count_hedges(abs_before):
        warnings.append({
            "line": 1,
            "severity": "WARNING",
            "code": "ABSTRACT_HOOK_HEDGED",
            "matches": [],
            "excerpt": abs_after.strip()[:160],
            "message": (
                "Revision injected new epistemic hedges into the Abstract; keep Abstract "
                "claims crisp and scope via concrete nouns/numbers instead."
            ),
        })

    if units_before >= 250 and length_growth_pct > 12.0:
        warnings.append({
            "line": 1,
            "severity": "WARNING",
            "code": "PROSE_BLOAT_SURGE",
            "matches": [],
            "excerpt": "",
            "message": (
                f"Manuscript grew by +{length_growth_pct:.1f}% ({units_before} -> {units_after} units); "
                "verify edits did not bolt on defensive patch paragraphs."
            ),
        })
    return warnings


def run_diff_audit(before_text: str, after_text: str) -> dict[str, Any]:
    """Compares `before` and `after` drafts for hedging surges and soul dilution."""
    clean_before = strip_comments(before_text)
    clean_after = strip_comments(after_text)

    units_before = count_units(clean_before)
    units_after = count_units(clean_after)
    hedges_before = count_hedges(clean_before)
    hedges_after = count_hedges(clean_after)
    density_before = round(100.0 * hedges_before / units_before, 3)
    density_after = round(100.0 * hedges_after / units_after, 3)
    density_delta = round(density_after - density_before, 3)
    length_growth_pct = round(100.0 * (units_after - units_before) / units_before, 2)

    before_lines_set = {ln.strip() for ln in clean_before.splitlines() if ln.strip()}
    added_lines = [
        (idx, raw_ln.strip())
        for idx, raw_ln in enumerate(clean_after.splitlines(), start=1)
        if raw_ln.strip() and raw_ln.strip() not in before_lines_set
    ]

    findings = audit_added_lines(added_lines)
    findings.extend(
        _macro_diff_warnings(
            clean_before,
            clean_after,
            units_before,
            units_after,
            density_before,
            density_after,
        )
    )

    unified_preview = list(
        difflib.unified_diff(
            clean_before.splitlines(),
            clean_after.splitlines(),
            fromfile="before",
            tofile="after",
            lineterm="",
            n=1,
        )
    )[:40]

    errors = sum(1 for f in findings if f["severity"] == "ERROR")
    warnings = sum(1 for f in findings if f["severity"] == "WARNING")
    return {
        "clean": errors == 0 and warnings == 0,
        "metrics": {
            "units_before": units_before,
            "units_after": units_after,
            "length_growth_pct": length_growth_pct,
            "hedges_before": hedges_before,
            "hedges_after": hedges_after,
            "hedge_density_per_100_before": density_before,
            "hedge_density_per_100_after": density_after,
            "hedge_density_delta": density_delta,
        },
        "counts": {"errors": errors, "warnings": warnings},
        "findings": findings,
        "diff_preview": unified_preview,
    }


def _audit_single_comment(
    item: Mapping[str, Any], round_idx: int, by_bucket: dict[str, int]
) -> list[dict[str, str]]:
    """Validates one triaged review comment entry."""
    issues: list[dict[str, str]] = []
    cid = str(item.get("id") or "unnamed")
    bucket = str(item.get("bucket") or "")
    if bucket not in VALID_BUCKETS:
        issues.append({
            "severity": "ERROR",
            "code": "INVALID_BUCKET",
            "message": f"Comment `{cid}` has invalid bucket `{bucket}`.",
        })
    else:
        by_bucket[bucket] += 1

    plan = str(item.get("planned_action") or "")
    if bucket in ACCEPTED_BUCKETS and DEFENSIVE_PLAN_RE.search(plan):
        issues.append({
            "severity": "ERROR",
            "code": "DEFENSIVE_ACTION_PLAN",
            "message": f"Accepted comment `{cid}` plans to soften/add qualifiers (`{plan}`); scope by exact domain noun/number instead.",
        })
    if (
        round_idx >= 3
        and bucket in ACCEPTED_BUCKETS
        and not bool(item.get("objective_bug"))
    ):
        issues.append({
            "severity": "WARNING",
            "code": "ROUND_3_DRIFT_RISK",
            "message": f"Comment `{cid}` accepted in Round {round_idx} without `objective_bug=true`; halt recursive non-bug edits after Round 2.",
        })
    return issues


def summarize_triage_ledger(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Audits an Area-Chair review triage ledger for soul lock and round discipline."""
    soul = payload.get("soul_anchor") if isinstance(payload.get("soul_anchor"), Mapping) else {}
    issues: list[dict[str, str]] = []

    if len(str(soul.get("core_thesis_kabt") or "").strip()) < 25:
        issues.append({
            "severity": "ERROR",
            "code": "MISSING_SOUL_ANCHOR",
            "message": "`soul_anchor.core_thesis_kabt` must be locked before triaging comments.",
        })

    round_idx = int(soul.get("round_index") or 1)
    comments = payload.get("comments") if isinstance(payload.get("comments"), list) else []
    if not comments:
        issues.append({
            "severity": "ERROR",
            "code": "EMPTY_COMMENTS",
            "message": "Ledger contains zero review comments.",
        })

    by_bucket: dict[str, int] = {b: 0 for b in sorted(VALID_BUCKETS)}
    for item in comments:
        issues.extend(_audit_single_comment(item, round_idx, by_bucket))

    total = len(comments)
    accepted = sum(by_bucket[b] for b in ACCEPTED_BUCKETS)
    accepted_ratio = round(accepted / total, 3) if total else 0.0
    if total >= 5 and accepted_ratio > 0.45:
        issues.append({
            "severity": "WARNING",
            "code": "UNFILTERED_APPEASEMENT_RISK",
            "message": f"Accepted {accepted}/{total} ({accepted_ratio:.0%}) raw AI comments (>45%); prune low-ROI overthinking items harder.",
        })

    errors = sum(1 for i in issues if i["severity"] == "ERROR")
    warnings = sum(1 for i in issues if i["severity"] == "WARNING")
    return {
        "clean": errors == 0 and warnings == 0,
        "manuscript_title": str(payload.get("manuscript_title") or ""),
        "round_index": round_idx,
        "counts": {
            "total_comments": total,
            "accepted_actions": accepted,
            "discarded_noise": total - accepted,
            "accepted_ratio": accepted_ratio,
            "by_bucket": by_bucket,
            "errors": errors,
            "warnings": warnings,
        },
        "issues": issues,
    }


def render_ledger_markdown(
    payload: Mapping[str, Any], report: Mapping[str, Any]
) -> str:
    """Renders a concise Area-Chair Triage Markdown brief for author sign-off."""
    soul = payload.get("soul_anchor") or {}
    comments = payload.get("comments") or []
    lines = [
        f"# Area-Chair LLM Review Triage Brief — {report['manuscript_title']} (Round {report['round_index']})",
        "",
        "## 1. Locked Manuscript Soul & Disclosed Scope",
        f"- **Core Thesis (`kABT`)**: {soul.get('core_thesis_kabt', '')}",
        f"- **Paper Archetype**: `{soul.get('paper_archetype', '')}`",
        f"- **Already-Disclosed Limitations**: {'; '.join(str(x) for x in (soul.get('disclosed_limitations') or []))}",
        "",
        "## 2. Worthwhile High-Leverage Actions (`DO NOW` & `CLARIFY ONCE`)",
        "",
        "| ID | Bucket | Comment Summary | Surgical Non-Defensive Action |",
        "| :--- | :--- | :--- | :--- |",
    ]
    for item in comments:
        if item.get("bucket") in ACCEPTED_BUCKETS:
            lines.append(
                f"| `{item.get('id')}` | `{item.get('bucket')}` | "
                f"{item.get('summary', '')} | {item.get('planned_action', '')} |"
            )

    lines.extend([
        "",
        "## 3. Discarded AI Reviewer Noise (`0` Manuscript Edits)",
        "",
        "| ID | Tag | Comment Summary | Why Safe to Ignore |",
        "| :--- | :--- | :--- | :--- |",
    ])
    for item in comments:
        if item.get("bucket") not in ACCEPTED_BUCKETS:
            lines.append(
                f"| `{item.get('id')}` | `{item.get('pathology_tag', item.get('bucket'))}` | "
                f"{item.get('summary', '')} | {item.get('rationale', '')} |"
            )
    lines.append("")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    """Builds the CLI argument parser."""
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init-ledger", help="Write a starter triage JSON ledger.")
    p_init.add_argument("output_json", type=pathlib.Path)

    p_sum = sub.add_parser("summarize-ledger", help="Validate and render triage ledger.")
    p_sum.add_argument("ledger_json", type=pathlib.Path)
    p_sum.add_argument("--output", "-o", type=pathlib.Path, default=None)
    p_sum.add_argument("--markdown-out", type=pathlib.Path, default=None)
    p_sum.add_argument("--strict", action="store_true")

    p_diff = sub.add_parser("diff-audit", help="Audit before/after draft diff for hedging.")
    p_diff.add_argument("before_file", type=pathlib.Path)
    p_diff.add_argument("after_file", type=pathlib.Path)
    p_diff.add_argument("--output", "-o", type=pathlib.Path, default=None)
    p_diff.add_argument("--strict", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entrypoint."""
    args = build_parser().parse_args(argv)
    if args.command == "init-ledger":
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        with args.output_json.open("w", encoding="utf-8") as handle:
            json.dump(_STARTER_LEDGER, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
        sys.stdout.write(f"Wrote starter ledger -> {args.output_json}\n")
        return 0

    if args.command == "summarize-ledger":
        with args.ledger_json.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        report = summarize_triage_ledger(payload)
        if args.markdown_out is not None:
            args.markdown_out.parent.mkdir(parents=True, exist_ok=True)
            with args.markdown_out.open("w", encoding="utf-8") as handle:
                handle.write(render_ledger_markdown(payload, report))
    else:
        before_txt = args.before_file.read_text(encoding="utf-8")
        after_txt = args.after_file.read_text(encoding="utf-8")
        report = run_diff_audit(before_txt, after_txt)

    out_json = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", encoding="utf-8") as handle:
            handle.write(out_json)
    sys.stdout.write(out_json)
    if args.strict and not report["clean"]:
        return 1
    return 1 if report["counts"]["errors"] > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
