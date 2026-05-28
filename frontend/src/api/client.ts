/** Empty string uses same origin; Vite proxies /api to the backend in dev. */
const API_URL = import.meta.env.VITE_API_URL ?? "";

export interface UploadResponse {
  source_file_id: string;
  job_id: string;
  filename: string;
  duplicate: boolean;
}

export interface JobStatusResponse {
  id: string;
  source_file_id: string;
  status: string;
  progress_pct: number;
  error?: string | null;
}

export interface DocumentListItem {
  id: string;
  source_file_id: string;
  title?: string | null;
  doc_type?: string | null;
  document_date?: string | null;
  sender_name?: string | null;
  sender_normalized?: string | null;
  page_count: number;
  score?: number | null;
}

export interface DocumentSearchResponse {
  items: DocumentListItem[];
  total: number;
}

export interface PageResponse {
  id: string;
  page_number: number;
  thumbnail_path?: string | null;
  is_scanned: boolean;
  text_content: string;
  ocr_confidence?: number | null;
}

export interface LogicalDocumentResponse {
  id: string;
  source_file_id: string;
  page_ids: string[];
  title?: string | null;
  grouping_confidence?: number | null;
  metadata: {
    doc_type?: string | null;
    document_date?: string | null;
    sender_name?: string | null;
    sender_normalized?: string | null;
    confidence: Record<string, number>;
    extra_fields: Record<string, unknown>;
  };
  pages: PageResponse[];
}

export interface SettingsResponse {
  llm_enabled: boolean;
  llm_base_url: string;
  llm_model: string;
  llm_confidence_threshold: number;
  ocr_dpi: number;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, init);
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export function uploadPdf(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);
  return request<UploadResponse>("/api/v1/files", {
    method: "POST",
    body: formData,
  });
}

export function getJobStatus(sourceFileId: string): Promise<JobStatusResponse> {
  return request<JobStatusResponse>(`/api/v1/files/${sourceFileId}/status`);
}

export function searchDocuments(params: URLSearchParams): Promise<DocumentSearchResponse> {
  return request<DocumentSearchResponse>(`/api/v1/documents?${params.toString()}`);
}

export function getDocument(documentId: string): Promise<LogicalDocumentResponse> {
  return request<LogicalDocumentResponse>(`/api/v1/documents/${documentId}`);
}

export interface DocumentMetadataUpdate {
  doc_type?: string;
  document_date?: string | null;
  sender_name?: string | null;
}

export function listSenderNames(): Promise<string[]> {
  return request<{ items: string[] }>("/api/v1/documents/senders").then((response) => response.items);
}

export function updateDocumentMetadata(
  documentId: string,
  payload: DocumentMetadataUpdate,
): Promise<LogicalDocumentResponse> {
  return request<LogicalDocumentResponse>(`/api/v1/documents/${documentId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export function getDocumentFileUrl(documentId: string): string {
  return `${API_URL}/api/v1/documents/${documentId}/file`;
}

export function getSettings(): Promise<SettingsResponse> {
  return request<SettingsResponse>("/api/v1/settings");
}

export function updateSettings(payload: Partial<SettingsResponse>): Promise<SettingsResponse> {
  return request<SettingsResponse>("/api/v1/settings", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export function getPageThumbnailUrl(pageId: string): string {
  return `${API_URL}/api/v1/pages/${pageId}/thumbnail`;
}

export function getPagePreviewUrl(pageId: string): string {
  return `${API_URL}/api/v1/pages/${pageId}/preview`;
}
