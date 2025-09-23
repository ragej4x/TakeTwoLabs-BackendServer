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

## Supabase configuration (DB + Storage)

Set these environment variables before running:

```bash
set DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:PORT/DBNAME
set SUPABASE_URL=https://YOUR-PROJECT.supabase.co
set SUPABASE_ANON_KEY=YOUR_SUPABASE_ANON_KEY
set SUPABASE_BUCKET=uploads
```

Then run migrations (tables are created automatically on startup for now). Point `DATABASE_URL` to your Supabase Postgres.


!Fk9lratv007