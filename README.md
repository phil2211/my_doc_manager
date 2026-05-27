# PDF Scan Metadata Manager

Local-first web application for ingesting multipage scanned PDFs, extracting metadata (document type, date, sender), grouping pages into logical documents, and searching them deterministically via MongoDB.

## Features

- Upload multipage PDF scans via web UI
- OCR for scanned pages (Tesseract) and native text extraction for text PDFs
- Heuristic page grouping with optional LLM fallback (Ollama / OpenAI-compatible APIs)
- Rule-based classification and metadata extraction with LLM escalation
- MongoDB storage using Motor/pymongo directly (no ODM)
- Search by document type, date range, sender prefix, and full text

## Prerequisites

- Docker and Docker Compose (recommended), or:
  - Python 3.12+
  - Node.js 20+
  - MongoDB 7
  - Tesseract OCR

### macOS local setup

```bash
brew install tesseract tesseract-lang
```

Optional local LLM:

```bash
brew install ollama
ollama pull llama3.2
```

## Quick start with Docker

```bash
cp .env.example .env
docker compose up --build
```

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- MongoDB: localhost:27017

## Local development

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example ../.env
mkdir -p ../data/files
uvicorn app.main:app --reload --port 8000
```

Ensure MongoDB is running and `MONGODB_URI` in `.env` is correct.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Set `VITE_API_URL=http://localhost:8000` if needed.

## API endpoints

| Method | Path | Description |
| ------ | ---- | ----------- |
| POST | `/api/v1/files` | Upload PDF |
| GET | `/api/v1/files/{id}/status` | Processing job status |
| GET | `/api/v1/documents` | Search documents |
| GET | `/api/v1/documents/{id}` | Document detail |
| GET | `/api/v1/documents/{id}/file` | Download original PDF |
| GET | `/api/v1/pages/{id}/thumbnail` | Page thumbnail |
| GET/PUT | `/api/v1/settings` | Processing settings |

## Configuration

See [`.env.example`](.env.example):

- `MONGODB_URI` — MongoDB connection string
- `FILE_STORAGE_PATH` — directory for uploaded PDFs and thumbnails
- `LLM_ENABLED` — enable LLM backends for grouping/classification/extraction
- `LLM_BASE_URL` — OpenAI-compatible endpoint (default: Ollama)
- `LLM_MODEL` — model name
- `LLM_CONFIDENCE_THRESHOLD` — escalate to LLM when rule confidence is below this

## Running tests

```bash
cd backend
pip install -r requirements.txt
pytest
```

## Architecture

```
Upload → Page split/OCR → Page grouping → Classification → Metadata extraction → MongoDB
```

Collections: `source_files`, `pages`, `logical_documents`, `processing_jobs`

Pluggable backends live under `backend/app/services/` for OCR, grouping, classification, and extraction.

## License

MIT
