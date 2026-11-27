"""Tests for in-memory inventory operations."""

from decimal import Decimal

import pytest

from inventory import Category, Item, Store


@pytest.fixture
def stocked_store() -> tuple[Store, Item, Item]:
    """Return a store with two items from different categories."""
    store = Store()
    bolts = Item("HDW-0002", "Bolts", Category.HARDWARE, Decimal("0.30"), 12)
    tea = Item("FOD-0001", "Tea", Category.FOOD, Decimal("3.50"), 4)
    store.add_item(bolts)
    store.add_item(tea)
    return store, bolts, tea


def test_get_and_remove(stocked_store: tuple[Store, Item, Item]) -> None:
    store, bolts, tea = stocked_store
    assert store.get_item(bolts.sku) == bolts
    assert store.remove_item(bolts.sku) == bolts
    assert store.get_item(bolts.sku) is None
    assert store.remove_item(bolts.sku) is None
    assert store.list_items() == [tea]


def test_list_is_filtered_and_independent(stocked_store: tuple[Store, Item, Item]) -> None:
    store, bolts, tea = stocked_store
    assert store.list_items(Category.FOOD) == [tea]
    assert store.list_items(Category.OFFICE) == []
    snapshot = store.list_items()
    assert snapshot == [bolts, tea]
    snapshot.clear()
    assert store.list_items() == [bolts, tea]


def test_duplicate_sku_keeps_original(stocked_store: tuple[Store, Item, Item]) -> None:
    store, bolts, _ = stocked_store
    replacement = Item(bolts.sku, "Nuts", Category.HARDWARE, Decimal("1"), 5)
    with pytest.raises(ValueError, match="duplicate SKU"):
        store.add_item(replacement)
    assert store.get_item(bolts.sku) == bolts


@pytest.mark.parametrize("sku", ["hdw-0002", "HDW0002", "HDW-002", "HDW-????"])
def test_invalid_sku_is_rejected(sku: str) -> None:
    store = Store()
    with pytest.raises(ValueError, match="invalid SKU"):
        store.add_item(Item(sku, "Bolts", Category.HARDWARE, Decimal("1"), 5))
    assert store.list_items() == []
