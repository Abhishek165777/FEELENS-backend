
from models.transaction import Transaction

# Create a sample transaction
transaction = Transaction(
    "2026-10-01",
    "SMS Charge",
    50,
    "Debit"
)

# Display transaction details
print("Date:", transaction.date)
print("Description:", transaction.description)
print("Amount:", transaction.amount)
print("Type:", transaction.transaction_type)
