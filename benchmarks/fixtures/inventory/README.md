# Inventory

A small inventory tracker with SKU lookup, category filtering, order pricing,
JSON persistence, and a plain-text stock report. The runtime uses only the
Python standard library.

From this directory, run the tests with pytest installed.

```sh
python -m pytest -q
```

The CLI reads an inventory snapshot from a JSON file created by `save_json`.

```sh
python -m inventory.cli --input stock.json list --category food
python -m inventory.cli --input stock.json report
```

SKUs consist of three uppercase ASCII letters, a hyphen, and four ASCII
digits. Money is represented by `Decimal`. Pricing rounds half up to cents.
Pagination uses one-based page numbers and represents an empty result as one
empty page.
