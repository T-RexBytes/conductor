"""Decimal arithmetic for discounts, taxes, and inventory orders."""

import re
from collections.abc import Iterable
from decimal import ROUND_HALF_UP, Decimal

from .models import Item

_CENT = Decimal("0.01")


def apply_discount(amount: Decimal, rate: Decimal) -> Decimal:
    """Apply a fractional discount between zero and one and round to cents."""
    if not rate.is_finite() or not 0 <= rate <= 1:
        raise ValueError("discount rate must be between zero and one")
    return (amount * (1 - rate)).quantize(_CENT, rounding=ROUND_HALF_UP)


def add_tax(amount: Decimal, rate: Decimal) -> Decimal:
    """Add tax at a nonnegative fractional rate and round to cents."""
    if not rate.is_finite() or rate < 0:
        raise ValueError("tax rate must be finite and nonnegative")
    return (amount * (1 + rate)).quantize(_CENT, rounding=ROUND_HALF_UP)


def order_total(
    items: Iterable[Item],
    *,
    discount_rate: Decimal = Decimal("0"),
    tax_rate: Decimal = Decimal("0"),
) -> Decimal:
    """Price quantities at unit price, then apply the discount and tax."""
    subtotal = Decimal("0")
    for item in items:
        if re.fullmatch(r"[A-Z]{3}-[0-9]{4}", item.sku) is None:
            raise ValueError(f"invalid SKU: {item.sku}")
        subtotal += item.unit_price * item.quantity
    return add_tax(apply_discount(subtotal, discount_rate), tax_rate)
