"""Check T06. Usage: python check_t06.py <workdir> <fixture_dir>."""

import sys
from pathlib import Path

sys.dont_write_bytecode = True

from _inventory_check import report, verify_tests


if __name__ == "__main__":
    workdir = Path(sys.argv[1]).resolve()
    try:
        reason = verify_tests(workdir, "T06")
    except (OSError,) as exc:
        reason = str(exc)
    sys.exit(report(reason))
