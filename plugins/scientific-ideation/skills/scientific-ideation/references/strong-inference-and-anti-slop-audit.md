# Strong Inference & Empirical Anti-LLM-Slop Audit

Synthesizes **John R. Platt's *"Strong Inference"*** (*Science* 146(3642): 347–353, 1964, `10.1126/science.146.3642.347`), **Chenglei Si, Diyi Yang & Tatsunori Hashimoto's *"Can LLMs Generate Novel Research Ideas? A Large-Scale Human Study with 100+ NLP Researchers"*** (ICLR 2025, `arXiv:2409.04109`), and **Zachary C. Lipton & Jacob Steinhardt's *"Troubling Trends in Machine Learning Scholarship"*** (*ACM Queue* / ICML 2018, `arXiv:1807.03341`).

---

## 1. John Platt's Strong Inference Protocol (1964)

Fields that advance exponentially do not run "let's try X and see if accuracy goes up" experiments—they climb a **logical exclusion tree**:

1. **Step 1a — Devise Multiple Working Hypotheses ($H_1, H_2, \dots, H_0$)**:
   - Never allow a researcher or agent to become emotionally attached to a single pet hypothesis $H_1$ (*Chamberlin's trap*).
   - For every observed failure mode, explicitly list rival explanations.
   - *Example*: Suppose long-context retrieval drops from 92% to 54% at 128k tokens.
     - $H_1$ (*Representation Eviction*): Early eviction permanently discards dormant key vectors needed at later hops.
     - $H_2$ (*Positional Entropy Dilution*): Keys remain present/recoverable, but softmax denominator dilution flattens attention logits below precision noise.
     - $H_0$ (*Positional OOD Artifact*): The model simply never saw RoPE frequencies beyond 32k during fine-tuning.
2. **Step 1b — Devise a Crucial Experiment (*Experimentum Crucis*)**:
   - Design an intervention whose outcomes **cleanly separate $H_1$, $H_2$, and $H_0$** before building any new architecture:
     - *Test*: Keep the *exact full KV cache* (zero eviction) and rescale attention temperature $\tau(L) \propto \ln L$ on in-distribution vs. extrapolated lengths. If full-cache + temperature scaling restores 91% accuracy, **$H_1$ (eviction) is immediately falsified as the root bottleneck**, saving weeks of wasted sketching code!
3. **Step 1c — Execute Cleanly & Recycle ($1' \to 2'$)**:
   - Eliminate the falsified branch, subdivide the surviving branch ($H_{2a}$ vs. $H_{2b}$), and repeat.
4. **Platt's Two Razor Questions (Mandatory on Every Proposal)**:
   - *"What concrete experimental result would **disprove** your hypothesis?"* (If no outcome could disprove it, it is unfalsifiable dogma, not science.)
   - *"Which rival hypothesis does your planned experiment **exclude**?"*

---

## 2. Countering the 7 Empirical Failure Modes of AI-Generated Ideas (`Si et al., ICLR 2025`)

In a blind evaluation of ~300 expert reviews across 100+ researchers (`arXiv:2409.04109` §6–7), LLM-generated ideas scored high on surface novelty but failed systematically in 7 ways. Enforce the right-column countermeasure on every idea:

| Empirical AI Failure Mode (`Si et al. §6–7`) | Symptom in Raw Agent Output | Mandatory Countermeasure in `scientific-ideation` |
| :--- | :--- | :--- |
| **F1. Implementation Vagueness** | *"We form a Semantic Pivot Constellation and take a weighted sum..."* (how are weights computed? supervised? cosine? learned?) | **Explicit Operator Signature**: Require exact input/output shapes, mathematical formula/loss, and optimization/inference algorithm steps. |
| **F2. Dataset & Task Mismatch** | Proposing single-ground-truth QA (`TruthfulQA`, `GSM8K`) to evaluate multi-perspective ambiguity or system-level security. | **Phenomenon-Dataset Alignment Check**: Verify that the dataset actually exhibits variance on the target failure mode and isn't ceiling-saturated. |
| **F3. Missing Simple / Compute-Matched Baselines** | Comparing a 5-call iterative agent against 1-shot greedy decoding (`1×` vs `5×` test-time compute!). | **Iso-Compute / Iso-Tuning Baseline**: Always include best-of-$N$, multi-turn self-refinement, or equal-FLOPs/equal-hyperparameter-sweep vanilla baselines. |
| **F4. Unrealistic Hidden Oracle Assumptions** | *"First, prompt the model to identify its own ungrounded hallucinations, then..."* (begging the core question!). | **Prerequisite Audit**: List every sub-step's required accuracy; if step 1 requires an unsolved oracle, test step 1's sensitivity to 30%–50% noise first. |
| **F5. Blind Resource / Annotation Blowup** | Casual step 4: *"Fine-tune a 176B model and hire native dialect experts across 12 languages."* | **Hardware & Time Envelope Gate**: Bound GPU memory, wall-clock hours, and zero-human-annotation automated evaluation upfront. |
| **F6. Unmotivated `A + B` Mashup** | Applying trendy technique A to trendy domain B when vanilla models already solve the task or A doesn't address B's bottleneck. | **Zero-Shot Sanity Check**: Verify on 10 real examples that strong current baselines *actually fail* on the motivating examples! |
| **F7. Diversity Plateau & Bad Self-Judging** | Generating 50 ideas yields minor paraphrases of 3 templates; LLM `1–10` self-scores correlate poorly (`~50%`) with human experts. | **Orthogonal Axis Forcing (`K = 3–5`) + Pairwise Tournament + Human Selection**: Force distinct archetypes and rank via structured pairwise trade-offs, never raw LLM point scores. |

---

## 3. Eliminating Scholarship Traps at Birth (`Lipton & Steinhardt, arXiv:1807.03341`)

1. **Explanation vs. Speculation Quarantine (§3.1)**:
   - Never coin an unmeasured intuitive story (like unquantified *"internal covariate shift"*) and state it as causal fact. Every claimed mechanism must name **the exact scalar/distribution metric that quantifies it** (e.g., Hessian top eigenvalue $\lambda_{\max}$, layerwise Wasserstein-2 shift, exact subspace overlap).
2. **Anti-Bundle-of-Tricks Rule (§3.2)**:
   - Reviewers should ask: *"Might I have accepted a cleaner version if the authors hadn't bolted 3 extra tweaks on top?"* Design ideas around **one crisp causal modification** paired with **isolating ablations**.
3. **Anti-Mathiness Prediction Test (§3.3, §5.1)**:
   - Before proposing a theoretical bound, apply Lipton & Steinhardt's litmus test: ***"Would I actually rely on this theorem to predict a regime transition or get the system to work?"*** Ban decorative convex/asymptotic bounds detached from the real algorithm.
4. **Sober Technical Naming Over Suitcase/Anthropomorphic Words (§3.4)**:
   - Ban anthropomorphic terms (*"curiosity module"*, *"consciousness gate"*, *"thought resonance"*) and unpack Minsky **suitcase words** (*"generalization"* $\to$ specify *i.i.d. test risk* vs. *covariate shift* vs. *length extrapolation*; *"interpretability"* $\to$ specify *sparse feature attribution faithfulness* vs. *counterfactual simulatability*).
