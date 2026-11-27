"""Check the renamed store lookup through the package API."""

from decimal import Decimal

from inventory import Category, Item, Store


def test_get_item_returns_item_or_none() -> None:
    store = Store()
    item = Item("OFF-0019", "Pencil", Category.OFFICE, Decimal("0.45"), 6)

    assert store.get_item(item.sku) is None
    store.add_item(item)
    assert store.get_item(item.sku) is item
    store.remove_item(item.sku)
    assert store.get_item(item.sku) is None
