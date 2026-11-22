# Project Organization, Data Hygiene & Reproducible Workflows

Synthesizes **Greg Wilson et al., *"Good Enough Practices in Scientific Computing"*** (*PLOS Computational Biology*, 2017, `10.1371/journal.pcbi.1005510` / `arXiv:1609.00037`) and **Greg Wilson et al., *"Best Practices for Scientific Computing"*** (*PLOS Biology*, 2014, `10.1371/journal.pbio.1001745` / `arXiv:1210.0530`).

---

## 1. Canonical Research Project Anatomy (Wilson 2017 §3–4)

Divide research into repositories by **code and data overlap**: separate efforts sharing zero code/data; merge efforts sharing $>50\%$; extract shared cross-project utilities into an independent installable package.

```text
<project-name>/
├── README.md                 # Title, purpose, setup, and 1-2 runnable command examples
├── LICENSE                   # Explicit license (MIT/Apache-2.0/BSD for code; CC0/CC-BY-4.0 for data)
├── CITATION.cff              # Machine- & human-readable citation metadata + Zenodo/data DOIs
├── CONTRIBUTING.md           # Environment setup, smoke-test command, and contribution checklist
├── pyproject.toml            # Explicit dependencies + Ruff (Google style) + pytest config (locked via uv.lock)
├── data/
│   ├── raw/                  # STRICTLY READ-ONLY original data (chmod a-w) + source/download provenance README
│   └── processed/            # Non-destructively cleaned, tidy analysis-ready datasets
├── src/
│   └── <package_name>/       # Core reusable "scientific guts" (importable, unit-tested modules; zero CLI bloat)
├── scripts/
│   └── run_pipeline.py       # Driver/controller scripts wiring src/ + configs + data -> results/
├── results/
│   ├── intermediate/         # Checkpoints, cached simulations, or stage outputs (enables partial re-runs)
│   ├── figures/              # Programmatically generated vector PDFs / lossless PNGs (semantic names!)
│   └── tables/               # Programmatically generated CSV / JSON / Booktabs .tex + provenance.json
├── doc/
│   ├── notebook.md           # Reverse-chronological research log / negative results / design rationale
│   ├── CHANGELOG.md          # Dated record of material pipeline/parameter changes
│   └── manuscript/           # Plain-text LaTeX / Markdown manuscript sources
└── tests/
    ├── fixtures/             # Tiny (<50 KB) synthetic/toy dataset with known ground-truth output
    └── test_smoke.py         # End-to-end smoke + analytical/invariant unit tests
```

### Critical File-Naming Rules (Wilson 2017 §1b, §4f · Google §3.16.3)
1. **Semantic Content Names Only**: Name files by *what they represent* (`cortical_rank_sweep.csv`, `fit_bradley_terry.py`)—**NEVER** by sequential run counters (`result1.csv`, `final_v3_revised.py`) or **manuscript figure numbers (`fig_3_a.pdf`, `table_2.tex`)**, which inevitably shift during manuscript revisions!
2. **Metadata-Rich Regular Data Filenames**: Encode queryable experimental dimensions uniformly (`2026-11-site_a-trial_02.csv`, ISO-8601 `YYYY-MM-DD` dates, zero spaces) so `glob` patterns remain trivial.
3. **Python Module Filenames**: Always `lower_with_under.py`—**never** use dashes (`-`) in `.py` or package directory names (dashes break `import` and `pytest` discovery).

---

## 2. Scientific Data Management & Tidy Data (Wilson 2017 §1 · Wilson 2014 §4.1)

1. **Raw Data Immutability (`1a`)**:
   - Never hand-edit or overwrite raw files. Lock permissions (`chmod a-w data/raw/*`). If raw data lives in an external multi-TB archive (e.g., `/srv/ml/datasets` or public repositories), commit a script + manifest recording exact URLs, version tags, download timestamps, and SHA-256 checksums instead of duplicating TB-scale files.
2. **Open Formats & Self-Explaining Schemas (`1b`, `4.1`)**:
   - Prefer open, non-proprietary, long-lived formats: **`CSV` / `Parquet`** (tabular), **`JSON` / `YAML`** (configs/graphs/metadata), **`HDF5` / `Zarr` / `Safetensors`** (dense arrays/weights).
   - Replace cryptic codes (`var1`, `treat=1/2`) with self-explaining snake_case (`reaction_latency_ms`, `treatment_group="control"|"stimulated"`).
   - **Ban Numeric Missing-Value Sentinels**: Never encode missingness as `-99`, `999`, or `-1` (which silently corrupt means and regressions!). Use explicit `NA` / `NaN` / `null`.
   - **Single Authoritative Representation (DRY for Data)**: Define physical constants, unit conversions, and entity lookup tables **once** in a single canonical module/file.
3. **Tidy Data Principles (`1c`, Wickham 2014)**:
   - **One column = one atomic variable** (split `"male_treated"` into `sex` and `treatment`; store numeric magnitudes as pure numbers `3.4` in `mass_kg`, **never** string `"3.4kg"`!).
   - **One row = one observation**. Reshape human-entered wide matrices into long tidy tables before statistical modeling or plotting.
   - **Consistent Join Keys Across Tables (`1e`)**: Normalize entity IDs identically across relational tables (`"014025"` everywhere—never `"14,025"` in one table and `14025` in another).
4. **Script Every Transformation & Retain Intermediate Products (`1d`)**:
   - Script 100% of data cleaning and filtering. If an interactive step is unavoidable (e.g., manual ROI bounding box), save the exact ROI coordinates in a committed JSON/CSV config and apply the crop via script.
   - Persist clean intermediate checkpoints (`results/intermediate/`) so downstream analysis and plotting can re-run in seconds without recomputing multi-hour upstream stages.

---

## 3. Automation & Machine-Readable Provenance (Wilson 2014 §2 · Wilson 2017 §2h)

1. **Single-Command Regeneration**:
   - Express pipeline stages via a `Makefile`, `justfile`, or top-level driver script so `make all` (or `uv run scripts/run_pipeline.py`) regenerates cleaned data → statistical summaries → figures/tables end-to-end.
   - **Never Toggle Behavior by Commenting/Uncommenting Code (`2h`)**: Control ablations, seeds, and regimes exclusively through CLI flags or versioned YAML/TOML/dataclass configs.
2. **Automatic Provenance Sidecars**:
   - Alongside every generated result file (`results/tables/main_metrics.json`), automatically write a machine-readable provenance record capturing:
     - `timestamp_utc`, `git_commit_sha`, and `git_is_dirty` boolean (`subprocess.check_output(["git", "status", "--porcelain"])`),
     - Full resolved configuration / CLI arguments and explicit `seed`,
     - Python, OS, hardware device, and key library versions (`numpy`, `scipy`, `torch`, `jax`),
     - SHA-256 digests (or dataset version IDs) of input files.
   - *Downstream Bridge*: This provenance sidecar directly feeds `scientific-figures` (repeatable plotting) and `scientific-writing` (`Lock Hard Assets` with zero unverified numbers!).

---

## 4. Version Control, Collaboration & Archival Hygiene (Wilson 2017 §3, §5–6)

- **Atomic Reversible Commits (`5b`)**: Size each Git commit as *"one logical change you might want to revert in a single step"* with a clear message explaining *why*. Never commit broken half-edited states to `main`.
- **What Must NEVER Enter Git**:
  1. **Secrets, tokens, passwords, or SSH keys** (`.env` must be in `.gitignore`; load via `python-dotenv` or environment variables).
  2. **Restricted human-subjects / PII / HIPAA clinical data**.
  3. **Large binary blobs (`>50–100 MB`)** or regenerable build caches (`__pycache__/`, `.venv/`, checkpoints).
- **Licensing & Citability (`1f`, `2j`, `3c–3d`)**:
  - Always include an explicit `LICENSE` (**MIT / Apache-2.0 / BSD-3-Clause** for software; **CC0 / CC-BY-4.0** for data and docs—avoid `NC` non-commercial clauses that block legitimate academic/public-health reuse) and `CITATION.cff`.
  - Mint permanent DOIs on **Zenodo / Figshare / Dryad** for both code releases and final datasets upon manuscript submission, and export supplementary tables/figure source data as machine-readable `CSV`/`JSON`/`HDF5` rather than trapping them inside PDFs.
