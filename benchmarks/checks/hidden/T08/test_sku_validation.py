"""Pin the original SKU rules for all three entry points."""

from decimal import Decimal

import pytest

from inventory import Category, Item, Store, order_total
from inventory.validation import validate_sku


@pytest.mark.parametrize("sku", ["AAA-0000", "ZZZ-9999", "FOD-0123"])
def test_valid_skus_are_preserved(sku: str) -> None:
    item = Item(sku, "Tea", Category.FOOD, Decimal("1.25"), 2)
    store = Store()

    assert validate_sku(sku) == sku
    store.add_item(item)
    assert store.find_item(sku) is item
    assert order_total([item]) == Decimal("2.50")


@pytest.mark.parametrize("sku", [
    "", "fod-0123", "FOD0123", "FOD-123", "FOD-01234", " FOD-0123",
    "FOD-0123 ", "FOD-0123\n", "FOD-\u0660\u0661\u0662\u0663", "\u00c9TE-0123",
])
def test_invalid_skus_keep_the_same_error(sku: str) -> None:
    item = Item(sku, "Tea", Category.FOOD, Decimal("1"), 1)
    store = Store()

    for call, argument in ((validate_sku, sku), (store.add_item, item), (order_total, [item])):
        with pytest.raises(ValueError) as error:
            call(argument)
        assert str(error.value) == f"invalid SKU: {sku}"
    assert store.list_items() == []
