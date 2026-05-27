# Personal Document Assistant - Design Specification

## 1. Overview
A web application designed to process scanned PDF documents. It extracts metadata (Date, Category, Sender), groups related pages, and uploads the finalized, properly named PDFs to Google Drive. The system uses a hybrid rule-based and LLM approach with a self-learning mechanism to improve accuracy over time based on user corrections.

## 2. Architecture & Tech Stack
- **Frontend**: React (Vite) + Tailwind CSS. Provides UI for uploading PDFs and an interactive review screen for low-confidence extractions.
- **Backend**: Python (FastAPI). Handles API requests, PDF manipulation, and AI processing.
- **Database**: MongoDB. Stores known senders, categories, user corrections (for few-shot learning), and Google Drive OAuth tokens.
- **PDF Processing**: `pdfplumber` or `PyMuPDF` for text extraction (from already-OCRed PDFs), and `pypdf` for splitting/merging pages.
- **AI/LLM Integration**: `LiteLLM` or `LangChain` to support both local LLMs (Ollama) and cloud LLMs (OpenAI/Anthropic).

## 3. Data Flow & Processing Pipeline
1. **Upload**: User uploads a scanned PDF via the React UI.
2. **Page Extraction**: Backend splits the PDF into individual pages and extracts text from each.
3. **Rule-Based Pass**: 
   - Regex searches for Dates.
   - Keyword matching against the MongoDB database for Known Senders and Categories.
4. **LLM Fallback**: If the rule-based pass fails to find all metadata with high confidence, the page text is sent to the configured LLM with a prompt to extract Date, Sender, and Category.
5. **Grouping**: Pages with the same Sender and Date, or pages that the LLM identifies as continuations, are grouped together into a single document.
6. **Confidence Check**:
   - **High Confidence**: Document is queued for auto-saving.
   - **Low/Partial Confidence**: Document is flagged for the Interactive Review UI.

## 4. Self-Learning Mechanism
When a document is flagged for Interactive Review, the user corrects the metadata in the React UI. Upon saving:
- **Sender Updates**: If a new sender is entered, it is saved to the `senders` MongoDB collection along with keywords found in the document.
- **Category Updates**: The mapping between the sender/keywords and the chosen category is updated in MongoDB.
- **LLM Few-Shot Examples**: The corrected document's text and final metadata are saved to a `corrections` collection. Future LLM prompts will query MongoDB for similar past corrections and include them as examples, teaching the LLM the user's specific document formats over time.

## 5. Output & Google Drive Integration
- **Authentication**: OAuth 2.0 flow to connect the user's Google Drive account. Tokens stored securely in MongoDB.
- **File Generation**: The backend merges the grouped pages into new PDF files.
- **Naming Convention**: `YYYY-MM-DD_Category_SenderName.pdf` (e.g., `2026-05-27_Bill_ElectricCompany.pdf`).
- **Folder Structure**: Files are uploaded to Google Drive organized by Year and Category (e.g., `MyDocuments / 2026 / Bills / ...`).
- **Cleanup**: Once successfully uploaded to Google Drive, the local temporary PDFs are deleted.