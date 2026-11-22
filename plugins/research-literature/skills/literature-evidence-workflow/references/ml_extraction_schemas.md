# Structured Evidence Matrix Extraction Schemas (Elicit++ Pattern)

Use these strict JSON schemas inside `run_workflow` `agent(..., schema=EXTRACTION_SCHEMA)` calls so every parallel paper-reading subagent outputs uniform, provenance-anchored fields without hallucinating missing metrics.

---

## 1. Machine Learning / Computational Research Schema (Default)

```json
{
  "type": "object",
  "required": [
    "included",
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
    "verbatim_quote"
  ],
  "properties": {
    "included": {
      "type": "boolean",
      "description": "True iff the paper satisfies all pre-registered inclusion criteria and none of the exclusion criteria."
    },
    "exclusion_reason": {
      "type": "string",
      "description": "Concise reason if included is false; empty string otherwise."
    },
    "citation_label": {
      "type": "string",
      "description": "Compact label with BibTeX key, e.g. 'Rafailov et al. (2023) [\\cite{rafailov2023direct}]'"
    },
    "method_family": {
      "type": "string",
      "description": "Taxonomic school/camp (2-5 words) for grouping Related Work by mechanism rather than chronology."
    },
    "problem_regime": {
      "type": "string",
      "description": "Exact task setting, supervision assumption, or data regime."
    },
    "core_mechanism": {
      "type": "string",
      "description": "Objective, architecture, or algorithmic mechanism in 1 crisp phrase."
    },
    "key_assumptions": {
      "type": "string",
      "description": "Explicit or implicit assumptions required for the method/theory to hold."
    },
    "datasets_and_scale": {
      "type": "string",
      "description": "Benchmarks, model parameter scales, or sample sizes evaluated."
    },
    "primary_metric_delta": {
      "type": "string",
      "description": "Headline effect size / delta over named baseline (or '[not reported in abstract]' if abstract_only)."
    },
    "compute_or_complexity": {
      "type": "string",
      "description": "Asymptotic complexity, GPU hours, or memory overhead if stated; else 'Not stated'."
    },
    "verified_limitation": {
      "type": "string",
      "description": "Failure mode, boundary condition, or limitation stated in paper Discussion/Appendix or citing audit."
    },
    "provenance_tier": {
      "type": "string",
      "enum": ["latex_source", "oa_pdf_fulltext", "abstract_only"]
    },
    "provenance_anchor": {
      "type": "string",
      "description": "Exact section/table/equation/page anchor, e.g. 'Sec. 4.2, Table 2' or '[Page 6]'."
    },
    "verbatim_quote": {
      "type": "string",
      "description": "1-2 verbatim sentences from the source text grounding the primary claim or limitation."
    }
  }
}
```

---

## 2. Empirical / Natural & Biomedical Science Schema

Swap columns via `--columns "citation_label:Study,system_or_cohort:System,intervention:Intervention,effect_size:Effect Size,confounders:Caveats"` in `compile_evidence_matrix.py`:

- `citation_label`: First author, year, and verified key
- `study_design`: Experimental / observational / simulation / clinical phase
- `system_or_cohort`: Organism, cell line, dataset, or patient sample size $N$
- `intervention`: Perturbation, assay, or treatment variable
- `effect_size`: Fold-change, $R^2$, hazard ratio, or $\Delta$ with CI (never bare $p$-values alone!)
- `confounders`: Controls, batch effects, or scope limitations
- `provenance_tier`, `provenance_anchor`, `verbatim_quote`
