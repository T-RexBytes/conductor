"""Smoke tests for the package-level API."""

import inventory


def test_public_exports_are_importable() -> None:
    namespace: dict[str, object] = {}
    exec("from inventory import *", namespace)
    for name in (
        "Category", "Item", "Page", "Store", "add_tax", "apply_discount",
        "load_json", "order_total", "paginate", "save_json", "stock_report",
    ):
        assert namespace[name] is getattr(inventory, name)
