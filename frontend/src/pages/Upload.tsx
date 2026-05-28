import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getJobStatus, uploadPdf, type JobStatusResponse, type UploadResponse } from "../api/client";

export default function Upload() {
  const [dragging, setDragging] = useState(false);
  const [uploadResult, setUploadResult] = useState<UploadResponse | null>(null);
  const [jobStatus, setJobStatus] = useState<JobStatusResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    if (!uploadResult || uploadResult.duplicate) return;
    if (jobStatus && ["completed", "failed"].includes(jobStatus.status)) return;

    const interval = window.setInterval(async () => {
      try {
        const status = await getJobStatus(uploadResult.source_file_id);
        setJobStatus(status);
      } catch (pollError) {
        setError(String(pollError));
      }
    }, 1500);

    return () => window.clearInterval(interval);
  }, [uploadResult, jobStatus]);

  async function handleFile(file: File) {
    if (!file.name.toLowerCase().endsWith(".pdf")) {
      setError("Only PDF files are supported.");
      return;
    }

    setUploading(true);
    setError(null);
    setJobStatus(null);
    try {
      const result = await uploadPdf(file);
      setUploadResult(result);
      if (result.duplicate) {
        const status = await getJobStatus(result.source_file_id);
        setJobStatus(status);
      }
    } catch (uploadError) {
      setError(String(uploadError));
    } finally {
      setUploading(false);
    }
  }

  return (
    <section className="card grid">
      <h2>Upload PDF Scan</h2>
      <div
        className={`dropzone ${dragging ? "dragging" : ""}`}
        onDragOver={(event) => {
          event.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={(event) => {
          event.preventDefault();
          setDragging(false);
          const file = event.dataTransfer.files[0];
          if (file) void handleFile(file);
        }}
      >
        <p>Drag and drop a multipage PDF here, or choose a file.</p>
        <input
          type="file"
          accept="application/pdf"
          onChange={(event) => {
            const file = event.target.files?.[0];
            if (file) void handleFile(file);
          }}
        />
      </div>

      {uploading && <p className="status">Uploading...</p>}
      {error && <p className="error">{error}</p>}

      {uploadResult && (
        <div className="status">
          <p className="success">
            Uploaded <strong>{uploadResult.filename}</strong>
            {uploadResult.duplicate ? " (duplicate detected)" : ""}
          </p>
          {jobStatus && (
            <>
              <p>
                Status: <span className="badge">{jobStatus.status}</span> — {jobStatus.progress_pct}%
              </p>
              {jobStatus.error && <p className="error">{jobStatus.error}</p>}
              {jobStatus.status === "completed" && (
                <p>
                  Processing complete. <Link to="/search">Search documents</Link>
                </p>
              )}
            </>
          )}
        </div>
      )}
    </section>
  );
}
