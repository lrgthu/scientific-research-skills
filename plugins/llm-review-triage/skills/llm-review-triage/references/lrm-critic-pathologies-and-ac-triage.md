# Frontier Reasoning-Critic Pathologies & Area-Chair Triage Protocol

Modern Large Reasoning Models (LRMs) do not fail like early short-context chatbots—they read your entire LaTeX repository, trace equation indices accurately, and write fluent, authoritative critiques. That very fluency makes them **dangerous when treated as infallible arbiters**. Understanding *why* frontier reasoning models over-criticize is the key to extracting their 20% genuine signal without letting the other 80% deform your paper.

---

## 1. Anatomy of the Six Frontier LRM Critic Pathologies

### P1. Adversarial Limitation Weaponization (`LIMITATION_BOOMERANG`)
- **Mechanism**: When prompted to *"critique this paper like a strict top-tier reviewer,"* a reasoning model searches its context window for claims that are **provably vulnerable**. An author's own honest `Limitations` or `Scope` paragraph is a goldmine for the model's chain-of-thought: because *you* already admitted *"our exact equivalence assumes stationary noise / we evaluate up to 14B models,"* the model knows with 100% certainty that attacking non-stationary noise or 70B models cannot be factually wrong! It then elaborates a multi-paragraph technical indictment around the exact boundary you transparently reported.
- **Why Obeying It Is Toxic**: If reporting an honest limitation causes you either to run months of out-of-scope experiments or to litter the main text with apologetic disclaimers, you punish scientific honesty and turn a focused paper into an unfocused sprawl.
- **Area-Chair Rule**: **Honest, upfront scope disclosure is a shield, not an admission of guilt.** If the draft already states boundary $B$ clearly and your claims in the Abstract/Intro do not falsely claim $\neg B$, **reject the demand (`0` edits needed)**.

### P2. Test-Time Overthinking & Confounder Inflation (`OVERTHINKING_NITPICK`)
- **Mechanism**: Reasoning models trained with reinforcement learning allocate deep CoT budgets to "find flaws" and suffer from **inability to stop early on clean inputs** (*harmful overthinking*). When no first-order flaw exists, the model keeps digging into second- and third-order hypotheticals:
  - Measure-zero pathological inputs (*"What if the covariance matrix has exact multiplicity $k$ eigenvalues at initialization?"*),
  - Unbounded confounder lists (*"Did you sweep optimizer $\beta_2 \in \{0.95, 0.98, 0.999\}$ jointly with warmup schedule?"*),
  - Microscopic notation nitpicks elevated to "Major Technical Concerns."
- **Area-Chair Diagnostic**: Apply the **First-Order Flip Test**:
  > *"Is there a realistic (>10% prior probability) chance that controlling for this variable would **reverse or nullify** our primary conclusion?"*
  - If **Yes** $\rightarrow$ `Bucket 1` (worth testing/checking!).
  - If **No** (at most shifts numbers by $O(\epsilon)$ without changing rankings or mechanism) $\rightarrow$ **Discard as Overthinking Noise.**

### P3. Uncalibrated Effort-to-Information Asymmetry (`LOW_ROI_SCOPE_CREEP`)
- **Mechanism**: An LRM pays `0` GPU-hours to write *"It would strengthen the paper to also evaluate on video generation, RL control, and 70B pretraining from scratch."* It has zero internal cost model weighting **marginal bits of scientific insight** against **weeks of engineering/compute and manuscript dilution**.
- **Area-Chair Diagnostic**: Compute **`ROI = Marginal Falsification Power / (Compute + Prose Dilution Cost)`**. An additional experiment is worthwhile *only* when it **excludes a rival mechanistic explanation ($H_2$)** for your core thesis—never merely to pad dataset count $N \to N+3$.

### P4. Formalist Epistemic Perfectionism (`DEFENSIVE_HEDGING_TRAP`)
- **Mechanism**: Frontier models are heavily post-trained to avoid overclaiming and pass literal factuality verifiers. Consequently, they attack **scientific inductive generalization** itself: whenever you state a clean conceptual takeaway (*" Dormant-subspace sketching prevents multi-hop collapse"*), the critic demands you reduce it to a narrow, hyper-qualified empirical observation (*"On the two tested benchmarks with 8B models under RULER-32k, the proposed heuristic partially mitigates recall degradation relative to two baselines"*).
- **Why Obeying It Kills the Paper**: Science is not a court transcript of raw CSV cells (`Data`); science is `Data → Information → Knowledge → Understanding` *(Schimel)*. Stripping every generalizable mechanism statement down to a timid empirical log erases the paper's intellectual contribution.

### P5. Genre Blindness & Decorative "Mathiness" Demands (`GENRE_MISMATCH`)
- **Mechanism**: Critic prompts pull models toward a homogenized " prototypical NeurIPS/ICML checklist" (new algorithm + convergence theorem + 8 SOTA tables + scaling law + ablation grid).
  - Give it a crisp **Empirical Diagnostic / Assumption-Refutation paper**, and it demands a novel SOTA architecture.
  - Give it a clean **Systems / Algorithmic paper**, and it demands a decorative toy convex convergence bound (*spurious mathiness*, Lipton & Steinhardt 2018).
- **Area-Chair Rule**: Judge every critique strictly against the paper's **chosen Genre Contract**. Never bolt a fake toy theorem onto an empirical paper or bolt a half-baked heuristic onto a clean diagnostic study.

### P6. Multi-Round Contractive Relaxation (`RECURSIVE_SOUL_DRIFT`)
- **Mechanism**: Every round of `Draft -> LRM Critic -> Revise` applies a risk-minimizing smoothing operator:
  - **Round 1** catches 85%+ of real mathematical typos, missing baseline controls, and genuine clarity gaps.
  - **Round 2** catches minor residual inconsistencies from Round-1 edits, while starting to nitpick stylistic edges.
  - **Round 3+** enters **contractive drift**: because the real flaws are gone, the fresh stateless critic attacks your remaining bold hooks, demands caveats on the caveats you added in Round 2, and nudges your terminology toward generic LLM-preferred phrasing.
- **Hard Stopping Protocol**:
  - Cap proactive full-manuscript AI review at **1 substantive round + 1 bug-check pass**.
  - On `Round >= 2`, freeze narrative structure, claims, and experimental scope; accept **only** verifiable objective bugs (broken equations, code bugs, numeric mismatches, undefined symbols).

---

## 2. The Four High-Leverage Signals Worth Mining (`The 20% Gold`)

Frontier reasoning models *are* extraordinary at specific analytical tasks where exhaustive attention beats tired human eyes. Prioritize comments that hit these four targets:

1. **`[G1] Exact Mathematical, Dimensional, or Algorithmic Bugs`**:
   - Missing transpose/normalization factor, boundary index off-by-one, division-by-zero / `NaN` regime, theorem conclusion that requires an unstated Lipschitz/convexity condition, or subtle train-test / prompt-template leakage.
2. **`[G2] Missing Iso-Compute / Iso-Tuning Simple Baselines`**:
   - Pointing out a concrete, cheap baseline that spends the **same** test-time tokens, memory bytes, or hyperparameter trials (e.g., *"Does your 3-pass router actually beat simple best-of-3 sampling at equal latency?"*). Answering this makes the paper **dramatically stronger** against real human reviewers!
3. **`[G3] Cross-Artifact Numeric, Symbol, or Sign Contradictions`**:
   - Catching that Section 4 calls $\tau$ a temperature while Algorithm 1 uses $\tau$ as a threshold, or that Table 2's subgroup rank contradicts a generalization in Figure 3's caption.
4. **`[G4] True Reader-Expectation Bottlenecks`**:
   - Identifying a genuine logical leap between two paragraphs where an unstated step existed only in the author's head, or an acronym/notation used 2 pages before its definition.
