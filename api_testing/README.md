# FeeLens AI — Backend API Testing

This archive contains the backend only; no frontend is included.

## Run in Windows PowerShell
Open a terminal in this `backend` folder, then run:

```powershell
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload
```

Open `http://127.0.0.1:8000/docs` to test the API interactively.

## API endpoints
- `GET /` — API welcome message
- `GET /health` — health check
- `POST /api/v1/charges/detect` — upload a CSV statement and detect possible fees

The CSV must contain `Date`, `Description`, `Amount`, and `Type` columns. Detection is keyword-based and flags possible charges for review; it does not prove a charge is incorrect.

## Run automated tests
With the server stopped or from a second terminal in this `backend` folder, run:

```powershell
python -m pytest api_testing/pytest -v
```

## Test with Postman
Import `api_testing/postman/feelens_ai_api.postman_collection.json`. Start the API first. For the upload request, choose **Body → form-data**, set the key to `file`, change its type to **File**, and select `api_testing/sample_requests/sample_bank_statement.csv`.
