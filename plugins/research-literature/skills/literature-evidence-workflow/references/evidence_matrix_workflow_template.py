"""Reference `run_workflow` script for parallel Elicit-style evidence matrix extraction.

Usage:
1. Run `unpack_paper_corpus.py` to create `<corpus_dir>/corpus_manifest.json`.
2. Copy/adapt this script into `<Artifact Directory Path>/scratch/run_matrix.py` (or pass inline as `Script`),
   and invoke `run_workflow(ScriptPath=..., Args={...}, Description="Parallel paper screening & matrix extraction")`.
3. Pass the resulting JSON output to `compile_evidence_matrix.py`.
"""

import json
from pathlib import Path

EXTRACTION_SCHEMA = {
    "type": "object",
    "required": [
        "included",
        "exclusion_reason",
        "citation_label",
        "method_family",
        "problem_regime",
        "core_mechanism",
        "key_assumptions",
        "datasets_and_scale",
        "primary_metric_delta",
        "compute_or_complexity",
        "verified_limitation",
        "provenance_tier",
        "provenance_anchor",
        "verbatim_quote",
    ],
    "properties": {
        "included": {"type": "boolean"},
        "exclusion_reason": {"type": "string"},
        "citation_label": {"type": "string"},
        "method_family": {"type": "string"},
        "problem_regime": {"type": "string"},
        "core_mechanism": {"type": "string"},
        "key_assumptions": {"type": "string"},
        "datasets_and_scale": {"type": "string"},
        "primary_metric_delta": {"type": "string"},
        "compute_or_complexity": {"type": "string"},
        "verified_limitation": {"type": "string"},
        "provenance_tier": {"type": "string", "enum": ["latex_source", "oa_pdf_fulltext", "abstract_only"]},
        "provenance_anchor": {"type": "string"},
        "verbatim_quote": {"type": "string"},
    },
}

manifest_path = Path(args["manifest_path"])
research_question = args["research_question"]
inclusion_rubric = args["inclusion_rubric"]
output_json_path = Path(args["output_json_path"])

manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
papers = manifest["papers"]

phase(f"Screen & Extract {len(papers)} Papers in Parallel")
log(f"Loaded corpus manifest with {len(papers)} papers: {manifest['tier_counts']}")


def build_extractor(paper):
    prompt = f"""Screen and extract structured evidence for ONE paper from our local unpacked corpus.

Research Question:
{research_question}

Strict Screening Rubric (Inclusion / Exclusion):
{inclusion_rubric}

Paper Metadata:
- Title: {paper.get('title')}
- Authors: {', '.join((paper.get('authors') or [])[:6])}
- Year / Venue: {paper.get('year')} / {paper.get('venue')}
- DOI / arXiv: {paper.get('doi')} / {paper.get('arxiv_id')}
- Provenance Tier: {paper['provenance_tier']}
- Primary Text File: {paper['primary_text_path']}
- Extracted Tables File: {paper.get('tables_path')}

Instructions:
1. Use `read_file` to inspect `{paper['primary_text_path']}` (and `{paper.get('tables_path')}` if present).
2. Evaluate against the Screening Rubric first. If off-target, set `included: false` with a concise `exclusion_reason`.
3. Never invent numbers or hyperparameters. If `provenance_tier` is `abstract_only`, explicitly write `[abstract-only: not reported]` for unstated details.
4. Record the exact `provenance_anchor` (e.g. `Sec. 4.1, Table 2` or `[Page 5]`) and a 1-2 sentence `verbatim_quote`.
"""
    short_title = (paper.get("title") or paper["canonical_id"])[:42]
    return agent(
        prompt=prompt,
        schema=EXTRACTION_SCHEMA,
        role=f"Extract: {short_title}",
        model="flash",
    )


rows = await parallel(papers, build_extractor)

output_json_path.parent.mkdir(parents=True, exist_ok=True)
output_json_path.write_text(json.dumps({"rows": rows}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
log(f"Saved {len(rows)} extracted records -> {output_json_path}")
print(str(output_json_path))
