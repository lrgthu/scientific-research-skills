# Problem Taste, Hamming Attack Vectors & Alon Pareto Selection

Synthesizes **Richard W. Hamming's *"You and Your Research"*** (Bellcore Colloquium, 1986), **Uri Alon's *"How To Choose a Good Scientific Problem"*** (*Molecular Cell* 35(6): 726–728, 2009, `10.1016/j.molcel.2009.09.013`), and **Lipton & Steinhardt's *"Troubling Trends in Machine Learning Scholarship"*** (`arXiv:1807.03341`).

---

## 1. Hamming's Law: Importance × Tractable Attack Vector

Hamming observed a sharp divide between researchers who do foundational work and equally talented peers who spend years on forgettable increments:

1. **Importance Without an Attack Is Daydreaming**:
   - Asking *"How do we achieve AGI / solve teleportation?"* is not a research problem because there is no concrete **Attack Vector (Handle / Lever)**.
   - Conversely, tweaking a loss weight for `+0.3%` on a saturated leaderboard has an easy attack, **zero consequence**, and high scoop risk.
2. **The Mandatory "Why Now / Attack Vector" Question**:
   Every candidate idea must answer in 1–2 sentences: **What specific lever makes this bottleneck Newly Tractable right now?**
   Valid attack levers fall into four categories:
   - **Analytical / Equivalence Lever**: Discovering an exact algebraic mapping or duality (e.g., DPO eliminating explicit reward-model PPO via closed-form KL-constrained partition cancellation).
   - **Empirical Anomaly / Contradiction Lever**: Observing a stark discrepancy between folklore theory and actual model behavior (e.g., Santurkar et al. showing BatchNorm does *not* reduce internal covariate shift; Zhang et al. showing deep nets fit random labels with zero training error).
   - **Hardware / Scaling Regime Shift**: A bottleneck that was negligible at $N = 2\text{k}$ becomes dominant at $N = 128\text{k}$ (e.g., KV-cache memory bandwidth overtaking matmul FLOPs during autoregressive decoding).
   - **Cross-Subfield Isomorphism**: Importing a mature, mathematically exact tool from numerical linear algebra, control theory, signal processing, or statistical physics into a regime where ML currently uses unstable heuristics—*provided the assumptions genuinely match*.
3. **The "10–20 Bottlenecks" Matrix**:
   Keep concrete unsolved failure modes separate from candidate tools. Ideation succeeds when you match a **real bottleneck** to a **sharp new lever**, never when you hold a hammer and hunt for arbitrary nails.

---

## 2. Uri Alon's 2D Pareto Frontier (`Feasibility × Knowledge Gain`)

Plot every candidate project on two honest axes calibrated to **your actual lab resources and timeline**:

- **X-Axis — Feasibility ($1\text{–}10$)**: Inverse of engineering friction, compute wall-clock cost, data acquisition bottlenecks, and dependency on unverified external components.
- **Y-Axis — Knowledge Gain & Scientific Interest ($1\text{–}10$)**: How much community understanding or capability shifts *regardless of whether the benchmark number moves by 0.5% or 5%*, weighted by genuine researcher curiosity.

```text
Knowledge Gain (Y)
  10 |          ★ [Sweet Spot: High-Gain + High-Feasibility]
     |               * (Flagship Frontier: High-Gain, Moderate-Hard)
   6 |                      *
     |    [DOMINATED INTERIOR — DO NOT WORK HERE]
   2 |    x (Hard + Low-Gain Trap!)          o (Easy + Low-Gain Commodity)
     +--------------------------------------------------------------------►
     1 (Very Hard / Infeasible)                         10 (Highly Feasible)
```

### Quadrant Triage Rules

| Zone | Profile | Action |
| :--- | :--- | :--- |
| **Pareto Sweet Spot** (`Feasibility >= 7`, `Gain >= 7`) | Clean leverage point; testable on existing hardware/benchmarks within days, illuminates a broad principle. | **Execute Immediately (Priority 1).** Double-check `scholarly_graph.py lineage` + `semantic_siblings` carefully because fast high-gain ideas attract concurrent work. |
| **Flagship Frontier** (`Feasibility 4–6`, `Gain >= 8`) | Ambitious multi-week/month effort requiring custom systems, proofs, or curated data. | **De-risk First**: Extract a 2-hour **Crucial Toy Sub-Problem** (`Feasibility >= 8`) before committing to the full flagship build. |
| **Easy + Low-Gain Commodity** (`Feasibility >= 8`, `Gain <= 4`) | Plugging existing Trick X into Dataset Y (`A + B` incrementalism). | **Reject** (except as a 1-day onboarding warm-up for a novice). High scoop rate, high reviewer apathy (*"incremental, limited insight"*). |
| **Hard + Low-Gain Dominated Trap** (`Feasibility <= 5`, `Gain <= 5`) | Massive engineering/compute grind yielding a narrow, non-transferable tweak. | **Strictly Forbidden (Alon's Rule #1).** Kill immediately. |

---

## 3. Five First-Class Research Idea Archetypes (Beyond "Yet Another Module")

LLMs default to proposing complex multi-stage pipelines (*"Module A feeds Router B with Auxiliary Loss C"*). Counter this bias by deliberately spanning **5 distinct archetypes**:

1. **Assumption-Refutation / Diagnostic Paper** *(High Gain, High Feasibility!)*:
   - *Pattern*: Folks believe Method X works because of Property P. Design a surgical controlled intervention removing P (or inducing P without X) and prove P is irrelevant—isolating the true driver Q.
   - *Classic exemplars*: Zhang et al. (2017, Rethinking Generalization), Santurkar et al. (2018, How Does BatchNorm Help Optimization?), Melis et al. (2018, Tuned LSTMs vs. Complex Architectures).
2. **Benchmark / Evaluation Illusion Audit**:
   - *Pattern*: Demonstrate that a popular benchmark allegedly testing capability $C$ can be solved ($>70\%$) by a trivial shortcut baseline lacking $C$, and construct the clean counterfactual split that genuinely requires $C$.
   - *Classic exemplars*: Chen et al. (2016, CNN/DailyMail single-sentence shortcut), Gururangan et al. (2018, Annotation Artifacts in NLI), Recht et al. (2019, ImageNet v2).
3. **Exact Simplification / Reduction ("Subtraction Idea")**:
   - *Pattern*: Show that a brittle 3-stage pipeline collapses algebraically into a single stable 1-stage objective with fewer hyperparameters and lower memory/compute.
4. **Scaling / Phase-Transition / Boundary Law**:
   - *Pattern*: Map the quantitative dimensionless law governing *when* Method A overtakes Method B across compute, context length, rank, noise, or data scarcity—turning conflicting empirical folklore into a predictive phase diagram.
5. **Bottleneck-Targeted Algorithmic / Systems Mechanism**:
   - *Pattern*: Measure the true physical/statistical bottleneck first (e.g., memory-bandwidth Stall, rank collapse, gradient variance spike), then introduce *one* minimal operator specifically engineered to eliminate that measured bottleneck.
