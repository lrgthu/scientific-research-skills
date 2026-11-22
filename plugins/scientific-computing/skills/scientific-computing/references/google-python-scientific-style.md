# Google Python Style Guide for Scientific & ML Computing

Operationalizes the **Google Python Style Guide** (`https://google.github.io/styleguide/pyguide.html`) reconciled with **Wilson et al. (2014, 2017)** for modern Python 3.10+ (`uv`, `ruff`, `pytest`, NumPy/SciPy/PyTorch/JAX) research codebases.

---

## 1. Python Language Rules (Google §2 + Scientific Nuances)

### 1.1 Module-Only Absolute Imports (§2.2, §2.3, §3.13)
- **Import packages and modules, NOT individual functions or classes**:
  - **Yes**: `import numpy as np`, `import torch`, `from myproj.solvers import rk4` → call `rk4.integrate(...)` (makes provenance of every function call unmistakable!).
  - **No**: `from myproj.solvers.rk4 import integrate` (obscures origin), `from foo import *` (banned), `from . import rk4` (no relative imports), `import os, sys` (one import per line).
  - **Explicit Exemptions**: `typing`, `collections.abc`, and `typing_extensions` may import multiple symbols directly (`from collections.abc import Mapping, Sequence`). Standard scientific aliases (`import numpy as np`, `import pandas as pd`, `import matplotlib.pyplot as plt`, `import torch.nn.functional as F`, `import jax.numpy as jnp`) are idiomatic and encouraged.
- **Import Grouping Order** (top of file, lexicographically sorted within each group, separated by a blank line):
  1. `from __future__ import annotations`
  2. Standard library (`import dataclasses`, `from pathlib import Path`)
  3. Third-party packages (`import numpy as np`, `import scipy.linalg`)
  4. First-party repository modules (`from myproj.data import loader`)

### 1.2 Exceptions vs. Assertions & `NaN`-Safe Preconditions (§2.4, §3.10.2 · Wilson 2014 §5.1)
- **Reconciling Wilson's Defensive Assertions with Google §2.4.4**:
  - **Public Inputs, Configs, & Preconditions → Raise Built-in/`*Error` Exceptions (`ValueError`, `TypeError`)**: Never rely on `assert` to validate arguments or control flow because `python -O` disables `assert` completely!
  - **`NaN`-Safe Numerical Range Guard (Google §3.10.2 Critical Rule!)**:
    - **WRONG**: `if p < 0.0 or p > 1.0: raise ValueError(...)` — if `p = float('nan')`, both comparisons evaluate to `False` and `NaN` silently corrupts the entire simulation/training run!
    - **RIGHT**: Negate the valid closed interval (**`if not 0.0 <= p <= 1.0:`**) and check `np.all(np.isfinite(arr))` / `torch.isfinite(tensor).all()` at module boundaries!
    - Format grep-friendly error messages with explicit interpolated values: `raise ValueError(f"Expected probability in [0, 1], got {p=!r}")`.
  - **Internal Invariants & `pytest` Tests → `assert` (Executable Documentation)**: Use `assert` liberally in `pytest` suites and for internal post-calculation sanity invariants that could be removed without altering program semantics.
- **Strict `try / except` Discipline**: Never write bare `except:` or catch-all `except Exception:` (unless re-raising or isolating a top-level worker loop with full traceback logging). Keep `try:` bodies minimal so unrelated bugs are never masked.

### 1.3 Zero Mutable Globals & Zero Mutable Default Arguments (§2.5, §2.12)
- **No Mutable Global State**: Never mutate module-level dicts/lists/RNGs/configs during execution. Module-level `CAPS_WITH_UNDER` immutable constants (`BOLTZMANN_J_PER_K = 1.380649e-23`, `_DEFAULT_TOL = 1e-6`) are encouraged.
- **No Mutable Default Arguments**: Default values evaluate **once at import time**:
  - **No**: `def run_sweep(lrs: list[float] = [1e-3, 1e-4], meta: dict = {}):` or `def log_step(ts=time.time()):`
  - **Yes**: `def run_sweep(lrs: Sequence[float] = (1e-3, 1e-4), meta: Mapping[str, Any] | None = None):` (initializing `meta = dict(meta) if meta is not None else {}` inside the body).

### 1.4 Truthiness, NumPy/Tensor Caveats, & Comprehensions (§2.7–2.11, §2.14)
- **Boolean & `None` Checks**: Always write `if x is None:` / `if x is not None:` (never `if not x:` when `0` or `0.0` is a valid scientific value!). Use implicit emptiness `if not items:` for Python `list`/`dict`/`str`/`tuple`, and explicit `if step % 100 == 0:` for integers.
- **NumPy / PyTorch / JAX Emptiness (§2.14.4)**: Never write `if arr:` on arrays/tensors (raises `ValueError` for multi-element arrays!). Check `if arr.size == 0:` (NumPy) or `if tensor.numel() == 0:` (PyTorch).
- **Readable Comprehensions & Helpers (§2.6–2.10)**:
  - Allow single-`for` comprehensions; **ban multi-`for` comprehensions**—write explicit nested loops for clarity.
  - Prefer `operator.mul` over `lambda x, y: x * y`; convert multi-line lambdas into named `_helper()` module-level functions (prefer module-level `_helper()` over nested functions unless closing over local variables, so `_helper()` can be unit-tested directly!).

### 1.5 Decorators & Avoiding "Power Features" (§2.17, §2.19)
- **Avoid `@staticmethod`**: Write a plain module-level function instead. Reserve `@classmethod` strictly for named alternative constructors (`Config.from_yaml(path)`). Never perform file/network/GPU I/O inside a decorator at import time.
- **Ban Magic Metaprogramming**: Avoid custom metaclasses, bytecode manipulation, dynamic `sys.path` hacks, `__del__` finalizers, or string `eval`/`exec`. Use standard `@dataclass(frozen=True)` and `enum.Enum` instead.

---

## 2. Python Style, Typing & Documentation Rules (Google §3–4)

### 2.1 Layout, Line Length, & Entrypoints (§3.1–3.7, §3.14, §3.17–3.18)
- **4-Space Indentation, Zero Semicolons, Zero Backslash Continuations**: Wrap long expressions using **implicit line joining inside `(...)`, `[...]`, `{...}`**—never trailing `\` backslashes. Use trailing commas when closing brackets sit on a new line so `ruff format` / `black` formats one item per line cleanly.
- **Line & Function Length**: Target `80` chars (`88` max when using `ruff format` / `black`, keeping docstring summary lines $\le 80$ chars; URLs and long imports exempt). Keep functions **focused and short ($\le 40\text{–}60$ lines, $\le 6$ arguments)**; group cohesive hyperparameters into a `@dataclass(frozen=True)`.
- **Mandatory `main()` Guard (§3.17)**: Every executable `.py` file must put execution inside `def main() -> None:` gated by `if __name__ == "__main__": main()` so `pytest` and documentation tools can import any file with zero side effects.

### 2.2 Stateful Resources & Lazy Logging (§3.10.1, §3.11)
- **Deterministic Resource Cleanup (§3.11)**: Always manage files, sockets, `h5py.File`, `mmap`, temporary directories, and database connections via `with` blocks—and **explicitly close Matplotlib figures (`plt.close(fig)`)** inside loops so parameter sweeps never leak memory or file handles!
- **Pattern-Literal Logging (§3.10.1)**: Call `logger.info("Epoch %d: val_loss=%.5f", epoch, val_loss)` using `%`-placeholders rather than f-strings (avoids formatting overhead when log level is suppressed and preserves structured log patterns).

### 2.3 Naming & The Mathematical Notation Rule (§3.16, §3.16.5)
- **Standard Conventions**: `module_name.py`, `ClassName` (`HTTPClient`, all-caps acronyms), `ExceptionError`, `function_name()`, `CAPS_CONSTANT`, `_internal_helper()`. Never bake container types into names (`user_by_id`, not `id_to_user_dict`).
- **Mathematical Notation Clause (§3.16.5 — Scientific Python Essential)**:
  1. **Public API signatures** must still use clear `descriptive_snake_case` (`regularization_strength: float`, `learning_rate: float`).
  2. **Inside mathematically dense implementations**, concise variable names matching the **established notation of a reference paper or textbook** (e.g., `Q`, `K`, `V`, `Sigma_inv`, `beta`) ARE preferred over verbose prose names **provided you**:
     - Cite the exact paper/equation URL in the function docstring or block comment (`# Notation follows Eq. (4) of Ho et al. (2020), https://arxiv.org/abs/2006.11239`), and
     - Scope linter suppressions narrowly (`# noqa: N803,N806` or `# pylint: disable=invalid-name`).

### 2.4 Modern Type Annotations (§2.21, §3.19)
- Annotate all public functions, dataclasses, and error-prone numerical boundaries using Python 3.10+ syntax:
  - Use `X | None` (never implicit `x: str = None`); spaces around `=` when annotated (`tol: float = 1e-6`).
  - Accept abstract `collections.abc.Sequence` / `Mapping` / `Iterable` in parameters; return concrete `list` / `dict` / `tuple[np.ndarray, float]`.
  - Declare complex tensor/array aliases with `TypeAlias` (`FloatArray: TypeAlias = np.typing.NDArray[np.floating[Any]]`).

### 2.5 Google-Style Docstrings for Scientific Functions (§3.8 · Wilson 2014 §7)
- Document **purpose, mathematical contract, shapes, dtypes, and units**—never restate obvious Python syntax (`i += 1  # Increment i` is banned; refactor convoluted code rather than writing paragraphs excusing how it works!).
- Omit redundant docstrings on `test_*` methods and `@override` methods unless explaining subtle test fixtures/tolerances.

```python
def compute_mahalanobis_distance(
    observations: np.typing.NDArray[np.float64],
    mean: np.typing.NDArray[np.float64],
    covariance_cholesky: np.typing.NDArray[np.float64],
) -> np.typing.NDArray[np.float64]:
    """Computes squared Mahalanobis distances via triangular Cholesky solve.

    Solves L y = (x - mu)^T rather than inverting the covariance matrix
    explicitly for numerical conditioning.

    Args:
        observations: Sample matrix of shape (n_samples, n_features) in
            physical units matching `mean`.
        mean: Distribution center of shape (n_features,).
        covariance_cholesky: Lower-triangular Cholesky factor L of shape
            (n_features, n_features) such that Sigma = L @ L.T.

    Returns:
        1D float64 array of shape (n_samples,) containing non-negative squared
        Mahalanobis distances (dimensionless).

    Raises:
        ValueError: If input dimensions mismatch or arrays contain NaN/Inf.
    """
```
