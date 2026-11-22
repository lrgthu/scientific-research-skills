# Scientific Computing & Python Engineering (`v1.0.0`)

Global plugin bundling the decoupled **`scientific-computing`** skill plus an **Always-On Global Rule (`rules/AGENTS.md`)** synthesizing **Greg Wilson et al.'s *"Best Practices for Scientific Computing"*** (*PLOS Biology*, 2014, `arXiv:1210.0530`), **Greg Wilson et al.'s *"Good Enough Practices in Scientific Computing"*** (*PLOS Computational Biology*, 2017, `arXiv:1609.00037`), and the **Google Python Style Guide**, tailored for modern Python (`uv`, `pytest`, `ruff`, NumPy/SciPy/PyTorch/JAX) research workflows:

1. **`scientific-computing` Skill** (`skills/scientific-computing/SKILL.md` + `references/` + `scripts/`):
   - **Project & Data Hygiene**: Canonical `data/raw/` (read-only) → `src/` (scientific guts vs. driver scripts) → `results/` layout, Tidy Data (`1 col = 1 var`, `1 row = 1 obs`), semantic filenames (never `result1.csv` or `fig_3a.png`), provenance manifests, and `CITATION.cff` / `LICENSE` discipline.
   - **Google-Style Scientific Python**: Module-level imports, `NaN`-safe precondition `ValueError`s vs. internal invariants, zero mutable globals/defaults, NumPy/Tensor `.size`/`.numel()` truthiness safety, `with`-managed stateful resources (`open`, `h5py.File`, `plt.close`), modern type annotations (`Sequence`/`Mapping`, `X | None`), Google `Args:/Returns:/Raises:` docstrings with array shapes/dtypes/units, and cited paper mathematical notation exemptions.
   - **Verification & Performance**: Explicit seeded `np.random.default_rng(seed)` generators, toy/analytical smoke tests, symmetry/conservation property tests, bug-to-test regression capture, high-level prototypes as low-level test oracles, and profile-before-optimizing discipline.
   - **Executable Tooling**:
     - `scripts/scaffold_research_project.py` — Scaffolds a complete reproducible scientific Python project (`uv` + Google-style `ruff` + `pytest` + provenance runner).
     - `scripts/audit_scientific_python.py` — AST-based static auditor catching Google Style violations and scientific reproducibility/numerical hazards.
