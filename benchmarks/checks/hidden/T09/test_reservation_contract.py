"""Exercise stock reservations through the public store methods."""

from decimal import Decimal

import pytest

from inventory import Category, Item, Store


@pytest.fixture
def store() -> Store:
    stock = Store()
    stock.add_item(Item("FOD-0001", "Tea", Category.FOOD, Decimal("1"), 5))
    stock.add_item(Item("FOD-0002", "Coffee", Category.FOOD, Decimal("2"), 4))
    return stock


def test_expiry_boundary_and_sku_isolation(store: Store) -> None:
    first = store.reserve("FOD-0001", 3, 2.5, 10.0)
    second = store.reserve("FOD-0002", 4, 10, 10.0)
    assert isinstance(first, str) and isinstance(second, str) and first != second
    assert store.available("FOD-0001", 12.499) == 2
    assert store.available("FOD-0001", 12.5) == 5
    assert store.available("FOD-0002", 12.5) == 0
    store.reserve("FOD-0001", 5, 1, 12.5)
    assert store.available("FOD-0001", 12.5) == 0
    store.release(second)
    assert store.available("FOD-0002", 12.5) == 4
    with pytest.raises(ValueError):
        store.release(second)


@pytest.mark.parametrize("quantity", [0, -1, 1.5, True, 6])
def test_invalid_reservation_leaves_stock_available(store: Store, quantity: int) -> None:
    with pytest.raises(ValueError):
        store.reserve("FOD-0001", quantity, 5, 10.0)
    assert store.available("FOD-0001", 10.0) == 5
    store.reserve("FOD-0001", 5, 5, 10.0)
    with pytest.raises(ValueError):
        store.reserve("FOD-0001", 1, 5, 10.0)


def test_unknown_skus_and_ids_raise_value_error(store: Store) -> None:
    with pytest.raises(ValueError):
        store.available("FOD-9999", 10.0)
    with pytest.raises(ValueError):
        store.reserve("FOD-9999", 1, 5, 10.0)
    with pytest.raises(ValueError):
        store.release("unknown")


def test_remove_item_preserves_its_return_contract(store: Store) -> None:
    item = store.find_item("FOD-0001")
    store.reserve("FOD-0001", 2, 5, 10.0)
    assert store.remove_item("FOD-0001") is item
    assert store.remove_item("FOD-0001") is None
    assert store.find_item("FOD-0001") is None
    with pytest.raises(ValueError):
        store.available("FOD-0001", 10.0)
    assert store.available("FOD-0002", 10.0) == 4
