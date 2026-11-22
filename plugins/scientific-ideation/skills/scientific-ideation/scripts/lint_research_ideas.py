#!/usr/bin/env python3
r"""Validates, stress-tests, and Pareto-ranks structured research idea portfolios.

Operationalizes Stage-0 scientific ideation checks synthesized from:
- John R. Platt (1964), "Strong Inference" (10.1126/science.146.3642.347)
- Richard W. Hamming (1986), "You and Your Research"
- Uri Alon (2009), "How To Choose a Good Scientific Problem" (10.1016/j.molcel.2009.09.013)
- Lipton & Steinhardt (2018), "Troubling Trends in ML Scholarship" (arXiv:1807.03341)
- Si, Yang & Hashimoto (2025), "Can LLMs Generate Novel Research Ideas?" (arXiv:2409.04109)
"""

# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

from __future__ import annotations

import argparse
from collections.abc import Mapping, Sequence
import json
import pathlib
import re
import sys
from typing import Any

VALID_ARCHETYPES = frozenset({
    "algorithmic_mechanism",
    "diagnostic_refutation",
    "benchmark_audit",
    "exact_simplification",
    "scaling_or_boundary_law",
    "systems_or_regime_shift",
})

PRIOR_ART_ID_RE = re.compile(
    r"(?:arxiv:\s*\d{4}\.\d{4,5}|10\.\d{4,9}/\S+|doi:\s*10\.\d{4,9}/\S+|"
    r"openreview\.net/forum\?id=[A-Za-z0-9_-]+|^W\d{6,}$)",
    re.IGNORECASE,
)

ABT_CONTRAST_RE = re.compile(
    r"\b(?:but|however|whereas|yet|although|despite|fails?|breaks?|collapses?|"
    r"degrades?|suffers?|bottleneck|violates?|ignores?)\b|但是|然而|却|失效|崩溃|瓶颈",
    re.IGNORECASE,
)

BUZZWORD_SLOP_RE = re.compile(
    r"\b(?:consciousness|sentient|quantum\s+resonance|semantic\s+resonance|"
    r"pivot\s+constellation|thought\s+lattice|thought\s+vector|"
    r"cognitive\s+synergy|holistic\s+synergy|paradigm[- ]shifting|"
    r"soul|telepathy|magic(?:al)?)\b",
    re.IGNORECASE,
)

STOPWORDS = frozenset({
    "the",
    "and",
    "for",
    "with",
    "from",
    "that",
    "this",
    "into",
    "using",
    "via",
    "over",
    "under",
    "through",
    "across",
    "model",
    "models",
    "method",
    "methods",
    "based",
    "novel",
    "improve",
    "improving",
})

SCORE_KEYS = ("knowledge_gain", "feasibility", "attack_clarity", "scoop_safety")

_STARTER_TEMPLATE: dict[str, Any] = {
    "topic": "Replace with your concrete research topic or observed bottleneck",
    "constraints": {
        "compute_budget": "Local prototyping + 1x GPU (<= 24h per full run)",
        "max_crucial_test_hours": 4.0,
        "target_venue": "ICLR / NeurIPS / ICML",
    },
    "candidates": [
        {
            "id": "idea_1_mechanism",
            "title": "Subspace-Preserving Key Sketching for Multi-Hop Retrieval",
            "archetype": "algorithmic_mechanism",
            "c_abt": (
                "Attention-score KV eviction preserves single-hop perplexity [AND], "
                "but multi-hop reasoning queries keys that stay dormant during early "
                "hops and get prematurely evicted [BUT]; therefore we maintain a "
                "streaming Frequent-Directions residual sketch of evicted keys at "
                "matched byte budget [THEREFORE]."
            ),
            "attack_vector": (
                "Layerwise key matrices exhibit rapid singular-value decay while "
                "hard eviction zeroes out low-score orthogonal directions."
            ),
            "competing_hypotheses": [
                "H1 (Dormant Subspace Loss): Recall drops because evicted tokens carry unique key directions queried only at hop >= 2.",
                "H2 (Logit Entropy Dilution): Recall drops from softmax denominator growth even when exact keys remain in cache.",
            ],
            "proposed_operator": (
                "Retain top-k heavy-hitter tokens plus a rank-r Frequent-Directions "
                "sketch K_sketch in R^{r x d_k} of evicted keys with log-mass correction."
            ),
            "compute_matched_baseline": (
                "SnapKV / H2O heavy-hitter eviction and uniform INT4 KV quantization "
                "at identical total bytes per token."
            ),
            "verified_prior_art": ["arXiv:2306.14048", "arXiv:2404.14469"],
            "crucial_experiment": {
                "setup": "200-sample 2-hop synthetic needle + RULER slice at 32k tokens.",
                "metric": "Exact 2-hop recall at 20% KV byte budget vs. decode latency.",
                "kill_condition": (
                    "Falsify H1 if exact SVD rank-32 residual oracle improves 2-hop "
                    "recall by < 5 percentage points over INT4 KV quantization."
                ),
                "estimated_hours": 2.0,
            },
            "cloud_pivot_plan": (
                "If oracle rank-32 SVD fails (< 5 pp gain), H1 is refuted in favor of "
                "H2; pivot to a diagnostic study of head-wise softmax dilution."
            ),
            "scores": {
                "knowledge_gain": 8.5,
                "feasibility": 8.0,
                "attack_clarity": 8.5,
                "scoop_safety": 7.5,
            },
        },
        {
            "id": "idea_2_diagnostic",
            "title": "Disentangling Eviction Loss from Length-Induced Entropy Dilution",
            "archetype": "diagnostic_refutation",
            "c_abt": (
                "Recent KV-compression benchmarks attribute long-context multi-hop "
                "failures to token eviction [AND], but full-cache baselines also "
                "degrade sharply when distractor entropy increases [BUT]; therefore "
                "we isolate eviction error from attention-temperature dilution via "
                "controlled counterfactual interventions [THEREFORE]."
            ),
            "attack_vector": (
                "Exact counterfactual cache injection separates missing-key errors "
                "from attention-score calibration errors without retraining."
            ),
            "competing_hypotheses": [
                "H1 (Calibration Bottleneck): Injecting ground-truth bridge tokens into evicted caches still fails without position-aware temperature scaling.",
                "H2 (Pure Eviction Bottleneck): Restoring bridge tokens alone recovers >= 95% of short-context accuracy.",
            ],
            "proposed_operator": (
                "Counterfactual 2x2 factorial probe crossing {evicted vs. oracle-retained "
                "bridge keys} x {unit softmax vs. length-scaled softmax temperature}."
            ),
            "compute_matched_baseline": (
                "Full FP16 KV cache and Yarn/RoPE-rescaled full-cache inference."
            ),
            "verified_prior_art": ["arXiv:2306.14048", "arXiv:2309.00071"],
            "crucial_experiment": {
                "setup": "300 2-hop retrieval prompts across 4k, 16k, 32k, and 64k lengths.",
                "metric": "Factorial attribution of recall drop (%) across eviction vs. dilution.",
                "kill_condition": (
                    "Falsify H1 if oracle-retained bridge keys alone recover >= 95% "
                    "accuracy at 64k without temperature rescaling."
                ),
                "estimated_hours": 1.5,
            },
            "cloud_pivot_plan": (
                "If bridge-key retention recovers >= 95% accuracy, use that exact "
                "oracle upper bound to train a lightweight bridge-key predictor."
            ),
            "scores": {
                "knowledge_gain": 8.0,
                "feasibility": 9.0,
                "attack_clarity": 9.0,
                "scoop_safety": 8.0,
            },
        },
    ],
}


def content_tokens(text: str) -> set[str]:
    """Extracts normalized content tokens (>=3 chars) for similarity checks."""
    words = re.findall(r"[a-z0-9]{3,}", text.lower())
    return {w for w in words if w not in STOPWORDS}


def validate_scores(
    raw_scores: Mapping[str, Any], cid: str
) -> tuple[dict[str, float], list[dict[str, str]]]:
    """Validates 1-10 numeric scores using NaN-safe range checks."""
    clean: dict[str, float] = {}
    issues: list[dict[str, str]] = []
    for key in SCORE_KEYS:
        val = raw_scores.get(key)
        if not isinstance(val, (int, float)) or isinstance(val, bool):
            issues.append({
                "candidate_id": cid,
                "severity": "ERROR",
                "code": "INVALID_SCORE",
                "message": f"Missing or non-numeric score `{key}` (expected 1.0..10.0).",
            })
            clean[key] = 0.0
            continue
        fval = float(val)
        if not 1.0 <= fval <= 10.0:
            issues.append({
                "candidate_id": cid,
                "severity": "ERROR",
                "code": "INVALID_SCORE",
                "message": f"Score `{key}={val!r}` outside [1.0, 10.0] (or NaN).",
            })
            clean[key] = 0.0
        else:
            clean[key] = fval
    return clean, issues


def _audit_candidate_core(cand: Mapping[str, Any], cid: str) -> list[dict[str, str]]:
    """Checks archetype, cABT contrast, competing hypotheses, and core fields."""
    issues: list[dict[str, str]] = []
    archetype = str(cand.get("archetype") or "").strip()
    if archetype not in VALID_ARCHETYPES:
        issues.append({
            "candidate_id": cid,
            "severity": "WARNING",
            "code": "UNKNOWN_ARCHETYPE",
            "message": f"Archetype `{archetype}` not in {sorted(VALID_ARCHETYPES)}.",
        })

    c_abt = str(cand.get("c_abt") or "").strip()
    if len(c_abt) < 40 or not ABT_CONTRAST_RE.search(c_abt):
        issues.append({
            "candidate_id": cid,
            "severity": "ERROR",
            "code": "MISSING_ABT_CONTRADICTION",
            "message": "`c_abt` lacks a sharp bottleneck contrast (`but`/`however`/`fails`); avoid flat AAA descriptions.",
        })

    hyps = cand.get("competing_hypotheses")
    if not isinstance(hyps, list) or len([h for h in hyps if str(h).strip()]) < 2:
        issues.append({
            "candidate_id": cid,
            "severity": "ERROR",
            "code": "SINGLE_PET_HYPOTHESIS",
            "message": "Provide >= 2 competing hypotheses (H1 vs. H2/H0) per Platt's Strong Inference.",
        })

    for field_name in (
        "attack_vector",
        "proposed_operator",
        "compute_matched_baseline",
        "cloud_pivot_plan",
    ):
        val = str(cand.get(field_name) or "").strip()
        if len(val) < 20:
            issues.append({
                "candidate_id": cid,
                "severity": "ERROR",
                "code": "VAGUE_OR_MISSING_SPEC",
                "message": f"Field `{field_name}` is missing or too vague (<20 chars).",
            })
    return issues


def _audit_candidate_fields(
    cand: Mapping[str, Any], max_hours: float
) -> list[dict[str, str]]:
    """Checks prior-art grounding, crucial-experiment kill rules, and buzzword slop."""
    cid = str(cand.get("id") or cand.get("title") or "unnamed")
    issues = _audit_candidate_core(cand, cid)

    prior = cand.get("verified_prior_art")
    valid_refs = [
        str(item).strip()
        for item in (prior if isinstance(prior, list) else [])
        if PRIOR_ART_ID_RE.search(str(item).strip())
    ]
    if not valid_refs:
        issues.append({
            "candidate_id": cid,
            "severity": "ERROR",
            "code": "UNGROUNDED_PRIOR_ART",
            "message": "`verified_prior_art` must cite >= 1 verified arXiv/DOI/OpenAlex/OpenReview ID from a live scoop check.",
        })

    crucial = cand.get("crucial_experiment")
    if not isinstance(crucial, Mapping):
        issues.append({
            "candidate_id": cid,
            "severity": "ERROR",
            "code": "MISSING_CRUCIAL_EXPERIMENT",
            "message": "Missing `crucial_experiment` object.",
        })
    else:
        kill = str(crucial.get("kill_condition") or "").strip()
        if len(kill) < 20:
            issues.append({
                "candidate_id": cid,
                "severity": "ERROR",
                "code": "MISSING_KILL_CONDITION",
                "message": "`crucial_experiment.kill_condition` must define an explicit falsification threshold.",
            })
        hours = crucial.get("estimated_hours")
        if not isinstance(hours, (int, float)) or not 0.0 < float(hours) <= max_hours:
            issues.append({
                "candidate_id": cid,
                "severity": "WARNING",
                "code": "CRUCIAL_TEST_TOO_SLOW",
                "message": f"`estimated_hours={hours!r}` exceeds `{max_hours}h` fast-falsification budget.",
            })

    combined_text = " ".join(
        str(cand.get(k) or "") for k in ("title", "c_abt", "proposed_operator")
    )
    slop_match = BUZZWORD_SLOP_RE.search(combined_text)
    if slop_match:
        issues.append({
            "candidate_id": cid,
            "severity": "WARNING",
            "code": "ANTHROPOMORPHIC_OR_BUZZWORD_SLOP",
            "message": f"Detected anthropomorphic/buzzword term `{slop_match.group(0)}`; replace with sober mathematical/functional terminology (Lipton & Steinhardt §3.4).",
        })
    return issues


def compute_pareto_tiers(points: Sequence[tuple[float, float]]) -> list[int]:
    """Computes 1-indexed Pareto dominance tiers on (feasibility, knowledge_gain)."""
    remaining = set(range(len(points)))
    tiers = [0] * len(points)
    current_tier = 1
    while remaining:
        front: list[int] = []
        for idx in remaining:
            fx, gy = points[idx]
            dominated = any(
                other != idx
                and points[other][0] >= fx
                and points[other][1] >= gy
                and (points[other][0] > fx or points[other][1] > gy)
                for other in remaining
            )
            if not dominated:
                front.append(idx)
        for idx in front:
            tiers[idx] = current_tier
            remaining.remove(idx)
        current_tier += 1
    return tiers


def _check_portfolio_diversity(
    candidates: Sequence[Mapping[str, Any]],
) -> list[dict[str, str]]:
    """Flags archetype monoculture and high-overlap duplicate ideas (Si et al. §6.1)."""
    issues: list[dict[str, str]] = []
    if len(candidates) >= 3:
        archetypes = {str(c.get("archetype") or "") for c in candidates}
        if len(archetypes) == 1:
            issues.append({
                "candidate_id": "PORTFOLIO",
                "severity": "WARNING",
                "code": "ARCHETYPE_MONOCULTURE",
                "message": "All >=3 candidates use the exact same archetype; diversify across mechanism, diagnostic refutation, simplification, or scaling-law axes.",
            })

    token_sets = [
        (
            str(c.get("id") or f"idx_{i}"),
            content_tokens(
                f"{c.get('title', '')} {c.get('proposed_operator', '')}"
            ),
        )
        for i, c in enumerate(candidates)
    ]
    for i in range(len(token_sets)):
        id_a, set_a = token_sets[i]
        for j in range(i + 1, len(token_sets)):
            id_b, set_b = token_sets[j]
            union = set_a | set_b
            jaccard = len(set_a & set_b) / len(union) if union else 0.0
            if jaccard >= 0.50:
                issues.append({
                    "candidate_id": f"{id_a} vs {id_b}",
                    "severity": "WARNING",
                    "code": "DUPLICATE_IDEA_PAIR",
                    "message": f"High lexical overlap (Jaccard={jaccard:.2f} >= 0.50); enforce orthogonal candidate mechanisms.",
                })
    return issues


def _build_ranked_entries(
    raw_cands: Sequence[Mapping[str, Any]],
    parsed_scores: Sequence[dict[str, float]],
    tiers: Sequence[int],
) -> list[dict[str, Any]]:
    """Builds Pareto-sorted candidate summary records."""
    ranked: list[dict[str, Any]] = []
    for idx, (cand, sdict, tier) in enumerate(zip(raw_cands, parsed_scores, tiers)):
        composite = round(
            0.35 * sdict["knowledge_gain"]
            + 0.30 * sdict["feasibility"]
            + 0.20 * sdict["attack_clarity"]
            + 0.15 * sdict["scoop_safety"],
            2,
        )
        crucial = cand.get("crucial_experiment") or {}
        ranked.append({
            "id": str(cand.get("id") or f"idea_{idx + 1}"),
            "title": str(cand.get("title") or ""),
            "archetype": str(cand.get("archetype") or ""),
            "pareto_tier": tier,
            "is_pareto_optimal": tier == 1,
            "composite_score": composite,
            "scores": sdict,
            "kill_condition": str(crucial.get("kill_condition") or ""),
            "estimated_hours": crucial.get("estimated_hours"),
            "cloud_pivot_plan": str(cand.get("cloud_pivot_plan") or ""),
        })
    ranked.sort(key=lambda item: (item["pareto_tier"], -item["composite_score"]))
    return ranked


def audit_portfolio(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Audits an entire research idea portfolio and ranks candidates on Alon's Pareto front."""
    constraints = payload.get("constraints")
    max_hours = 8.0
    if isinstance(constraints, Mapping) and isinstance(
        constraints.get("max_crucial_test_hours"), (int, float)
    ):
        max_hours = float(constraints["max_crucial_test_hours"])

    raw_cands = payload.get("candidates")
    if not isinstance(raw_cands, list) or not raw_cands:
        return {
            "clean": False,
            "topic": str(payload.get("topic") or ""),
            "counts": {"candidates": 0, "errors": 1, "warnings": 0},
            "issues": [{
                "candidate_id": "PORTFOLIO",
                "severity": "ERROR",
                "code": "EMPTY_CANDIDATES",
                "message": "Portfolio must contain a non-empty `candidates` list.",
            }],
            "ranked_candidates": [],
        }

    issues: list[dict[str, str]] = []
    parsed_scores: list[dict[str, float]] = []
    for cand in raw_cands:
        cid = str(cand.get("id") or cand.get("title") or "unnamed")
        issues.extend(_audit_candidate_fields(cand, max_hours))
        sdict, s_issues = validate_scores(
            cand.get("scores") if isinstance(cand.get("scores"), Mapping) else {},
            cid,
        )
        issues.extend(s_issues)
        if 0.0 < sdict["feasibility"] <= 5.0 and 0.0 < sdict["knowledge_gain"] <= 5.0:
            issues.append({
                "candidate_id": cid,
                "severity": "WARNING",
                "code": "HARD_LOW_GAIN_TRAP",
                "message": f"Candidate sits in Alon's Hard + Low-Gain trap (feasibility={sdict['feasibility']}, gain={sdict['knowledge_gain']}); prune immediately.",
            })
        parsed_scores.append(sdict)

    issues.extend(_check_portfolio_diversity(raw_cands))
    tiers = compute_pareto_tiers([
        (s["feasibility"], s["knowledge_gain"]) for s in parsed_scores
    ])
    ranked = _build_ranked_entries(raw_cands, parsed_scores, tiers)
    errors = sum(1 for item in issues if item["severity"] == "ERROR")
    warnings = sum(1 for item in issues if item["severity"] == "WARNING")
    return {
        "clean": errors == 0 and warnings == 0,
        "topic": str(payload.get("topic") or ""),
        "counts": {
            "candidates": len(raw_cands),
            "pareto_optimal": sum(1 for r in ranked if r["is_pareto_optimal"]),
            "errors": errors,
            "warnings": warnings,
        },
        "ranked_candidates": ranked,
        "issues": issues,
    }


def render_markdown_brief(
    payload: Mapping[str, Any], report: Mapping[str, Any]
) -> str:
    """Renders a clean Markdown Murder-Board & Alon Pareto decision brief."""
    lines = [
        f"# Stage-0 Ideation & Strong Inference Brief: {report['topic']}",
        "",
        "## 1. Alon Pareto Frontier & Priority Ranking",
        "",
        "| Rank | ID | Archetype | Pareto Tier | Gain | Feasibility | Attack | Scoop Safety | Composite | Crucial Test (h) |",
        "| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |",
    ]
    for rank_idx, item in enumerate(report["ranked_candidates"], start=1):
        sc = item["scores"]
        badge = "Tier 1 (Optimal)" if item["is_pareto_optimal"] else f"Tier {item['pareto_tier']}"
        lines.append(
            f"| {rank_idx} | `{item['id']}` | `{item['archetype']}` | {badge} | "
            f"{sc['knowledge_gain']:.1f} | {sc['feasibility']:.1f} | "
            f"{sc['attack_clarity']:.1f} | {sc['scoop_safety']:.1f} | "
            f"**{item['composite_score']:.2f}** | {item['estimated_hours']} |"
        )

    cand_by_id = {
        str(c.get("id") or f"idea_{i + 1}"): c
        for i, c in enumerate(payload.get("candidates") or [])
    }
    lines.extend(["", "## 2. Strong Inference & Crucial Falsification Cards", ""])
    for item in report["ranked_candidates"]:
        raw = cand_by_id.get(item["id"], {})
        lines.extend([
            f"### `{item['id']}` — {item['title']}",
            f"- **`cABT`**: {raw.get('c_abt', '')}",
            f"- **Hamming Attack Vector**: {raw.get('attack_vector', '')}",
            f"- **Proposed Operator**: {raw.get('proposed_operator', '')}",
            f"- **Iso-Compute Baseline**: {raw.get('compute_matched_baseline', '')}",
            f"- **Competing Hypotheses**: {'; '.join(str(h) for h in (raw.get('competing_hypotheses') or []))}",
            f"- **Kill Condition (`Experimentum Crucis`)**: {item['kill_condition']}",
            f"- **Cloud Pivot ($A \\to \\text{{Cloud}} \\to C$)**: {item['cloud_pivot_plan']}",
            "",
        ])

    if report["issues"]:
        lines.extend(["## 3. Audit Findings", ""])
        for iss in report["issues"]:
            lines.append(
                f"- **[{iss['severity']}] `{iss['code']}`** (`{iss['candidate_id']}`): {iss['message']}"
            )
        lines.append("")
    return "\n".join(lines)


def parse_cli(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parses CLI arguments for lint_research_ideas."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "input_json",
        nargs="?",
        type=pathlib.Path,
        default=None,
        help="Path to candidate ideas JSON file.",
    )
    parser.add_argument(
        "--init-template",
        type=pathlib.Path,
        default=None,
        help="Write a starter candidate-ideas JSON template to this path and exit.",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=pathlib.Path,
        default=None,
        help="Optional path to save JSON audit report.",
    )
    parser.add_argument(
        "--markdown-out",
        type=pathlib.Path,
        default=None,
        help="Optional path to render Markdown Murder-Board decision brief.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return exit code 1 if any ERROR or WARNING is found.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entrypoint."""
    args = parse_cli(argv)
    if args.init_template is not None:
        args.init_template.parent.mkdir(parents=True, exist_ok=True)
        with args.init_template.open("w", encoding="utf-8") as handle:
            json.dump(_STARTER_TEMPLATE, handle, indent=2)
            handle.write("\n")
        sys.stdout.write(f"Wrote template -> {args.init_template}\n")
        return 0

    if args.input_json is None or not args.input_json.is_file():
        sys.stderr.write("Provide an existing `input_json` or `--init-template <path>`.\n")
        return 2

    with args.input_json.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    report = audit_portfolio(payload)
    out_text = json.dumps(report, indent=2) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", encoding="utf-8") as handle:
            handle.write(out_text)
    if args.markdown_out is not None:
        md_text = render_markdown_brief(payload, report)
        args.markdown_out.parent.mkdir(parents=True, exist_ok=True)
        with args.markdown_out.open("w", encoding="utf-8") as handle:
            handle.write(md_text)

    sys.stdout.write(out_text)
    if args.strict and not report["clean"]:
        return 1
    return 1 if report["counts"]["errors"] > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
