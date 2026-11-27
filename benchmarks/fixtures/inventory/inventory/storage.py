"""Read and write inventory snapshots as UTF-8 JSON."""

import json
from decimal import Decimal
from pathlib import Path

from .models import Category, Item
from .store import Store


def save_json(store: Store, path: str | Path) -> None:
    """Write all stock records, preserving order and Decimal precision."""
    records = [
        {
            "sku": item.sku,
            "name": item.name,
            "category": item.category.value,
            "unit_price": str(item.unit_price),
            "quantity": item.quantity,
        }
        for item in store.list_items()
    ]
    Path(path).write_text(
        json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def load_json(path: str | Path) -> Store:
    """Load stock records from a JSON snapshot into a new store."""
    records = json.loads(Path(path).read_text(encoding="utf-8"))
    store = Store()
    for record in records:
        store.add_item(
            Item(
                sku=record["sku"],
                name=record["name"],
                category=Category(record["category"]),
                unit_price=Decimal(record["unit_price"]),
                quantity=record["quantity"],
            )
        )
    return store
