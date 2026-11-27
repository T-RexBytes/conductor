"""Check T10. Usage: python check_t10.py <workdir> <fixture_dir>."""

import ast
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

from _inventory_check import report


_FINDING = re.compile(r"inventory/[\w./-]+\.py:([1-9]\d*) - \S.*")


def check(workdir: Path, fixture: Path) -> str | None:
    """Verify the audit points at the fixture bug and preserves Python files."""
    path = workdir / "docs" / "MONEY-AUDIT.md"
    if not path.is_file():
        return "docs/MONEY-AUDIT.md missing"

    original = {p.relative_to(fixture): p.read_bytes() for p in fixture.rglob("*.py")}
    current = {p.relative_to(workdir): p.read_bytes() for p in workdir.rglob("*.py")}
    changed = sorted(path for path in original.keys() | current.keys()
                     if original.get(path) != current.get(path))
    if changed:
        return f"Python file added, removed or changed: {changed[0].as_posix()}"

    source = Path("inventory/report.py")
    tree = ast.parse(original[source])
    rounding_lines = [
        node.lineno for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
        and node.func.attr == "quantize"
    ]
    found = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        match = _FINDING.fullmatch(line)
        if match is None:
            return "expected each finding in path:line - issue format"
        if line.startswith("inventory/report.py:"):
            found |= any(abs(int(match[1]) - lineno) <= 2 for lineno in rounding_lines)
    if not found:
        return "audit must cite the stock report rounding code"
    return None


if __name__ == "__main__":
    try:
        reason = check(Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve())
    except (OSError, UnicodeError, SyntaxError) as exc:
        reason = str(exc)
    sys.exit(report(reason))
