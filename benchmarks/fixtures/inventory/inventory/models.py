"""Data types shared by the inventory modules."""

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum


class Category(str, Enum):
    """Categories accepted by the store and CLI."""

    FOOD = "food"
    HARDWARE = "hardware"
    OFFICE = "office"


@dataclass(frozen=True)
class Item:
    """An immutable stock record with a unit price and on-hand quantity."""

    sku: str
    name: str
    category: Category
    unit_price: Decimal
    quantity: int

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("item name must not be blank")
        if not self.unit_price.is_finite() or self.unit_price < 0:
            raise ValueError("unit price must be finite and nonnegative")
        if self.quantity < 0:
            raise ValueError("quantity must be nonnegative")
