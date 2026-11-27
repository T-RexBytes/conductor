"""Validation shared by inventory storage and pricing."""

import re


def validate_sku(sku: str) -> str:
    """Return a canonical SKU, rejecting input outside the accepted format."""
    if re.fullmatch(r"[A-Z]{3}-[0-9]{4}", sku) is None:
        raise ValueError(f"invalid SKU: {sku}")
    return sku
