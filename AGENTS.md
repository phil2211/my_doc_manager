# AGENTS.md

## Cursor Cloud specific instructions

### Project Overview

PDF Scan Metadata Manager — a local-first web app for ingesting scanned PDFs, extracting metadata (date, sender, document type), grouping pages into logical documents, and searching via MongoDB. See `README.md` for full architecture.

### Services

| Service | Port | Start command |
|---------|------|---------------|
| MongoDB 7 | 27017 | `mongod --dbpath /data/db --bind_ip_all` |
| Backend (FastAPI) | 8000 | `cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000` |
| Frontend (Vite/React) | 5173 | `cd frontend && npm run dev` |

### Running services

1. Start MongoDB first — the backend depends on it at startup (creates indexes during lifespan).
2. MongoDB must have an `admin:changeme` user in the `admin` database (matches `.env.example`). Create once with:
   ```
   mongosh admin --eval "db.createUser({user:'admin',pwd:'changeme',roles:[{role:'root',db:'admin'}]})"
   ```
3. Copy `.env.example` to `.env` at the repo root before starting backend.
4. Create `data/files` directory at repo root (`mkdir -p data/files`) — used for uploaded PDFs and thumbnails.

### Testing

- **Backend tests:** `cd backend && source .venv/bin/activate && pytest -v` (9 unit tests, no MongoDB required)
- **TypeScript check:** `cd frontend && npx tsc --noEmit`
- **Frontend has no eslint config** in the current branch — only TypeScript type checking is available.

### Gotchas

- The backend settings module (`app/core/config.py`) reads `.env` from the CWD, so start uvicorn from the repo root or set `MONGODB_URI` as an env var.
- `LLM_ENABLED` defaults to `false` — rule-based extraction works without any LLM server.
- Tesseract must be installed system-wide (`tesseract-ocr`, `tesseract-ocr-deu`, `tesseract-ocr-eng`) for OCR on scanned pages.
- `pytest-asyncio` version installed is 1.4.0 with `asyncio_mode = auto` in `pytest.ini`.
