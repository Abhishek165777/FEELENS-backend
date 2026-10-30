import csv
import io

def read_statement(file_content):
    text = file_content.decode("utf-8-sig")

    reader = csv.DictReader(io.StringIO(text))

    transactions = []

    for row in reader:
        transactions.append(row)

    return transactions