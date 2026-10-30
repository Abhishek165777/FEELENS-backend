import csv
from collections import Counter
from io import StringIO
from fastapi import APIRouter, File, HTTPException, UploadFile
from services.ollama_service import ask_ollama

router = APIRouter(prefix="/api/v1/ai", tags=["AI statement summary"])


def build_aggregates(raw: bytes) -> dict:
    try:
        text = raw.decode("utf-8-sig")
        reader = csv.DictReader(StringIO(text))
        if not reader.fieldnames:
            raise ValueError("CSV has no header row")
        # Normalize harmless whitespace around the required header names.
        reader.fieldnames = [name.strip() if name else name for name in reader.fieldnames]
        required = {"Date", "Description", "Amount", "Type"}
        if not required.issubset(set(reader.fieldnames)):
            raise ValueError("CSV must contain Date, Description, Amount and Type columns. Map bank-specific headers to these names first.")
        count = 0
        debit_total = credit_total = 0.0
        debit_count = credit_count = 0
        for row in reader:
            amount_text = str(row.get("Amount", "")).replace(",", "").strip()
            try:
                amount = abs(float(amount_text))
            except (TypeError, ValueError) as exc:
                raise ValueError("Amount must be a valid number in every transaction row.") from exc
            txn_type = str(row.get("Type", "")).strip().lower()
            if txn_type in {"debit", "dr", "withdrawal"}:
                debit_total += amount
                debit_count += 1
            elif txn_type in {"credit", "cr", "deposit"}:
                credit_total += amount
                credit_count += 1
            else:
                raise ValueError("Each Type value must be Debit or Credit.")
            count += 1
        if not count:
            raise ValueError("CSV contains no transaction rows")
        return {"transaction_count": count, "debit_count": debit_count, "credit_count": credit_count,
                "total_debits": round(debit_total, 2), "total_credits": round(credit_total, 2),
                "net_cash_flow": round(credit_total - debit_total, 2)}
    except (UnicodeDecodeError, csv.Error, ValueError) as exc:
        raise ValueError(str(exc)) from exc


@router.post("/statement-summary")
async def summarize_statement(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Upload a CSV file.")
    raw = await file.read()
    if len(raw) > 5 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="CSV file must be 5 MB or smaller.")
    try:
        aggregates = build_aggregates(raw)
        # Only aggregate totals/counts go to Ollama. Raw descriptions, dates, and IDs are never sent.
        prompt = ("Summarise these bank-statement aggregates in plain language. Explain debit and credit totals, "
                  "net cash flow, and any limitations. Do not infer individual fees or suspicious activity from totals alone. "
                  "Do not ask for personal or account details. Aggregates: " + str(aggregates))
        summary = await ask_ollama(prompt)
        return {"aggregates": aggregates, "summary": summary,
                "privacy_note": "Only computed totals and counts were sent to the local Ollama model; raw transaction rows were not sent."}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
