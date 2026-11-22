# Global Scientific Ideation & Strong Inference Rules (Platt · Hamming · Alon · Lipton & Steinhardt · Si et al.)

## 1. Scope Gate (Research Ideation & Hypothesis Design Only; Execution/Ops Exempt)

- **GATE 0 — Research Problem Selection, Brainstorming, Hypothesis Framing, & Pre-Mortem Critique (`scientific-ideation`)**:
  Whenever **any** research session or subagent/workflow/swarm task involves **choosing a research problem, brainstorming new research ideas/directions, evaluating whether a user's idea is worth pursuing, formulating hypotheses, designing minimal falsification experiments, or running a pre-project reviewer stress-test**:
  - You **MUST** read the `scientific-ideation` skill (`skills/scientific-ideation/SKILL.md`, using its path from your available skills list, plus relevant `references/*.md`) **before** generating or judging ideas, and chain into `scholarly-graph-audit` / `literature-evidence-workflow` to verify live prior art.
- **EXPLICIT EXEMPTION**:
  Pure execution of an already-locked experiment (`scientific-computing`), pure manuscript prose/figure polishing (`scientific-writing` / `scientific-figures`), and everyday software/ops tasks are **exempt**.

---

## 2. Core Non-Negotiable Scientific Ideation Guardrails

1. **Zero Armchair Brainstorming — Literature & Failure-Mode Grounding First (Si et al. 2025)**:
   - **Never** invent "novel" ideas from parametric memory alone or combine two trendy buzzwords (`Method A + Domain B`) without causal bottleneck grounding.
   - Before presenting candidate ideas as novel, verify the live frontier (`scholarly_graph.py lineage` + `semantic_siblings` scoop check) and anchor motivation in **verified baseline failure modes** (`citation-audit` contrasting contexts or assumption matrices).

2. **Hamming Attack Vector & Alon Pareto Frontier (Hamming 1986 · Alon 2009)**:
   - Every proposed problem must state an explicit **Attack Vector ("Why Now / Concrete Lever")**—a specific mathematical equivalence, hardware/scaling shift, measurement lens, or empirical anomaly that makes a previously blocked bottleneck tractable now.
   - Evaluate candidates on **Uri Alon's 2D `Feasibility × Knowledge Gain` Pareto Frontier** (calibrated to the user's actual compute, data, and timeline), ruthlessly pruning **Hard + Low-Gain** traps and overcrowded incremental tweaks. Remember **non-algorithmic archetypes**: clean diagnostic/understanding studies, impossibility/scaling laws, and strong baseline refutations are first-class high-impact ideas.

3. **Strong Inference Over Lonely Pet Hypotheses (Platt 1964 · Olson `cABT`)**:
   - **Ban single-hypothesis confirmation bias**: For every candidate idea, formulate **at least two competing mechanistic hypotheses ($H_1$ vs. $H_2$ / strong null $H_0$)** and compress the pitch into one jargon-free **`cABT`** (`Agreement [AND] → Sharp Bottleneck [BUT] → Falsifiable Mechanism [THEREFORE]`).
   - Enforce **Orthogonal Idea Diversity**: When proposing multiple ideas ($K = 3\text{–}5$), force each candidate onto a **distinct mechanistic axis** (e.g., *Objective/Representation* vs. *Inference/Algorithm* vs. *Data/Diagnostic Phenomenon*) to defeat LLM semantic homogenization.

4. **Anti-Slop Concrete Specification & 1-Hour Crucial Experiment (Lipton & Steinhardt 2018 · Si et al. 2025)**:
   - **Ban poetic black-box module names & unpacked suitcase words** (*"Semantic Resonance"*, *"Thought Lattice"*), **ban bundle-of-tricks soups** (isolate *one* primary causal mechanism), and **ban hidden oracle assumptions**.
   - Every surviving idea **must** specify: (a) **exact mathematical/algorithmic operator**, (b) **compute/tuning-matched simple baseline** (equal FLOPs/tokens/hyperparameter budget), (c) a **Crucial Experiment (*Experimentum Crucis*, $\le 1\text{–}4$ hours on toy/small scale)** with an explicit quantitative **Kill Condition** that would falsify $H_1$, and (d) an **Alon Cloud Pivot Plan ($A \to \text{Cloud} \to C$)** if $H_1$ fails.
