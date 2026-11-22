#!/usr/bin/env python3
r"""Static AST auditor for Scientific Python and Google Python Style compliance.

Checks Python source files or directories for reproducibility, numerical safety,
resource-management, and modularity hazards synthesized from:
- Wilson et al. (2014), "Best Practices for Scientific Computing" (arXiv:1210.0530)
- Wilson et al. (2017), "Good Enough Practices in Scientific Computing" (arXiv:1609.00037)
- Google Python Style Guide (https://google.github.io/styleguide/pyguide.html)
"""

# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

from __future__ import annotations

import argparse
import ast
from collections.abc import Iterable, Sequence
import dataclasses
import io
import json
import pathlib
import re
import sys
import tokenize
from typing import Any

SKIP_DIRS = frozenset({
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    "build",
    "dist",
    "node_modules",
})

IMMUTABLE_CALL_DEFAULTS = frozenset({
    "tuple",
    "frozenset",
    "bytes",
    "Path",
    "PurePath",
    "PurePosixPath",
    "Decimal",
    "Fraction",
})

MODULE_ONLY_STDLIB = frozenset({
    "os",
    "os.path",
    "sys",
    "json",
    "math",
    "re",
    "subprocess",
    "shutil",
    "tempfile",
    "time",
    "random",
    "pickle",
    "csv",
    "gzip",
    "hashlib",
    "glob",
    "statistics",
})

GLOBAL_RNG_CALLS = frozenset({
    "random.seed",
    "random.random",
    "random.uniform",
    "random.gauss",
    "random.normalvariate",
    "random.randint",
    "random.randrange",
    "random.choice",
    "random.choices",
    "random.shuffle",
    "random.sample",
    "np.random.seed",
    "numpy.random.seed",
    "np.random.rand",
    "numpy.random.rand",
    "np.random.randn",
    "numpy.random.randn",
    "np.random.randint",
    "numpy.random.randint",
    "np.random.random",
    "numpy.random.random",
    "np.random.choice",
    "numpy.random.choice",
    "np.random.normal",
    "numpy.random.normal",
    "np.random.uniform",
    "numpy.random.uniform",
    "np.random.shuffle",
    "numpy.random.shuffle",
    "np.random.permutation",
    "numpy.random.permutation",
})

RESOURCE_OPEN_CALLS = frozenset({
    "open",
    "io.open",
    "gzip.open",
    "bz2.open",
    "lzma.open",
    "h5py.File",
    "sqlite3.connect",
    "tarfile.open",
    "zipfile.ZipFile",
})

LOG_METHODS = frozenset({
    "debug",
    "info",
    "warning",
    "warn",
    "error",
    "critical",
    "exception",
})

SIDE_EFFECT_TOP_CALLS = GLOBAL_RNG_CALLS | frozenset({
    "print",
    "open",
    "subprocess.run",
    "subprocess.Popen",
    "subprocess.call",
    "subprocess.check_call",
    "subprocess.check_output",
    "os.makedirs",
    "os.remove",
    "shutil.rmtree",
    "plt.plot",
    "plt.savefig",
    "plt.show",
    "np.save",
    "np.savez",
    "torch.save",
    "torch.manual_seed",
    "torch.cuda.manual_seed_all",
})

NON_SEMANTIC_PATH_RE = re.compile(
    r"(?:^|[/\\])(?:fig(?:ure)?[_-]?\d+[a-z]?|tab(?:le)?[_-]?\d+[a-z]?|"
    r"result[_-]?\d+|output[_-]?\d+|temp[_-]?\d+|test_out[_-]?\d+)\."
    r"(?:png|pdf|svg|eps|jpg|jpeg|csv|tsv|parquet|json|tex|npy|npz|pt|pth|h5)$",
    re.IGNORECASE,
)

JPEG_PLOT_RE = re.compile(r"\.(?:jpg|jpeg)$", re.IGNORECASE)
ARRAY_TYPE_RE = re.compile(r"\b(?:ndarray|Tensor|Array)\b")


@dataclasses.dataclass(frozen=True)
class Finding:
    """Single static analysis finding on a Python source file."""

    file: str
    line: int
    severity: str
    rule: str
    message: str


def dotted_name(node: ast.AST) -> str | None:
    """Extracts a dotted identifier such as 'np.random.seed' from an AST node."""
    parts: list[str] = []
    cur: ast.AST | None = node
    while isinstance(cur, ast.Attribute):
        parts.append(cur.attr)
        cur = cur.value
    if isinstance(cur, ast.Name):
        parts.append(cur.id)
        return ".".join(reversed(parts))
    return None


def is_test_path(path: pathlib.Path) -> bool:
    """Returns True when path is a pytest/unittest test module."""
    return (
        path.name.startswith("test_")
        or path.name.endswith("_test.py")
        or "tests" in path.parts
    )


def extract_suppressed_lines(source: str) -> dict[int, str]:
    """Collects inline '# noqa', '# pylint: disable=', and '# sci-lint: ignore' lines."""
    suppressed: dict[int, str] = {}
    try:
        tokens = tokenize.generate_tokens(io.StringIO(source).readline)
        for tok_type, tok_str, (srow, _), _, _ in tokens:
            if tok_type == tokenize.COMMENT:
                lowered = tok_str.lower()
                if (
                    "noqa" in lowered
                    or "pylint: disable" in lowered
                    or "sci-lint: ignore" in lowered
                ):
                    suppressed[srow] = lowered
    except tokenize.TokenError:
        pass
    return suppressed


def is_suppressed(line: int, rule: str, suppressed_lines: dict[int, str]) -> bool:
    """Checks whether a finding on `line` is suppressed by an inline comment."""
    comment = suppressed_lines.get(line)
    if not comment:
        return False
    if "sci-lint: ignore" in comment:
        return True
    if re.search(r"#\s*noqa\b(?!:)", comment):
        return True
    return rule.lower() in comment


def is_main_guard(node: ast.If) -> bool:
    """Returns True if `node` is `if __name__ == '__main__':`."""
    test = node.test
    if not isinstance(test, ast.Compare) or len(test.ops) != 1:
        return False
    if not isinstance(test.ops[0], ast.Eq) or len(test.comparators) != 1:
        return False
    left, right = test.left, test.comparators[0]
    return (
        isinstance(left, ast.Name)
        and left.id == "__name__"
        and isinstance(right, ast.Constant)
        and right.value == "__main__"
    )


def executable_body_lines(fn: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
    """Counts function lines excluding a leading docstring block."""
    if not fn.body or fn.end_lineno is None:
        return 0
    start_line = fn.body[0].lineno
    first = fn.body[0]
    if (
        isinstance(first, ast.Expr)
        and isinstance(first.value, ast.Constant)
        and isinstance(first.value.value, str)
        and first.end_lineno is not None
    ):
        if len(fn.body) == 1:
            return 0
        start_line = fn.body[1].lineno
    return max(0, fn.end_lineno - start_line + 1)


def check_imports(tree: ast.Module, rel_file: str) -> list[Finding]:
    """Audits Google Style §2.2 & §3.13 import conventions."""
    out: list[Finding] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import) and len(node.names) > 1:
            out.append(
                Finding(
                    rel_file,
                    node.lineno,
                    "WARNING",
                    "multiple_imports_on_line",
                    "Place each import on its own line (Google Python Style §3.13).",
                )
            )
        elif isinstance(node, ast.ImportFrom):
            if any(alias.name == "*" for alias in node.names):
                out.append(
                    Finding(
                        rel_file,
                        node.lineno,
                        "ERROR",
                        "wildcard_import",
                        "Wildcard `from ... import *` pollutes namespace and breaks reproducibility (Google §2.2).",
                    )
                )
            if node.level and node.level > 0:
                out.append(
                    Finding(
                        rel_file,
                        node.lineno,
                        "WARNING",
                        "relative_import",
                        "Avoid relative imports; import via the full package path (Google §2.2).",
                    )
                )
            if node.module in MODULE_ONLY_STDLIB:
                out.append(
                    Finding(
                        rel_file,
                        node.lineno,
                        "WARNING",
                        "symbol_import_instead_of_module",
                        f"Import module `{node.module}` directly rather than individual symbols (Google §2.2).",
                    )
                )
    return out


def check_top_level_exec(tree: ast.Module, rel_file: str) -> list[Finding]:
    """Flags top-level side effects outside `if __name__ == '__main__':` (Google §3.17)."""
    out: list[Finding] = []
    for stmt in tree.body:
        if isinstance(stmt, ast.If) and is_main_guard(stmt):
            continue
        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
            cname = dotted_name(stmt.value.func) or ""
            if cname in SIDE_EFFECT_TOP_CALLS or cname.endswith(".parse_args"):
                out.append(
                    Finding(
                        rel_file,
                        stmt.lineno,
                        "WARNING",
                        "unprotected_top_level_exec",
                        f"Top-level call `{cname}(...)` runs on import; move inside `def main()` under `if __name__ == '__main__':` (Google §3.17).",
                    )
                )
        elif isinstance(stmt, (ast.Assign, ast.AnnAssign)) and isinstance(
            stmt.value, ast.Call
        ):
            cname = dotted_name(stmt.value.func) or ""
            if cname.endswith(".parse_args") or cname in RESOURCE_OPEN_CALLS:
                out.append(
                    Finding(
                        rel_file,
                        stmt.lineno,
                        "WARNING",
                        "unprotected_top_level_exec",
                        f"Top-level `{cname}(...)` executes at import time; wrap CLI/IO inside `main()` (Google §3.17).",
                    )
                )
    return out


def _check_mutable_defaults(
    fn: ast.FunctionDef | ast.AsyncFunctionDef, rel_file: str
) -> list[Finding]:
    """Audits mutable or runtime-call default arguments (Google §2.12)."""
    out: list[Finding] = []
    defaults = list(fn.args.defaults) + [
        d for d in fn.args.kw_defaults if d is not None
    ]
    for dnode in defaults:
        is_mut_lit = isinstance(
            dnode,
            (ast.List, ast.Dict, ast.Set, ast.ListComp, ast.DictComp, ast.SetComp),
        )
        cname = dotted_name(dnode.func) if isinstance(dnode, ast.Call) else None
        is_mut_call = isinstance(dnode, ast.Call) and (
            (cname.split(".")[-1] if cname else "") not in IMMUTABLE_CALL_DEFAULTS
        )
        if is_mut_lit or is_mut_call:
            out.append(
                Finding(
                    rel_file,
                    dnode.lineno,
                    "ERROR",
                    "mutable_default_arg",
                    f"Function `{fn.name}` uses a mutable/call default; default to `None` and initialize inside body (Google §2.12).",
                )
            )
    return out


def _check_function_defaults_and_signature(
    fn: ast.FunctionDef | ast.AsyncFunctionDef,
    user_args: list[ast.arg],
    rel_file: str,
    is_test: bool,
) -> list[Finding]:
    """Audits mutable defaults, argument count, chunk length, and docstrings."""
    out = _check_mutable_defaults(fn, rel_file)
    if len(user_args) > 7 and not is_test:
        out.append(
            Finding(
                rel_file,
                fn.lineno,
                "WARNING",
                "too_many_arguments",
                f"Function `{fn.name}` takes {len(user_args)} parameters (>7); bundle cohesive settings into a frozen `@dataclass` (Wilson 2014 §1).",
            )
        )

    body_len = executable_body_lines(fn)
    if body_len > 65 and not is_test:
        out.append(
            Finding(
                rel_file,
                fn.lineno,
                "WARNING",
                "long_function",
                f"Function `{fn.name}` spans {body_len} executable lines (>65); decompose into smaller single-purpose chunks (Wilson 2017 §2b, Google §3.18).",
            )
        )

    has_override = any(
        (dotted_name(dec) or "").endswith("override") for dec in fn.decorator_list
    )
    if (
        not is_test
        and not fn.name.startswith("_")
        and fn.name != "main"
        and not has_override
        and body_len > 10
        and ast.get_docstring(fn) is None
    ):
        out.append(
            Finding(
                rel_file,
                fn.lineno,
                "WARNING",
                "missing_docstring",
                f"Public function `{fn.name}` ({body_len} lines) lacks a Google-style docstring specifying Args/Returns/units (Google §3.8).",
            )
        )
    return out


def _check_function_body_invariants(
    fn: ast.FunctionDef | ast.AsyncFunctionDef,
    user_args: list[ast.arg],
    rel_file: str,
    is_test: bool,
) -> list[Finding]:
    """Checks public precondition asserts and array/tensor truthiness traps."""
    out: list[Finding] = []
    param_names = {a.arg for a in user_args}
    array_params = {
        a.arg
        for a in user_args
        if a.annotation is not None
        and ARRAY_TYPE_RE.search(ast.unparse(a.annotation))
    }

    if not is_test and not fn.name.startswith("_"):
        for stmt in fn.body[:4]:
            if isinstance(stmt, ast.Assert):
                names = {
                    n.id for n in ast.walk(stmt.test) if isinstance(n, ast.Name)
                }
                if names & param_names:
                    out.append(
                        Finding(
                            rel_file,
                            stmt.lineno,
                            "WARNING",
                            "assert_public_precondition",
                            f"Public function `{fn.name}` uses `assert` to validate inputs (`python -O` strips asserts); raise `ValueError` instead (Google §2.4.4).",
                        )
                    )

    for sub in ast.walk(fn):
        if isinstance(sub, ast.If):
            tname: str | None = None
            if isinstance(sub.test, ast.Name):
                tname = sub.test.id
            elif (
                isinstance(sub.test, ast.UnaryOp)
                and isinstance(sub.test.op, ast.Not)
                and isinstance(sub.test.operand, ast.Name)
            ):
                tname = sub.test.operand.id
            if tname in array_params:
                out.append(
                    Finding(
                        rel_file,
                        sub.lineno,
                        "ERROR",
                        "ambiguous_array_truthiness",
                        f"Implicit truthiness check on array/tensor `{tname}` raises ValueError on multi-element arrays; check `{tname} is None` or `{tname}.size == 0` / `.numel() == 0` (Google §2.14.4).",
                    )
                )
    return out


def check_functions_and_docstrings(
    tree: ast.Module, path: pathlib.Path, rel_file: str
) -> list[Finding]:
    """Audits module/class/function docstrings, defaults, and complexity."""
    out: list[Finding] = []
    is_test = is_test_path(path)
    if (
        not is_test
        and path.name != "__init__.py"
        and tree.body
        and ast.get_docstring(tree) is None
    ):
        out.append(
            Finding(
                rel_file,
                1,
                "WARNING",
                "missing_docstring",
                "Module is missing a top-level summary docstring (Google §3.8.1).",
            )
        )

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            if (
                not is_test
                and not node.name.startswith("_")
                and ast.get_docstring(node) is None
            ):
                out.append(
                    Finding(
                        rel_file,
                        node.lineno,
                        "WARNING",
                        "missing_docstring",
                        f"Public class `{node.name}` is missing a docstring (Google §3.8.3).",
                    )
                )
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            all_args = (
                list(node.args.posonlyargs)
                + list(node.args.args)
                + list(node.args.kwonlyargs)
            )
            uargs = [a for a in all_args if a.arg not in {"self", "cls"}]
            out.extend(
                _check_function_defaults_and_signature(node, uargs, rel_file, is_test)
            )
            out.extend(
                _check_function_body_invariants(node, uargs, rel_file, is_test)
            )
    return out


def _extract_var_in_simple_bound(comp: ast.Compare) -> tuple[str, str] | None:
    """Returns (var_name, 'low'|'high') if `comp` is a simple `x < c` or `x > c`."""
    if len(comp.ops) != 1 or len(comp.comparators) != 1:
        return None
    op = comp.ops[0]
    left, right = comp.left, comp.comparators[0]
    if isinstance(left, ast.Name) and isinstance(op, (ast.Lt, ast.LtE)):
        return (left.id, "low")
    if isinstance(left, ast.Name) and isinstance(op, (ast.Gt, ast.GtE)):
        return (left.id, "high")
    if isinstance(right, ast.Name) and isinstance(op, (ast.Gt, ast.GtE)):
        return (right.id, "low")
    if isinstance(right, ast.Name) and isinstance(op, (ast.Lt, ast.LtE)):
        return (right.id, "high")
    return None


def _collect_managed_calls(tree: ast.Module) -> set[int]:
    """Returns AST node IDs of calls wrapped in `with` or `enter_context`."""
    managed: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.With, ast.AsyncWith)):
            for item in node.items:
                ctx = item.context_expr
                if isinstance(ctx, ast.Call):
                    managed.add(id(ctx))
                    for arg in ctx.args:
                        if isinstance(arg, ast.Call):
                            managed.add(id(arg))
        elif isinstance(node, ast.Call):
            cname = dotted_name(node.func) or ""
            if cname.endswith(".enter_context") or cname.endswith("closing"):
                for arg in node.args:
                    if isinstance(arg, ast.Call):
                        managed.add(id(arg))
    return managed


def _audit_except_and_bounds(node: ast.AST, rel_file: str) -> list[Finding]:
    """Checks bare/swallowed except handlers and NaN-unsafe range guards."""
    out: list[Finding] = []
    if isinstance(node, ast.ExceptHandler):
        if node.type is None:
            out.append(
                Finding(
                    rel_file,
                    node.lineno,
                    "ERROR",
                    "bare_except",
                    "Bare `except:` traps SystemExit and KeyboardInterrupt; catch specific exception types (Google §2.4).",
                )
            )
        elif dotted_name(node.type) in {"Exception", "BaseException"}:
            logged_or_raised = any(
                isinstance(sub, ast.Raise)
                or (
                    isinstance(sub, ast.Call)
                    and (dotted_name(sub.func) or "").split(".")[-1]
                    in LOG_METHODS | {"warn"}
                )
                for sub in ast.walk(node)
            )
            if not logged_or_raised:
                out.append(
                    Finding(
                        rel_file,
                        node.lineno,
                        "WARNING",
                        "swallowed_broad_except",
                        "Broad `except Exception:` without logging or re-raising silently masks numerical/data corruption (Google §2.4).",
                    )
                )
    elif isinstance(node, ast.If) and isinstance(node.test, ast.BoolOp):
        if isinstance(node.test.op, ast.Or) and len(node.test.values) == 2:
            b0, b1 = node.test.values
            if isinstance(b0, ast.Compare) and isinstance(b1, ast.Compare):
                v0 = _extract_var_in_simple_bound(b0)
                v1 = _extract_var_in_simple_bound(b1)
                raises = any(isinstance(s, ast.Raise) for s in node.body)
                if (
                    raises
                    and v0
                    and v1
                    and v0[0] == v1[0]
                    and {v0[1], v1[1]} == {"low", "high"}
                ):
                    out.append(
                        Finding(
                            rel_file,
                            node.lineno,
                            "WARNING",
                            "nan_unsafe_range_check",
                            f"Range check on `{v0[0]}` using `or` silently lets `NaN` pass! Rewrite as `if not lo <= {v0[0]} <= hi:` (Google §3.10.2).",
                        )
                    )
    return out


def _audit_call_expression(
    node: ast.Call, managed_calls: set[int], rel_file: str
) -> list[Finding]:
    """Audits global RNG calls, unclosed files, f-string logging, and JPEG plots."""
    out: list[Finding] = []
    cname = dotted_name(node.func) or ""
    if cname in GLOBAL_RNG_CALLS:
        out.append(
            Finding(
                rel_file,
                node.lineno,
                "WARNING",
                "legacy_global_rng",
                f"Global RNG call `{cname}(...)` couples stochastic state across modules; pass an isolated `np.random.default_rng(seed)` or `random.Random(seed)` (Wilson 2014 §2).",
            )
        )
    if cname in RESOURCE_OPEN_CALLS and id(node) not in managed_calls:
        out.append(
            Finding(
                rel_file,
                node.lineno,
                "WARNING",
                "unclosed_resource",
                f"Resource `{cname}(...)` opened outside a `with` context manager; wrap in `with` for deterministic cleanup (Google §3.11).",
            )
        )
    parts = cname.split(".")
    if (
        len(parts) >= 2
        and parts[-1] in LOG_METHODS
        and ("log" in parts[0].lower() or parts[0] == "logging")
        and node.args
        and isinstance(node.args[0], ast.JoinedStr)
    ):
        out.append(
            Finding(
                rel_file,
                node.lineno,
                "WARNING",
                "fstring_in_logging",
                f"`{cname}(f'...')` eagerly formats strings even when log level is disabled; use `%`-pattern `{cname}('... %s', val)` (Google §3.10.1).",
            )
        )
    if cname.endswith("savefig") and node.args:
        first_arg = node.args[0]
        if (
            isinstance(first_arg, ast.Constant)
            and isinstance(first_arg.value, str)
            and JPEG_PLOT_RE.search(first_arg.value)
        ):
            out.append(
                Finding(
                    rel_file,
                    node.lineno,
                    "ERROR",
                    "jpeg_scientific_figure",
                    f"`savefig({first_arg.value!r})` uses lossy JPEG compression; save scientific figures as vector `.pdf`/`.svg` or lossless `.png`.",
                )
            )
    return out


def check_exceptions_numerics_and_resources(
    tree: ast.Module, rel_file: str
) -> list[Finding]:
    """Audits bare excepts, RNG state, NaN hazards, unclosed files, logging, and paths."""
    out: list[Finding] = []
    managed = _collect_managed_calls(tree)

    for node in ast.walk(tree):
        out.extend(_audit_except_and_bounds(node, rel_file))
        if isinstance(node, ast.Compare):
            for op, comp in zip(node.ops, node.comparators):
                if isinstance(op, (ast.Eq, ast.NotEq)):
                    for side in (node.left, comp):
                        if (
                            isinstance(side, ast.Constant)
                            and isinstance(side.value, float)
                            and side.value != 0.0
                        ):
                            out.append(
                                Finding(
                                    rel_file,
                                    node.lineno,
                                    "WARNING",
                                    "exact_float_equality",
                                    f"Exact equality check against float `{side.value}` is brittle under IEEE-754 rounding; use `math.isclose` or `np.allclose` with explicit `rtol`/`atol` (Wilson 2014 §5).",
                                )
                            )
                            break
        elif isinstance(node, ast.Call):
            out.extend(_audit_call_expression(node, managed, rel_file))
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            if len(node.value) <= 200 and NON_SEMANTIC_PATH_RE.search(node.value):
                out.append(
                    Finding(
                        rel_file,
                        node.lineno,
                        "WARNING",
                        "non_semantic_artifact_path",
                        f"Artifact path `{node.value}` uses manuscript-order or placeholder numbering; name files semantically (e.g., `perplexity_vs_rank.pdf`, Wilson 2017 §4f).",
                    )
                )
    return out


def iter_python_files(target: pathlib.Path) -> Iterable[pathlib.Path]:
    """Yields Python files under target, skipping caches and virtual environments."""
    if target.is_file():
        if target.suffix == ".py":
            yield target
        return
    for item in sorted(target.rglob("*.py")):
        if any(part in SKIP_DIRS for part in item.parts):
            continue
        yield item


def audit_file(path: pathlib.Path, root: pathlib.Path) -> list[Finding]:
    """Runs all AST and token checks on a single Python file."""
    rel = str(path.relative_to(root)) if path.is_relative_to(root) else str(path)
    source = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(source, filename=rel)
    except SyntaxError as exc:
        return [
            Finding(
                rel,
                exc.lineno or 1,
                "ERROR",
                "syntax_error",
                f"Python syntax error: {exc.msg}",
            )
        ]

    suppressed = extract_suppressed_lines(source)
    raw_findings: list[Finding] = []
    raw_findings.extend(check_imports(tree, rel))
    raw_findings.extend(check_top_level_exec(tree, rel))
    raw_findings.extend(check_functions_and_docstrings(tree, path, rel))
    raw_findings.extend(check_exceptions_numerics_and_resources(tree, rel))

    filtered = [
        f for f in raw_findings if not is_suppressed(f.line, f.rule, suppressed)
    ]
    filtered.sort(key=lambda item: (item.file, item.line, item.rule))
    return filtered


def audit_target(target: pathlib.Path) -> dict[str, Any]:
    """Audits a file or directory and returns a structured JSON-ready report."""
    resolved = target.resolve()
    root = resolved if resolved.is_dir() else resolved.parent
    files = list(iter_python_files(resolved))
    all_findings: list[Finding] = []
    for py_file in files:
        all_findings.extend(audit_file(py_file, root))

    by_rule: dict[str, int] = {}
    errors = 0
    warnings = 0
    for item in all_findings:
        by_rule[item.rule] = by_rule.get(item.rule, 0) + 1
        if item.severity == "ERROR":
            errors += 1
        else:
            warnings += 1

    return {
        "target": str(resolved),
        "files_scanned": len(files),
        "clean": len(all_findings) == 0,
        "counts": {
            "total": len(all_findings),
            "errors": errors,
            "warnings": warnings,
            "by_rule": by_rule,
        },
        "findings": [dataclasses.asdict(f) for f in all_findings],
    }


def parse_cli(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parses CLI options for audit_scientific_python."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "target",
        type=pathlib.Path,
        help="Python file or directory to audit.",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=pathlib.Path,
        default=None,
        help="Optional path to write JSON audit report.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with code 1 if any ERROR or WARNING finding is reported.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entrypoint."""
    args = parse_cli(argv)
    if not args.target.exists():
        sys.stderr.write(f"Target path does not exist: {args.target}\n")
        return 2
    report = audit_target(args.target)
    payload = json.dumps(report, indent=2) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", encoding="utf-8") as handle:
            handle.write(payload)
    sys.stdout.write(payload)
    if args.strict and not report["clean"]:
        return 1
    if report["counts"]["errors"] > 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
