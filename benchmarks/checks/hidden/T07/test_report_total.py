"""Exercise report totals and preserve the stock table layout."""

from decimal import Decimal

import pytest

from inventory import Category, Item, Store, order_total, stock_report


@pytest.mark.parametrize("lines", [
    [],
    [("1.25", 3)],
    [("0.335", 3), ("0.005", 1)],
    [("0.335", 1), ("0.335", 1)],
    [("0.334", 1), ("0.334", 1), ("10.125", 0)],
])
def test_report_total_matches_order(lines: list[tuple[str, int]]) -> None:
    store = Store()
    for index, (price, quantity) in enumerate(lines):
        store.add_item(Item(f"FOD-{index:04}", "Tea", Category.FOOD, Decimal(price), quantity))

    assert stock_report(store).splitlines()[-1] == (
        f"Total value: {order_total(store.list_items()):.2f}"
    )
