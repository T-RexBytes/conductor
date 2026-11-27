# Inventory architecture

## `inventory/__init__.py`

The package exposes the domain types and core operations. It re-exports
`Category` and `Item` from `models`, `Store` from `store`, `Page` and
`paginate` from `pagination`, `apply_discount`, `add_tax`, and `order_total`
from `pricing`, `stock_report` from `report`, and `load_json` and `save_json`
from `storage`.

## `inventory/models.py`

`Category` holds the supported categories and their serialized values.
`Item` is an immutable stock record with a SKU, name, category, Decimal unit
price, and quantity. It validates the name, price, and quantity at construction.
This module has no public functions or methods of its own and uses only the
standard library.

## `inventory/store.py`

`Store` indexes records by SKU and retains insertion order. Its public methods
are `add_item`, which validates the SKU and rejects duplicates, `remove_item`,
which removes and returns an item if present, `find_item`, which looks up an item
by SKU, and `list_items`, which returns a snapshot optionally filtered by
category. It uses `Item` and `Category` from `models`.

## `inventory/pricing.py`

`apply_discount` and `add_tax` apply fractional rates and round half up to
cents. `order_total` checks each SKU, sums unit prices times quantities, and
applies the discount before tax. It uses `Item` from `models`.

## `inventory/pagination.py`

`paginate` returns a slice of a sequence in a `Page` with a one-based page number
and the total page count. It rejects invalid page sizes and page numbers.
This module uses only the standard library.

## `inventory/storage.py`

`save_json` writes a UTF-8 snapshot with prices encoded as strings to preserve
Decimal precision. `load_json` restores the records into a new store. This
module uses `Item` and `Category` from `models` and `Store` from `store`.

## `inventory/report.py`

`stock_report` reads inventory from `Store` and formats a plain-text table
sorted by SKU with a total value footer.
It uses `Store` from `store`.

## `inventory/cli.py`

`main` loads a snapshot and runs the selected command. `list` prints stock
records and supports a category filter. `report` prints the stock table.
This module uses `Category` from `models`, `load_json` from `storage`, and
`stock_report` from `report`.
