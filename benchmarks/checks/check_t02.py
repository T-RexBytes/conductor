"""Pass/fail check for T02. Usage: python check_t02.py <workdir> <fixture_dir>"""

import ast
import sys
from pathlib import Path


def public_functions(source: str) -> list[str]:
    tree = ast.parse(source)
    return [n.name for n in tree.body if isinstance(n, ast.FunctionDef) and not n.name.startswith("_")]


def main(workdir: Path, fixture: Path) -> int:
    doc = workdir / "docs" / "API.md"
    if not doc.is_file():
        print("FAIL: docs/API.md missing")
        return 1
    text = doc.read_text(encoding="utf-8")
    current = (workdir / "calc.py").read_text(encoding="utf-8")
    original = (fixture / "calc.py").read_text(encoding="utf-8")
    if current != original:
        print("FAIL: calc.py was modified")
        return 1
    missing = [name for name in public_functions(current) if name not in text]
    if missing:
        print(f"FAIL: undocumented functions: {missing}")
        return 1
    if text.count("```") < 2:
        print("FAIL: no usage examples")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()))
