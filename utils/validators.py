
def validate_transaction(transaction):
    errors = []

    if not transaction.get("Date"):
        errors.append("Date is missing")

    if not transaction.get("Description"):
        errors.append("Description is missing")

    try:
        amount = float(transaction.get("Amount", ""))

        if amount < 0:
            errors.append("Amount cannot be negative")

    except (ValueError, TypeError):
        errors.append("Amount must be a valid number")

    transaction_type = transaction.get("Type", "").strip().title()

    if transaction_type not in ["Credit", "Debit"]:
        errors.append("Type must be Credit or Debit")

    return errors
