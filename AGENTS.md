# AGENTS.md

## Cursor Cloud specific instructions

### Project overview

PDF Scan Metadata Manager — a monorepo with a **Python/FastAPI backend** and a **React/Vite/TypeScript frontend**, using **MongoDB 7** for storage and **Tesseract OCR** for scanned PDF text extraction. See `README.md` for full architecture and API endpoint docs.

### Services

| Service | Command | Port | Notes |
|---------|---------|------|-------|
| MongoDB | `sudo docker start mongodb` (container already exists) | 27017 | Credentials: `admin` / `changeme` |
| Backend | `cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000` | 8000 | Reads `.env` from repo root |
| Frontend | `cd frontend && npm run dev` | 5173 | Vite dev server, hot reload |

### Running tests

- **Backend**: `cd backend && source .venv/bin/activate && pytest -v`
- **Frontend type check**: `cd frontend && npx tsc --noEmit`

### Non-obvious caveats

- The `.env` file is read by Pydantic Settings from the **repo root** (not from `backend/`). The `env_file` path in `backend/app/core/config.py` is `".env"`, resolved relative to the working directory. Always start the backend from `backend/` with the `.env` file in the repo root, or the defaults in the Settings class will be used.
- MongoDB must be running before starting the backend — the app connects on startup and creates indexes via `ensure_indexes()` in the lifespan hook.
- Docker daemon needs to be running (`sudo dockerd` in background) before starting the MongoDB container. In Cloud Agent VMs, Docker uses `fuse-overlayfs` storage driver and `iptables-legacy`.
- LLM features are **disabled by default** (`LLM_ENABLED=false`). The app works fully without an LLM, using rule-based classification, regex extraction, and heuristic grouping.
- Tesseract OCR (`tesseract-ocr`, `tesseract-ocr-deu`, `tesseract-ocr-fra`) must be installed system-wide.
- The `backend/.venv` virtual environment is not committed; it must be created and populated via `python3 -m venv .venv && pip install -r requirements.txt`.
