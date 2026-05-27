# Personal Document Assistant Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a web application that extracts metadata from scanned PDFs, categorizes them using rules and LLMs, learns from user corrections, and uploads the final PDFs to Google Drive.

**Architecture:** A React (Vite) frontend communicates with a Python (FastAPI) backend. The backend uses `pdfplumber` for text extraction, MongoDB for storing rules/corrections, and `LiteLLM` for AI categorization.

**Tech Stack:** Python, FastAPI, React, Vite, Tailwind CSS, MongoDB, pdfplumber, pypdf, LiteLLM, Pytest, Vitest.

---

### Task 1: Project Setup & Database Connection

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/src/database.py`
- Create: `backend/tests/test_database.py`

- [ ] **Step 1: Write the failing test for database connection**

```python
# backend/tests/test_database.py
import pytest
from src.database import get_db_client

def test_get_db_client():
    client = get_db_client()
    assert client is not None
    assert client.admin.command('ping')['ok'] == 1.0
```

- [ ] **Step 2: Run test to verify it fails**
Run: `cd backend && pytest tests/test_database.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'src'"

- [ ] **Step 3: Write minimal implementation**

```python
# backend/requirements.txt
fastapi
uvicorn
pymongo
pytest
```

```python
# backend/src/database.py
from pymongo import MongoClient
import os

def get_db_client():
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    return MongoClient(mongo_uri)
```

- [ ] **Step 4: Run test to verify it passes**
Run: `cd backend && pip install -r requirements.txt && pytest tests/test_database.py -v`
Expected: PASS (Assuming local MongoDB is running)

- [ ] **Step 5: Commit**
```bash
git add backend/requirements.txt backend/src/database.py backend/tests/test_database.py
git commit -m "feat: setup backend and mongodb connection"
```

### Task 2: PDF Text Extraction & Splitting

**Files:**
- Create: `backend/src/pdf_processor.py`
- Create: `backend/tests/test_pdf_processor.py`
- Modify: `backend/requirements.txt`

- [ ] **Step 1: Write the failing test**

```python
# backend/tests/test_pdf_processor.py
import os
from src.pdf_processor import extract_text_from_page

def test_extract_text_from_page(tmp_path):
    # Create a dummy PDF for testing (requires reportlab or similar in tests, or a static test file)
    # For simplicity, assuming a static test file exists at tests/fixtures/sample.pdf
    # This test will fail until the function is implemented
    text = extract_text_from_page("tests/fixtures/sample.pdf", page_num=0)
    assert isinstance(text, str)
```

- [ ] **Step 2: Run test to verify it fails**
Run: `cd backend && pytest tests/test_pdf_processor.py -v`
Expected: FAIL with "ImportError"

- [ ] **Step 3: Write minimal implementation**

```python
# backend/requirements.txt (append)
pdfplumber
pypdf
```

```python
# backend/src/pdf_processor.py
import pdfplumber

def extract_text_from_page(pdf_path: str, page_num: int) -> str:
    with pdfplumber.open(pdf_path) as pdf:
        if page_num >= len(pdf.pages):
            raise ValueError("Page number out of range")
        page = pdf.pages[page_num]
        return page.extract_text() or ""
```

- [ ] **Step 4: Run test to verify it passes**
Run: `cd backend && pip install -r requirements.txt && mkdir -p tests/fixtures && touch tests/fixtures/sample.pdf && pytest tests/test_pdf_processor.py -v`
Expected: PASS (after adding a valid sample PDF)

- [ ] **Step 5: Commit**
```bash
git add backend/requirements.txt backend/src/pdf_processor.py backend/tests/test_pdf_processor.py
git commit -m "feat: add pdf text extraction"
```

### Task 3: Rule-Based Extraction

**Files:**
- Create: `backend/src/rules_engine.py`
- Create: `backend/tests/test_rules_engine.py`

- [ ] **Step 1: Write the failing test**

```python
# backend/tests/test_rules_engine.py
from src.rules_engine import extract_metadata_via_rules

def test_extract_metadata_via_rules():
    text = "Invoice Date: 2026-05-27\nFrom: Electric Company\nTotal: $50.00"
    # Mock DB call for known senders
    known_senders = ["Electric Company"]
    metadata = extract_metadata_via_rules(text, known_senders)
    assert metadata["date"] == "2026-05-27"
    assert metadata["sender"] == "Electric Company"
```

- [ ] **Step 2: Run test to verify it fails**
Run: `cd backend && pytest tests/test_rules_engine.py -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```python
# backend/src/rules_engine.py
import re

def extract_metadata_via_rules(text: str, known_senders: list[str]) -> dict:
    metadata = {"date": None, "sender": None, "category": None}
    
    # Simple date regex YYYY-MM-DD
    date_match = re.search(r'\d{4}-\d{2}-\d{2}', text)
    if date_match:
        metadata["date"] = date_match.group(0)
        
    for sender in known_senders:
        if sender.lower() in text.lower():
            metadata["sender"] = sender
            break
            
    return metadata
```

- [ ] **Step 4: Run test to verify it passes**
Run: `cd backend && pytest tests/test_rules_engine.py -v`
Expected: PASS

- [ ] **Step 5: Commit**
```bash
git add backend/src/rules_engine.py backend/tests/test_rules_engine.py
git commit -m "feat: add rule-based metadata extraction"
```

### Task 4: LLM Fallback Integration

**Files:**
- Create: `backend/src/llm_service.py`
- Create: `backend/tests/test_llm_service.py`
- Modify: `backend/requirements.txt`

- [ ] **Step 1: Write the failing test**

```python
# backend/tests/test_llm_service.py
from src.llm_service import extract_metadata_via_llm
from unittest.mock import patch

@patch('src.llm_service.completion')
def test_extract_metadata_via_llm(mock_completion):
    mock_completion.return_value.choices = [
        type('obj', (object,), {'message': type('obj', (object,), {'content': '{"date": "2026-05-27", "sender": "Unknown", "category": "Bill"}'})})
    ]
    result = extract_metadata_via_llm("Some text")
    assert result["category"] == "Bill"
```

- [ ] **Step 2: Run test to verify it fails**
Run: `cd backend && pytest tests/test_llm_service.py -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```python
# backend/requirements.txt (append)
litellm
```

```python
# backend/src/llm_service.py
import json
from litellm import completion

def extract_metadata_via_llm(text: str, few_shot_examples: list = None) -> dict:
    # In a real implementation, few_shot_examples would be injected into the prompt
    response = completion(
        model="gpt-4o-mini", # Configurable
        messages=[{"role": "user", "content": f"Extract JSON with date, sender, category from: {text}"}],
        response_format={ "type": "json_object" }
    )
    content = response.choices[0].message.content
    return json.loads(content)
```

- [ ] **Step 4: Run test to verify it passes**
Run: `cd backend && pip install -r requirements.txt && pytest tests/test_llm_service.py -v`
Expected: PASS

- [ ] **Step 5: Commit**
```bash
git add backend/requirements.txt backend/src/llm_service.py backend/tests/test_llm_service.py
git commit -m "feat: add llm fallback extraction"
```

### Task 5: Self-Learning (Corrections & Few-Shot)

**Files:**
- Create: `backend/src/learning_service.py`
- Create: `backend/tests/test_learning_service.py`

- [ ] **Step 1: Write the failing test**

```python
# backend/tests/test_learning_service.py
from src.learning_service import save_correction
from mongomock import MongoClient

def test_save_correction():
    client = MongoClient()
    db = client.doc_manager
    save_correction(db, "Raw text here", {"sender": "New Sender", "category": "Bill"})
    
    assert db.corrections.count_documents({}) == 1
    assert db.senders.count_documents({"name": "New Sender"}) == 1
```

- [ ] **Step 2: Run test to verify it fails**
Run: `cd backend && pip install mongomock && pytest tests/test_learning_service.py -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```python
# backend/src/learning_service.py
def save_correction(db, raw_text: str, corrected_metadata: dict):
    # Save the correction for few-shot learning
    db.corrections.insert_one({
        "raw_text": raw_text,
        "metadata": corrected_metadata
    })
    
    # Update known senders
    sender = corrected_metadata.get("sender")
    if sender:
        db.senders.update_one(
            {"name": sender},
            {"$set": {"name": sender}},
            upsert=True
        )
```

- [ ] **Step 4: Run test to verify it passes**
Run: `cd backend && pytest tests/test_learning_service.py -v`
Expected: PASS

- [ ] **Step 5: Commit**
```bash
git add backend/src/learning_service.py backend/tests/test_learning_service.py
git commit -m "feat: add self-learning corrections logic"
```

### Task 6: Google Drive Integration

**Files:**
- Create: `backend/src/drive_service.py`
- Create: `backend/tests/test_drive_service.py`
- Modify: `backend/requirements.txt`

- [ ] **Step 1: Write the failing test**

```python
# backend/tests/test_drive_service.py
from src.drive_service import generate_filename

def test_generate_filename():
    metadata = {"date": "2026-05-27", "category": "Bill", "sender": "Electric Co"}
    assert generate_filename(metadata) == "2026-05-27_Bill_Electric Co.pdf"
```

- [ ] **Step 2: Run test to verify it fails**
Run: `cd backend && pytest tests/test_drive_service.py -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```python
# backend/requirements.txt (append)
google-api-python-client
google-auth-httplib2
google-auth-oauthlib
```

```python
# backend/src/drive_service.py
def generate_filename(metadata: dict) -> str:
    date = metadata.get("date", "UnknownDate")
    cat = metadata.get("category", "UnknownCategory")
    sender = metadata.get("sender", "UnknownSender")
    return f"{date}_{cat}_{sender}.pdf"

# (OAuth and Upload functions would be implemented here, mocked in tests)
```

- [ ] **Step 4: Run test to verify it passes**
Run: `cd backend && pip install -r requirements.txt && pytest tests/test_drive_service.py -v`
Expected: PASS

- [ ] **Step 5: Commit**
```bash
git add backend/requirements.txt backend/src/drive_service.py backend/tests/test_drive_service.py
git commit -m "feat: add drive service and filename generation"
```

### Task 7: Frontend - Upload UI

**Files:**
- Create: `frontend/package.json` (via Vite init)
- Create: `frontend/src/App.jsx`
- Create: `frontend/src/components/UploadDropzone.jsx`

- [ ] **Step 1: Initialize Frontend**
Run: `npm create vite@latest frontend -- --template react && cd frontend && npm install && npm install tailwindcss @tailwindcss/vite`
(Configure Tailwind in vite.config.js and index.css)

- [ ] **Step 2: Write the Component**

```jsx
# frontend/src/components/UploadDropzone.jsx
import { useState } from 'react';

export default function UploadDropzone({ onUpload }) {
  const [file, setFile] = useState(null);

  const handleUpload = () => {
    if (file) onUpload(file);
  };

  return (
    <div className="border-2 border-dashed p-8 text-center">
      <input type="file" accept="application/pdf" onChange={(e) => setFile(e.target.files[0])} />
      <button onClick={handleUpload} className="mt-4 bg-blue-500 text-white px-4 py-2 rounded">
        Upload PDF
      </button>
    </div>
  );
}
```

- [ ] **Step 3: Integrate into App**

```jsx
# frontend/src/App.jsx
import UploadDropzone from './components/UploadDropzone';

function App() {
  const handleUpload = (file) => {
    console.log("Uploading", file.name);
    // API call to backend would go here
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Document Assistant</h1>
      <UploadDropzone onUpload={handleUpload} />
    </div>
  );
}
export default App;
```

- [ ] **Step 4: Commit**
```bash
git add frontend/
git commit -m "feat: add frontend upload ui"
```

### Task 8: Frontend - Interactive Review UI

**Files:**
- Create: `frontend/src/components/ReviewScreen.jsx`

- [ ] **Step 1: Write the Component**

```jsx
# frontend/src/components/ReviewScreen.jsx
import { useState } from 'react';

export default function ReviewScreen({ document, onSave }) {
  const [metadata, setMetadata] = useState(document.metadata);

  return (
    <div className="p-4 border rounded shadow">
      <h2 className="text-xl mb-2">Review Document</h2>
      <div className="flex flex-col gap-2">
        <input 
          value={metadata.date || ''} 
          onChange={e => setMetadata({...metadata, date: e.target.value})}
          placeholder="Date (YYYY-MM-DD)"
          className="border p-1"
        />
        <input 
          value={metadata.sender || ''} 
          onChange={e => setMetadata({...metadata, sender: e.target.value})}
          placeholder="Sender"
          className="border p-1"
        />
        <input 
          value={metadata.category || ''} 
          onChange={e => setMetadata({...metadata, category: e.target.value})}
          placeholder="Category"
          className="border p-1"
        />
        <button onClick={() => onSave(metadata)} className="bg-green-500 text-white px-4 py-2 rounded">
          Confirm & Save
        </button>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Commit**
```bash
git add frontend/src/components/ReviewScreen.jsx
git commit -m "feat: add interactive review ui"
```
