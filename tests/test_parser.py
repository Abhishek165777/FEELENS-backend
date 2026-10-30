
from services.file_parser import read_statement

with open("sample_data/sample_bank_statement.csv", "rb") as file:
    file_content = file.read()

transactions = read_statement(file_content)

print("Bank transactions:")

for transaction in transactions:
    print(transaction)

