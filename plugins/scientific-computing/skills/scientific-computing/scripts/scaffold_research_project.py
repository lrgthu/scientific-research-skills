#!/usr/bin/env python3
r"""Scaffolds a reproducible scientific Python project layout.

Implements the directory structure, read-only raw-data separation, provenance
recording, citation metadata, Google-style Ruff linting, and analytical smoke
testing recommended by:
- Wilson et al. (2017), "Good Enough Practices in Scientific Computing"
  (PLOS Comp Biol, 10.1371/journal.pcbi.1005510)
- Wilson et al. (2014), "Best Practices for Scientific Computing"
  (PLOS Biology, 10.1371/journal.pbio.1001745)
- Google Python Style Guide (https://google.github.io/styleguide/pyguide.html)
"""

# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

from __future__ import annotations

import argparse
from collections.abc import Sequence
import dataclasses
import datetime
import json
import pathlib
import re
import sys

_PACKAGE_RE = re.compile(r"^[a-z][a-z0-9_]*$")

_PROVENANCE_TEMPLATE = '''r"""Machine-readable provenance capture for reproducible computational runs."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import datetime
import hashlib
import importlib.metadata
import json
import pathlib
import platform
import re
import subprocess
from typing import Any

_NON_SEMANTIC_NAME_RE = re.compile(
    r"^(?:fig(?:ure)?[_-]?\\d+[a-z]?|tab(?:le)?[_-]?\\d+[a-z]?|result[_-]?\\d+|output[_-]?\\d+)\\.",
    re.IGNORECASE,
)


def sha256_file(path: pathlib.Path) -> str:
    """Computes the hexadecimal SHA-256 digest of a file on disk.

    Args:
        path: Path to an existing input or artifact file.

    Returns:
        64-character lowercase hexadecimal SHA-256 digest.
    """
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_state(repo_dir: pathlib.Path | None = None) -> dict[str, Any]:
    """Queries current Git commit SHA and working-tree cleanliness."""
    cwd = repo_dir or pathlib.Path.cwd()
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        status = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        return {"commit": commit, "dirty": bool(status)}
    except (OSError, subprocess.CalledProcessError):
        return {"commit": None, "dirty": None}


def build_provenance_record(
    *,
    config: Mapping[str, Any],
    seed: int,
    inputs: Sequence[pathlib.Path] = (),
    packages: Sequence[str] = ("numpy",),
) -> dict[str, Any]:
    """Builds a provenance dictionary capturing code, environment, seed, and inputs.

    Args:
        config: Serializable parameter dictionary governing the experiment run.
        seed: Explicit integer random seed passed to the local RNG generator.
        inputs: Input file paths to hash via SHA-256.
        packages: Installed distribution names whose versions should be recorded.

    Returns:
        JSON-serializable provenance dictionary.
    """
    pkg_versions: dict[str, str | None] = {}
    for pkg in packages:
        try:
            pkg_versions[pkg] = importlib.metadata.version(pkg)
        except importlib.metadata.PackageNotFoundError:
            pkg_versions[pkg] = None

    return {
        "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "git": git_state(),
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "packages": pkg_versions,
        "seed": seed,
        "config": dict(config),
        "input_sha256": {str(p): sha256_file(p) for p in inputs if p.is_file()},
    }


def write_provenance_json(
    output_path: pathlib.Path, record: Mapping[str, Any]
) -> pathlib.Path:
    """Writes a provenance sidecar JSON after verifying semantic naming.

    Args:
        output_path: Target path for the JSON provenance sidecar.
        record: Provenance dictionary produced by build_provenance_record.

    Returns:
        The written output_path.

    Raises:
        ValueError: If output_path uses a numbered placeholder filename.
    """
    if _NON_SEMANTIC_NAME_RE.match(output_path.name):
        raise ValueError(
            f"Refusing non-semantic filename {output_path.name!r}; name artifacts "
            "by scientific content rather than manuscript order."
        )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(dict(record), handle, indent=2, sort_keys=True)
        handle.write("\\n")
    return output_path
'''

_CORE_TEMPLATE = '''r"""Core numerical routines with NaN-safe validation and isolated RNG streams."""

from __future__ import annotations

import dataclasses
import math

import numpy as np


@dataclasses.dataclass(frozen=True)
class SimulationConfig:
    """Parameters governing a 1D Ornstein-Uhlenbeck relaxation process.

    Attributes:
        num_steps: Number of discrete integration steps (>= 1).
        dt_seconds: Integration time step in seconds (0 < dt_seconds <= 10.0).
        damping_rate: Relaxation rate lambda in s^-1 (0 <= damping_rate <= 1e3).
        noise_scale: Diffusion amplitude sigma in m * s^-0.5 (>= 0).
    """

    num_steps: int = 100
    dt_seconds: float = 0.01
    damping_rate: float = 0.5
    noise_scale: float = 0.0


def validate_config(config: SimulationConfig) -> None:
    """Validates SimulationConfig preconditions with NaN-safe range checks.

    Args:
        config: Immutable simulation configuration.

    Raises:
        ValueError: If any parameter is negative, out of bounds, or NaN.
    """
    if config.num_steps < 1:
        raise ValueError(f"num_steps must be >= 1, got {config.num_steps!r}.")
    if not 0.0 < config.dt_seconds <= 10.0:
        raise ValueError(
            f"dt_seconds must lie in (0.0, 10.0], got {config.dt_seconds!r}."
        )
    if not 0.0 <= config.damping_rate <= 1000.0:
        raise ValueError(
            f"damping_rate must lie in [0.0, 1000.0], got {config.damping_rate!r}."
        )
    if not 0.0 <= config.noise_scale <= 1000.0:
        raise ValueError(
            f"noise_scale must lie in [0.0, 1000.0], got {config.noise_scale!r}."
        )


def simulate_ornstein_uhlenbeck(
    initial_positions_m: np.ndarray,
    config: SimulationConfig,
    *,
    rng: np.random.Generator,
) -> np.ndarray:
    """Integrates exact-step Ornstein-Uhlenbeck paths dx = -lambda x dt + sigma dW.

    Uses the exact Ornstein-Uhlenbeck transition kernel so the deterministic limit
    (sigma = 0) matches x(t) = x(0) * exp(-lambda * t) to machine precision.

    Args:
        initial_positions_m: 1D float array of shape (num_particles,) giving initial
            particle displacements in meters.
        config: Validated time-stepping and physical rate configuration.
        rng: Isolated NumPy Generator instance (e.g., np.random.default_rng(seed)).

    Returns:
        Float64 array of shape (num_steps + 1, num_particles) containing particle
        positions in meters at times t_k = k * dt_seconds.

    Raises:
        ValueError: If initial_positions_m is empty, non-1D, contains non-finite
            values, or if config fails validation.
    """
    validate_config(config)
    state0 = np.asarray(initial_positions_m, dtype=np.float64)
    if state0.ndim != 1 or state0.size == 0:
        raise ValueError(
            f"initial_positions_m must be a non-empty 1D array; got {state0.shape}."
        )
    if not np.all(np.isfinite(state0)):
        raise ValueError("initial_positions_m contains NaN or infinite values.")

    num_particles = state0.shape[0]
    trajectory = np.empty((config.num_steps + 1, num_particles), dtype=np.float64)
    trajectory[0] = state0

    decay = math.exp(-config.damping_rate * config.dt_seconds)
    if config.noise_scale == 0.0:
        std_step = 0.0
    elif config.damping_rate == 0.0:
        std_step = config.noise_scale * math.sqrt(config.dt_seconds)
    else:
        stationary_var = -math.expm1(-2.0 * config.damping_rate * config.dt_seconds)
        std_step = config.noise_scale * math.sqrt(
            stationary_var / (2.0 * config.damping_rate)
        )

    for step in range(config.num_steps):
        if std_step > 0.0:
            noise = rng.normal(loc=0.0, scale=std_step, size=num_particles)
        else:
            noise = 0.0
        trajectory[step + 1] = decay * trajectory[step] + noise

    return trajectory
'''

_DRIVER_TEMPLATE = '''#!/usr/bin/env python3
r"""End-to-end driver script producing tidy CSV results and a provenance sidecar."""

# __PEP723_OPEN__
# requires-python = ">=3.10"
# dependencies = [
#   "numpy>=1.26",
# ]
# __PEP723_CLOSE__

from __future__ import annotations

import argparse
from collections.abc import Sequence
import csv
import dataclasses
import pathlib
import sys

import numpy as np

_REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(_REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "src"))

from __PKG_NAME__ import core  # noqa: E402
from __PKG_NAME__ import provenance  # noqa: E402


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parses CLI options so experiments never require commenting out code."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=42, help="Explicit RNG seed.")
    parser.add_argument("--num-steps", type=int, default=100, help="Time steps.")
    parser.add_argument("--dt-seconds", type=float, default=0.02, help="Step size (s).")
    parser.add_argument(
        "--damping-rate", type=float, default=0.5, help="Relaxation rate (s^-1)."
    )
    parser.add_argument(
        "--noise-scale", type=float, default=0.05, help="Noise amplitude (m*s^-0.5)."
    )
    parser.add_argument(
        "--output-dir",
        type=pathlib.Path,
        default=_REPO_ROOT / "results" / "intermediate",
        help="Destination directory for tidy outputs and provenance JSON.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    """Executes simulation and writes tidy CSV + provenance JSON sidecar."""
    args = parse_args(argv)
    cfg = core.SimulationConfig(
        num_steps=args.num_steps,
        dt_seconds=args.dt_seconds,
        damping_rate=args.damping_rate,
        noise_scale=args.noise_scale,
    )
    rng = np.random.default_rng(args.seed)
    init_pos = np.array([-1.0, 0.0, 1.5], dtype=np.float64)
    traj = core.simulate_ornstein_uhlenbeck(init_pos, cfg, rng=rng)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = args.output_dir / "ornstein_uhlenbeck_trajectory.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["step", "time_s", "particle_id", "position_m"])
        for step_idx in range(traj.shape[0]):
            time_s = step_idx * cfg.dt_seconds
            for pid in range(traj.shape[1]):
                writer.writerow(
                    [step_idx, f"{time_s:.6f}", pid, f"{traj[step_idx, pid]:.10f}"]
                )

    prov_record = provenance.build_provenance_record(
        config=dataclasses.asdict(cfg),
        seed=args.seed,
    )
    provenance.write_provenance_json(
        args.output_dir / "ornstein_uhlenbeck_trajectory_provenance.json",
        prov_record,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''

_SMOKE_TESTS_TEMPLATE = '''r"""Analytical, invariance, precondition, and smoke tests for __PKG_NAME__."""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys

import numpy as np
import pytest

from __PKG_NAME__ import core

_REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent


def test_deterministic_limit_matches_closed_form_exponential() -> None:
    cfg = core.SimulationConfig(
        num_steps=50, dt_seconds=0.05, damping_rate=0.8, noise_scale=0.0
    )
    x0 = np.array([-2.0, 0.5, 3.0])
    traj = core.simulate_ornstein_uhlenbeck(x0, cfg, rng=np.random.default_rng(0))
    times = np.arange(cfg.num_steps + 1)[:, None] * cfg.dt_seconds
    expected = x0[None, :] * np.exp(-cfg.damping_rate * times)
    np.testing.assert_allclose(traj, expected, rtol=1e-12, atol=1e-12)


def test_zero_damping_zero_noise_conserves_initial_position() -> None:
    cfg = core.SimulationConfig(
        num_steps=25, dt_seconds=0.1, damping_rate=0.0, noise_scale=0.0
    )
    x0 = np.array([1.25, -4.5])
    traj = core.simulate_ornstein_uhlenbeck(x0, cfg, rng=np.random.default_rng(7))
    np.testing.assert_allclose(traj[-1], x0, rtol=0.0, atol=1e-15)


@pytest.mark.parametrize(
    "bad_dt",
    [0.0, -0.01, 25.0, float("nan"), float("inf")],
)
def test_nan_and_out_of_range_parameters_raise_value_error(bad_dt: float) -> None:
    cfg = core.SimulationConfig(dt_seconds=bad_dt)
    with pytest.raises(ValueError, match="dt_seconds"):
        core.simulate_ornstein_uhlenbeck(
            np.array([1.0]), cfg, rng=np.random.default_rng(0)
        )


def test_isolated_rng_reproducibility_and_seed_sensitivity() -> None:
    cfg = core.SimulationConfig(num_steps=30, noise_scale=0.4)
    x0 = np.array([0.0, 1.0])
    run_a = core.simulate_ornstein_uhlenbeck(x0, cfg, rng=np.random.default_rng(123))
    run_b = core.simulate_ornstein_uhlenbeck(x0, cfg, rng=np.random.default_rng(123))
    run_c = core.simulate_ornstein_uhlenbeck(x0, cfg, rng=np.random.default_rng(124))
    np.testing.assert_allclose(run_a, run_b, rtol=0.0, atol=0.0)
    assert not np.allclose(run_a, run_c)


def test_pipeline_cli_smoke_writes_tidy_csv_and_provenance(
    tmp_path: pathlib.Path,
) -> None:
    script = _REPO_ROOT / "scripts" / "run_pipeline.py"
    subprocess.run(
        [
            sys.executable,
            str(script),
            "--num-steps",
            "10",
            "--seed",
            "99",
            "--output-dir",
            str(tmp_path),
        ],
        check=True,
    )
    csv_file = tmp_path / "ornstein_uhlenbeck_trajectory.csv"
    prov_file = tmp_path / "ornstein_uhlenbeck_trajectory_provenance.json"
    assert csv_file.is_file()
    assert prov_file.is_file()
    meta = json.loads(prov_file.read_text(encoding="utf-8"))
    assert meta["seed"] == 99
    assert meta["config"]["num_steps"] == 10
'''


@dataclasses.dataclass(frozen=True)
class ScaffoldSpec:
    """Configuration for a scaffolded scientific Python repository.

    Attributes:
        project_dir: Root directory to create or populate.
        dist_name: Distribution name in kebab-case for pyproject.toml.
        pkg_name: Importable Python package name in snake_case under src/.
        author: Primary author or research group name.
        license_id: SPDX license identifier ('MIT', 'BSD-3-Clause', 'Apache-2.0').
        python_req: Minimum Python version specifier (e.g., '>=3.11').
    """

    project_dir: pathlib.Path
    dist_name: str
    pkg_name: str
    author: str
    license_id: str
    python_req: str


def derive_package_name(raw_name: str) -> str:
    """Normalizes a directory or project label into a valid Python snake_case identifier.

    Args:
        raw_name: Raw user-supplied package or directory name.

    Returns:
        Normalized snake_case Python package name.

    Raises:
        ValueError: If raw_name cannot be normalized into a valid identifier.
    """
    cleaned = re.sub(r"[^a-zA-Z0-9_]+", "_", raw_name.strip().lower()).strip("_")
    if cleaned and cleaned[0].isdigit():
        cleaned = f"proj_{cleaned}"
    if not _PACKAGE_RE.match(cleaned):
        raise ValueError(
            f"Cannot derive a valid snake_case Python package name from {raw_name!r}."
        )
    return cleaned


def render_license(license_id: str, author: str, year: int) -> str:
    """Renders standard open-source license text for the scaffolded repository."""
    if license_id == "MIT":
        return (
            f"MIT License\n\nCopyright (c) {year} {author}\n\n"
            "Permission is hereby granted, free of charge, to any person obtaining a copy\n"
            'of this software and associated documentation files (the "Software"), to deal\n'
            "in the Software without restriction, including without limitation the rights\n"
            "to use, copy, modify, merge, publish, distribute, sublicense, and/or sell\n"
            "copies of the Software, and to permit persons to whom the Software is\n"
            "furnished to do so, subject to the following conditions:\n\n"
            "The above copyright notice and this permission notice shall be included in all\n"
            "copies or substantial portions of the Software.\n\n"
            'THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR\n'
            "IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,\n"
            "FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE\n"
            "AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER\n"
            "LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,\n"
            "OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE\n"
            "SOFTWARE.\n"
        )
    if license_id == "BSD-3-Clause":
        return (
            f"BSD 3-Clause License\n\nCopyright (c) {year}, {author}\n"
            "All rights reserved.\n\n"
            "Redistribution and use in source and binary forms, with or without\n"
            "modification, are permitted provided that the standard BSD 3-Clause\n"
            "conditions are met.\n"
        )
    return (
        f"Copyright {year} {author}\n\n"
        'Licensed under the Apache License, Version 2.0 (the "License");\n'
        "you may not use this file except in compliance with the License.\n"
        "You may obtain a copy of the License at\n\n"
        "    http://www.apache.org/licenses/LICENSE-2.0\n"
    )


def render_pyproject(spec: ScaffoldSpec) -> str:
    """Renders pyproject.toml with src-layout, pytest, and Google-docstring Ruff rules."""
    return f"""[build-system]
requires = ["hatchling>=1.24"]
build-backend = "hatchling.build"

[project]
name = "{spec.dist_name}"
version = "0.1.0"
description = "Reproducible scientific computing pipeline and core library."
readme = "README.md"
requires-python = "{spec.python_req}"
license = {{text = "{spec.license_id}"}}
authors = [{{name = "{spec.author}"}}]
dependencies = [
  "numpy>=1.26",
]

[project.optional-dependencies]
dev = [
  "pytest>=8.0",
  "ruff>=0.6",
]

[tool.hatch.build.targets.wheel]
packages = ["src/{spec.pkg_name}"]

[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]
addopts = "-ra -q"

[tool.ruff]
line-length = 88
src = ["src", "scripts", "tests"]

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP", "N", "D", "NPY", "RUF"]
ignore = ["UP017"]

[tool.ruff.lint.isort]
force-single-line = true
force-sort-within-sections = true
single-line-exclusions = ["typing", "collections.abc"]

[tool.ruff.lint.pydocstyle]
convention = "google"

[tool.ruff.lint.per-file-ignores]
"tests/*" = ["D"]
"""


def _render_docs_map(spec: ScaffoldSpec, today: datetime.date) -> dict[str, str]:
    """Builds root documentation, metadata, and directory placeholder files."""
    return {
        "pyproject.toml": render_pyproject(spec),
        "LICENSE": render_license(spec.license_id, spec.author, today.year),
        "CITATION.cff": (
            "cff-version: 1.2.0\n"
            'message: "If you use this software, please cite it using this metadata."\n'
            f'title: "{spec.dist_name}"\nversion: 0.1.0\n'
            f"date-released: {today.isoformat()}\nlicense: {spec.license_id}\n"
            f'authors:\n  - name: "{spec.author}"\n'
        ),
        ".gitignore": (
            "__pycache__/\n*.py[cod]\n.venv/\ndist/\nbuild/\n*.egg-info/\n"
            ".pytest_cache/\n.ruff_cache/\n.env\n.env.*\n*.pem\n*.key\n"
            "*.h5\n*.hdf5\n*.parquet\n*.npz\n*.pt\n*.safetensors\n"
            "results/intermediate/*\n!results/intermediate/.gitkeep\n"
        ),
        "README.md": (
            f"# {spec.dist_name}\n\n"
            "Reproducible scientific Python project structured following Wilson et al. "
            "(2014, 2017) and the Google Python Style Guide.\n\n"
            "## Quickstart\n\n```bash\n"
            "uv run --with pytest --with numpy pytest\n"
            "uv run scripts/run_pipeline.py --seed 42\n```\n"
        ),
        "CONTRIBUTING.md": (
            "# Contributing\n\n"
            "1. Keep `data/raw/` strictly read-only (`chmod a-w`).\n"
            "2. Place reusable scientific code in `src/`, not inside notebooks.\n"
            "3. Follow Google Python Style (`uv run --with ruff ruff check`).\n"
            "4. Add a `pytest` regression or invariant test for every bug or feature.\n"
        ),
        "data/raw/README.md": (
            "# Raw Data Directory (Read-Only)\n\n"
            "Store immutable original datasets here (`chmod a-w data/raw/*`).\n"
            "Record download URLs, access dates, licenses, and SHA-256 checksums.\n"
        ),
        "data/processed/.gitkeep": "",
        "results/intermediate/.gitkeep": "",
        "results/figures/.gitkeep": "",
        "results/tables/.gitkeep": "",
        "doc/notebook.md": (
            f"# Computational Research Log — {spec.dist_name}\n\n"
            f"## {today.isoformat()}\n- Initialized reproducible project scaffold.\n"
        ),
        "doc/CHANGELOG.md": "# Changelog\n\n## [0.1.0] - Initial Scaffold\n",
    }


def build_file_map(spec: ScaffoldSpec) -> dict[str, str]:
    """Assembles relative file paths and text contents for the new repository."""
    files = _render_docs_map(spec, datetime.date.today())
    files.update({
        f"src/{spec.pkg_name}/__init__.py": (
            f'r"""Core scientific library for {spec.dist_name}."""\n\n'
            '__version__ = "0.1.0"\n'
        ),
        f"src/{spec.pkg_name}/provenance.py": _PROVENANCE_TEMPLATE,
        f"src/{spec.pkg_name}/core.py": _CORE_TEMPLATE,
        "scripts/run_pipeline.py": (
            _DRIVER_TEMPLATE.replace("__PKG_NAME__", spec.pkg_name)
            .replace("__PEP723_OPEN__", "/// script")
            .replace("__PEP723_CLOSE__", "///")
        ),
        "tests/test_smoke.py": _SMOKE_TESTS_TEMPLATE.replace(
            "__PKG_NAME__", spec.pkg_name
        ),
    })
    return files


def scaffold_project(spec: ScaffoldSpec, *, force: bool = False) -> list[pathlib.Path]:
    """Writes all scaffold files to disk safely.

    Args:
        spec: Validated ScaffoldSpec describing target directory and naming.
        force: Whether to overwrite existing files in spec.project_dir.

    Returns:
        Sorted list of created file paths.

    Raises:
        FileExistsError: If a target file already exists and force is False.
    """
    files = build_file_map(spec)
    if not force:
        collisions = [
            spec.project_dir / rel
            for rel in files
            if (spec.project_dir / rel).exists()
        ]
        if collisions:
            joined = ", ".join(str(p) for p in collisions[:3])
            raise FileExistsError(
                f"Refusing to overwrite existing files ({joined}); pass --force to overwrite."
            )

    written: list[pathlib.Path] = []
    for rel_path, content in sorted(files.items()):
        dest = spec.project_dir / rel_path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content, encoding="utf-8")
        if rel_path.startswith("scripts/") and rel_path.endswith(".py"):
            dest.chmod(0o755)
        written.append(dest)
    return written


def parse_cli(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parses command-line arguments for scaffold_research_project."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "project_dir",
        type=pathlib.Path,
        help="Target directory for the new scientific Python project.",
    )
    parser.add_argument(
        "--name",
        default=None,
        help="Importable snake_case package name (defaults to normalized project_dir name).",
    )
    parser.add_argument(
        "--author",
        default="Research Team",
        help="Author or lab name for LICENSE, pyproject.toml, and CITATION.cff.",
    )
    parser.add_argument(
        "--license",
        dest="license_id",
        choices=("MIT", "BSD-3-Clause", "Apache-2.0"),
        default="MIT",
        help="Open-source license to generate (default: MIT).",
    )
    parser.add_argument(
        "--python",
        dest="python_req",
        default=">=3.11",
        help="Python version constraint for pyproject.toml (default: '>=3.11').",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing scaffold files if present.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entrypoint."""
    args = parse_cli(argv)
    project_dir = args.project_dir.resolve()
    pkg_name = derive_package_name(args.name or project_dir.name)
    dist_name = pkg_name.replace("_", "-")
    spec = ScaffoldSpec(
        project_dir=project_dir,
        dist_name=dist_name,
        pkg_name=pkg_name,
        author=args.author,
        license_id=args.license_id,
        python_req=args.python_req,
    )
    written = scaffold_project(spec, force=args.force)
    summary = {
        "project_dir": str(project_dir),
        "dist_name": dist_name,
        "package_name": pkg_name,
        "files_created": len(written),
    }
    sys.stdout.write(json.dumps(summary, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
