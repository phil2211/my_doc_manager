import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { searchDocuments, type DocumentListItem } from "../api/client";

const DOC_TYPES = ["", "bill", "contract", "information", "commercial", "other"];

export default function Search() {
  const [docType, setDocType] = useState("");
  const [sender, setSender] = useState("");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [query, setQuery] = useState("");
  const [items, setItems] = useState<DocumentListItem[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function runSearch() {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      if (docType) params.set("doc_type", docType);
      if (sender) params.set("sender", sender);
      if (dateFrom) params.set("date_from", `${dateFrom}T00:00:00`);
      if (dateTo) params.set("date_to", `${dateTo}T23:59:59`);
      if (query) params.set("q", query);
      const response = await searchDocuments(params);
      setItems(response.items);
      setTotal(response.total);
    } catch (searchError) {
      setError(String(searchError));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void runSearch();
  }, []);

  return (
    <section className="card grid">
      <h2>Search Documents</h2>
      <div className="filters">
        <div>
          <label htmlFor="docType">Type</label>
          <select id="docType" value={docType} onChange={(event) => setDocType(event.target.value)}>
            {DOC_TYPES.map((type) => (
              <option key={type || "all"} value={type}>
                {type || "All types"}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label htmlFor="sender">Sender prefix</label>
          <input id="sender" value={sender} onChange={(event) => setSender(event.target.value)} />
        </div>
        <div>
          <label htmlFor="dateFrom">Date from</label>
          <input id="dateFrom" type="date" value={dateFrom} onChange={(event) => setDateFrom(event.target.value)} />
        </div>
        <div>
          <label htmlFor="dateTo">Date to</label>
          <input id="dateTo" type="date" value={dateTo} onChange={(event) => setDateTo(event.target.value)} />
        </div>
        <div>
          <label htmlFor="query">Full-text query</label>
          <input id="query" value={query} onChange={(event) => setQuery(event.target.value)} />
        </div>
      </div>
      <button onClick={() => void runSearch()} disabled={loading}>
        {loading ? "Searching..." : "Search"}
      </button>
      {error && <p className="error">{error}</p>}
      <p className="status">{total} result(s)</p>
      <table className="table">
        <thead>
          <tr>
            <th>Title</th>
            <th>Type</th>
            <th>Date</th>
            <th>Sender</th>
            <th>Pages</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item) => (
            <tr key={item.id}>
              <td>
                <Link to={`/documents/${item.id}`}>{item.title || "Untitled document"}</Link>
              </td>
              <td>{item.doc_type || "-"}</td>
              <td>{item.document_date ? new Date(item.document_date).toLocaleDateString() : "-"}</td>
              <td>{item.sender_name || "-"}</td>
              <td>{item.page_count}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
