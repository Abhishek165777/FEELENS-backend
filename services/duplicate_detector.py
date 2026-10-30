"""Detect transactions that may have been posted more than once."""
from collections import defaultdict
from decimal import Decimal, InvalidOperation
import re


def _normalise_amount(value: object) -> str:
    raw = str(value or "").strip().replace(",", "").replace("₹", "").replace("INR", "")
    raw = re.sub(r"\s+", "", raw)
    try:
        return str(Decimal(raw).quantize(Decimal("0.01")))
    except (InvalidOperation, ValueError):
        return raw.casefold()


def _normalise_text(value: object) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip()).casefold()


def detect_possible_duplicates(transactions: list[dict]) -> list[dict]:
    """Group exact matches on date, description, amount and transaction type.

    Row numbers refer to CSV lines (header is line 1). This is a review aid:
    identical recurring payments can be legitimate, so results are never
    automatically removed or labelled as confirmed fraud.
    """
    groups = defaultdict(list)
    for index, transaction in enumerate(transactions, start=2):
        key = (
            _normalise_text(transaction.get("Date")),
            _normalise_text(transaction.get("Description")),
            _normalise_amount(transaction.get("Amount")),
            _normalise_text(transaction.get("Type")),
        )
        # Empty records should not be grouped together as duplicates.
        if any(key):
            groups[key].append((index, transaction))

    duplicates = []
    for entries in groups.values():
        if len(entries) < 2:
            continue
        first_row, first = entries[0]
        duplicates.append({
            "date": str(first.get("Date", "")),
            "description": str(first.get("Description", "")),
            "amount": str(first.get("Amount", "")),
            "type": str(first.get("Type", "")),
            "rows": [row for row, _ in entries],
            "duplicate_count": len(entries) - 1,
            "reason": "Same date, description, amount and transaction type appear multiple times. Verify with your bank statement.",
        })
    return sorted(duplicates, key=lambda item: item["rows"][0])
