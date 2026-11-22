# Global Scientific Computing & Python Engineering Rules (Wilson et al. 2014, 2017 · Google Python Style)

## 1. Scope Gate (Research Code, Pipelines, & Data Only; Pure Prose & Ops Exempt)

- **GATE C — Scientific Software, Research Pipelines, ML/Simulation Code, & Data Analysis (`scientific-computing`)**:
  Whenever **any** research task involves **scaffolding a research codebase, writing/refactoring/reviewing Python numerical, statistical, simulation, data-processing, or ML/AI experiment code, designing scientific tests, or organizing research datasets and provenance pipelines**:
  - You **MUST** read the `scientific-computing` skill (`skills/scientific-computing/SKILL.md`, using its path from your available skills list, plus relevant `references/*.md`) and propagate these standards to delegated subagents/workflows.
- **EXPLICIT EXEMPTION**:
  Pure manuscript prose editing (`scientific-writing`), literature bibliography lookups (`research-literature`), and non-research infrastructure/ops configuration tweaks are **exempt**.

---

## 2. Core Non-Negotiable Scientific Computing & Python Guardrails

1. **Data Immutability, Tidy Structure, & Provenance (Wilson et al. 2014, 2017)**:
   - **Never modify or overwrite raw data** (`data/raw/` is strictly read-only); script every cleaning/transformation step into `results/` or `data/processed/` using open formats (`CSV`, `Parquet`, `JSON`, `YAML`, `HDF5`), explicit `NA`/`NaN` (ban `-99`/`999` sentinel codes), and **Tidy Data** (`1 column = 1 variable`, `1 row = 1 observation`, units separated from numbers).
   - **Semantic Naming & Provenance**: Name files by content/function (`spectral_loss_sweep.csv`, **never** `result1.csv` or manuscript-coupled `fig_3a.png`). Every experiment/analysis run that generates paper numbers or figures must record machine-readable **provenance** (git commit hash, CLI args/config, RNG seed, library versions, input data hashes/IDs).
   - **VCS Hygiene**: Track all human-authored code, configs, tests, and text in Git via small, reversible commits; **never** commit secrets/API keys, restricted PII/medical data, or large (`>100 MB`) binary artifacts.

2. **Cognitive Chunking, Modularity, & DRY (Wilson et al. 2014, 2017 · Google §3.17–3.18)**:
   - Write code for **human working memory**: decompose into focused, single-purpose functions ($\le 40\text{–}60$ lines, $\le 6$ parameters—bundle larger parameter sets into frozen `@dataclass` configs), separate **core library modules (`src/<pkg>/`)** from **driver scripts (`scripts/`)**, and guard all script entrypoints with `def main(...) -> None:` under `if __name__ == "__main__":` (zero import-time side effects).
   - **Never comment/uncomment code blocks to toggle experiments**—use CLI flags (`argparse`/`absl.flags`) or config files. Reuse vetted libraries (`numpy`, `scipy`, `torch`, `jax`, `scikit-learn`) instead of hand-rolling standard numerical routines, and eliminate copy-paste `score1, score2` clones.

3. **Google Python Style Adapted for Scientific Computing (`pyguide`)**:
   - **Imports & State (§2.2, §2.5, §2.12, §3.13)**: Import **modules/packages** (`import numpy as np`, `from myproj.sim import integrators`), never individual functions/classes (except `typing` and `collections.abc`) and never relative imports or wildcards. Ban mutable global state and **ban mutable default arguments** (`def fn(items: Sequence[int] | None = None)`, never `items=[]`).
   - **Exceptions, `NaN`-Safe Preconditions, & Truthiness (§2.4, §2.14, §3.10.2)**: Validate public inputs with explicit `if not 0.0 <= p <= 1.0: raise ValueError(...)` (**never** rely on `assert` for input validation since `python -O` strips `assert`, and **always** write negated range checks `not (lo <= x <= hi)` so `NaN`s cannot slip through!). Never use bare `except:`. Check `x is None` explicitly, and check NumPy/Tensor emptiness via `arr.size == 0` / `tensor.numel() == 0` (**never** `if not arr:`).
   - **Resources, Logging, Types, & Docstrings (§3.8, §3.10.1, §3.11, §3.16.5, §3.19)**: Always close files, `h5py.File`, and `matplotlib` figures (`with ...` / `plt.close(fig)`). Pass `%`-pattern literals to `logger.info("Loss=%s", loss)` (not f-strings). Annotate public signatures (`Sequence`/`Mapping` inputs, `X | None`). Use Google `"""Summary.\n\nArgs:\nReturns:\nRaises:\n"""` docstrings specifying **array/tensor shapes, dtypes, and physical units**; single-letter math names inside kernels are allowed *only* when citing the exact reference paper/equation in the docstring/comment.

4. **Calibration, Testing, & Optimize-Last Discipline (Wilson et al. 2014)**:
   - Treat scientific code like laboratory apparatus: pass **explicit seeded RNG objects** (`np.random.default_rng(seed)`), compare floats with `np.allclose` / `torch.allclose(..., rtol, atol)` (never `==`), ship a fast **smoke test on toy/synthetic data with known analytical/conservation answers**, turn every discovered bug into a permanent `pytest` regression test, and **never optimize before correctness is verified and profiled** (using clean Python prototypes as test oracles for JIT/CUDA/C++ kernels).
