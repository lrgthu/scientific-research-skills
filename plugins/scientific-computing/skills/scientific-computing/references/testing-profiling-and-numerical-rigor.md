# Scientific Testing, Numerical Rigor & Profiling Discipline

Synthesizes **Greg Wilson et al., *"Best Practices for Scientific Computing"*** (2014, Sections 5–6: *Plan for Mistakes* & *Optimize Software Only After It Works Correctly*) and **Wilson et al. (2017, Practice 2i)** for numerical, statistical, and ML Python code.

---

## 1. Solving the "Scientific Oracle Problem": Five Verification Layers

In scientific research, you write programs precisely because the exact answer on real data is unknown. Calibrate computational apparatus using **five complementary test layers** in `pytest`:

1. **Analytical & Closed-Form Limit Tests**:
   - Test solvers and estimators where exact closed-form solutions exist: zero-coupling / linear limits, 1D Gaussian integrals (exact KL divergence / entropy), rank-1 SVD matrices, or finite-difference gradient checks (`scipy.optimize.check_grad` / `torch.autograd.gradcheck` in `float64`).
2. **Physical, Algebraic & Shape Invariant Tests (Property Testing)**:
   - Verify laws that must hold for *any* valid input:
     - Conservation laws ($\sum_i p_i = 1$, probability non-negativity, energy/mass conservation, PSD symmetry $K = K^\top$),
     - Symmetries & equivariances (permuting batch/graph nodes permutes outputs identically; shifting logits by a constant $c$ leaves `softmax`/`logsumexp` invariant; rescaling units scales outputs predictably),
     - Strict shape & `dtype` preservation (`output.shape == expected_shape`, `np.isfinite(output).all()`).
3. **Metamorphic, Synthetic-Recovery & Convergence-Order Tests**:
   - **Parameter Recovery**: Simulate synthetic data from known ground-truth parameters $\theta^*$ with controlled noise $\sigma$ and verify $|\hat{\theta} - \theta^*|$ shrinks at the theoretical rate as $N \to \infty$ or $\sigma \to 0$.
   - **Discretization Order**: Halving step size $\Delta t$ in a $p$-th order integrator shrinks error by $\approx 2^p$.
   - **Single-Batch Overfit Gate (ML/Deep Learning)**: Before launching multi-hour training runs, verify in a 3-second test that the model + loss + optimizer drives loss $\to 0$ on a single fixed batch of 4 examples (catches detached computation graphs, sign-flipped losses, and misaligned masks immediately!).
4. **High-Level Reference Prototype as Test Oracle (Wilson 2014 Practice 6.2)**:
   - Write a crystal-clear, unoptimized 15-line pure-Python/NumPy reference function first. Keep it permanently inside `tests/` and assert `np.testing.assert_allclose(fast_vectorized_or_cuda(x), reference_oracle(x), rtol=1e-5, atol=1e-7)`.
5. **End-to-End Toy Smoke Test & Bug-to-Test Capture (Wilson 2017 2i · Wilson 2014 5.3)**:
   - Ship a tiny synthetic fixture (`tests/fixtures/`, $<50\text{ KB}$) that exercises data loading → core computation → metric/figure export in $<5$ seconds so collaborators and CI verify installation across laptop, workstation, and GPU server instantly.
   - **Rule of Regression**: Every time a scientific or numerical bug is discovered, **first write a failing `pytest` test that reproduces the bug**, then fix it so the bug can never silently return.

---

## 2. Numerical Stability & Stochastic Reproducibility

1. **Never Test Floating-Point Equality with `==`**:
   - Use `math.isclose`, `np.testing.assert_allclose(actual, desired, rtol=..., atol=...)`, or `torch.testing.assert_close(...)` with tolerances calibrated to precision (`float64`: `rtol=1e-7, atol=1e-10`; `float32`: `rtol=1e-4, atol=1e-6`; `bfloat16`/`float16`: `rtol=1e-2, atol=1e-2`). Note that `atol` is mandatory whenever `desired` contains zeros!
2. **Eliminate Classic Numerical Anti-Patterns**:
   - **Linear Systems**: Never compute `np.linalg.inv(A) @ b`—use `np.linalg.solve(A, b)`, `scipy.linalg.cho_solve` (SPD), or `np.linalg.lstsq`.
   - **Log-Domain Arithmetic**: Never compute `np.log(np.sum(np.exp(x)))` (underflows/overflows outside $[-700, 700]$)—use `scipy.special.logsumexp` / `torch.logsumexp`, `np.log1p(x)` for small $x$, and `np.expm1(x)`.
   - **Catastrophic Cancellation**: Use Welford/shifted algorithms (`np.var`, `torch.var`) rather than naive $\mathbb{E}[X^2] - (\mathbb{E}[X])^2$ in `float32`.
3. **Explicit, Isolated Random Number Generators**:
   - **Ban Legacy Global RNGs** (`random.random()`, `np.random.seed()`, `np.random.rand()`), which couple unrelated functions and break under multiprocessing or import reordering.
   - Instantiate and thread explicit generator instances:
     ```python
     rng = np.random.default_rng(seed)
     child_rngs = rng.spawn(n_workers)  # Statistically independent parallel streams!
     ```
   - In PyTorch/JAX, pass explicit `torch.Generator(device=...).manual_seed(seed)` or split `jax.random.key(seed)` keys explicitly (`key, subkey = jax.random.split(key)`).

---

## 3. Optimize Only After Correctness Is Verified & Profiled (Wilson 2014 §6)

1. **Sequence of Operations**:
   1. **Make it right** in readable high-level Python/NumPy/PyTorch with passing analytical & invariant tests.
   2. **Decide if speedup actually matters** (a script running once in 12 seconds needs zero optimization; an inner loop running $10^7$ times does).
   3. **Measure with a Profiler** (`python -m cProfile -s cumtime`, `pyinstrument`, `line_profiler`, or `torch.profiler`) on a realistic workload—never guess where the bottleneck lives!
   4. **Optimize Incrementally Against the Reference Oracle**:
      - Replace Python elementwise loops with **vectorized array/tensor operations** or `einsum` (verifying intermediate tensor shapes explicitly!).
      - Apply JIT compilation (`@jax.jit`, `torch.compile`, `@numba.njit`) or C++/CUDA extensions **only** on the profiled hotspot, asserting `assert_allclose` against your unoptimized Step 1 oracle after every change.
