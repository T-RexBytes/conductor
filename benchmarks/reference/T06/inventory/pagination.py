"""One-based pagination for sequences."""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class Page(Generic[T]):
    """A slice of items plus its page number and the total page count."""

    items: list[T]
    page: int
    total_pages: int


def paginate(items: Sequence[T], page: int, page_size: int) -> Page[T]:
    """Return a page, raising ValueError for invalid sizes or page numbers.

    An empty sequence has one empty page.
    """
    if page_size < 1:
        raise ValueError("page_size must be positive")

    full_pages, remainder = divmod(len(items), page_size)
    total_pages = max(1, full_pages + bool(remainder))
    if not 1 <= page <= total_pages:
        raise ValueError(f"page must be between 1 and {total_pages}")

    start = (page - 1) * page_size
    return Page(list(items[start:start + page_size]), page, total_pages)
