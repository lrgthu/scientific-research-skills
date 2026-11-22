---
name: scientific-computing
description: >
  Reproducible scientific computing, research project/data engineering,
  numerical verification, and Google-style Python engineering skill synthesizing
  Greg Wilson et al.'s "Best Practices for Scientific Computing" (PLOS Biology,
  2014, arXiv:1210.0530), "Good Enough Practices in Scientific Computing" (PLOS
  Comp Biol, 2017, arXiv:1609.00037), and the Google Python Style Guide. Use
  whenever scaffolding research repositories, organizing scientific datasets or
  data-cleaning pipelines, writing/refactoring/reviewing Python simulation,
  statistical, numerical, or ML/AI research code, designing analytical/invariant
  tests, or profiling computational bottlenecks. Don't use for pure manuscript
  prose editing or non-research ops/infrastructure configs.
---

# Scientific Computing & Google-Style Python Engineering Skill

> **Core Premise**: Scientific software is **experimental apparatus**—it must be built for human limited working memory, calibrated against analytical and physical invariants, automated end-to-end with machine-readable provenance, and styled consistently so errors have nowhere to hide *(synthesizing Wilson et al., 2014, `10.1371/journal.pbio.1001745`; Wilson et al., 2017, `10.1371/journal.pcbi.1005510`; and the Google Python Style Guide)*.

## Reference Modules & Executable Scripts

Load the reference module(s) matching your task, and use the bundled scripts in `<SKILL_DIR>/scripts/`:

1. **[Project Organization, Data Hygiene & Reproducible Workflows](./references/project-data-and-reproducibility.md)** — **Read when starting a project, organizing files/datasets, or wiring pipelines**: Canonical `data/raw/` (read-only) → `src/` (library guts) → `scripts/` (drivers) → `results/` layout, Tidy Data (`1 col = 1 var`, `1 row = 1 obs`), semantic filenames (banning `result1.csv` and `fig_3a.png`), provenance JSON sidecars, Git hygiene, `LICENSE`, `CITATION.cff`, and Zenodo/DOI archiving.
2. **[Google Python Style Guide for Scientific & ML Computing](./references/google-python-scientific-style.md)** — **Read when writing, refactoring, or reviewing Python code**: Module-only absolute imports, `NaN`-safe precondition `ValueError`s (`if not lo <= x <= hi:`) vs. internal `assert`s, zero mutable globals/defaults, NumPy/Tensor `.size`/`.numel()` truthiness, `with`-managed stateful resources (`open`, `h5py.File`, `plt.close`), `%`-pattern logging, modern type hints (`Sequence`/`Mapping`, `X | None`), Google `Args:/Returns:/Raises:` docstrings with **shapes, dtypes, and units**, and the **Mathematical Notation Clause (§3.16.5)**.
3. **[Scientific Testing, Numerical Rigor & Profiling Discipline](./references/testing-profiling-and-numerical-rigor.md)** — **Read when validating correctness, debugging numerical instability, or optimizing speed**: 5 scientific test oracles (closed-form limits, conservation/equivariance invariants, synthetic parameter recovery & single-batch overfit, high-level reference oracle for fast kernels, `<5s` toy smoke tests), `logsumexp`/`solve` stability, isolated `default_rng(seed)` streams, bug-to-test capture, and profile-before-optimizing workflow.
4. **Bundled CLI Tools (`<SKILL_DIR>/scripts/`)**:
   - `uv run "<SKILL_DIR>/scripts/scaffold_research_project.py" <project_dir> --name <pkg_name>` — Scaffolds a complete Wilson (2017) + `uv`/`ruff` (Google docstring profile)/`pytest` research repository with provenance runner and smoke test.
   - `uv run "<SKILL_DIR>/scripts/audit_scientific_python.py" <path_to_py_or_dir>` — Runs an AST static audit catching Google Style defects and scientific reproducibility/numerical anti-patterns.

---

## Mandatory 5-Phase Scientific Coding Workflow

### Phase 1: Architecture, Data Separation, & Explicit Environment (`Wilson 2017 §1–4`)

1. **Separate Read-Only Raw Data, Reusable Library Guts, Driver Scripts, & Generated Results**:
   - Keep `data/raw/` strictly **immutable** (`chmod a-w`); write scripted, non-destructive transformations outputting open-format **Tidy Data** (`CSV`/`Parquet`/`HDF5`, explicit `NaN`/`NA` instead of `-99`, units separated from numbers) into `data/processed/` or `results/intermediate/`.
   - Separate **importable core algorithms (`src/<pkg>/`)** from **CLI driver scripts (`scripts/`)**. Never trap reusable scientific logic inside Jupyter notebooks or top-level scripts without `def main() -> None:` + `if __name__ == "__main__":`.
   - Declare dependencies explicitly in `pyproject.toml` (locked via `uv.lock`) or PEP 723 inline `# /// script` headers for standalone utilities.
   - **Never comment/uncomment code blocks to toggle experiments**—use typed CLI flags (`argparse` / `absl.flags`) or frozen `@dataclass` configs.

### Phase 2: Cognitive Chunking & Google-Style Scientific Python (`Wilson 2014 §1, §4, §7` · `Google §2–3`)

1. **Design for Human Working Memory ($\le 7$ Chunks)**:
   - Keep functions single-purpose, $\le 40\text{–}60$ lines, with $\le 6$ parameters (group cohesive experiment/solver parameters into `@dataclass(frozen=True)` objects so callers cannot swap positional floats accidentally!).
   - Eliminate copy-paste `score1, score2` clones via functions/containers (DRY), and prefer battle-tested libraries (`numpy`, `scipy`, `torch`, `jax`, `scikit-learn`) over custom re-implementations of standard numerical algorithms.
2. **Enforce Core Google Python Rules**:
   - **Imports**: Import modules/packages (`from myproj.sim import integrators`, `import numpy as np`), never individual functions/classes (except `typing` & `collections.abc`) and never relative/wildcard imports.
   - **No Mutable Globals or Mutable Defaults**: Ban `def fn(x=[])` and mutable module globals.
   - **Defensive `NaN`-Safe Validation**: Validate public preconditions with `if not lo <= x <= hi: raise ValueError(f"... {x=!r}")` (catches `NaN`s and survives `python -O`!), check `np.isfinite` at boundaries, and never use bare `except:`.
   - **Array/Tensor Truthiness & Resource Safety**: Check `x is None` explicitly; check array emptiness via `arr.size == 0` / `tensor.numel() == 0` (never `if not arr:`); close files, `h5py.File`, and Matplotlib figures (`with ...` / `plt.close(fig)`).
   - **Docstrings & Paper Math Notation**: Write Google-style `"""Summary <=80 chars.\n\nArgs:\nReturns:\nRaises:\n"""` docstrings specifying **array shapes, dtypes, and physical units**. Use `descriptive_snake_case` in public APIs; single-letter math symbols inside kernels are permitted *only* when citing the reference paper/equation in the docstring!

### Phase 3: Numerical Stability & Isolated Stochasticity (`Wilson 2014 §2, §5`)

1. **Isolated Seeded RNGs**: Thread explicit `np.random.default_rng(seed)` (using `.spawn()` for parallel workers) or `torch.Generator` / `jax.random.key(seed)`—never rely on unseeded or global `random`/`np.random` state.
2. **Numerical Conditioning**: Prefer `linalg.solve` / `cho_solve` over `linalg.inv`, `logsumexp` / `log1p` / `expm1` over naive `log(sum(exp(x)))`, and explicit `dtype` promotion (`float64` accumulators when summing millions of `float16`/`bfloat16` values).
3. **Provenance Sidecars**: Every driver run that produces manuscript numbers, tables, or figures must save a companion `*_provenance.json` (git commit SHA + dirty status, full config/CLI args, seed, package versions, input checksums) using **semantic filenames** (`spectral_loss_scaling.json`, never `result1.json` or `fig3.png`).

### Phase 4: Multi-Layer Scientific Verification (`Wilson 2014 §5` · `Wilson 2017 §2i`)

Before trusting any scientific output or claiming a task complete:
1. Run `pytest` covering **(a) closed-form analytical toy cases**, **(b) conservation/equivariance/shape/finiteness invariants** (`assert_allclose` with explicit `rtol`/`atol`, never `==` on floats), and **(c) an `<5s` end-to-end smoke test on tiny synthetic data** (plus single-batch overfit for ML models).
2. Convert every discovered bug into a permanent `pytest` regression test before fixing it.
3. Run `uv run "<SKILL_DIR>/scripts/audit_scientific_python.py" <target_path>` (and `ruff check` if installed) and resolve any flagged defects.

### Phase 5: Profile Before Optimizing & Bridge to Downstream Figures/Manuscript (`Wilson 2014 §6`)

1. **Correctness → Profile → Vectorize/JIT Against Oracle**: Never micro-optimize unprofiled code. When speed is a proven bottleneck, profile first (`cProfile`/`pyinstrument`/`torch.profiler`), keep the simple readable Python/NumPy implementation in `tests/` as your **reference oracle**, and assert `assert_allclose` against it after vectorizing or JIT-compiling.
2. **Bridge to `scientific-figures` & `scientific-writing`**: Feed tidy, provenance-stamped `results/` outputs directly into `scientific-figures` scripts (zero manual Excel/Illustrator edits, zero copy-pasted numbers into LaTeX).
