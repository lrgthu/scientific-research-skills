---
name: scientific-ideation
description: >
  Stage-0 scientific problem selection, non-trivial research ideation,
  competing-hypothesis formulation, anti-scoop novelty grounding, reviewer
  murder-board stress-testing, and 1-hour crucial falsification experiment
  design. Synthesizes John Platt's Strong Inference (Science, 1964), Richard
  Hamming's Attack-Vector Heuristic (1986), Uri Alon's Feasibility-Interest
  Pareto Frontier & Cloud Schema (Molecular Cell, 2009), Lipton & Steinhardt's
  Troubling Trends in ML Scholarship (arXiv:1807.03341), and Si, Yang &
  Hashimoto's empirical AI-ideation failure taxonomy (ICLR 2025,
  arXiv:2409.04109). Use whenever brainstorming new research ideas, choosing
  what problem to work on, stress-testing or critiquing a user's raw research
  idea, turning baseline failures into falsifiable hypotheses, or ranking
  candidate project directions before coding.
---

# Scientific Ideation, Problem Taste & Strong Inference Skill (Stage 0)

> **Core Premise**: Naive LLM "brainstorming" fails predictably—it recombines trendy buzzwords (`Method A + Task B`), collapses onto repetitive variations (~95% duplication at scale), hides impossible oracle sub-steps behind poetic module names, and over-rates its own ideas *(Si, Yang & Hashimoto, ICLR 2025, `arXiv:2409.04109`)*. Genuine breakthroughs start from **verified anomaly/failure-mode friction**, an explicit **Hamming Attack Vector**, **Platt's competing hypotheses ($H_1$ vs. $H_2$)**, and a **1–4 hour Crucial Experiment** designed to *kill* weak ideas before spending weeks of compute.

## Reference Modules & Executable Tooling

Load the reference module(s) matching your current ideation step, and validate candidate portfolios with `<SKILL_DIR>/scripts/lint_research_ideas.py`:

1. **[Problem Taste, Attack Vectors & Alon Pareto Selection](./references/problem-taste-and-pareto-selection.md)** — **Read when scouting directions or choosing between candidate problems**: Hamming's *Importance × Attack Vector ("Why Now?")* test, Uri Alon's 2D `Feasibility × Knowledge Gain` Pareto Frontier, **5 High-Value Research Archetypes** (beyond "new loss/architecture": Diagnostic/Refutation studies, Scaling/Boundary laws, Formulation shifts, Representation bridges, Systems/Exactness levers), and orthogonal axis diversification.
2. **[Strong Inference & Anti-LLM-Slop Audit](./references/strong-inference-and-anti-slop-audit.md)** — **Read when generating or critiquing candidate mechanisms**: Platt's competing-hypothesis trees ($H_1, H_2, H_0$), Si et al.'s **7 Empirical AI-Ideation Failure Modes (F1–F7)**, and Lipton & Steinhardt's **4 Scholarship Traps (T1–T4)** (Explanation vs. Speculation, Bundle-of-Tricks soup, Spurious Mathiness, Anthropomorphic/Suitcase words).
3. **[Crucial Experiment Spec, Compute-Matched Baselines & Reviewer Murder Board](./references/crucial-experiment-and-murder-board.md)** — **Read when finalizing proposals or transitioning to code**: Designing `<4 hr` *Experimentum Crucis* kill tests, Melis-style compute/tuning-matched simple baselines, Pairwise Reviewer Pre-Mortem ("Murder Board"), and Uri Alon's **Cloud Pivot Plan ($A \to \text{Cloud} \to C$)**.
4. **Bundled CLI Validator & Pareto Ranker (`<SKILL_DIR>/scripts/lint_research_ideas.py`)**:
   - `uv run "<SKILL_DIR>/scripts/lint_research_ideas.py" --init-template /tmp/ideas_spec.json` — Writes a starter candidate-portfolio JSON template.
   - `uv run "<SKILL_DIR>/scripts/lint_research_ideas.py" /tmp/ideas_spec.json --markdown-out ./ideation_murder_board.md --strict` — Validates completeness, flags anthropomorphic/suitcase buzzwords and semantic duplicates, computes the non-dominated **Alon Pareto Frontier**, and renders a structured **Murder-Board Decision Brief**.

---

## Mandatory 5-Phase Scientific Ideation Workflow

### Phase 1: Anchor Constraints & Mine Real Friction (`Stage 0 ⇄ Stage 1 Bridge`)

1. **Calibrate Resource Envelope First (Alon 2009 · Si et al. F5)**:
   - Identify the user's real constraints before proposing anything: compute budget (e.g., local Apple Silicon MPS/MLX rapid prototyping vs. single-GPU workstation vs. multi-GPU cluster), target venue/timeline, and available datasets/simulators. Never propose 100B-parameter full fine-tuning or massive human annotation unless the user explicitly has that budget.
2. **Ground in Live Scholarly Friction (`scholarly-graph-audit` + `literature-evidence-workflow`)**:
   - **Never brainstorm from parametric memory alone.** Read `scholarly-graph-audit` (`SKILL.md`) and run:
     - `scholarly_graph.py lineage` on 1–4 seed papers to inspect `active_frontier` and `semantic_siblings` (**Anti-Scoop Check**—catch concurrent preprints using different terminology!).
     - `scholarly_graph.py citation-audit` / `tex-context` (or `unpack_paper_corpus.py` on 3–6 frontier `.tex` sources) to extract **verbatim failure modes, hidden assumptions, and trade-off walls** (`Camp A sacrifices X` vs. `Camp B requires O(N^2)`).

### Phase 2: Orthogonal Divergent Generation Across Distinct Axes (`Hamming 1986 · Si et al. F7`)

To defeat LLM semantic collapse, generate $K = 3\text{–}5$ candidates where **no two candidates share the same mechanistic family**:
- **Axis A — Mechanistic / Mathematical Reformulation**: Replace a heuristic surrogate with an exact, closed-form, invariant, or better-conditioned operator.
- **Axis B — Diagnostic / Assumption-Refutation Study** *(Lipton & Steinhardt §5.1)*: No new Rube Goldberg module—design a surgical empirical or theoretical probe proving *why* a widely believed assumption or benchmark fails (e.g., random-label memorization, BatchNorm smoothness, tuned-LSTM vs. complex architectures).
- **Axis C — Regime / Systems / Compute-Allocation Shift**: Reallocate test-time/training-time compute, memory, or data curation along an overlooked bottleneck with a concrete **Hamming Attack Vector** (*what changed recently that makes this tractable now?*).

### Phase 3: Strong Inference & Anti-Slop Filtering (`Platt 1964 · Lipton & Steinhardt 2018 · Si et al. F1–F6`)

Run every candidate through 5 ruthless filters—discard or rewrite any candidate that fails:
1. **1-Sentence Jargon-Free `cABT` Test**: State `[Agreement: what works today] AND [Bottleneck: exact regime where & why it breaks] BUT [Consequence: falsifiable single mechanism] THEREFORE`. If there is no sharp `[BUT]`, kill it.
2. **Platt Competing-Hypothesis Fork ($H_1$ vs. $H_2$ / $H_0$)**: Write at least two plausible, mutually exclusive explanations ($H_1$: your proposed mechanism drives the gain; $H_2$: gain is merely implicit regularization / extra compute / hyperparameter sensitivity; $H_0$: effect vanishes under controlled evaluation).
3. **Concrete Operator Gate (Zero Black-Box Poetry)**: Write the exact mathematical objective, tensor transformation, or algorithmic step. Ban anthropomorphic/sci-fi labels (*"Semantic Resonance"*, *"Cognitive Lattice"*) and unpacked suitcase words.
4. **Single-Causal-Lever Discipline (Anti-Bundle-of-Tricks)**: Strip auxiliary bells and whistles. One clean lever + two informative ablations/negative results beats a 4-component un-ablated soup.
5. **Compute-Matched Simple Baseline Gate**: Define the strongest *trivial* baseline given the **exact same** extra parameters, inference tokens, wall-clock FLOPs, or tuning trials.

### Phase 4: Reviewer Murder Board, Alon Pareto Ranking & Cloud Pivot (`lint_research_ideas.py`)

1. Encode the surviving 3–5 candidates into JSON and run `lint_research_ideas.py --strict --markdown-out ideation_murder_board.md`.
2. **Pairwise Tournament Over Absolute LLM Self-Scores** *(Si et al. §3.3, §6.2)*: Never trust standalone `8.5/10` LLM excitement numbers. Compare candidates **head-to-head pairwise** on:
   - *Which idea has fewer hidden oracle assumptions?*
   - *Which idea's kill test yields cleaner scientific information even if $H_1$ is falsified?*
   - *What is the #1 lethal review weakness a skeptical Area Chair will write, and how does the experimental design preempt it?*
3. **Pre-Register Alon's Cloud Pivot ($A \to \text{Cloud} \to C$)**: Explicitly state what publishable diagnostic/boundary law ($C$) you still learn if the primary hypothesis ($B$) is refuted.

### Phase 5: 1–4 Hour Crucial Experiment Handoff (`Stage 0 → Stage 2 Bridge`)

Never jump from ideation straight into building a 5,000-line training framework:
1. Specify the **Crucial Experiment (*Experimentum Crucis*)**: synthetic/toy dataset or smallest real benchmark slice executable in **$\le 1\text{–}4$ hours**, exact metric, and **Quantitative Kill Condition** (e.g., *"If exact rank-16 sketch recall is within $<1\%$ of uniform eviction on synthetic needle-in-a-haystack at 16k context, falsify $H_1$ immediately"*).
2. Once the user selects a candidate (or asks to test the top candidate), **load `scientific-computing` (`SKILL.md`)** to implement this clean, seeded falsification experiment first.
