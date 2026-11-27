"""Tests for stock holds and their effect on availability."""

from decimal import Decimal

import pytest

from inventory import Category, Item, Store


def test_reserve_release_and_expire() -> None:
    store = Store()
    item = Item("FOD-0001", "Tea", Category.FOOD, Decimal("1"), 5)
    store.add_item(item)

    first = store.reserve(item.sku, 3, 5, 10.0)
    second = store.reserve(item.sku, 2, 7, 10.0)
    assert first != second
    with pytest.raises(ValueError):
        store.reserve(item.sku, 1, 5, 14.9)
    assert store.available(item.sku, 15.0) == 3
    store.release(second)
    assert store.available(item.sku, 15.0) == 5
    with pytest.raises(ValueError):
        store.release(second)
