
from utils.validators import validate_transaction

# Test a valid transaction
transaction = {
    "Date": "2026-10-01",
    "Description": "SMS Charge",
    "Amount": "50",
    "Type": "Debit"
}

errors = validate_transaction(transaction)

if errors:
    print("Validation errors:", errors)
else:
    print("Transaction is valid!")

# Test an invalid transaction
invalid_transaction = {
    "Date": "",
    "Description": "ATM Charge",
    "Amount": "abc",
    "Type": "Unknown"
}

errors = validate_transaction(invalid_transaction)

print("Invalid transaction errors:", errors)
