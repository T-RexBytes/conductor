"""Tests for the plain-text stock report."""

from decimal import Decimal

from inventory import Category, Item, Store, stock_report


def test_report_sorts_rows_and_formats_prices() -> None:
    store = Store()
    store.add_item(Item("OFF-0002", "Long notebook", Category.OFFICE, Decimal("3.5"), 12))
    store.add_item(Item("FOD-0001", "Tea", Category.FOOD, Decimal("8"), 1))

    header, divider, first_row, second_row, total = stock_report(store).splitlines()
    assert header.split() == ["SKU", "Name", "Category", "Unit", "price", "Quantity"]
    assert set(divider) == {"-", " "}
    assert first_row.split() == ["FOD-0001", "Tea", "food", "8.00", "1"]
    assert second_row.split() == ["OFF-0002", "Long", "notebook", "office", "3.50", "12"]
    assert total == "Total value: 50.00"
    assert len(first_row) == len(second_row)


def test_empty_report_has_header_and_divider() -> None:
    header, divider, total = stock_report(Store()).splitlines()
    assert "Quantity" in header
    assert len(header) == len(divider)
    assert total == "Total value: 0.00"
