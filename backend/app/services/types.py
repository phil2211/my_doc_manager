from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class PageContext:
    page_id: str
    page_number: int
    text_content: str
    layout_features: dict
    is_blank: bool = False


@dataclass
class PageGroup:
    page_ids: list[str]
    page_numbers: list[int]
    confidence: float
    title: str | None = None


@dataclass
class ClassificationResult:
    doc_type: str
    confidence: float
    signals: list[str] = field(default_factory=list)


@dataclass
class MetadataResult:
    document_date: str | None
    sender_name: str | None
    sender_normalized: str | None
    confidence: dict[str, float] = field(default_factory=dict)
    extra_fields: dict = field(default_factory=dict)
