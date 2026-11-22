# Scientific Writing & Figures (Global Research Communication Suite `v1.3.0`)

Global Antigravity plugin (`isGlobal: true`) bundling **two decoupled, on-demand skills** plus a unified **Always-On Global Rule (`rules/AGENTS.md`)** for scholarly writing, data visualization, and publication figure/table engineering:

1. **`scientific-writing` Skill** (`skills/scientific-writing/SKILL.md` + `references/`):
   - Synthesizes **Joshua Schimel's *Writing Science*** (Oxford University Press) and **George D. Gopen & Judith A. Swan's *"The Science of Scientific Writing"*** (*American Scientist*, 1990).
   - Enforces the **Anti-Patchwork Holistic Reconstruction Protocol** on full-paper and post-experiment iterations.
2. **`scientific-figures` Skill** (`skills/scientific-figures/SKILL.md` + `references/` + `resources/`):
   - Synthesizes the complete **Claus O. Wilke *Fundamentals of Data Visualization* (Chapters 1–29)** and **Nicolas P. Rougier, Michael Droettboom & Philip E. Bourne's *"Ten Simple Rules for Better Figures"*** (*PLOS Computational Biology*, 2014, `10.1371/journal.pcbi.1003833`).
   - Covers message-driven chart selection (Amounts, Distributions, Proportions & Nested Proportions, Associations/Paired Data, Time Series/Trends, Geospatial, Uncertainty/Contrasts), Proportional Ink, Log/Ratio scaling, Okabe–Ito CVD-safe palettes, Redundant Coding & Direct Labeling, Small Multiples vs. Compound Alignment, Clean Publication Tables (Booktabs discipline), Vector/Lossless File Formats (`publication_rcparams.py`), Ch. 29 Visual Storytelling, and mandatory post-render visual inspection.

## Scope & Decoupled Trigger Design

- **Pure Plotting / Table Tasks** → Activates `scientific-figures` only (zero prose-grammar context bloat).
- **Pure Manuscript / Proposal Prose Tasks** → Activates `scientific-writing` only (zero Matplotlib/colormap code bloat).
- **Full Paper + Figures / Tables / Captions Tasks** → Both skills coordinate seamlessly across figure story arcs (`OCAR`), left-to-right visual flow, clean Booktabs tables, and self-contained captions.
- **Exempt**: Everyday chat Q&A, code comments/`README.md`/PRs, non-scientific UI, homelab/ops dashboards, and 3D biomolecular structures (where interactive sidecar viewers take priority).
