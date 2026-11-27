import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import calc  # noqa: E402


def test_add():
    assert calc.add(2, 3) == 5


def test_subtract():
    assert calc.subtract(5, 3) == 2


def test_multiply():
    assert calc.multiply(4, 3) == 12


def test_divide():
    assert calc.divide(6, 3) == 2


def test_divide_by_zero():
    import pytest
    with pytest.raises(ValueError):
        calc.divide(1, 0)
