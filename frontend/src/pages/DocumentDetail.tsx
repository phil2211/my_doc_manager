import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import {
  getDocument,
  getDocumentFileUrl,
  listSenderNames,
  getPagePreviewUrl,
  getPageThumbnailUrl,
  updateDocumentMetadata,
  type LogicalDocumentResponse,
  type PageResponse,
} from "../api/client";
import { DOC_TYPES, formatDocType } from "../constants/docTypes";
import { dateInputToApiValue, toDateInputValue } from "../utils/dates";

export default function DocumentDetail() {
  const { id } = useParams();
  const [document, setDocument] = useState<LogicalDocumentResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [lightboxPage, setLightboxPage] = useState<PageResponse | null>(null);
  const [savingType, setSavingType] = useState(false);
  const [savingDate, setSavingDate] = useState(false);
  const [savingSender, setSavingSender] = useState(false);
  const [senderDraft, setSenderDraft] = useState("");
  const [knownSenders, setKnownSenders] = useState<string[]>([]);

  useEffect(() => {
    if (!id) return;
    void getDocument(id)
      .then(setDocument)
      .catch((detailError) => setError(String(detailError)));
    void listSenderNames()
      .then(setKnownSenders)
      .catch(() => setKnownSenders([]));
  }, [id]);

  useEffect(() => {
    setSenderDraft(document?.metadata.sender_name ?? "");
  }, [document?.metadata.sender_name]);

  useEffect(() => {
    if (!lightboxPage) return;

    function onKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        setLightboxPage(null);
      }
    }

    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [lightboxPage]);

  async function handleDocTypeChange(nextType: string) {
    if (!id || !document || nextType === (document.metadata.doc_type ?? "")) {
      return;
    }

    setSavingType(true);
    setError(null);
    try {
      const updated = await updateDocumentMetadata(id, { doc_type: nextType });
      setDocument(updated);
    } catch (typeError) {
      setError(String(typeError));
    } finally {
      setSavingType(false);
    }
  }

  async function handleDateChange(nextValue: string) {
    if (!id || !document) return;

    const currentValue = toDateInputValue(document.metadata.document_date);
    if (nextValue === currentValue) return;

    setSavingDate(true);
    setError(null);
    try {
      const updated = await updateDocumentMetadata(id, {
        document_date: dateInputToApiValue(nextValue),
      });
      setDocument(updated);
    } catch (dateError) {
      setError(String(dateError));
    } finally {
      setSavingDate(false);
    }
  }

  async function saveSender() {
    if (!id || !document) return;

    const trimmed = senderDraft.trim();
    const current = (document.metadata.sender_name ?? "").trim();
    if (trimmed === current) return;

    setSavingSender(true);
    setError(null);
    try {
      const updated = await updateDocumentMetadata(id, {
        sender_name: trimmed || null,
      });
      setDocument(updated);
      setSenderDraft(updated.metadata.sender_name ?? "");
      if (trimmed && !knownSenders.includes(trimmed)) {
        setKnownSenders((prev) => [...prev, trimmed].sort((a, b) => a.localeCompare(b)));
      }
    } catch (senderError) {
      setError(String(senderError));
      setSenderDraft(document.metadata.sender_name ?? "");
    } finally {
      setSavingSender(false);
    }
  }

  if (error) {
    return <p className="error">{error}</p>;
  }

  if (!document) {
    return <p className="status">Loading document...</p>;
  }

  const senderSuggestions = Array.from(
    new Set([
      ...knownSenders,
      ...(document.metadata.sender_name ? [document.metadata.sender_name] : []),
      ...(senderDraft.trim() ? [senderDraft.trim()] : []),
    ]),
  ).sort((a, b) => a.localeCompare(b));

  return (
    <section className="grid">
      <p>
        <Link to="/search">← Back to search</Link>
      </p>
      <div className="card grid">
        <h2>{document.title || "Untitled document"}</h2>
        <p>
          <a href={getDocumentFileUrl(document.id)} target="_blank" rel="noreferrer">
            Open original PDF
          </a>
        </p>
        <div className="grid">
          <div className="field-row">
            <label htmlFor="doc-type">Type</label>
            <select
              id="doc-type"
              value={document.metadata.doc_type ?? "other"}
              disabled={savingType}
              onChange={(event) => void handleDocTypeChange(event.target.value)}
            >
              {DOC_TYPES.map((type) => (
                <option key={type} value={type}>
                  {formatDocType(type)}
                </option>
              ))}
            </select>
            {savingType && <span className="status">Saving…</span>}
          </div>
          <div className="field-row">
            <label htmlFor="doc-date">Date</label>
            <input
              id="doc-date"
              type="date"
              value={toDateInputValue(document.metadata.document_date)}
              disabled={savingDate}
              onChange={(event) => void handleDateChange(event.target.value)}
            />
            <button
              type="button"
              className="secondary"
              disabled={savingDate || !document.metadata.document_date}
              onClick={() => void handleDateChange("")}
            >
              Clear
            </button>
            {savingDate && <span className="status">Saving…</span>}
          </div>
          <div className="field-row field-row-wide">
            <label htmlFor="doc-sender">Sender</label>
            <input
              id="doc-sender"
              type="text"
              list="sender-suggestions"
              value={senderDraft}
              disabled={savingSender}
              placeholder="Select or type sender name"
              onChange={(event) => setSenderDraft(event.target.value)}
              onBlur={() => void saveSender()}
              onKeyDown={(event) => {
                if (event.key === "Enter") {
                  event.preventDefault();
                  void saveSender();
                }
              }}
            />
            <datalist id="sender-suggestions">
              {senderSuggestions.map((sender) => (
                <option key={sender} value={sender} />
              ))}
            </datalist>
            <button
              type="button"
              className="secondary"
              disabled={savingSender || !senderDraft.trim()}
              onClick={() => void saveSender()}
            >
              Save
            </button>
            {savingSender && <span className="status">Saving…</span>}
          </div>
          <p>
            <strong>Grouping confidence:</strong>{" "}
            {document.grouping_confidence?.toFixed(2) ?? "-"}
          </p>
        </div>
        {Object.keys(document.metadata.confidence).length > 0 && (
          <div>
            <strong>Confidence scores</strong>
            <ul>
              {Object.entries(document.metadata.confidence).map(([key, value]) => (
                <li key={key}>
                  {key}: {value.toFixed(2)}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      <div className="card grid">
        <h3>Pages</h3>
        <p className="status">Click a thumbnail to view the page larger.</p>
        <div className="thumbnails">
          {document.pages.map((page) => (
            <button
              key={page.id}
              type="button"
              className="thumbnail-button"
              onClick={() => setLightboxPage(page)}
              aria-label={`View page ${page.page_number} larger`}
            >
              <img
                className="thumbnail"
                src={getPageThumbnailUrl(page.id)}
                alt={`Page ${page.page_number}`}
                loading="lazy"
              />
              <span>Page {page.page_number}</span>
            </button>
          ))}
        </div>
      </div>

      {lightboxPage && (
        <div
          className="lightbox"
          role="dialog"
          aria-modal="true"
          aria-label={`Page ${lightboxPage.page_number} preview`}
          onClick={() => setLightboxPage(null)}
        >
          <div className="lightbox-panel" onClick={(event) => event.stopPropagation()}>
            <div className="lightbox-header">
              <strong>Page {lightboxPage.page_number}</strong>
              <button type="button" className="secondary" onClick={() => setLightboxPage(null)}>
                Close
              </button>
            </div>
            <img
              className="lightbox-image"
              src={getPagePreviewUrl(lightboxPage.id)}
              alt={`Page ${lightboxPage.page_number}`}
            />
          </div>
        </div>
      )}

      <div className="card grid">
        <h3>Extracted text</h3>
        {document.pages.map((page) => (
          <div key={page.id}>
            <h4>Page {page.page_number}</h4>
            <pre style={{ whiteSpace: "pre-wrap" }}>{page.text_content || "(empty)"}</pre>
          </div>
        ))}
      </div>
    </section>
  );
}
