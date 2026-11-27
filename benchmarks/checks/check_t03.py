"""Check T03. Usage: python check_t03.py <workdir> <fixture_dir>."""

import ast
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

from _inventory_check import report


def public_functions(source: Path) -> set[str]:
    """Find public functions and methods declared in this source file."""
    tree = ast.parse(source.read_bytes())
    bodies = [tree.body]
    bodies.extend(
        node.body for node in tree.body
        if isinstance(node, ast.ClassDef) and not node.name.startswith("_")
    )
    return {
        node.name
        for body in bodies
        for node in body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and not node.name.startswith("_")
    }


def check(workdir: Path, fixture: Path) -> str | None:
    """Validate the architecture document and compare all Python sources."""
    path = workdir / "docs" / "ARCHITECTURE.md"
    if not path.is_file():
        return "docs/ARCHITECTURE.md missing"
    text = path.read_text(encoding="utf-8")

    original = {p.relative_to(fixture): p.read_bytes() for p in fixture.rglob("*.py")}
    current = {p.relative_to(workdir): p.read_bytes() for p in workdir.rglob("*.py")}
    changed = sorted(path for path in original.keys() | current.keys()
                     if original.get(path) != current.get(path))
    if changed:
        return f"Python file added, removed or changed: {changed[0].as_posix()}"

    headings = re.findall(r"^ {0,3}#{1,6}[ \t]+(.+)$", text, flags=re.MULTILINE)
    for module in sorted((fixture / "inventory").rglob("*.py")):
        if not any(re.search(rf"\b{re.escape(module.stem)}\b", title, re.IGNORECASE)
                   for title in headings):
            return f"missing heading for {module.name}"
        for name in sorted(public_functions(module)):
            if not re.search(rf"\b{re.escape(name)}\b", text):
                return f"undocumented public function: {name}"
    return None


if __name__ == "__main__":
    try:
        reason = check(Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve())
    except (OSError, UnicodeError, SyntaxError) as exc:
        reason = str(exc)
    sys.exit(report(reason))
