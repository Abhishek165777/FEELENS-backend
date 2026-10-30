
def detect_charges(transactions):
    possible_charges = []

    suspicious_keywords = [
        "SMS CHARGE",
        "ANNUAL FEE",
        "MAINTENANCE CHARGE",
        "ATM EXTRA CHARGE",
        "PROCESSING FEE"
    ]

    for transaction in transactions:
        description = transaction.get("Description", "").upper()

        for keyword in suspicious_keywords:
            if keyword in description:
                possible_charges.append({
                    "date": transaction.get("Date", ""),
                    "description": description,
                    "amount": transaction.get("Amount", ""),
                    "type": transaction.get("Type", ""),
                    "reason": "Possible bank fee to review"
                })
                break

    return possible_charges
