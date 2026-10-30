import csv

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import os
from services.file_parser import read_statement
from services.charge_detector import detect_charges
from services.duplicate_detector import detect_possible_duplicates
from utils.validators import validate_transaction
from routes.ai import router as ai_router
from routes.summary import router as summary_router

app = FastAPI(
    title="FeeLens AI API",
    description="Review bank statement CSV files and flag possible bank fees.",
    version="1.0.0",
)

# Allow the supplied static frontend to call this API from VS Code Live Server.
# Override FEELENS_CORS_ORIGINS with a comma-separated list for other local origins.
_default_origins = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "http://127.0.0.1:5501",
    "http://localhost:5501",
]
_allowed_origins = [
    origin.strip()
    for origin in os.getenv("FEELENS_CORS_ORIGINS", ",".join(_default_origins)).split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

@app.get("/")
def home():
    return {"message": "FeeLens AI API is running", "docs": "/docs"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/v1/charges/detect")
async def detect_statement_charges(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Upload a .csv bank statement file.")

    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="CSV file must be 5 MB or smaller.")
    if not content:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")

    try:
        transactions = read_statement(content)
    except (UnicodeDecodeError, ValueError, csv.Error) as exc:
        raise HTTPException(status_code=400, detail="Could not read the CSV file.") from exc

    if not transactions:
        raise HTTPException(status_code=400, detail="The CSV file has no transaction rows.")

    required_columns = {"Date", "Description", "Amount", "Type"}
    available_columns = set(transactions[0].keys())
    missing = sorted(required_columns - available_columns)
    if missing:
        raise HTTPException(
            status_code=400,
            detail={"message": "CSV is missing required columns.", "missing_columns": missing},
        )

    validation_errors = []
    for row_number, transaction in enumerate(transactions, start=2):
        errors = validate_transaction(transaction)
        if errors:
            validation_errors.append({"row": row_number, "errors": errors})

    charges = detect_charges(transactions)
    duplicates = detect_possible_duplicates(transactions)
    total_debits = 0.0
    total_credits = 0.0
    for transaction in transactions:
        txn_type = str(transaction.get("Type", "")).strip().lower()
        try:
            amount = abs(float(str(transaction.get("Amount", "0")).replace(",", "").replace("₹", "").strip()))
            if txn_type in {"debit", "dr", "withdrawal"}:
                total_debits += amount
            elif txn_type in {"credit", "cr", "deposit"}:
                total_credits += amount
        except ValueError:
            pass
    return {
        "filename": file.filename,
        "total_transactions": len(transactions),
        "total_debits": round(total_debits, 2),
        "total_credits": round(total_credits, 2),
        "possible_charge_count": len(charges),
        "possible_charges": charges,
        "possible_duplicate_group_count": len(duplicates),
        "possible_duplicate_transaction_count": sum(item["duplicate_count"] for item in duplicates),
        "possible_duplicates": duplicates,
        "validation_errors": validation_errors,
    }

app.include_router(ai_router)
app.include_router(summary_router)
