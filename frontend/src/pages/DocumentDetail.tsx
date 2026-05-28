import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import {
  getDocument,
  getDocumentFileUrl,
  type LogicalDocumentResponse,
} from "../api/client";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function DocumentDetail() {
  const { id } = useParams();
  const [document, setDocument] = useState<LogicalDocumentResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    void getDocument(id)
      .then(setDocument)
      .catch((detailError) => setError(String(detailError)));
  }, [id]);

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
        <div className="thumbnails">
          {document.pages.map((page) => (
            <div key={page.id}>
              <img
                className="thumbnail"
                src={`${API_URL}/api/v1/pages/${page.id}/thumbnail`}
                alt={`Page ${page.page_number}`}
              />
              <p>Page {page.page_number}</p>
            </div>
          ))}
        </div>
      </div>

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
