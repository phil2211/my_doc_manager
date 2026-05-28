import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import {
  getDocument,
  getDocumentFileUrl,
  getPagePreviewUrl,
  getPageThumbnailUrl,
  type LogicalDocumentResponse,
  type PageResponse,
} from "../api/client";

export default function DocumentDetail() {
  const { id } = useParams();
  const [document, setDocument] = useState<LogicalDocumentResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [lightboxPage, setLightboxPage] = useState<PageResponse | null>(null);

  useEffect(() => {
    if (!id) return;
    void getDocument(id)
      .then(setDocument)
      .catch((detailError) => setError(String(detailError)));
  }, [id]);

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

  if (error) {
    return <p className="error">{error}</p>;
  }

  if (!document) {
    return <p className="status">Loading document...</p>;
  }

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
          <p>
            <strong>Type:</strong> {document.metadata.doc_type || "-"}
          </p>
          <p>
            <strong>Date:</strong>{" "}
            {document.metadata.document_date
              ? new Date(document.metadata.document_date).toLocaleDateString()
              : "-"}
          </p>
          <p>
            <strong>Sender:</strong> {document.metadata.sender_name || "-"}
          </p>
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
