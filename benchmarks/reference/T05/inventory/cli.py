"""Command-line interface for an inventory snapshot."""

import argparse
from pathlib import Path

from .models import Category
from .report import stock_report
from .storage import export_csv, load_json


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Inspect an inventory snapshot.")
    parser.add_argument("--input", required=True, type=Path, help="inventory JSON file")
    commands = parser.add_subparsers(dest="command", required=True)

    listing = commands.add_parser("list", help="list the items in the snapshot")
    listing.add_argument("--category", choices=[category.value for category in Category])
    commands.add_parser("report", help="print a stock report")
    csv_export = commands.add_parser("csv", help="export the inventory as CSV")
    csv_export.add_argument("path", type=Path, help="destination CSV file")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Load a snapshot and run the requested command."""
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        store = load_json(args.input)
    except (OSError, ValueError, ArithmeticError, KeyError, TypeError) as exc:
        parser.error(f"could not load inventory: {exc}")

    if args.command == "list":
        category = Category(args.category) if args.category else None
        for item in store.list_items(category):
            print(f"{item.sku}\t{item.name}\t{item.quantity}")
    elif args.command == "report":
        print(stock_report(store))
    else:
        try:
            export_csv(store, args.path)
        except OSError as exc:
            parser.error(f"could not export inventory: {exc}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
