"""Check T04. Usage: python check_t04.py <workdir> <fixture_dir>."""

import sys
import tokenize
from pathlib import Path

sys.dont_write_bytecode = True

from _inventory_check import report, verify_tests


def check(workdir: Path) -> str | None:
    """Reject remaining identifiers using the old lookup method name."""
    for source in sorted(workdir.rglob("*.py")):
        with source.open("rb") as stream:
            if any(
                token.type == tokenize.NAME and token.string == "find_item"
                for token in tokenize.tokenize(stream.readline)
            ):
                return f"find_item identifier remains in {source.relative_to(workdir).as_posix()}"
    return verify_tests(workdir, "T04")


if __name__ == "__main__":
    workdir = Path(sys.argv[1]).resolve()
    try:
        reason = check(workdir)
    except (OSError, SyntaxError, tokenize.TokenError) as exc:
        reason = str(exc)
    sys.exit(report(reason))
