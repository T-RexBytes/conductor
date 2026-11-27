"""In-memory storage for inventory records."""

import re
from uuid import uuid4

from .models import Category, Item


class Store:
    """Index items by SKU and preserve insertion order when listing."""

    def __init__(self) -> None:
        self._items: dict[str, Item] = {}
        self._reservations: dict[str, dict[str, tuple[int, float]]] = {}

    def add_item(self, item: Item) -> None:
        """Add a stock record, raising ValueError for invalid or duplicate SKUs."""
        if re.fullmatch(r"[A-Z]{3}-[0-9]{4}", item.sku) is None:
            raise ValueError(f"invalid SKU: {item.sku}")
        if self.find_item(item.sku) is not None:
            raise ValueError(f"duplicate SKU: {item.sku}")
        self._items[item.sku] = item

    def remove_item(self, sku: str) -> Item | None:
        """Remove and return an item, or return None when absent."""
        self._reservations.pop(sku, None)
        return self._items.pop(sku, None)

    def find_item(self, sku: str) -> Item | None:
        """Return the item with this SKU, or None when absent."""
        return self._items.get(sku)

    def list_items(self, category: Category | None = None) -> list[Item]:
        """Return a snapshot of the items, optionally filtered by category."""
        return [
            item for item in self._items.values()
            if category is None or item.category == category
        ]

    def available(self, sku: str, now: float) -> int:
        """Return the number of units without an active reservation."""
        item = self.find_item(sku)
        if item is None:
            raise ValueError(f"unknown SKU: {sku}")
        held = sum(
            quantity for quantity, expires_at in self._reservations.get(sku, {}).values()
            if now < expires_at
        )
        return item.quantity - held

    def reserve(self, sku: str, quantity: int, ttl_seconds: float, now: float) -> str:
        """Hold units for the supplied duration and return their reservation ID."""
        if not isinstance(quantity, int) or isinstance(quantity, bool) or quantity <= 0:
            raise ValueError("reservation quantity must be a positive integer")
        if quantity > self.available(sku, now):
            raise ValueError(f"insufficient available stock: {sku}")
        reservation_id = uuid4().hex
        self._reservations.setdefault(sku, {})[reservation_id] = (quantity, now + ttl_seconds)
        return reservation_id

    def release(self, reservation_id: str) -> None:
        """Remove the hold associated with a known reservation ID."""
        for reservations in self._reservations.values():
            if reservation_id in reservations:
                del reservations[reservation_id]
                return
        raise ValueError(f"unknown reservation ID: {reservation_id}")
