"""Pass/fail check for T01. Usage: python check_t01.py <workdir>"""

import importlib.util
import subprocess
import sys
from pathlib import Path


def main(workdir: Path) -> int:
    spec = importlib.util.spec_from_file_location("calc", workdir / "calc.py")
    if spec is None or spec.loader is None:
        print("FAIL: calc.py not found")
        return 1
    calc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(calc)
    if not hasattr(calc, "divide"):
        print("FAIL: divide() missing")
        return 1
    if calc.divide(6, 3) != 2:
        print("FAIL: divide(6, 3) != 2")
        return 1
    try:
        calc.divide(1, 0)
    except ValueError as exc:
        if "division by zero" not in str(exc):
            print("FAIL: wrong ValueError message")
            return 1
    else:
        print("FAIL: divide(1, 0) did not raise ValueError")
        return 1
    tests = (workdir / "tests" / "test_calc.py").read_text(encoding="utf-8")
    if "divide" not in tests:
        print("FAIL: no tests for divide()")
        return 1
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q"], cwd=workdir, capture_output=True, text=True
    )
    if result.returncode != 0:
        print("FAIL: test suite does not pass")
        return 1
    if calc.add(2, 3) != 5 or calc.multiply(4, 3) != 12:
        print("FAIL: existing behavior changed")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1]).resolve()))
