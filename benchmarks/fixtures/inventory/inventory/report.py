"""Formatting for plain-text inventory reports."""

from decimal import ROUND_HALF_UP, Decimal

from .store import Store


def stock_report(store: Store) -> str:
    """Return a SKU-sorted table with prices and quantities right-aligned."""
    header = ("SKU", "Name", "Category", "Unit price", "Quantity")
    items = store.list_items()
    rows = [
        (item.sku, item.name, item.category.value, f"{item.unit_price:.2f}", str(item.quantity))
        for item in sorted(items, key=lambda item: item.sku)
    ]
    widths = [max(map(len, column)) for column in zip(header, *rows)]
    lines = [
        "  ".join(label.ljust(width) for label, width in zip(header, widths)).rstrip(),
        "  ".join("-" * width for width in widths),
    ]
    for sku, name, category, price, quantity in rows:
        lines.append(
            f"{sku:<{widths[0]}}  {name:<{widths[1]}}  {category:<{widths[2]}}"
            f"  {price:>{widths[3]}}  {quantity:>{widths[4]}}"
        )
    total = sum(
        (item.unit_price * item.quantity).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        for item in items
    )
    lines.append(f"Total value: {total:.2f}")
    return "\n".join(lines)
