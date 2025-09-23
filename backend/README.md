# TakeTwoLabs FastAPI Backend

Minimal FastAPI backend providing CORS-enabled CRUD for entries.

## Setup

```bash
# From the backend directory
python -m venv .venv
# Windows PowerShell
. .venv/Scripts/Activate.ps1
pip install -r requirements.txt
```

## Run

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

- Health check: `GET /health`
- List entries: `GET /entries`
- Create entry: `POST /entries`
- Update entry: `PATCH /entries/{id}`
- Delete entry: `DELETE /entries/{id}`

CORS is open to `http://localhost:3000` so Vite dev server can access it.

## Notes
- Data is stored in-memory and resets on server restart.
- File uploads are not handled; `waiverPdf` is ignored on the backend.

