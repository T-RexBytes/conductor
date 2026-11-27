"""Tests for inventory records and categories."""

from dataclasses import FrozenInstanceError
from decimal import Decimal

import pytest

from inventory import Category, Item


def test_item_retains_decimal_precision() -> None:
    item = Item("OFF-0001", "Notebook", Category.OFFICE, Decimal("2.345"), 0)
    assert item.unit_price == Decimal("2.345")
    assert item.category.value == "office"
    assert item.quantity == 0


def test_item_is_immutable() -> None:
    item = Item("OFF-0001", "Notebook", Category.OFFICE, Decimal("2"), 1)
    with pytest.raises(FrozenInstanceError):
        item.quantity = 2


@pytest.mark.parametrize(
    ("name", "price", "quantity"),
    [
        ("  ", "2", 1),
        ("Notebook", "-1", 1),
        ("Notebook", "NaN", 1),
        ("Notebook", "Infinity", 1),
        ("Notebook", "2", -1),
    ],
)
def test_item_rejects_invalid_fields(name: str, price: str, quantity: int) -> None:
    with pytest.raises(ValueError):
        Item("OFF-0001", name, Category.OFFICE, Decimal(price), quantity)
