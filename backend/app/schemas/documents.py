from __future__ import annotations

from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

DocType = Literal["bill", "contract", "information", "commercial", "other"]


class SourceFileResponse(BaseModel):
    id: str
    filename: str
    storage_path: str
    sha256: str
    uploaded_at: datetime
    status: str


class UploadResponse(BaseModel):
    source_file_id: str
    job_id: str
    filename: str
    duplicate: bool = False


class JobStatusResponse(BaseModel):
    id: str
    source_file_id: str
    status: str
    progress_pct: int
    error: str | None = None
    started_at: datetime
    completed_at: datetime | None = None


class PageResponse(BaseModel):
    id: str
    page_number: int
    thumbnail_path: str | None = None
    is_scanned: bool = False
    text_content: str = ""
    ocr_confidence: float | None = None


class DocumentMetadataResponse(BaseModel):
    doc_type: str | None = None
    document_date: datetime | None = None
    sender_name: str | None = None
    sender_normalized: str | None = None
    confidence: dict[str, float] = Field(default_factory=dict)
    extra_fields: dict[str, Any] = Field(default_factory=dict)


class LogicalDocumentResponse(BaseModel):
    id: str
    source_file_id: str
    page_ids: list[str]
    title: str | None = None
    grouping_confidence: float | None = None
    metadata: DocumentMetadataResponse
    pages: list[PageResponse] = Field(default_factory=list)


class DocumentListItem(BaseModel):
    id: str
    source_file_id: str
    title: str | None = None
    doc_type: str | None = None
    document_date: datetime | None = None
    sender_name: str | None = None
    sender_normalized: str | None = None
    page_count: int = 0
    score: float | None = None


class DocumentSearchResponse(BaseModel):
    items: list[DocumentListItem]
    total: int


class DocumentMetadataUpdateRequest(BaseModel):
    doc_type: DocType | None = None
    document_date: date | None = None


class SettingsResponse(BaseModel):
    llm_enabled: bool
    llm_base_url: str
    llm_model: str
    llm_confidence_threshold: float
    ocr_dpi: int


class SettingsUpdateRequest(BaseModel):
    llm_enabled: bool | None = None
    llm_base_url: str | None = None
    llm_model: str | None = None
    llm_confidence_threshold: float | None = None
    ocr_dpi: int | None = None
