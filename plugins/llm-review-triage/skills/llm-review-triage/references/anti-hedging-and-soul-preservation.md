# Anti-Defensive-Writing Charter & Human-Voice Preservation

When an external review raises a **legitimate** boundary or over-generalization point (`Bucket 2`), most authors—and almost all unguided AI revisers—fix it the **wrong** way: by injecting hedging adverbs, throat-clearing disclaimers, and bolt-on patch paragraphs until the manuscript reads like a frightened legal contract (*"不像人话"*).

Follow these five rules to maintain **100% scientific rigor AND 100% sharp, confident human voice**.

---

## Rule 1: Scope by Concrete Domain Noun / Number, NEVER by Stacked Hedge Words

Epistemic rigor comes from **stating the exact domain where your evidence holds**, NOT from stacking modal/adverbial qualifiers (`may`, `might`, `potentially`, `somewhat`, `preliminarily`, `to some extent`, `tend to`, `appear to` / `在一定程度上`, `可能`, `或许`, `似乎`, `有望`, `初步`).

### English Contrasts

| Raw Overclaim | TOXIC Defensive Revision *(Banned!)* | SHARP Calibrated Revision *(Required!)* |
| :--- | :--- | :--- |
| *"Rank-16 key sketching eliminates long-context retrieval degradation."* | *"To some extent, under certain evaluated model configurations and task settings, our preliminary rank-16 sketching heuristic may potentially help mitigate portions of retrieval degradation."* *(31 words, 6 hedges, zero information!)* | *"Across 7B–14B decoders up to 128k tokens, rank-16 key sketching recovers 99.1% of full-cache multi-hop recall."* *(17 words, **0 hedges**, exact scope + exact effect size!)* |
| *"Standard KV eviction fails because it ignores dormant subspaces."* | *"It could perhaps be argued that standard eviction heuristics might sometimes underperform partly due to potential neglect of low-score subspaces."* | *"Score-accumulating KV eviction drops keys that stay dormant during early hops, cutting 2-hop recall by 38 percentage points (Fig. 2a)."* |

### 中文对比（拒绝“免责声明体”，保留干净人话）

| 原始过满表述 | 错误的防御性改法 *(严禁！不像人话)* | 正确的精确边界改法 *(利落、准确、有锋芒)* |
| :--- | :--- | :--- |
| *“我们的方法彻底解决了长上下文检索退化问题。”* | *“在某种程度上，在本文所考察的部分特定受限实验设定与超参配置下，我们初步提出的框架或许可能有望在一定范围内较为有效地缓解部分检索退化现象。”* | *“在 7B–14B 模型及 128k 上下文范围内，秩-16 残差速写恢复了全量缓存 99.1% 的多跳检索召回率。”* |
| *“实验证明传统方法存在本质缺陷。”* | *“值得注意的是，尽管现有基线在诸多场景依然有效，但我们的实验结果似乎初步暗示其在特定多跳条件下可能存在一定局限。”* | *“当推理跳数 $\ge 2$ 时，累积注意力驱逐会误删早期休眠的关键向量，导致召回率骤降 38 个百分点（图 2a）。”* |

**Hard Quantitative Cap**: Never place **$\ge 2$ epistemic hedges in the same clause** (`might potentially`, `somewhat appear to`, `可能在一定程度上`). At most **one** clean epistemic verb (`suggests`, `indicates`) is allowed **only** when separating *Empirical Data* (zero hedges!) from *Speculative Mechanism Hypothesis* (quarantined explicitly as a hypothesis).

---

## Rule 2: Single-Locus `"But, Yes"` Containment (单点集中边界法)

Synthesizing Joshua Schimel's **`"But, yes"`** principle (*Writing Science*, Ch. 15):

1. **Quarantine Limitations in ONE Designated Locus**:
   - State methodological and scope boundaries **once**, candidly and unapologetically, in the dedicated `Scope & Limitations` subsection (or early Discussion paragraph), immediately followed by **why the core contribution remains valid and useful within its target domain (`"But [boundary X]; yes [core insight Y holds cleanly across Z]"`)**.
2. **Keep High-Leverage Locations 100% Caveat-Free**:
   - **NEVER** inject reviewer-appeasement caveats into:
     - The **Title**,
     - **Abstract** opening or `THEREFORE` takeaway sentence,
     - **Introduction** `kABT` hook or contribution bullets (unless a single crisp domain noun like *"for causal transformers"* suffices),
     - **Section / Subsection headings**, or
     - **Results** point-first topic sentences (`LD` leads).

---

## Rule 3: Zero "Reviewer-Appeasement Scar Tissue" (严禁补丁疤痕句)

When an author caves to an external reviewer, they leave telltale meta-discourse scars that break Gopen & Swan's `Old (Topic) → New (Stress)` flow. **Strictly ban all of the following phrases in manuscript prose** (save reviewer dialogue strictly for a separate rebuttal letter if responding to human referees!):

- *"It is worth noting / important to note / should be noted that..."* (`值得注意的是 / 需要指出的是`)
- *"To address potential concerns regarding..."* (`为了回应潜在的顾虑……`)
- *"We acknowledge that our method is not a silver bullet / panacea and..."*
- *"While we do not claim universal superiority across all conceivable settings..."*
- *"One might argue that..., however, we emphasize that..."* (unless framing a genuine scientific `H1 vs H2` test!)

Instead, weave any genuinely needed definition or scope noun directly into the natural subject/object of the existing sentence.

---

## Rule 4: Protect Conceptual Intuition via Explicit Quarantine, Not Deletion

Frontier formalist critics often attack intuitive geometric or physical analogies (*"Calling this 'subspace aliasing' is informal unless you prove a Nyquist sampling theorem"*).
- **Wrong Reaction**: Deleting the vivid intuition that made readers *understand* your method in 10 seconds, leaving dry symbol manipulation.
- **Right Reaction (*Lipton & Steinhardt Quarantine*)**: Keep the vivid intuition, label it honestly as **geometric intuition** in 3 words (*"Intuitively, hard eviction acts like..."*), and keep your formal proposition/algorithm statement mathematically crisp right below it. You get **both** memorable human intuition **and** unassailable formal precision!

---

## Rule 5: Pre-Commit vs. Post-Edit Soul Check (`diff-audit`)

Before accepting any review-driven manuscript edit, verify four invariants (automated via `scripts/audit_review_and_hedging.py diff-audit`):
1. **Did `hedges_per_100_words` stay flat or decrease?** (Any jump $> +0.5$ hedges / 100 words signals defensive regression.)
2. **Zero `STACKED_HEDGE_CHAIN`s and zero `APOLOGETIC_SCAR_TISSUE` matches** in added/modified lines.
3. **Did mean sentence length in the Abstract & Introduction stay $\le 28\text{–}32$ words?** (Defensive clause-stuffing bloats sentences past Gopen–Swan syntactic closure.)
4. **Read the Abstract & Conclusion aloud**: Does it still sound like a confident human scientist sharing a sharp discovery, rather than a committee of lawyers?
