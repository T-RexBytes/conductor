"""Read and write inventory snapshots and export them as CSV."""

import csv
import json
from decimal import Decimal
from io import StringIO
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


def export_csv(store: Store, path: str | Path) -> None:
    """Write SKU-sorted records to a UTF-8 CSV file with LF line endings."""
    with Path(path).open("w", encoding="utf-8", newline="") as stream:
        stream.write("sku,name,category,unit_price,quantity\n")
        buffer = StringIO(newline="")
        # The default CSV terminator makes the writer quote both CR and LF
        # inside fields. Replace only the terminator it adds to each row.
        writer = csv.writer(buffer)
        for item in sorted(store.list_items(), key=lambda item: item.sku):
            writer.writerow(
                (item.sku, item.name, item.category.value, f"{item.unit_price:.2f}", item.quantity)
            )
            stream.write(buffer.getvalue().removesuffix("\r\n") + "\n")
            buffer.seek(0)
            buffer.truncate()
