"""Tests for inventory snapshot persistence."""

import json
from decimal import Decimal
from pathlib import Path

import pytest

from inventory import Category, Item, Store, load_json, save_json


def test_round_trip_preserves_order_and_precision(tmp_path: Path) -> None:
    path = tmp_path / "stock.json"
    store = Store()
    store.add_item(Item("OFF-0002", "Caf\u00e9 notebook", Category.OFFICE, Decimal("2.3400"), 3))
    store.add_item(Item("FOD-0001", "Tea", Category.FOOD, Decimal("3"), 0))

    save_json(store, path)

    records = json.loads(path.read_text(encoding="utf-8"))
    assert records[0]["unit_price"] == "2.3400"
    assert records[0]["name"] == "Caf\u00e9 notebook"
    assert load_json(str(path)).list_items() == store.list_items()


def test_round_trip_empty_store(tmp_path: Path) -> None:
    path = tmp_path / "stock.json"
    save_json(Store(), str(path))
    assert load_json(path).list_items() == []


def test_load_rejects_invalid_category(tmp_path: Path) -> None:
    path = tmp_path / "stock.json"
    record = {"sku": "OFF-0001", "name": "Pen", "category": "unknown", "unit_price": "1", "quantity": 1}
    path.write_text(json.dumps([record]), encoding="utf-8")
    with pytest.raises(ValueError, match="unknown"):
        load_json(path)
