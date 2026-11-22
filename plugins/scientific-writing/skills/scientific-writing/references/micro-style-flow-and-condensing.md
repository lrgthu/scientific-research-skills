# Micro-Architecture, Reader Expectations, Janus Flow, Verbs & Condensing

Synthesized from Joshua Schimel's *Writing Science* (Chapters 10–16) and George D. Gopen & Judith A. Swan's *"The Science of Scientific Writing"* (*American Scientist*, 1990).

---

## 0. Reader-Expectation Theory: Clarification, Not Simplification (Gopen & Swan)

1. **Structure Governs Interpretation**: Readers do not passively absorb facts; they *interpret* meaning from **where** each piece of substance sits within a unit of discourse (clause, sentence, paragraph, section, or table). When structural clues violate reader expectations, readers burn cognitive energy unraveling syntax and interpret the same passage in 10 contradictory ways.
2. **The `[A]/[B]/[C]/[D]` Jargon-Lifting Proof**: Ask ten readers why an opaque scientific paragraph is hard to read, and nine blame technical vocabulary. Yet even if you replace every technical term with placeholders (`URFA6L → [A]`, `immunoprecipitation → [C]`), the passage *still* fails when Subjects and Verbs are separated by 25 words, Topics shift randomly, and Stress positions hold filler! For peer scientific writing, **never dilute technical precision—clarify the structure**.
3. **Skillful Violation Principle**: None of the reader-expectation principles below are rigid algorithms. Great stylists occasionally violate an expectation for dramatic effect—*but only because they fulfill reader expectations 95% of the time*, making the violation stand out as a deliberate highlight rather than habitual confusion.

---

## 1. Internal Structure: Hierarchical Nested Story Arcs (Schimel Ch. 10)

Every unit of discourse—defined as anything with a beginning and an end—is expected to **serve a single function and make a single point**, nested hierarchically:

```text
Whole Paper / Proposal
 └── Major Sections (Intro, Methods, Results, Discussion — never intermingle!)
      └── Subsections / Modules (single method, dataset, or argument)
           └── Paragraphs (unit of composition)
                └── Sentences (Topic → Action Verb → Stress)
                     └── Clauses (Medial Syntactic Closures)
```

### Serial Complete Arcs vs. Broken "Spaghetti" Arcs
- **Rule of Modularity**: Every subsection and paragraph must **open, develop, and resolve its single theme completely** before the next module begins.
- **Why Broken Arcs & Patchwork Insertions Fail**: Discussing Idea A, splicing in Caveat B, returning to Idea A, and drifting to Idea C destroys power positions and multiplies transition waste (3 complete serial arcs need 2 transitions; fragmenting them creates 12+).
- **Beware "Stream-of-Consciousness" Drift**: Sentences can link word-to-word (`California → fish → algae → upwelling → winds → El Niño → CO2 → ocean pH → shellfish`) yet drift across 8 topics with zero thematic closure!
- **5-Question Arc Check**:
  1. Does every section, paragraph, and clause serve **one** clear function?
  2. Are linkages between paragraphs in a section explicit?
  3. Has every extraneous or bolted-on tangent been deleted or moved to its own arc?
  4. Is every topic **fully resolved** before introducing a new topic?
  5. Is every major unit signaled by an informative subhead or clear opening lead?

---

## 2. Paragraphs: The Unit of Composition (Schimel Ch. 11)

Never insert a paragraph break just "to come up for air." Every paragraph must follow a deliberate structure along the **Point-First ↔ Point-Last** spectrum:

- **Point-First Paragraphs (~70–75% — Default Workhorse)**:
  - **`TS-D` (Topic Sentence → Development)**: Sentence 1 states the core claim/pattern; remaining sentences flesh out quantitative details or mechanisms. Ideal for **Methods**, **Results**, and clean arguments.
  - **Extended `LD`**: Takes 2–3 sentences to frame the Lead before developing details.
- **Point-Last Paragraphs (~25–30% — Transitions, Complex Assembly, Openings/Resolutions)**:
  - **`LDR`**: Opens with a framing premise, develops the chain, and lands a synthesized punchline at the end.
  - **`OCAR` Paragraph**: Opens by posing a conditional question/setup (`"If mammoths migrated..., Sr ratios should match... However... Thus, we conclude..."`).
- **Ban Point-Nowhere Paragraphs**: When the *Curse of Knowledge* jumbles 3–4 half-explained threads into one cryptic paragraph, split the threads into separate linked paragraphs and give each a clear `LD`, `LDR`, or `OCAR` shape.

---

## 3. Sentences: `Topic`, Syntactic Resolution, & `Stress` Closure (Schimel Ch. 12 + Gopen & Swan)

Readers take a **"mental breath"** at the start of a sentence (summoning tension to track unfolding syntax) and exhale emphasis at **syntactic closure** ("First things first" in the Topic; "Save the best for last" in the Stress—*never start with strawberry shortcake and work down to broccoli*).

| Position | Grammatical Unit | Reader Expectation (Gopen & Swan + Schimel) | Emphasis (`2–3–1` Rule) |
| :--- | :--- | :--- | :--- |
| **Topic Position** | **Subject / Opening** | **(1) Whose story** the sentence tells + **(2) Backward-linking "old information"** establishing perspective and context *before* asking the reader to consider anything new. | **`2` (Medium)** — Context & orientation |
| **Action & Middle** | **Immediate Main Verb + Modifiers** | **Syntactic Resolution** via immediate arrival of an active, informative verb; middle `3`-position holds secondary qualifiers or gentle term reminders. | **`3` (Lowest — Middle)** — Low-emphasis container |
| **Stress Position** | **Syntactic Closure** (End of clause/sentence) | **New, emphasis-worthy information** arriving right as the reader exhales at syntactic closure. | **`1` (Highest)** — Ultimate interpretive weight |

### Five Precision Sentence Rules

1. **Eliminate Subject–Verb Separation (Syntactic Resolution Rule)**:
   - Without the verb, readers do not know what the subject is doing. While waiting across a 15–25 word interruption (`"The slowest-decaying eigenmode of the cortical population covariance (Mode-1), a low-rank subspace spanning bilateral premotor and parietal regions..., predicts..."`), readers **refuse to grant primary importance to anything inside the gap**, branding it as mere interruptive aside!
   - **Fix**: Reconnect Subject and Verb immediately (`"The slowest-decaying eigenmode is Mode-1, a low-rank subspace...; it predicts..."`), or delete the aside if incidental.

2. **Guard the Stress Position Against Imposters**:
   - When emphatic material is buried mid-sentence, either (a) obvious filler occupies the end and leaves readers guessing what mattered, or worse, (b) **imposter material** (`"...was observed"`, `"...products on the market"`, `"...rather than by weather"`) occupies the Stress and hijacks the reader's interpretation!

3. **Create Secondary Stress Positions Cleanly (`;` / `:` / `both...and` / Lists)**:
   - A sentence's Stress coincides with **syntactic closure**—when the reader knows nothing remains in the syntactic unit except what is presently being read.
   - You can extend sentences effortlessly to 50–100 words ("well-wrought serpents") by creating **medial syntactic closures**:
     - **Semicolon (`;`)** or **Colon (`:`)**: Preceded by a grammatically complete clause, giving the first Stress-worthy item full closure before launching the second (`"...subunit 6 gene; it has been identified as..."`).
     - **Numbered/Indented Lists**: Clearly announced at the end of a lead clause; each list item gets its own internal Stress closure.
     - **Flag Word `both ... and ...`**: Alerts the reader up front that *two* distinct effects will arrive together in a single Stress position (`"these groups serve both to solubilize... and to prevent..."`).
     - **Right-Opening (`LD`) Branching**: Open with a tight `Subject + Action Verb + Core Stress` main clause, then branch rightward with parallel modifying clauses (`"We focused on two members: Rab5, which controls..., and Rab7, which governs..."`).

4. **Obey the Gopen–Swan Sentence Length Law**:
   - Arbitrary 25- or 29-word readability caps are false (10-word sentences can be impenetrable; 80-word well-punctuated sentences can be crystal clear).
   - **True Definition**: **A sentence is too long when—and only when—it has more viable candidates for Stress positions than there are Stress positions available.** Either create an additional Stress position (`;` / `:`) or split into two sentences!

5. **Overcome Linear Writer Anxiety (`Old → New` Nuance)**:
   - Authors write backward sentences (`New info in Topic → Old context in Stress`) because they rush anxiously to jot down a new thought before forgetting it, tacking on context afterward.
   - *Nuanced Principle (Not Naive Rule)*: Since middle words are also old or new, you cannot put *all* old info in the Topic. Instead: **"Put in the Topic position the old information that links backward (and names whose story it is); put in the Stress position the new information you want the reader to emphasize."**

---

## 4. Flow & Structural Logic Debugging (`Janus` Relay + Diagnostics)

```text
LIST (Static):        [Topic A ... Stress 1] ──► [Topic A ... Stress 2]
STORY (Janus Relay):  [Topic A ... Stress B] ──► [Topic B' ... Stress C]
BROKEN / CONFUSING:   [New Topic X ... Old A] ──► [New Topic Y ... Old A]
```

### Three Powerful Paragraph Diagnostics (Gopen & Swan + Schimel)

1. **The Topic-String Diagnostic (Catching Shifting Perspectives)**:
   - List vertically *only* the grammatical Topics of every sentence in a paragraph (e.g., Gopen & Swan's earthquake passage: `Large earthquakes / The rates / Therefore... one / subsequent mainshocks / great plate boundary ruptures / southern segment of San Andreas / smaller standard deviation`).
   - If every sentence introduces brand-new information in the Topic while the true recurring refrain (`recurrence intervals`) hides mid-sentence, rewrite so the controlling character(s) and backward-linking `Old` threads occupy the Topic positions!

2. **Perceiving Hidden Logical Gaps via `Old → New` Alignment**:
   - Dysfunctional syntax **submerges logical holes in the science itself**.
   - *Classic Diagnostic*: Once Sentence 2 places two concrete mechanisms in the Stress (`both to bound per-layer rounding error and to prevent attention-logit saturation`), the reader expects Sentence 3's Topic to pick up those mechanisms. Jumping straight to `"Across benchmarks, 4-bit perplexity degraded by <0.08"` exposes an **unarticulated scientific leap**! You must **supply the missing mechanistic bridge** (`"Once those <0.2% outlier channels are decoupled, the remaining weights follow a compact Gaussian distribution that maps cleanly onto uniform INT4 grids"`).
   - Also check **Global Intruder Sentences** (Schimel Ex. 13.4): If Sentence 1 and Sentence 3 link naturally (`groundwater → low water tables`) across an off-topic Sentence 2 (`industrial landscapes`), **delete or relocate Sentence 2** rather than forcing a passive bridge!

3. **Paragraph-to-Paragraph `Resolution → Opening` Relay**:
   - Open Paragraph $N+1$ by reaching back to grab the Stress or synthesized concept that resolved Paragraph $N$.

---

## 5. Locating & Energizing the Action (Schimel Ch. 14 + Gopen & Swan)

**Reader Expectation**: *Readers expect the action of every clause or sentence to be articulated by its verb.*

### A. The Verb-List Diagnostic (Gopen & Swan)
Extract the vertical list of main verbs in a paragraph. If it reads like `is / is...is / are presumed to be / are transcribed / has / can be alleviated`, the players are on stage doing nothing, forcing readers to guess the hypotheses! Surface the hidden scientific actions (`limit`, `inhibit`, `destabilize`, `accelerate`) as real verbs—which simultaneously exposes whether the causal link between those actions (e.g., how `inhibit` explains `limit`) has actually been stated!

### B. Active vs. Strategic Passive Voice
- **Default to Active Voice** (`Actor → Action Verb → Object`), including direct `"We measured / trained..."` when the authors performed the action.
- **When Passive Voice Is Superior (Gopen & Swan's `Bees vs. Pollen` Rule)**:
  - `"Bees disperse pollen"` tells a story about **bees**; `"Pollen is dispersed by bees"` tells a story about **pollen**. In a paragraph whose continuing character is *pollen* (or *water retention*, or *Complex I*), **the passive sentence is superior** because it keeps the continuing old-information character in the Topic position!
  - Also use passive when the human actor is irrelevant or unknown (`"Samples were collected"`).

### C. Replace Fuzzy Verbs & Zombie Nominalizations

| Weak Fuzzy Verb / Nominalization | Crisp Action Verb / Adjective |
| :--- | :--- |
| `occur`, `facilitate`, `conduct`, `implement`, `affect`, `perform`, `mediate` | `modify`, `increase`, `decrease`, `inhibit`, `limit`, `accelerate`, `invade`, `disrupt`, `bind`, `prune`, `converge` |
| `conducted an investigation of` | `investigated` |
| `caused an enhancement in the recovery of` | `enhanced recovery of` |
| `a failure to reproduce data is often observed` | `models often fail to reproduce data` |
| `there was a general inhibition of transcription` | `it inhibited transcription` |
| `there was a difference between reaction rates` | `reaction rates differed` |

*(Keep nominalizations ONLY when naming established domain schemas like `transcription`, `gene expression`, `epigenetics`, `attention`, or summarizing prior text like `"Despite these limitations..."`.)*

---

## 6. Words: Jargon Placement, Weight, & Noun Trains (Schimel Ch. 15)

- **Technical Term vs. Avoidable Jargon (`2–3–1` Placement)**:
  - Preserve necessary technical terms for specialist audiences; replace pretentious substitutes where plain words are sharper (*terrestrial autotrophs → plants*; *climate regime → climate*; *causative agent of → causes*).
  - **Topic (Start)** = assumes every reader knows it; **Stress (End)** = defines a new term; **Middle (`3`-position appositive)** = `"Programmed cell death, or apoptosis, plays..."` (reminds novices without annoying experts). Spell out acronyms on first use; use intuitive mnemonic group labels (`DEC`/`CON`, not `ASP`/`HBR`).
- **Anglo-Saxon Over Latinate Weight**: Prefer crisp short words (*length/time, death, let/allow, need, show, give, start, try, use, method*) over heavy Latin/French bloat (*duration, mortality, permit/facilitate, necessary, demonstrate, donate, initiate, attempt, utilize, methodology*) unless semantic nuance requires the Latinate word.
- **Compound Nouns vs. Noun Trains**: Flip 2-noun prepositional phrases (`rate of reaction → reaction rate`), but **break up 3–4+ word Noun Trains** (`resource allocation modification`, `microbial community composition influences`) with strategic prepositions to prevent garden-path ambiguity.

---

## 7. Condensing: "Prune Big Limbs, Shake Out Dead Leaves" (Schimel Ch. 16)

Never use tiny fonts or cramped layout tricks to beat page limits. Cut **10–20%+** via:
1. **Prune Big Limbs**: Remove non-essential/superseded datasets and consolidate broken arcs.
2. **Shake Out Dead Leaves (5 Delete-Key Targets)**:
   - **Redundancies**: `"develop, test, and apply"` → `"develop"`; `"most, but not all"` → `"most"`.
   - **Obvious Statements**: `"There is evidence that X can... (Chu 2008)"` → `"X can... (Chu 2008)"`.
   - **Empty Amplifiers**: Cut *very, quite, rather, dramatically, highly, substantially, structural and functional*; replace hype adverbs with **concrete numbers or mechanisms** (`"increased X 42-fold"`). Keep meaning-altering modifiers (*first*, *preliminary*).
   - **Metadiscourse**: Cut `"In this study, we found that aniline did not react"` → `"Aniline did not react"` (keep road-sign metadiscourse only at major transitions).
   - **Verbosity**: Strip multi-defect sludge to actors + actions and rebuild with active verbs, stopping before prose becomes telegraphic or barren.
