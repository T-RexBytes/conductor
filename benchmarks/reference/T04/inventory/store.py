"""In-memory storage for inventory records."""

import re

from .models import Category, Item


class Store:
    """Index items by SKU and preserve insertion order when listing."""

    def __init__(self) -> None:
        self._items: dict[str, Item] = {}

    def add_item(self, item: Item) -> None:
        """Add a stock record, raising ValueError for invalid or duplicate SKUs."""
        if re.fullmatch(r"[A-Z]{3}-[0-9]{4}", item.sku) is None:
            raise ValueError(f"invalid SKU: {item.sku}")
        if self.get_item(item.sku) is not None:
            raise ValueError(f"duplicate SKU: {item.sku}")
        self._items[item.sku] = item

    def remove_item(self, sku: str) -> Item | None:
        """Remove and return an item, or return None when absent."""
        return self._items.pop(sku, None)

    def get_item(self, sku: str) -> Item | None:
        """Return the item with this SKU, or None when absent."""
        return self._items.get(sku)

    def list_items(self, category: Category | None = None) -> list[Item]:
        """Return a snapshot of the items, optionally filtered by category."""
        return [
            item for item in self._items.values()
            if category is None or item.category == category
        ]
