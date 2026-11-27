"""Regression test for rounding the stock value after summing."""

from decimal import Decimal

from inventory import Category, Item, Store, order_total, stock_report


def test_report_rounds_total_after_summing() -> None:
    store = Store()
    store.add_item(Item("FOD-0001", "Tea", Category.FOOD, Decimal("0.335"), 1))
    store.add_item(Item("FOD-0002", "Coffee", Category.FOOD, Decimal("0.335"), 1))

    assert stock_report(store).splitlines()[-1] == (
        f"Total value: {order_total(store.list_items()):.2f}"
    )
