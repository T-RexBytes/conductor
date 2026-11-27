"""Tests for slicing sequences into pages."""

import pytest

from inventory import Page, paginate


def test_first_page() -> None:
    assert paginate(("a", "b", "c"), 1, 2) == Page(["a", "b"], 1, 2)


def test_partial_last_page() -> None:
    assert paginate([1, 2, 3, 4, 5], 3, 2) == Page([5], 3, 3)


def test_empty_sequence_has_one_page() -> None:
    assert paginate([], 1, 5) == Page([], 1, 1)


@pytest.mark.parametrize("page", [-1, 0, 3])
def test_rejects_out_of_range_pages(page: int) -> None:
    with pytest.raises(ValueError, match="page must be between"):
        paginate([1, 2, 3], page, 2)


@pytest.mark.parametrize("page_size", [-1, 0])
def test_rejects_nonpositive_page_size(page_size: int) -> None:
    with pytest.raises(ValueError, match="page_size must be positive"):
        paginate([1, 2, 3], 1, page_size)
