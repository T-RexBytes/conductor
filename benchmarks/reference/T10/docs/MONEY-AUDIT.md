inventory/report.py:13 - Unit price display uses Decimal formatting, which defaults to half-even while pricing rounds half-up.
inventory/report.py:27 - Rounding each line to cents before summing can shift the report total by a cent or more compared with order_total(), which rounds after summing.
