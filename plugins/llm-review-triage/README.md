# LLM Review Triage & Soul Guard (`v1.0.0`)

Standalone, **strictly on-demand** plugin (`0` bytes of Always-On `rules/AGENTS.md` overhead; never auto-bundled into normal writing, ideation, or coding turns) activated **only** when triaging external LLM / Large Reasoning Model (LRM) peer reviews (`/llm-review-triage` or when pasting critiques from frontier reasoning models).

## Why Frontier Reasoning-Model Reviews Need an Area-Chair Filter

Modern frontier reasoning models have full-manuscript context and strong technical fluency, which makes their failure modes **subtle and seductive** rather than obviously broken:

1. **Adversarial Limitation Weaponization (诚实局限回旋镖)**: Given full-paper recall and a *"be a tough reviewer"* prompt, test-time reasoning chains actively hunt for logically irrefutable vulnerabilities—and latch onto the **exact simplifying assumptions, scale caps, or boundary regimes the authors already honestly disclosed in `Limitations` / `Discussion`**, spinning elaborate counter-scenarios that punish scientific candor.
2. **Test-Time Overthinking & Nitpick Inflation (过度推演找茬)**: Lacking a *"this draft is already sound—stop searching"* reward in critic mode, extended chain-of-thought elevates **measure-zero pathological corner cases, second-order confounders ($O(\epsilon^2)$), notation pedantry, and low-ROI auxiliary sweeps**, dressing minor flaws in intimidating technical prose so every nitpick masquerades as a fatal defect.
3. **Formalist Legalism & Multi-Round Contractive Soul Drift (防御性免责声明陷阱)**: Post-trained heavily against overclaiming, frontier critics treat bold conceptual synthesis and crisp `ABT` claims as "unproven leaps," pressuring authors to shrink insights into tautological empirical logs wrapped in stacked qualifiers. Across $\ge 2\text{–}3$ iterative critique-revision rounds, this acts as a **contractive smoothing operator** (*textual relaxation*) that sands away originality and leaves unreadable legalistic prose (*"不像人话"*).

## Bundled Components

1. **`llm-review-triage` Skill** (`skills/llm-review-triage/SKILL.md` + `references/`):
   - **Pre-Triage Soul Lock**: Freezes the manuscript's `kABT` core insight, paper archetype, and already-disclosed `Limitations` before reading a single external comment.
   - **6-Pathology LRM Critic Filter** vs. **4 High-Leverage Action Categories** (objective math/logic/code defects, high-ROI competing-hypothesis tests, structural comprehension fixes, and single-sentence `"But, yes"` anchors).
   - **Anti-Defensive-Writing Charter**: Enforces **Exact Domain/Equation Scoping over Cowardly Qualifier Chains**, **Single-Locus Caveat Containment**, and **Multi-Round Contractive Drift Hard-Stops**.
2. **Deterministic Diff & Triage Auditor (`scripts/audit_review_and_hedging.py`)**:
   - `diff-audit <before> <after>`: Quantifies English & Chinese hedge-word surges, stacked qualifier chains (`might potentially appear to...` / `在一定程度上可能似乎...`), apologetic reviewer-appeasement scar tissue, Abstract/Intro hook dilution, and word-count bloat.
   - `init-ledger` / `summarize-ledger`: Validates triage acceptance discipline and compiles a concise Markdown **Area-Chair Action Brief**.
