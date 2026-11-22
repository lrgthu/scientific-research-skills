# Macro Structure, Sections, Proposals, Limitations & Public Framing

Distilled from Joshua Schimel's *Writing Science* (Chapters 1–9 and 18–21).

---

## 1. The Scientific Storytelling Chain (`Data → Understanding`)

Raw results never speak for themselves. Scientific communication moves rightward along a four-stage chain (five for public/applied audiences):

```text
Data ──► Information ──► Knowledge ──► Understanding (──► Application)
```

- **Data**: Raw instrument readings, logs, or benchmark tables (e.g., Rosalind Franklin's Photo 51 X-ray scattering image; raw loss curves or accuracy numbers). Interpretable only by a tiny circle of specialists.
- **Information**: Processed facts or empirical patterns extracted from data (e.g., helical dimensions of crystallized DNA; "Model A outperforms Model B by 4.2% on long-context tasks").
- **Knowledge**: Mechanistic models, syntheses, or testable theories explaining *how* the system works (e.g., Watson & Crick's base-paired double helix; why attention sink dynamics govern long-context degradation).
- **Understanding**: Broader insight into how that model explains larger phenomena and reshapes future questions (e.g., how complementary base pairing enables cell replication and heredity).
- **Application** *(Public, Clinical, Engineering, & Policy)*: What society, practitioners, or decision-makers can *do* with that understanding.

### Bottom-Up Discovery, Top-Down Telling ("Elaborate and Slash")
1. **Never impose `PLOT` on your characters**: Do not decide the story before analyzing the data. Treat molecules, organisms, ecosystems, models, or mathematical objects as "characters"—listen to both their main trends and their quiet outliers/anomalies (like Dietrich discovering lethal bedrock soil wedges in hillslope outliers).
2. **Elaborate wildly, then slash with Occam's Razor**: Explore boundary mechanisms and alternative explanations until you uncover the true underlying pattern; then pare away every tangent to tell that simple core story from the top down.
3. **Novelty Audit (Ch. 19)**:
   - Answering an *old question* in a *new system/dataset* = **Information** (incremental).
   - Answering an *old question* with a *new technology/architecture* = **Information** (incremental).
   - High-impact venues look for **new questions** (where/why established dogma breaks down, hidden mechanisms, or generalizable laws) that advance **Knowledge** and **Understanding**.

---

## 2. Making Ideas Sticky: `SUCCES` in Science (Ch. 3)

| Factor | Scientific Meaning | Pitfall to Avoid |
| :--- | :--- | :--- |
| **S — Simple** | Distill the core essence of a complex system into a compact principle, equation, or conceptual model anchored in **schemas** your audience already holds. | **Simplistic**: Dumbing down, dodging complexity, or reporting unanalyzed "inconsistency" instead of finding the governing variable (e.g., rich vs. poor soils). |
| **U — Unexpected** | Highlight a concrete **Knowledge Gap**—unmasking specific ignorance bounded by existing knowledge to spark curiosity. | Reinforcing textbook dogma or claiming `"little is known"` without specifying the exact unknown. |
| **C — Concrete** | Ground claims in tangible physical mechanisms, specific examples, and exact numbers. Navigate Clark's **Ladder of Abstraction**: link mid-rung specialist concepts to top-rung universal schemas or bottom-rung concrete data. | Floating in the "middle danger zone" of specialist abstractions and buzzwords ("lipstick on a pig"). |
| **C — Credible** | Maintain an unbroken chain: fair citations → transparent methods → concrete data + honest statistics → conclusions growing directly from those data. | Overselling, boldface hype, or claiming conclusions unsupported by the method's resolution. |
| **E — Emotional** | Engage the two valid scientific emotions: **Curiosity** (via a novel question) and **Excitement** (by satisfying that curiosity—vital to turn a grant panelist into your active advocate). | Appealing to trivia accumulation ("inner nerd" data dumps) or unscientific melodrama. |
| **S — Stories** | Package arguments and datasets into discrete, self-contained modular arcs threaded in series. | Presenting an undifferentiated chronology of everything you measured. |

---

## 3. Macro Story Structures (`OCAR`, `ABDCE`, `LDR`, `LD`) & The Hourglass (Ch. 4)

Every complete piece of scientific writing must fulfill four functional story elements (**`OCAR`** is a principle; `IMRaD` is merely one physical layout rule):
- **O — Opening**: Central characters, context, and the broad motivating problem.
- **C — Challenge**: Specific question(s), falsifiable hypothesis(es), and approach.
- **A — Action**: Methods, empirical/theoretical results, and analytical discussion.
- **R — Resolution**: How understanding of the Opening's broad problem has advanced (closing the **spiral**—returning to the starting topic, which has now moved forward).

### Selecting Structure by Audience Patience

1. **`OCAR` (Slowest — Specialist Journals)**:
   - Unfolds step-by-step: `Opening → Funnel → Challenge` (Introduction), `Action` (Methods, Results, Discussion body), `Resolution` (Conclusions).
   - Specialist readers want to inspect evidence before accepting conclusions; premature chest-beating can look like forcing data into a preconceived plot.
   - **Telegraphed `OCAR`** *(Biomedical & ML/CS Conferences: NeurIPS, ICML, ICLR, CVPR, ACL)*: Full `O → C` Introduction followed by a crisp final paragraph (`"In this paper, we show / make three contributions..."`) so reviewers can evaluate technical sections against the stated claims.

2. **`ABDCE` (Fast — Grant Proposals: NSF, NIH, DOE, DARPA)**:
   - **Action (`A`)**: Launch immediately into dramatic problem + core challenge/hook (*in medias res*) to survive the reviewer's irrevocable `"no/maybe"` cut in the first 1–2 pages (`"If you haven't told them in the first two pages, you haven't told them"`).
   - **Background (`B`)**: Step back to fill in essential literature boundaries, preliminary evidence, and character context.
   - **Development (`D`)**: Research plan, Specific Aims / work packages, methods, and pitfall mitigations.
   - **Climax (`C`)**: Synthesis/integration across aims or scales.
   - **Ending (`E` = Resolution)**: Mandatory closing synthesis paragraph crystallizing why this proposal *must* be funded.

3. **`LDR` (Faster — *Nature*/*Science*/*PNAS*, Abstracts, Executive Reports, Public Articles)**:
   - **Lead (`L`)**: Compresses `O` + `C` + core hook/preview to survive rapid editorial triage.
   - **Development (`D`)**: Evidence, mechanisms, and key figures.
   - **Resolution (`R`)**: High-impact closing insight tying back to the broad Lead.

4. **`LD` (Fastest — Inverted Pyramid)**:
   - Whole point in Sentence 1–2, followed by supporting details.
   - **Use for**: Methods subsections, Results data paragraphs, Right-Opening long sentences, press releases, and 5-minute policy hallway briefs.
   - **Never use pure `LD` for**: Full papers or full grant proposals (omitting `R` leaves reviewers without crystallized language to champion your work).

### The Hourglass Width Rule (Ch. 4.3 & Ch. 5.6)

```text
  \‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾/   Opening (Wide: targets intended community)
    \           /     Funnel  (Narrows via Knowledge Gap)
      |=======|       Challenge (Neck: specific questions/hypotheses)
      |       |       Action: Methods & Results (Stays narrow)
    /           \     Discussion (Widens via synthesis & implications)
  /_______________\   Resolution (MUST match Opening width!)
```

- **Opening wider than Resolution (`Y`-top, narrow bottom)**: Overpromising / bait-and-switch (e.g., opening with global Arctic carbon climate feedbacks, ending with `"winter microbial composition changed little"`). Readers feel cheated.
- **Opening narrower than Resolution**: Underselling (opening with cold-acclimation physiology of tundra bacteria when your results actually reshape global Arctic carbon models). Broad readers quit at Sentence 1.
- **Equal Width (On Target)**: Frame the Opening to promise the exact scope your Resolution delivers. If erring slightly wide in Sentence 1 to attract an interdisciplinary community, narrow immediately within Paragraph 1 (**Two-Step Opening**).

---

## 4. Section-by-Section Engineering Rules (Ch. 5–9)

### A. The Opening (Ch. 5)
Accomplish three goals in the opening power position: **(1) define the driving problem, (2) introduce the central characters, and (3) signal the target audience.**
- **Pawn-Push vs. Queen-Launch**:
  - *Master's Pawn-Push*: A deliberate positioning sentence placing the bridge character in its Stress position so Sentence 2 can narrow immediately (e.g., `"Continental mountain relief reflects a dynamic tug-of-war between tectonic uplift and surface erosion. Bedrock channel incision governs the pace of that erosion..."`). Never write an empty beginner's platitude!
  - *Queen-Launch*: Dive straight into tension, anomaly, or contrast in Sentence 1 (e.g., challenging a 100-year paradigm or contrasting Mars exploration with 99% unseen ocean microbes). Mandatory for *Nature*/*Science* and grant proposals.
- **Two-Step Opening (Interdisciplinary / Review Panels)**:
  - Step 1: Open with a schema shared by the entire panel/readership (e.g., plant community succession for an ecology panel; scaling laws for an ML area chair).
  - Step 2: Pivot briskly (within 2–4 sentences—quick like the dance!) to your specific mechanism (e.g., poplar tannins regulating soil microbes).
- **Tailor to Agency/Venue Mission**: Match the opening character to the funder/journal (e.g., `"ecological processes in coastal zones"` for basic-science NSF vs. `"California's treasured coastal forest resources"` for mission-driven CalEPA).
- **Kill Misdirection & No-Direction**:
  - *Misdirection*: Discussing Mechanism A for a whole paragraph and ambushing the reader with `"However, Mechanism B also..."` in Paragraph 2. Fix with an umbrella positioning sentence (`"X controls Y via two mechanisms..."`).
  - *No Direction*: Textbook definitions (`"In meiosis, genes show linkage..."`). Delete early warm-up paragraphs until you hit where the real story starts.

### B. The Funnel: Connecting `O` and `C` (Ch. 6)
An Introduction is **not** a literature review:
- **Literature Review = Solid Wall** (summarizing everything known about a topic).
- **Introduction = Hole in the Wall** (citing prior work *solely* to define the edges of ignorance and prove why answering `C` is essential to `O`).
- **Three Mandatory Funnel Diagnostics**:
  1. **Never write `"Little is known about X"`**: It is factually dubious, contradicted by your own citations, and linguistically fuzzy. State **concretely** what is missing (`"Only three studies measured k1 below 298 K, where secondary reactions overestimate rates"`).
  2. **Never commit the "Bizzwidget" Fallacy**: Never pitch your method, theory, or architecture (`"We propose Complex Systems Modeling Theory..."`) before establishing the concrete problem and why existing approaches fail. **To sell a solution, first sell the problem.**
  3. **Eliminate `"Smith (2003) found X"` Sentences**: Making authors the grammatical subject tells a story about researchers (data-dump mode) rather than nature. Rewrite as `"X occurs (Smith 2003)"`—*except* when highlighting an unresolved debate (`"Although Smith (2003) reported X, Jones (2005) found Y"` or `"Reports conflict on X, with some suggesting Y (...) and others Z (...)"`).

### C. The Challenge (Ch. 7)
- **Questions First, Objectives Second**: Never write `"Our objectives were to measure A and compare B"` without stating the **question** (`"we did Y"` without `"to learn X"`). Data collection is information; the question defines knowledge.
- **Canonical Template**:
  > `"To determine/test [Question or falsifiable Hypothesis X], we evaluated/measured/constructed [Approach & specific Objectives Y]."`
- **Questions vs. Hypotheses**: Transform a question into a formal hypothesis when testing whether a causal relationship/mechanism exists (`"We hypothesized that captivity reduces hippocampal volume..."`). Keep it as a direct question when quantifying an unknown parameter/rate (`"What is k1 down to 230 K?"`).
- **Intellectual Ordering**: When listing multiple goals, put the **primary scientific question first** (with strong verbs) and methodological validation/calibration **second**—never order goals chronologically just because you calibrated the instrument first!

### D. Action: Methods, Results, Statistics, & Discussion (Ch. 8)
- **Methods (`LD` + Named Schemas)**:
  - Never write a bare opaque pointer (`"measured by Turman et al. 2008"`) that forces readers to hunt down another paper just to understand your logic; never dump raw concentrations (`"25 uM 3-HPAA..."`) without a purpose lead.
  - Write: `"To characterize enzyme inactivation [purpose lead], we incubated PGHS-1 with... / modified the Lowry assay by..."`
- **Results vs. Discussion (Data vs. Inference vs. Interpretation)**:
  - Whether separated or combined, strictly distinguish:
    1. **Data**: What you measured/computed.
    2. **Inference**: Direct logical deductions from data—always put **data before inference** (`"Spectra A and B form complementary subsets [data], demonstrating independently folded modules [inference]"`) so interpretations grow from characters rather than imposing plot.
    3. **Interpretation**: Broader hypotheses, mechanisms, and synthesis.
- **Selecting & Presenting Data ("Murder Your Darlings" + Tabular Reader Expectations)**:
  - Include in main text only data essential to advance the core story; collapse covarying series and archive exhaustive tables in supplementary material/repositories.
  - **Tables & Multi-Panel Layouts (Gopen & Swan Left-to-Right Expectation)**: Because readers scan left to right, place **familiar context, independent variables, regular progressions, or baseline configurations on the LEFT** (e.g., `time (min)` `0, 3, 6, 9...`, or `Dataset / Baseline Architecture`) and **new, discovery-worthy results on the RIGHT** (e.g., `temperature (°C)`, `Proposed Method / Δ Metric`). Reversing columns (putting irregular results on the left and context on the right) or dumping inline key-value strings (`t=15', T=32°; t=0', T=25°...`) forces readers to waste cognitive energy unraveling structure instead of perceiving the discovery.
  - Frame every Results paragraph with **`LD` structure**: Sentence 1 states the synthesized pattern (`"Soil bacterial diversity varied across ecosystems, driven primarily by soil pH [r^2 = 0.58, P < 0.0001]"`), followed by caveats and concrete paired examples.
- **Statistics and Stories (Effect Size > $p$-Value)**:
  - Statistics ($p$, CIs, error bars) establish **credibility** (noise vs. signal); the **story** lives in the **effect size/magnitude and variance explained ($R^2$)**.
  - **Never write**: `"Treatment significantly increased Y (p < 0.05)"` or `"There was no significant effect (p > 0.05)"` (masks whether a $2.3\times$ effect had $p = 0.07$ due to small $N$, committing Type II error and conflating arbitrary threshold interpretation with data).
  - **Always write**:
    - Strong & significant: `"Warming increased methane emissions by a factor of 3.4 (p = 0.02)."`
    - Small & significant: `"Treatment increased response by only 30%, though consistently (p = 0.02)."`
    - Large & noisy: `"Response in the treatment was 2.3 times higher than control, but variable (p = 0.07)."`
    - Noisy correlation: `"The relationship between x and y is weak (R^2 = 0.10) but statistically significant (p = 0.001)."`
- **Discussion Structure**:
  - Build as an independent story arc using either **`LDR`** (open with the main answer/breakthrough, then develop evidence and implications toward `R`) or **`OCAR`** (restate the challenge tension, evaluate lines of evidence, resolve at `R`).

### E. The Resolution (Ch. 9)
Endings are the ultimate power position—readers remember your final words as the take-home message.
- **Walk Backward Through `OCAR`**:
  1. Synopsize the core finding (`A`).
  2. Synthesize what it answers/means as a conceptual model (`C`, e.g., `"p27 Y-phosphorylation acts as a molecular 'switch'"`).
  3. Widen back to the Opening's broad problem (`O`), closing the spiral at the exact width of the Opening.
- **Ending with a Question**: Effective *only* when posing a **concrete new question that grew *from* your results** (pointing forward to the next frontier).
- **Three Resolution Killers (Strictly Ban)**:
  1. **Weak**: Summarizing results and adding `"these findings may provide new insights into complex biology"` without stating *what* the insight is!
  2. **Distracting**: Ending with textbook truisms or **surprise characters/topics** never introduced in the Opening (if a great new implication emerges while drafting, weave it back into the Opening and Introduction!).
  3. **Undermining**: Ending with `"More research is needed to clarify our findings"` or `"although proof of clinical benefit remains to be established."` Flip caveats to the front of the sentence/penultimate paragraph (`"While clinical trials are needed..., our data show X is safe and active in vivo, offering a promising route to..."`).
- **Proposal Resolutions**: Always reserve a final ~0.5-page synthesis paragraph reiterating the big problem, how your multi-scale aims integrate to solve it, and how understanding will transform—handing panelists the exact words to argue `"Must Fund."`

---

## 5. Dealing with Limitations: The `"But, Yes"` Principle (Ch. 18)

Every real study has blemishes. Never use `"Yes, but"` (presenting claims and trailing off into caveats at the end). Use **`"But, yes"`**: address limitations **early, openly, and unapologetically**, constrain your claims to what the methods support, and finish on `"Yes"`.

| Location | When to Use | How to Execute `"But, Yes"` |
| :--- | :--- | :--- |
| **Introduction / Challenge** | Method cannot answer an overly broad question | Narrow the promised Knowledge Gap to match the method's true resolution (e.g., `"bacteria responsive to fresh organic inputs"` rather than `"total soil bacteria"`). |
| **Methods / Proposal "Potential Pitfalls"** | Unreplicated field designs, proxy assays, model assumptions, omitted baselines | Address immediately in Methods (or a dedicated Proposal *Potential Pitfalls* subsection): state the constraint plainly, explain *why* it is unavoidable or acceptable, show how controls/complementary methods bound it, and move on. |
| **Discussion Body** | Caveats affecting quantitative interpretation (e.g., survey bias, measurement ceiling) | Place early/mid-Discussion—ideally tucked into the middle (`3`-position) of an `LD` paragraph or an initial *"Experimental Considerations"* subsection (only when the setup is highly artificial)—never in the final Resolution! |
| **Conclusions** | Unavoidable overarching constraint | Put the detailed limitation discussion in the **next-to-last paragraph**; open the final paragraph with `"Despite these limitations, [strong concrete synthesis and forward contribution]."` |

---

## 6. Nancy Baron's Message Box for Peers, Panels, Public, & Policy (Ch. 20)

Use the **Message Box** to crystallize any proposal, paper abstract, executive summary, or public piece:

```text
               1. PROBLEM?
    (Specific unknown / broken state)
          ┌───────────────────┐
4. BENEFITS?  │   ISSUE (Topic)   │  2. SO WHAT?
(Resolution / │ ───────────────── │  (Why THIS audience
 payoff)      │ TARGET AUDIENCE   │   cares right now)
          └───────────────────┘
              3. SOLUTIONS?
       (Your core discovery / plan)
```

- **Writing for the Public**: Assume readers are **intelligent but lack specialist schemas** (never "dumb down"—use *more* story and `SUCCES`, *less* complexity and jargon). Use **`LDR`**, highlight either `"Huh, who knew?"` curiosity or `Application` (`"How does this affect me?"`), include human actors where natural, and **never** place a technical term in the Topic position of a sentence.
- **Writing for Policy / Decision Makers**: Time budget is ~5 minutes; culture is action/decision-driven. Use ultra-tight **`LD`/`LDR`**, strip technical filler (`"blah, blah, carbon"`), and make your final stress words the concrete actionable implication.
