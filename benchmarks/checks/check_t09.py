"""Check T09. Usage: python check_t09.py <workdir> <fixture_dir>."""

import ast
import sys
from pathlib import Path

sys.dont_write_bytecode = True

from _inventory_check import report, verify_tests


_CLOCKS = {
    "time": {"time", "time_ns", "monotonic", "monotonic_ns", "perf_counter",
             "perf_counter_ns", "process_time", "process_time_ns", "thread_time",
             "thread_time_ns", "clock_gettime", "clock_gettime_ns"},
    "datetime": {"now", "utcnow", "today"},
}


def reads_clock(tree: ast.AST) -> bool:
    """Recognize calls through module imports and direct imports, including aliases."""
    roots: dict[str, set[str]] = {}
    direct = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name in _CLOCKS:
                    roots[alias.asname or alias.name] = _CLOCKS[alias.name]
        if isinstance(node, ast.ImportFrom) and node.level == 0 and node.module in _CLOCKS:
            names = _CLOCKS[node.module]
            for alias in node.names:
                binding = alias.asname or alias.name
                if alias.name == "*":
                    direct.update(names)
                    if node.module == "datetime":
                        roots.update(dict.fromkeys(("datetime", "date"), names))
                elif alias.name in names:
                    direct.add(binding)
                elif node.module == "datetime" and alias.name in {"datetime", "date"}:
                    roots[binding] = names

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Name) and func.id in direct:
            return True
        if isinstance(func, ast.Attribute):
            root = func.value
            while isinstance(root, ast.Attribute):
                root = root.value
            if isinstance(root, ast.Name) and func.attr in roots.get(root.id, set()):
                return True
    return False


def check(workdir: Path) -> str | None:
    """Require a design note, caller-supplied time, and working reservations."""
    note = workdir / "docs" / "RESERVATIONS.md"
    if not note.is_file() or not note.read_text(encoding="utf-8").strip():
        return "docs/RESERVATIONS.md missing or empty"
    if reads_clock(ast.parse((workdir / "inventory" / "store.py").read_bytes())):
        return "inventory/store.py reads the clock"
    return verify_tests(workdir, "T09")


if __name__ == "__main__":
    try:
        reason = check(Path(sys.argv[1]).resolve())
    except (OSError, UnicodeError, SyntaxError) as exc:
        reason = str(exc)
    sys.exit(report(reason))
