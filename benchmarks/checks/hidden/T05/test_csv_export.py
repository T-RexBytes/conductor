"""Exercise CSV serialization and the inventory CLI entry point."""

import csv
import io
import subprocess
import sys
from decimal import Decimal
from pathlib import Path

from inventory import Category, Item, Store, save_json

_HEADER = ["sku", "name", "category", "unit_price", "quantity"]


def test_export_uses_utf8_lf_and_sorted_records(tmp_path: Path) -> None:
    from inventory.storage import export_csv

    store = Store()
    store.add_item(Item("ZZZ-0090", 'Cr\u00e8me "dark", 80%', Category.FOOD, Decimal("9.1"), 3))
    store.add_item(Item("AAA-0020", "Pens", Category.OFFICE, Decimal("11"), 0))
    path = tmp_path / "export.csv"

    export_csv(store, path)

    data = path.read_bytes()
    assert b"\r" not in data
    assert data.endswith(b"\n")
    assert list(csv.reader(io.StringIO(data.decode("utf-8")))) == [
        _HEADER,
        ["AAA-0020", "Pens", "office", "11.00", "0"],
        ["ZZZ-0090", 'Cr\u00e8me "dark", 80%', "food", "9.10", "3"],
    ]


def test_empty_export_has_only_header(tmp_path: Path) -> None:
    from inventory.storage import export_csv

    path = tmp_path / "empty.csv"
    export_csv(Store(), path)
    assert path.read_bytes() == b"sku,name,category,unit_price,quantity\n"


def test_cli_exports_to_requested_path(tmp_path: Path) -> None:
    source = tmp_path / "snapshot.json"
    destination = tmp_path / "output file.csv"
    store = Store()
    store.add_item(Item("HDW-0009", "Nut", Category.HARDWARE, Decimal("0.9"), 4))
    save_json(store, source)

    result = subprocess.run(
        [sys.executable, "-m", "inventory.cli", "--input", str(source), "csv", str(destination)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert destination.read_bytes() == (
        b"sku,name,category,unit_price,quantity\nHDW-0009,Nut,hardware,0.90,4\n"
    )
