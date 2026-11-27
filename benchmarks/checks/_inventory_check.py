"""Shared test runner for the inventory benchmark checks."""

import os
import shutil
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


def verify_tests(workdir: Path, task_id: str) -> str | None:
    """Run hidden and fixture tests against the submitted workdir."""
    hidden = Path(__file__).resolve().parent / "hidden" / task_id
    env = os.environ.copy()
    env["PYTHONPATH"] = str(workdir)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    command = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"]

    # A sibling directory keeps hidden tests outside the submission even when
    # the system temp directory has been redirected into the workdir.
    with TemporaryDirectory(prefix=f"conductor-{task_id}-", dir=workdir.parent) as temp:
        copied = Path(temp) / "hidden"
        shutil.copytree(hidden, copied)
        for suite, target in (("hidden", copied), ("fixture", workdir / "tests")):
            result = subprocess.run(
                [*command, str(target)],
                cwd=workdir,
                env=env,
                capture_output=True,
                text=True,
            )
            if result.returncode:
                details = result.stdout + result.stderr
                failing_test = next(
                    (
                        line.partition("::")[2].partition(" - ")[0]
                        for line in details.splitlines()
                        if line.startswith(("FAILED ", "ERROR ")) and "::" in line
                    ),
                    None,
                )
                suffix = f" ({failing_test})" if failing_test else ""
                return f"{suite} tests did not pass{suffix}"
    return None


def report(reason: str | None) -> int:
    """Print the benchmark verdict and return its exit status."""
    print(f"FAIL: {reason}" if reason else "PASS")
    return int(reason is not None)
