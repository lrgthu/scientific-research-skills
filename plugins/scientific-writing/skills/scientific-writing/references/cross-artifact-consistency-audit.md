# Cross-Artifact Numeric, Protocol & Directional Consistency Audit (跨正文—跨图—跨表数字与协议一致性锁死协议)

Nothing destroys reviewer trust faster—especially in rigorous empirical, benchmark, ablation-heavy, or small-effect / null-result (`Miniplot` / $10^{-3}$-scale $\Delta$) papers—than discovering that **the same baseline on the same dataset has three different numbers in `Table 2`, `Table S3`, and `Table S4`**, or that **a figure caption claims `Method A > Method B` while a supplementary table prints `Method A < Method B`**.

Even when the underlying science and code are 100% sound, cross-artifact discrepancies make it impossible for reviewers to tell which numbers represent the canonical protocol or which comparisons remain strictly paired.

---

## 1. Taxonomy of the 6 Reviewer-Fatal Consistency Pathologies

Audit every manuscript, rebuttal, and supplement explicitly against all six root causes:

| # | Pathology | Typical Underlying Root Cause | How Reviewers Catch It |
| :--- | :--- | :--- | :--- |
| **1** | **Silent Aggregation Operator Drift** (*隐式聚合口径漂移*) | Per-unit/per-subject/per-fold predictions are identical, **but** `Table 2` reports the **equal-weighted macro-mean** across $S$ units ($\frac{1}{S}\sum_{s=1}^S M_s$), whereas `Table S3` reads a summary field computing the **pooled micro-metric** ($M(\bigcup_s \mathcal{D}_s)$, e.g., $1 - \frac{\sum_s \text{SSE}_s}{\sum_s \text{SST}_s}$, or token-level vs. sequence-level accuracy). | Same `(Dataset, Region/Subset, Baseline)` prints `0.2106` in `Table 2` vs. `0.2071` in `Table S3`—exceeding the $10^{-3}$ effect size discussed in the paper! |
| **2** | **Unbadged Protocol / Feature / Mask Shift** (*同名异构协议混淆*) | An ablation table (`Table S4`) re-fits a baseline under a **truncated SVD rank $r$, lower token budget, re-selected top-$K$ mask, or altered split** so it pairs fairly with a compact ablation model—**yet labels the row with the unadorned canonical baseline name**. | Reviewer puts `Table 2` (`0.2911`) next to `Table S4` (`0.2724`) and flags an unexplained `0.0187` drop on the "exact same" baseline. |
| **3** | **Cross-Artifact Directional / Sign Inversion** (*图文/主附结论方向反转*) | Under **pooled selection** (`P-Pool`), Method A leads (`0.495 > 0.491`). Under **per-individual / per-domain stratified selection** (`P-Strat` in `Table S5`), Method B leads (`0.491 > 0.480`). A figure caption or prose bullet carelessly generalizes the pooled takeaway (`"Method A leads on Cohort X"`) onto the stratified breakdown, or plots pooled bars beside a stratified table. | Outright **sign/ranking contradiction**: `Figure S1` caption says `A > B`, while `Table S5` literally prints `A = 0.4800 < B = 0.4905`. |
| **4** | **Multi-Round Stale Cache / Script Skew** (*多轮实验陈旧缓存漂移*) | Main `Table 1` and `Results` were regenerated from `v36` JSON outputs after fixing preprocessing, while `Abstract`, `Introduction` preview, `Figure 4` script, or `Appendix Table S2` still hardcodes or loads `v32` JSONs. | Abstract claims `+4.1%` gain (`84.7%`), while `Table 1` shows `84.2%` vs. `80.5%` (`+3.7%`). |
| **5** | **Arithmetic, Unit, & Percentage-Point (`pp`) Confusion** (*算术差值与相对/绝对百分比混淆*) | Prose computes $\Delta$ from rounded display numbers when the table computed $\Delta$ before rounding (without noting it), or calls an increase from `20.0%` to `22.0%` a `"2% improvement"` (ambiguous) vs. `"10% improvement"` (relative) without distinguishing **`+2.0 percentage points (pp)`** from **`+10.0% relative`**. | Reviewer subtracts two table columns and gets a different $\Delta$ than stated in the text or abstract. |
| **6** | **Sample-Size ($N$), Split, & Hyperparameter Drift** (*元数据与超参前后不一*) | `Methods` states `5-fold nested CV, n = 10 seeds, λ = 0.1`; `Figure 2` caption states `n = 5 seeds`; `Appendix B` lists `8-fold CV` or `Top-1000` instead of `Top-500`. | Erodes confidence in experimental hygiene across the entire submission. |

---

## 2. Mandatory Solution 1: The Explicit Protocol Identity Registry (`P1`, `P2`, ...)

Whenever a manuscript contains multiple evaluation regimes (e.g., canonical full-rank benchmark vs. dimension-matched ablation vs. pooled-cohort vs. per-subject stratified evaluation), **bind every quantitative table, figure panel, and prose claim to a named Protocol ID (`P1`, `P2`, `P3-Pool`, `P3-Strat`)**.

### A. The 8-Tuple Experimental Identity Binding
Every reported number must have an unambiguous answer to all 8 coordinates:
1. **`Protocol ID`**: Short immutable badge (`P1`, `P2`, `P3-Pool`, `P3-Strat`).
2. **`Dataset & Target Definition`**: Exact dataset version, target variable, and preprocessing normalization.
3. **`Sample & Unit / ROI Mask`**: Exact filtering rule (e.g., *"training-only noise ceiling $\ge 10\%$, top-500 units selected strictly inside outer training fold"*—never test-leaked!).
4. **`Feature / Representation Version & Dimensionality`**: Exact backbone checkpoint, layer, and projection/SVD rank $d$ or $r_g$.
5. **`Split & Pairing Scope`**: Outer/inner CV folds or canonical train/val/test split, plus **which models share identical folds/masks and are therefore strictly paired**.
6. **`Exact Aggregation Formula`**: Mathematical definition distinguishing **Macro-Average** ($\bar{M}_{\text{unit}} = \frac{1}{S}\sum_{s=1}^S M_s$) from **Micro/Pooled Metric** ($M_{\text{pool}} = f(\sum_s \text{num}_s, \sum_s \text{den}_s)$).
7. **`Seeds & Uncertainty Estimator`**: Exact random seed set, replicate count $n$, and CI/SE formula (e.g., paired hierarchical bootstrap over $10{,}000$ resamples).
8. **`Authoritative Source Artifact`**: Exact canonical JSON/CSV/Parquet output file generated by deterministic scripts.

### B. Strict Disambiguation Rule in Main & Appendix Tables
- **Same Protocol (`P1` in `Table 2` and `Table S3`)**: Shared baseline cells **MUST match to the exact last decimal digit** (`0.2106 == 0.2106`). Zero silent re-aggregation!
- **Different Protocol (`P1` in `Table 2` vs. dimension-matched `P2` in `Table S4`)**:
  1. **Badge the table header, caption, and row/column explicitly**: e.g., `Stage-1 Ref. (Protocol P2: rank-r SVD)` rather than bare `Stage-1 Ref.`!
  2. **State the Pairing Scope & Gap Explanation in the Caption/Appendix**: Explicitly state *"All columns within Table S4 share identical rank-$r$ SVD inputs (`Protocol P2`) for strict parameter-matched comparison; the `0.011–0.019` shift relative to full-rank `Protocol P1` (Table 2) reflects SVD rank truncation alone."*

### C. Ready-to-Use Appendix Protocol Registry Template

Include a compact **Protocol & Pairing Registry** table in your Reproducibility Appendix whenever $>1$ evaluation regime exists:

| Protocol ID | Used In | Cohort & Mask | Feature / Rank | Split & Pairing | Exact Aggregation Formula | Source Artifact |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`P1` (Canonical)** | `Tab. 1, 2`, `Fig. 2, 3`, `Tab. S2, S3` | Full benchmark; train-fold mask | Full-rank Stage-1 ($d = 4096$) | 5-fold outer OOF; **strictly paired across all `P1` tables** | Equal-weight unit mean $\bar{R}^2 = \frac{1}{S}\sum_s R^2_s$ | `results/canonical_p1.json` |
| **`P2` (Rank-Matched)** | `Tab. S4` only | Same split; rank-$r$ train mask | Truncated SVD ($r \in \{96, 160\}$) | Strictly paired **within `Tab. S4`** against compact MLP | Same $\bar{R}^2 = \frac{1}{S}\sum_s R^2_s$ | `results/svd_matched_p2.json` |
| **`P3-Pool` vs. `P3-Strat`** | `Fig. S1a` (`Pool`) vs. `Fig. S1b, Tab. S5` (`Strat`) | Pooled 2,048 channels vs. per-individual | Full-rank Stage-1 | Paired within each selection scope | Pooled $R^2_{\text{pool}}$ (`P3-Pool`) vs. per-individual $R^2_{\text{pool}, a}$ (`P3-Strat`) | `results/stratified_p3.json` |

---

## 3. Mandatory Solution 2: Single-Source-of-Truth (`SSOT`) Generation & `pytest` Assertions

**Never hand-type experimental metrics into `.tex` prose or maintain separate aggregation math across `make_table2.py`, `make_supp_tables.py`, and `plot_fig3.py`.**

1. **One Canonical Metric Reader**: Write **one** shared Python function `load_protocol_metrics(protocol_id)` that reads the authoritative result JSON/Parquet and applies the single canonical aggregation formula.
2. **Programmatic Emission**:
   - Generate all main `.tex` tables, supplementary `.tex` tables, figure `.pdf`/`.png` panels, **and** a `\input{generated/metrics_macros.tex}` file (`\newcommand{\valAlphaDivNorm}{0.2106}`) from that single reader.
3. **Hard Cross-Artifact Consistency Test (`pytest` Gate)**:
   Add a deterministic test that fails CI/build immediately if any shared `(protocol, dataset, subset, method, metric)` diverges across tables, macros, or figure data arrays:

```python
def assert_cross_artifact_consistency(tables_registry: dict[str, dict[tuple, float]], tol: float = 1e-6) -> None:
    """Fail immediately if any two tables under the same Protocol ID disagree on a shared cell."""
    seen: dict[tuple, tuple[str, float]] = {}
    for table_id, cells in tables_registry.items():
        # key = (protocol_id, dataset, subset, method, metric_name)
        for key, val in cells.items():
            if key in seen:
                prev_table, prev_val = seen[key]
                diff = abs(val - prev_val)
                assert diff <= tol, (
                    f"CROSS-TABLE DRIFT on {key}: {prev_table}={prev_val:.6f} vs {table_id}={val:.6f} (diff={diff:.6g})"
                )
            else:
                seen[key] = (table_id, val)
```

---

## 4. Mandatory 5-Matrix Pre-Submission Consistency Audit Checklist

Before declaring any manuscript, revision, or rebuttal complete (and during **Anti-Patchwork `Tier-2 / Tier-3`** rewrites and **`SCFL` Pass 5**), run `lint_manuscript_visuals.py` on the full flattened LaTeX tree (`main.tex` + `appendix.tex`) **AND** verify these five cross-check matrices:

1. **Matrix 1 — `Abstract ⇄ Intro Preview ⇄ Results ⇄ Discussion ⇄ Conclusion`**:
   - [ ] Every headline score, $\Delta$, fold-change, $p$-value, dataset count, and parameter/budget figure in the Abstract matches the exact numbers in `Results` and main tables (zero `ABSTRACT_UNMATCHED_NUMBER` warnings).
   - [ ] Absolute differences (`+3.2 percentage points` / `+0.0187 R^2`) are never conflated with relative ratios (`1.04x` / `+3.9% relative`).
2. **Matrix 2 — `Main Tables ⇄ Supplementary / Appendix Tables`**:
   - [ ] Zero `CROSS_TABLE_VALUE_CONFLICT` warnings in `lint_manuscript_visuals.py`: every shared `(Dataset, Region/Subset, Baseline, Metric)` cell matches across all tables sharing a protocol.
   - [ ] Any table using a modified feature rank, subset mask, split, or aggregation formula carries an explicit **`Protocol ID` badge (`P2`)** in its caption and headers, with pairing boundaries stated explicitly.
3. **Matrix 3 — `Rendered Figures ⇄ Tables (Visual Value & Rank Lock)`**:
   - [ ] Call `read_file` on every rendered `.png`/`.pdf` figure (main + supplement!) and cross-check bar heights, dot coordinates, reference lines, and legend labels against the corresponding table cells.
   - [ ] Verify that every subgroup/baseline discussed in the text or companion table is actually plotted in the figure panel (no missing strata!).
4. **Matrix 4 — `Captions & Prose Claims ⇄ Stratified Subgroups (Zero Sign Inversion)`**:
   - [ ] Check every directional claim (`"A outperforms B on X"`, `"universal gain across cohorts"`, `"monotonic improvement"`): verify that **every** named subgroup `X` actually satisfies `A > B` in the corresponding table/panel!
   - [ ] Never project a **pooled-cohort** result onto **per-subject / per-stratum** breakdowns without checking Simpson's paradox / subgroup reversals; use Schimel's **`"But, yes"`** framing to report honest subgroup nuances explicitly.
5. **Matrix 5 — `Methods & Equations ⇄ Captions ⇄ Tables (Metadata & Symbol Lock)`**:
   - [ ] Sample sizes ($N$), seed counts ($n$), CV fold counts ($K$), statistical test names, confidence level (`95% CI` vs. `SEM`), hyperparameter defaults, and mathematical notation ($\beta, \lambda, r_g$) match **100% identically** across `Methods`, equations, captions, and appendix tables.
