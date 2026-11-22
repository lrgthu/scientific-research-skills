# Crucial Experiment Design, Reviewer Murder Board & Cloud Pivot Protocol

Operationalizes the transition from **Stage 0 (`scientific-ideation`)** to **Stage 2 (`scientific-computing`)**, ensuring weak ideas die in hours rather than months, and unexpected empirical findings turn into clean discoveries rather than dead ends.

---

## 1. The 1–4 Hour Crucial Experiment (*Experimentum Crucis*)

Before writing any multi-GPU training pipeline, distill a **minimal falsification experiment** executable in **$\le 1\text{–}4$ hours** (e.g., on local Apple Silicon MPS/MLX, CPU analytical synthetic regime, or a single GPU):

### Mandatory 6-Field Crucial Experiment Contract

1. **Micro-Setup / Toy Oracle**:
   - Construct the smallest controlled setting where the bottleneck provably occurs (e.g., synthetic linear/Gaussian/Markov ground truth with closed-form Bayes optimal score, or a 500-example stratified diagnostic slice of a real benchmark).
2. **Competing Predictions Table**:
   - Explicitly write what $H_1$ predicts vs. what $H_2$ / $H_0$ predicts on the exact same plot or metric.
3. **Iso-Compute / Iso-Tuning Simple Baseline**:
   - Match FLOPs, parameter count, context tokens, and random-search hyperparameter budget fairly (preventing Melis et al.'s hyperparameter illusion).
4. **Two Concrete Test-Case Walkthroughs (`Si et al. Appendix B`)**:
   - **Example 1 (Baseline Failure)**: Concrete input instance where and why the baseline fails.
   - **Example 2 (Mechanism Resolution)**: Exact intermediate trace showing how the proposed operator resolves that failure without an oracle cheat.
5. **Quantitative Kill Condition (Pre-Registered Falsification Threshold)**:
   - State an unambiguous stop rule: *"If `Method` improves `<metric>` by `< delta` over `Compute-Matched Baseline` (or if diagnostic correlation `r < 0.3`), **falsify $H_1$ and trigger the Cloud Pivot** rather than hacking hyperparameters."*
6. **Wall-Clock & Hardware Target**:
   - Explicit runtime budget (e.g., `20 min on M5 Pro CPU/MPS` or `1.5 hr on 1x RTX 5060 Ti / A100 40GB`).

---

## 2. Adversarial Reviewer "Murder Board" (Pre-Mortem Before Coding)

Simulate an uncompromising Area Chair + 3 specialist reviewers *before* writing code. Every candidate idea must survive four hostile attacks:

1. **The Scoop / Prior-Art Attack**:
   - *"Isn't this already done in [Frontier Paper X] from 4 months ago under a different name?"*
   - **Defense required**: Cite verified `arXiv`/`DOI` neighbors from `scholarly_graph.py lineage` and state the exact mathematical/regime delta.
2. **The Trivial Baseline Attack**:
   - *"Why not just increase temperature / run best-of-$N$ / tune weight decay / use a linear probe on existing features?"*
   - **Defense required**: Include that exact trivial baseline in the Crucial Experiment!
3. **The Narrow-Regime / Toy-Only Attack**:
   - *"Even if this works on synthetic setup X, why wouldn't it vanish on real noisy distributions?"*
   - **Defense required**: Pair the 1-hour synthetic oracle check with a concrete Phase-2 real-dataset validation path.
4. **The Confounder / Cost Attack**:
   - *"Your method adds 2.4× memory or 3× wall-clock latency—is it Pareto-superior at equal latency?"*
   - **Defense required**: Commit to plotting a **2D Pareto curve (Quality vs. Wall-Clock Latency / FLOPs / Memory)** rather than single-column accuracy tables.

---

## 3. Uri Alon's Cloud Pivot Plan ($A \to \text{Cloud} \to C$)

In real frontier research, initial hypothesis $B$ fails $>60\%$ of the time when entering **The Cloud** *(Alon, 2009)*. Panic and patchwork trick-stacking happen when researchers have no pre-planned $C$:

```text
Textbook Illusion:   Start (A) ──────────────────────────────► Intended Method Works (B)

Frontier Reality:    Start (A) ──► [The Cloud: B Refuted!] ──► Pivot Discovery (C)
```

Every candidate idea card **must** pre-register its **Cloud Pivot ($C$)**:
- **If $H_1$ fails because $H_2$ turns out to be the true bottleneck**: Pivot immediately to testing/solving $H_2$, using the clean Crucial Experiment negative result on $H_1$ as **Section 3 Motivating Diagnostic Evidence** (*"Contrary to natural intuition $H_1$, controlled intervention reveals..."* — an **Assumption-Refutation `ABT`** in `scientific-writing`!).
- **If the proposed mechanism matches (but does not beat) the simple iso-compute baseline**: Pivot to a **Clean Simplification / Strong-Baseline Audit** if existing complex SOTA methods *also* fail to beat that properly tuned iso-compute baseline!

---

## 4. JSON Schema for `scripts/lint_research_ideas.py`

Generate a template via `uv run scripts/lint_research_ideas.py --init-template ideas.json`:

```json
{
  "topic": "Long-context KV-cache compression without multi-hop retrieval collapse",
  "constraints": {
    "compute_budget": "Local M5 Pro prototyping + 1x 16GB/40GB GPU for full runs",
    "max_crucial_test_hours": 4.0,
    "target_venue": "ICLR / NeurIPS"
  },
  "candidates": [
    {
      "id": "idea_spectral_sketch",
      "title": "Subspace-Preserving Key Sketching for Multi-Hop Retrieval",
      "archetype": "algorithmic_mechanism",
      "c_abt": "Heavy-hitter KV eviction preserves local perplexity using cumulative attention scores [AND], but multi-hop reasoning queries keys that remain completely dormant until the final hop [BUT]; therefore we retain a low-rank orthogonal residual sketch of evicted keys to preserve dormant query-key inner products at fixed memory [THEREFORE].",
      "attack_vector": "Empirical observation that attention keys exhibit rapid singular-value decay per head while heavy-hitter eviction zeroes out the orthogonal subspace.",
      "competing_hypotheses": [
        "H1 (Dormant Subspace Loss): Multi-hop recall drops because hard token eviction destroys low-attention key directions queried only at later hops.",
        "H2 (Softmax Temperature Dilution): Recall drops primarily from context-length logit dilution even when dormant key directions are preserved."
      ],
      "proposed_operator": "Maintain top-k exact recent/heavy-hitter tokens plus a streaming Frequent-Directions rank-r sketch K_sketch in R^{r x d_k} of evicted keys with log-count logit correction.",
      "compute_matched_baseline": "Heavy-hitter eviction (H2O / SnapKV) + quantized INT4 KV cache at identical total byte budget per token.",
      "verified_prior_art": ["arXiv:2306.14048", "arXiv:2404.14469"],
      "crucial_experiment": {
        "setup": "2-hop synthetic passkey + RULER multi-hop slice (200 examples, 32k context) on an open 7B/8B model.",
        "metric": "2-hop exact-match recall at 20% KV byte budget vs. wall-clock prefill/decode ms.",
        "kill_condition": "Falsify H1 if exact SVD rank-32 oracle residual sketch recovers <5 percentage points recall over byte-matched INT4 uniform quantization.",
        "estimated_hours": 2.0
      },
      "cloud_pivot_plan": "If oracle rank-32 SVD sketch fails to recover recall (refuting H1 in favor of H2), pivot to characterizing head-wise softmax entropy dilution vs. RoPE frequency drift.",
      "scores": {
        "knowledge_gain": 8.5,
        "feasibility": 8.0,
        "attack_clarity": 8.5,
        "scoop_safety": 7.5
      }
    }
  ]
}
```
