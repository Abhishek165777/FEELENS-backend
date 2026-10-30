from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["docs"] == "/docs"

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_detect_charges_from_csv():
    csv_content = (
        "Date,Description,Amount,Type\n"
        "2026-10-01,SMS CHARGE,50,Debit\n"
        "2026-10-02,GROCERY STORE,450,Debit\n"
    )
    response = client.post(
        "/api/v1/charges/detect",
        files={"file": ("statement.csv", csv_content, "text/csv")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_transactions"] == 2
    assert data["possible_charge_count"] == 1
    assert data["possible_charges"][0]["description"] == "SMS CHARGE"

def test_reject_non_csv_file():
    response = client.post(
        "/api/v1/charges/detect",
        files={"file": ("statement.txt", "hello", "text/plain")},
    )
    assert response.status_code == 400

def test_reject_csv_with_missing_columns():
    response = client.post(
        "/api/v1/charges/detect",
        files={"file": ("statement.csv", "Date,Description\n2026-10-01,SMS CHARGE\n", "text/csv")},
    )
    assert response.status_code == 400
