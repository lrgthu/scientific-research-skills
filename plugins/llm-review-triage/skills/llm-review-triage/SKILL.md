---
name: llm-review-triage
description: >
  Standalone Area-Chair triage filter and manuscript soul-guard for evaluating
  external LLM / Large Reasoning Model (LRM) peer reviews, simulated referee
  reports, or multi-round AI critique loops. Separates genuine high-leverage
  math, experimental, and structural improvements from weaponized honest
  limitations (Limitation-Boomerangs), test-time overthinking nitpicks,
  low-ROI confounder hunts, multi-round contractive thesis drift, and defensive
  qualifier bloat that destroys human voice and originality. Invoke ONLY when
  the user shares or discusses AI/LLM-generated review feedback, asks which
  simulated review comments are worth addressing, or triggers /llm-review-triage.
  Do NOT invoke during normal drafting, coding, or literature tasks.
---

# LLM Review Triage & Manuscript Soul-Guard Skill (`/llm-review-triage`)

> **Core Premise**: Frontier reasoning models cast as "critical reviewers" exhibit three structural failure modes driven by test-time overthinking and conservative post-training: **(1) Adversarial Limitation Weaponization** (turning boundaries you already honestly disclosed into "major weaknesses"), **(2) Overthinking Nitpick Inflation** (allocating thousands of reasoning tokens to elevate measure-zero edge cases, $O(\epsilon^2)$ confounders, and low-ROI side quests into authoritative-sounding indictments), and **(3) Formalist Epistemic Legalism** (pushing you to bury bold, original insights under stacked defensive qualifiers until multi-round revisions converge into lifeless legal disclaimers). **Act as a seasoned, pragmatic Area Chair + Co-Author: ruthlessly discard noise, protect the paper's soul and human voice, and extract only genuine high-leverage improvements.**

## Reference Modules & Deterministic Auditor

1. **[Frontier Reasoning-Critic Pathologies & Area-Chair Triage Protocol](./references/lrm-critic-pathologies-and-ac-triage.md)** — **Read FIRST when triaging external AI reviews**: Dissects the 6 LRM critic failure modes, the **Causal-Threat × Signal-to-Cost Triage Matrix**, Limitation-Boomerang immunity, Cross-Model Echo collapsing, and **Multi-Round Contractive Drift Stopping Rules**.
2. **[Anti-Defensive-Writing Charter & Human-Voice Preservation](./references/anti-hedging-and-soul-preservation.md)** — **Read BEFORE editing a single sentence in response to an accepted comment**: **Exact Domain/Equation Scoping vs. Qualifier Soup** (English & Chinese contrasts), **Single-Locus `"But, Yes"` Containment**, banning `"reviewer-appeasement scar tissue"`, and preserving `kABT` punchiness.
3. **Bundled CLI Diff & Triage Auditor (`<SKILL_DIR>/scripts/audit_review_and_hedging.py`)**:
   - `uv run "<SKILL_DIR>/scripts/audit_review_and_hedging.py" init-ledger /tmp/triage_ledger.json` — Writes a starter Area-Chair triage JSON ledger.
   - `uv run "<SKILL_DIR>/scripts/audit_review_and_hedging.py" summarize-ledger /tmp/triage_ledger.json --markdown-out ./review_triage_brief.md` — Audits acceptance ratios & round drift and renders a clean Markdown decision brief.
   - `uv run "<SKILL_DIR>/scripts/audit_review_and_hedging.py" diff-audit <before_file> <after_file>` — Compares pre-edit vs. post-edit drafts to catch hedge surges, stacked qualifier chains (`might potentially...` / `在一定程度上可能...`), apologetic scar tissue, Abstract dilution, and bloat!

---

## Mandatory 5-Step Area-Chair Triage Workflow

### Step 1: Lock the Paper's Soul & Disclosed Boundaries BEFORE Reading the Review

Read the manuscript's Abstract, Introduction, Results structure, and Discussion/Limitations **before** evaluating the external review, and lock four **Immutable Anchors**:
1. **Soul & Original Value (`kABT` + Dobzhansky Spine)**: What is the bold, non-trivial insight or formulation that makes this paper worth reading? *(No review edit may flatten, apologize for, or bury this core claim.)*
2. **Paper Genre Contract**: Lock what kind of paper this *is* (*Clean Mechanism/Formulation*, *Diagnostic/Understanding Probe*, *Exact Simplification*, *Scaling/Boundary Law*, or *Systems Kernel*). Never allow an external critic to judge a surgical mechanism or diagnostic paper as if its goal were an exhaustive 12-benchmark engineering survey.
3. **Explicitly Disclosed Limitations Map**: Index every simplifying assumption, scale bound, domain constraint, and deferred direction already honestly stated in the draft (with exact section/line references).
4. **Critique Iteration Round (`R = 1, 2, >=3`)**:
   - **`Round 1`**: Open to high-leverage mechanism tests, real math/notation fixes, and genuine structural clarity gaps.
   - **`Round 2`**: **Objective-Defect-Only Gate**—accept *only* verifiable math/derivation errors, code/metric bugs, or cross-table numeric inconsistencies. Reject new experiment scope expansion and stylistic re-framing!
   - **`Round >= 3`**: **HARD ANTI-DRIFT STOP**—warn the user explicitly that multi-round LRM critique loops contract toward bland, hyper-hedged fixed points; reject 100% of prose/hedging/scope requests unless an objective mathematical or factual error is proven.

---

### Step 2: Decompose & Collapse Cross-Model Echoes

1. Break the external review(s) into atomic claims (`C1, C2, ...`).
2. **Collapse Correlated Model Priors**: If the user ran 2–4 different frontier models on the draft, do **not** treat shared checklist demands (*"extend to non-stationary / multimodal / 70B regimes"*, *"add theoretical convergence guarantees for the heuristic"*, *"tone down claims"*) as independent human-expert consensus—frontier models share heavily overlapping post-training critic rubrics. Judge every point strictly by **Does falsifying/ignoring this actually invalidate our core thesis inside our stated scope?**

---

### Step 3: Ruthless 4-Bucket Triage (Filter by Causal Threat & Signal-to-Cost ROI)

Classify each atomic comment into exactly one bucket (see [lrm-critic-pathologies-and-ac-triage.md](./references/lrm-critic-pathologies-and-ac-triage.md)):

| Triage Bucket | Diagnostic Test | Permitted Action |
| :--- | :--- | :--- |
| **1. `DO NOW — HIGH-LEVERAGE SUBSTANCE`**<br>*(Real bugs, sharp proofs, high-ROI experiments)* | • **True Defect**: Equation/index/sign error, unstated theorem condition needed for validity, data leakage, unfair baseline budget (`Melis` iso-compute gap), or cross-table numeric drift.<br>• **High-ROI Crucial Experiment**: A bounded test that rules out a **realistic first-order rival explanation ($H_2$)** for your main claim at high `Information Gain / Compute Cost`. | Fix the math/metric defect cleanly, or recommend the targeted experiment/ablation with concrete effort estimate. |
| **2. `CLARIFY STRUCTURALLY — ZERO HEDGING`**<br>*(Genuine reader friction, zero soul dilution)* | • **True Exposition Gap**: Undefined symbol, missing protocol detail, ambiguous figure caption, or an important detail buried in Appendix without a forward pointer.<br>• **Genuinely Unstated Real Boundary**: A material scope boundary not yet mentioned anywhere in the draft. | Fix via **structural clarity** (define at first use, add a 5-word `(Appendix B)` pointer, or add **1 crisp sentence** in `Limitations`). **Never add hedge soup!** |
| **3. `IGNORE — LIMITATION BOOMERANG`**<br>*(Punishing your own honesty)* | • Attacks or demands full experimental resolution of a limitation, scale cap, or assumption **already transparently stated** in your `Scope` / `Discussion` / `Limitations`. | **Touch nothing** (at most verify the existing disclosure is clear). Point out the exact lines where you already reported it honestly. |
| **4. `IGNORE — LRM OVERTHINKING & HEDGING TRAP`**<br>*(Artificial nitpicks & soul killers)* | • **Overthinking Corner Cases**: Measure-zero pathological inputs or $O(\epsilon^2)$ confounders that cannot flip the primary conclusion.<br>• **Quota Filler**: Inventing minor gripes solely because the prompt asked for `Weaknesses`.<br>• **Genre/Scope Creep**: Demanding tangential modalities, scales, or decorative theorems (`mathiness`) outside the paper's archetype.<br>• **Defensive-Writing Pressure**: Demanding timid qualifiers (*"preliminarily suggests under specific settings"*) when evidence supports your scoped claim. | **Discard completely.** State in 1 crisp line why obeying it would bloat the paper, dilute the story, or waste compute. |

---

### Step 4: Present the Area-Chair Triage Brief & Pause Before Editing

**HUMAN-IN-THE-LOOP DECISION GATE**: Unless the user explicitly said *"filter and apply directly"*, **output the structured Triage Brief first and let the user pick which `Bucket 1` / `Bucket 2` items to execute**:
- **(1) Locked Soul Summary** (`1–2` lines confirming what will *not* be compromised),
- **(2) Worthwhile Actions (`Bucket 1` + `Bucket 2`, sorted by impact/effort)** — concrete, surgical, non-defensive,
- **(3) Discarded Noise (`Bucket 3` + `Bucket 4`, grouped concisely)** — explaining why each is safe to ignore.

---

### Step 5: Execute Approved Changes Under the Human-Voice & Anti-Hedging Charter

When executing user-approved fixes (consult [anti-hedging-and-soul-preservation.md](./references/anti-hedging-and-soul-preservation.md)):
1. **Calibrate by Exact Noun/Equation Scope, NEVER by Qualifier Chains**:
   - *Forbidden*: `"Our approach may, to a certain extent, potentially help alleviate..."` / `"在一定程度上该框架或许可能有助于缓解……"`
   - *Required*: `"On $L \le 128\text{k}$ causal decoders, rank-16 sketching reduces..."` / `"在 $L \le 128\text{k}$ 的因果解码器上，秩-16 速写将……降低……"` (100% rigorous via explicit domain scope, strong verb, zero cowardly adverbs!).
2. **Single-Locus `"But, Yes"` Containment**: Keep caveats quarantined in the dedicated `Limitations` / scope paragraph—never sprinkle defensive apologies across the Abstract, Introduction hook, section titles, or Results topic sentences.
3. **Seamless Integration (Zero Patchwork Scars)**: Never paste `"To address potential concerns, it is worth noting that..."` scar paragraphs. If an approved new experiment reshapes a section's argument, hand off to `/scientific-writing` while keeping this Soul Lock active.
4. **Mandatory Post-Edit Diff Audit**: Run `uv run "<SKILL_DIR>/scripts/audit_review_and_hedging.py" diff-audit <before_file> <after_file>` and confirm **zero stacked hedge chains**, **zero apologetic boilerplate**, and **preserved Abstract/Intro punchiness**!
