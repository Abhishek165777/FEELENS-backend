from services.duplicate_detector import detect_possible_duplicates


def test_detects_identical_transactions_and_reports_csv_rows():
    rows = [
        {"Date": "2026-10-01", "Description": "UPI payment", "Amount": "1,000", "Type": "DEBIT"},
        {"Date": "2026-10-01", "Description": " upi   payment ", "Amount": "1000.00", "Type": "debit"},
        {"Date": "2026-10-02", "Description": "UPI payment", "Amount": "1000", "Type": "DEBIT"},
    ]
    result = detect_possible_duplicates(rows)
    assert len(result) == 1
    assert result[0]["rows"] == [2, 3]
    assert result[0]["duplicate_count"] == 1


def test_different_amount_or_type_is_not_duplicate():
    rows = [
        {"Date": "2026-10-01", "Description": "UPI payment", "Amount": "100", "Type": "DEBIT"},
        {"Date": "2026-10-01", "Description": "UPI payment", "Amount": "101", "Type": "DEBIT"},
        {"Date": "2026-10-01", "Description": "UPI payment", "Amount": "100", "Type": "CREDIT"},
    ]
    assert detect_possible_duplicates(rows) == []


def test_empty_rows_are_not_grouped():
    assert detect_possible_duplicates([{}, {}]) == []
