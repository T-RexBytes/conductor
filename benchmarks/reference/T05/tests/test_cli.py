"""Tests for the command-line entry point."""

from decimal import Decimal
from pathlib import Path

import pytest

from inventory import Category, Item, Store, save_json
from inventory.cli import main


@pytest.fixture
def snapshot(tmp_path: Path) -> Path:
    """Write stock from two categories for the CLI to read."""
    store = Store()
    store.add_item(Item("OFF-0002", "Notebook", Category.OFFICE, Decimal("3.5"), 12))
    store.add_item(Item("FOD-0001", "Tea", Category.FOOD, Decimal("8"), 1))
    path = tmp_path / "stock.json"
    save_json(store, path)
    return path


def test_list(snapshot: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--input", str(snapshot), "list"]) == 0
    assert capsys.readouterr().out.splitlines() == [
        "OFF-0002\tNotebook\t12",
        "FOD-0001\tTea\t1",
    ]


def test_list_filters_category(snapshot: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--input", str(snapshot), "list", "--category", "food"]) == 0
    assert capsys.readouterr().out == "FOD-0001\tTea\t1\n"


def test_report(snapshot: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--input", str(snapshot), "report"]) == 0
    assert "Unit price" in capsys.readouterr().out


def test_missing_snapshot_is_a_usage_error(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as error:
        main(["--input", str(tmp_path / "missing.json"), "list"])
    assert error.value.code == 2
    assert "could not load inventory" in capsys.readouterr().err


def test_csv_writes_snapshot_to_output_path(snapshot: Path, tmp_path: Path) -> None:
    path = tmp_path / "export.csv"

    assert main(["--input", str(snapshot), "csv", str(path)]) == 0

    assert path.read_bytes() == (
        b"sku,name,category,unit_price,quantity\n"
        b"FOD-0001,Tea,food,8.00,1\n"
        b"OFF-0002,Notebook,office,3.50,12\n"
    )
