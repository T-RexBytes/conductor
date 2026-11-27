"""Exercise pagination at exact and partial page boundaries."""

import pytest

from inventory.pagination import Page, paginate


@pytest.mark.parametrize(("count", "size"), [(1, 1), (6, 3), (12, 4)])
def test_exact_multiples_stop_at_last_full_page(count: int, size: int) -> None:
    items = list(range(count))
    last = count // size

    assert paginate(items, last, size) == Page(items[-size:], last, last)
    with pytest.raises(ValueError):
        paginate(items, last + 1, size)


def test_non_multiple_keeps_partial_page() -> None:
    assert paginate(tuple(range(7)), 3, 3) == Page([6], 3, 3)


def test_empty_sequence_keeps_one_empty_page() -> None:
    assert paginate([], 1, 2) == Page([], 1, 1)
    with pytest.raises(ValueError):
        paginate([], 2, 2)


@pytest.mark.parametrize("page", [0, 5])
def test_out_of_range_page_raises(page: int) -> None:
    with pytest.raises(ValueError):
        paginate([1, 2, 3], page, 2)
