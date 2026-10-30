
from services.file_parser import read_statement
from services.charge_detector import detect_charges

# Read the bank statement
with open("sample_data/sample_bank_statement.csv", "rb") as file:
    file_content = file.read()

transactions = read_statement(file_content)

# Detect possible bank charges
possible_charges = detect_charges(transactions)

# Display the results
print("Possible bank charges:")

for charge in possible_charges:
    print(charge)
