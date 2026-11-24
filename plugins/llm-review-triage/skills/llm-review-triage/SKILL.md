---
name: llm-review-triage
description: >
  Standalone Area-Chair triage filter and manuscript soul-guard for evaluating
  external LLM / Large Reasoning Model (LRM) peer reviews, simulated referee
  reports, or multi-round AI critique loops. Enforces mandatory item-by-item
  adversarial critical thinking (zero reflexive agreement) BEFORE allowing any
  comment into resolution/response planning; filters out weaponized honest
  limitations, test-time overthinking nitpicks, multi-round contractive thesis
  drift, and defensive qualifier bloat. Invoke ONLY when the user shares or
  discusses AI/LLM-generated review feedback, asks which simulated review
  comments are worth addressing, or triggers /llm-review-triage. Do NOT invoke
  during normal drafting, coding, or literature tasks.
---

# LLM Review Triage & Manuscript Soul-Guard Skill (`/llm-review-triage`)

> **Ironclad Behavioral Law — Zero Reflexive Agreement & Strict Two-Phase Gate**:
> Frontier reasoning models write hyper-fluent, authoritative-sounding critiques even when their premise is false, already addressed, or second-order trivial. **You are STRICTLY FORBIDDEN from nodding along (*"The reviewer raises a valid/fair point..."*) or brainstorming fixes while reading a comment.**
> You **MUST** enforce a hard two-stage separation:
> - **Stage A (Item-by-Item Adversarial Cross-Examination)**: Interrogate **every single comment individually** against the manuscript's actual text/math/data with a presumption of skepticism, actively testing whether the reviewer's premise is factually wrong, logically flawed, out of scope, or negligible in causal impact. **Zero solution/edit planning is permitted in Stage A.**
> - **Stage B (Resolution & Response Design — Survivors Only)**: **ONLY** comments that survive all 5 critical-thinking checks in Stage A may advance to Stage B to design surgical experiments, equation fixes, or non-defensive clarifications. Rejected comments get **zero** "just-in-case" compromise edits or footnotes.

## Reference Modules & Deterministic Auditor

1. **[Anti-Sycophancy Cross-Examination & LRM Critic Pathologies](./references/lrm-critic-pathologies-and-ac-triage.md)** — **Read FIRST upon receiving any external review**: The **5-Question Per-Comment Falsification Protocol**, worked examples of deconstructing intimidating-but-flawed LRM critiques, the 6 LRM critic failure modes, and **Multi-Round Contractive Drift Stopping Rules**.
2. **[Anti-Defensive-Writing Charter & Human-Voice Preservation](./references/anti-hedging-and-soul-preservation.md)** — **Read BEFORE designing Stage-B prose edits for surviving comments**: **Exact Domain/Equation Scoping vs. Qualifier Soup** (English & Chinese contrasts), **Single-Locus `"But, Yes"` Containment**, banning `"reviewer-appeasement scar tissue"`, and preserving `kABT` punchiness.
3. **Bundled CLI Triage & Diff Auditor (`<SKILL_DIR>/scripts/audit_review_and_hedging.py`)**:
   - `uv run "<SKILL_DIR>/scripts/audit_review_and_hedging.py" init-ledger /tmp/triage_ledger.json` — Scaffolds a two-stage Area-Chair triage JSON template requiring `critical_audit` per comment.
   - `uv run "<SKILL_DIR>/scripts/audit_review_and_hedging.py" summarize-ledger /tmp/triage_ledger.json --markdown-out ./review_triage_brief.md --strict` — Rejects missing per-comment critical audits, sycophantic agreement phrases, compromise edits on rejected comments, and Round $\ge 3$ drift.
   - `uv run "<SKILL_DIR>/scripts/audit_review_and_hedging.py" diff-audit <before_file> <after_file> --strict` — Audits pre- vs. post-edit drafts to block stacked hedge chains (`might potentially...` / `在一定程度上可能...`), apologetic scar tissue, Abstract dilution, and bloat!

---

## Mandatory Two-Stage Execution Workflow

### Pre-Gate: Lock the Paper's Soul & Disclosed Scope First

Read the manuscript's Abstract, Introduction, equations/tables, and Discussion/Limitations **before** reading the review, and record four **Immutable Anchors**:
1. **Soul & Original Value (`kABT` + Dobzhansky Spine)**: What bold insight or formulation gives this paper its life? *(Off-limits to dilution.)*
2. **Paper Genre Contract**: Lock the paper's archetype (*Mechanism/Formulation*, *Diagnostic/Refutation*, *Exact Simplification*, *Scaling/Boundary Law*, or *Systems Kernel*).
3. **Explicitly Disclosed Limitations Map**: Index every assumption, scale cap, and boundary already transparently stated in the draft (with exact section/line pointers).
4. **Critique Round (`R = 1, 2, >=3`)**: `Round 1` = open to surviving high-ROI substance; `Round 2` = objective math/code/numeric bugs only; `Round >= 3` = **HARD CONVERGENCE STOP** (reject all non-bug edits to prevent contractive relaxation into legalese).

---

### Stage A: Mandatory Item-by-Item Adversarial Cross-Examination (严禁轻易认同 · 严禁提前想改法)

Decompose the external review(s) into atomic comments `C1, C2, ..., CN` (collapsing duplicate echoes across multiple models—shared RLHF critic priors are **not** independent expert consensus).

For **EVERY SINGLE comment `Ci` (`i = 1..N`, zero batch-skipping)**, execute all **5 Critical Interrogation Questions** in order—**do NOT propose any edit, experiment, or wording change during Stage A**:

1. **Q1 — Textual & Mathematical Fact-Check (核对原文与公式事实)**:
   - Check the exact lines, equations, tables, code, and Appendix of the manuscript. Did the reviewer misread notation, overlook an existing ablation/proof detail, or attack a strawman claim we never made?
2. **Q2 — Premise & Counter-Claim Falsification (质疑审稿人推论本身)**:
   - Do **not** assume the reviewer's math or domain intuition is right just because it sounds sophisticated! Ask: *Is the reviewer's claimed failure mechanism or theoretical objection actually true in our regime, or does their counter-argument rely on a false assumption, wrong asymptotic scaling, or inapplicable textbook convention?*
3. **Q3 — Honest Boundary & Genre Immunity Check (核对已声明边界与体裁契约)**:
   - Did we already disclose this exact boundary honestly in `Limitations`/`Scope` without overclaiming in the Abstract (`LIMITATION_BOOMERANG`)? Does the request violate our paper's Genre Contract (e.g., demanding decorative toy `mathiness` on an empirical paper or 10 extra benchmarks on a focused diagnostic study)?
4. **Q4 — First-Order Causal Flip Test (一阶结论翻转检验)**:
   - Even if `Ci` is factually accurate, theoretically valid, and unstated: *Is there a realistic ($>10\%$) probability that this issue reverses our primary conclusion, invalidates our core mechanism, or causes a careful human expert to misinterpret our contribution?* Or is it test-time overthinking on a measure-zero edge case / $O(\epsilon^2)$ confounder?
5. **Q5 — Soul & ROI Gate (护魂与信噪比裁决)**:
   - Does addressing `Ci` genuinely sharpen the paper's truth/impact at high `Signal / (Compute + Prose Cost)`, without blunting the `kABT` spine?

#### Hard Stage-A Gate Verdict (Per Comment `Ci`)
- **`REJECTED_AT_AUDIT` (`survives_scrutiny = false`)**: Failed **any** of Q1–Q5 (`PHANTOM_OR_MISREAD`, `FLAWED_REVIEWER_PREMISE`, `LIMITATION_BOOMERANG`, `OVERTHINKING_NITPICK`, `LOW_ROI_SCOPE_CREEP`, `GENRE_MISMATCH`, or `DEFENSIVE_HEDGING_TRAP`).
  - **Hard Rule**: Terminated immediately. **Zero** manuscript edits, **zero** "compromise footnotes," **zero** "softening a word just to placate them."
- **`SURVIVES_CRITICAL_AUDIT` (`survives_scrutiny = true`)**: Passed **all** Q1–Q5—you verified against the manuscript and first principles that the critique exposes a **real math/logic/code defect**, a **high-ROI competing-hypothesis gap ($H_2$)**, or a **genuine reader comprehension stumbling block**.
  - **Only these survivors enter Stage B!**

---

### Stage B: Surgical Resolution & Response Design (仅限通过完整批判性质询的幸存条目！)

**ONLY** for comments marked `SURVIVES_CRITICAL_AUDIT = true`:

1. **Assign Surviving Bucket & Design Non-Defensive Action**:
   - **`DO_NOW_SUBSTANCE`**: Fix the verified equation/sign/code/leakage defect cleanly, or specify the bounded, high-ROI experiment/control (e.g., iso-compute simple baseline) with concrete runtime cost.
   - **`CLARIFY_STRUCTURALLY`**: Resolve genuine reader friction via **structural placement** (define symbol at first use, add a 5-word `(Appendix B)` pointer, quarantine intuition vs. theorem cleanly, or add **at most 1 crisp sentence** in the dedicated `Limitations` locus).
2. **Present the Two-Stage Triage Ledger & Pause for User Confirmation**:
   - Unless the user explicitly instructed *"audit and apply directly"*, **stop and present**:
     1. **Locked Soul Anchor**,
     2. **Stage-A Per-Comment Critical Interrogation Log** (showing *why* each comment survived or failed Q1–Q5, proving zero reflexive agreement), and
     3. **Stage-B Proposed Surgical Actions (for survivors only)**—waiting for the user's green light before modifying the manuscript.
3. **Execute Approved Survivor Fixes Under the Anti-Hedging Charter** ([anti-hedging-and-soul-preservation.md](./references/anti-hedging-and-soul-preservation.md)):
   - **Exact Noun/Equation Scope Over Qualifier Chains**: Scope claims with concrete nouns/numbers (*"Across 7B–14B causal decoders up to 128k tokens..."*), **NEVER** stacked hedges (*"might potentially appear to..."* / *"在一定程度上或许可能有望……"*).
   - **Single-Locus `"But, Yes"` Containment & Zero Scar Tissue**: Keep boundaries in one dedicated paragraph; ban `"It is worth noting that..."` / `"需要指出的是……"` scar phrases.
   - **Mandatory Post-Edit Diff Verification**: Run `uv run "<SKILL_DIR>/scripts/audit_review_and_hedging.py" diff-audit <before_file> <after_file> --strict` to verify zero stacked hedges, zero scar tissue, and intact Abstract/Intro punchiness!
