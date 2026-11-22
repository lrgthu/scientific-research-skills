# Scientific Ideation & Strong Inference (`v1.0.0`)

Global Stage-0 plugin bundling the **`scientific-ideation`** skill plus an **Always-On Global Rule (`rules/AGENTS.md`)** for research problem selection, non-trivial hypothesis generation, scoop-resistant novelty grounding, reviewer pre-mortem ("Murder Board"), and rapid falsification design:

1. **`scientific-ideation` Skill** (`skills/scientific-ideation/SKILL.md` + `references/` + `scripts/lint_research_ideas.py`):
   - **Problem Taste & Pareto Selection**: Operationalizes **Richard Hamming's *You and Your Research*** (*Importance × Concrete Attack Vector / Why-Now Lever*) and **Uri Alon's *How To Choose a Good Scientific Problem*** (`10.1016/j.molcel.2009.09.013`, 2D `Feasibility × Knowledge Gain` Pareto Frontier + `"The Cloud"` $A \to \text{Cloud} \to C$ pivot planning), recognizing both **Algorithmic/Methodological** and **Diagnostic/Empirical-Understanding** breakthroughs.
   - **Strong Inference & Anti-Slop Guardrails**: Operationalizes **John R. Platt's *Strong Inference*** (`10.1126/science.146.3642.347`, mandatory competing hypotheses $H_1$ vs. $H_2$ + crucial exclusion experiments), **Lipton & Steinhardt's *Troubling Trends in ML Scholarship*** (`arXiv:1807.03341`, separating causal mechanisms from bundle-of-tricks soup, spurious mathiness, and anthropomorphic suitcase words), and **Si, Yang & Hashimoto's ICLR 2025 empirical study** (`arXiv:2409.04109`, countering the 7 failure modes of LLM-generated ideas: operator vagueness, dataset mismatch, missing compute-matched baselines, hidden oracle assumptions, resource blowup, `A+B` buzzword mashups, and semantic diversity collapse).
   - **Executable Tooling**:
     - `scripts/lint_research_ideas.py` — Validates structured candidate idea specs (`--init-template`), flags anthropomorphic/suitcase-word buzzwords and duplicate semantic collapse, computes the non-dominated **Alon Pareto Frontier**, and compiles a Markdown **Murder-Board Decision Matrix**.

## Seamless Upstream/Downstream Bridges

- **Stage 0 ⇄ Stage 1 (`research-literature`)**: Grounds every candidate idea in live `scholarly_graph.py lineage` + `citation-audit` failure-mode contexts before scoring novelty (zero armchair hallucinated gaps).
- **Stage 0 → Stage 2 (`scientific-computing`)**: Hands the winning hypothesis's **Crucial Experiment** (`kill_condition`, synthetic/toy oracle, compute-matched baseline) directly into a clean, seeded Python falsification script.
