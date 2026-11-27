"""Tests for order pricing and rounding."""

from decimal import Decimal

import pytest

from inventory import Category, Item, add_tax, apply_discount, order_total


def test_discount_rounds_half_up() -> None:
    assert apply_discount(Decimal("10.05"), Decimal("0.10")) == Decimal("9.05")


def test_tax_rounds_half_up() -> None:
    assert add_tax(Decimal("1.00"), Decimal("0.005")) == Decimal("1.01")


@pytest.mark.parametrize("rate", ["-0.01", "1.01", "NaN", "Infinity"])
def test_invalid_discount(rate: str) -> None:
    with pytest.raises(ValueError, match="discount rate"):
        apply_discount(Decimal("10"), Decimal(rate))


@pytest.mark.parametrize("rate", ["-0.01", "NaN", "Infinity"])
def test_invalid_tax(rate: str) -> None:
    with pytest.raises(ValueError, match="tax rate"):
        add_tax(Decimal("10"), Decimal(rate))


def test_order_total_prices_quantities_before_discount_and_tax() -> None:
    items = [
        Item("FOD-0001", "Tea", Category.FOOD, Decimal("3.50"), 2),
        Item("FOD-0002", "Coffee", Category.FOOD, Decimal("5.00"), 1),
    ]
    assert order_total(iter(items), discount_rate=Decimal("0.10"), tax_rate=Decimal("0.05")) == (
        Decimal("11.34")
    )


def test_empty_order_keeps_cent_precision() -> None:
    assert str(order_total([])) == "0.00"


def test_order_rejects_invalid_sku_without_store() -> None:
    item = Item("invalid", "Tea", Category.FOOD, Decimal("3.50"), 1)
    with pytest.raises(ValueError, match="invalid SKU"):
        order_total([item])
