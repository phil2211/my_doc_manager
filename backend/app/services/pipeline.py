from __future__ import annotations

from datetime import datetime
from pathlib import Path

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.config import get_settings
from app.db.repositories import logical_documents as logical_documents_repo
from app.db.repositories import pages as pages_repo
from app.db.repositories import processing_jobs as jobs_repo
from app.db.repositories import source_files as source_files_repo
from app.services.classification.rules import RuleBasedClassifier
from app.services.extraction.regex_extractor import RegexExtractor
from app.services.grouping.heuristic import HeuristicGrouper
from app.services.llm.backends import LlmClassifier, LlmExtractor, LlmGrouper
from app.services.ocr.tesseract_backend import TesseractOcrBackend
from app.services.pdf_utils import compute_layout_features, ensure_storage_dir, save_thumbnail, split_pdf_to_pages
from app.services.types import PageContext


class ProcessingPipeline:
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.db = db
        self.settings = get_settings()
        self.ocr = TesseractOcrBackend()
        self.grouper = HeuristicGrouper()
        self.classifier = RuleBasedClassifier()
        self.extractor = RegexExtractor()
        self.llm_grouper = LlmGrouper()
        self.llm_classifier = LlmClassifier()
        self.llm_extractor = LlmExtractor()

    async def run(self, source_file_id: str, job_id: str, pdf_path: Path) -> None:
        try:
            await jobs_repo.update_job(
                self.db.processing_jobs,
                job_id,
                status="processing",
                progress_pct=5,
            )
            await source_files_repo.update_source_file_status(
                self.db.source_files,
                source_file_id,
                "processing",
            )

            storage_dir = ensure_storage_dir(source_file_id)
            pages_data = split_pdf_to_pages(pdf_path)
            page_records: list[dict] = []

            for index, page_data in enumerate(pages_data):
                text_content = page_data["native_text"]
                ocr_confidence = None

                if page_data["is_scanned"]:
                    ocr_result = self.ocr.extract_text(page_data["image_bytes"])
                    text_content = ocr_result.text or text_content
                    ocr_confidence = ocr_result.confidence

                thumbnail_path = storage_dir / f"page_{page_data['page_number']}.png"
                save_thumbnail(page_data["image_bytes"], thumbnail_path)
                layout_features = compute_layout_features(page_data["image_bytes"], text_content)

                page_records.append(
                    {
                        "source_file_id": source_files_repo._oid(source_file_id),
                        "page_number": page_data["page_number"],
                        "thumbnail_path": str(thumbnail_path),
                        "is_scanned": page_data["is_scanned"],
                        "text_content": text_content,
                        "ocr_confidence": ocr_confidence,
                        "layout_features": layout_features,
                        "logical_document_id": None,
                    }
                )

                progress = 5 + int(((index + 1) / max(len(pages_data), 1)) * 45)
                await jobs_repo.update_job(
                    self.db.processing_jobs,
                    job_id,
                    progress_pct=progress,
                )

            await pages_repo.insert_pages(self.db.pages, page_records)
            stored_pages = await pages_repo.get_pages_by_source_file(self.db.pages, source_file_id)

            page_contexts = [
                PageContext(
                    page_id=str(page["_id"]),
                    page_number=page["page_number"],
                    text_content=page.get("text_content", ""),
                    layout_features=page.get("layout_features", {}),
                    is_blank=page.get("layout_features", {}).get("is_blank", False),
                )
                for page in stored_pages
            ]

            await jobs_repo.update_job(self.db.processing_jobs, job_id, progress_pct=55)

            grouper = self.llm_grouper if self.settings.llm_enabled else self.grouper
            groups = grouper.group_pages(page_contexts)

            for group_index, group in enumerate(groups):
                group_pages = [page for page in stored_pages if str(page["_id"]) in group.page_ids]
                pages_text = [page.get("text_content", "") for page in group_pages]

                classification = self.classifier.classify(pages_text)
                metadata = self.extractor.extract_metadata(pages_text, classification.doc_type)

                if self.settings.llm_enabled:
                    if classification.confidence < self.settings.llm_confidence_threshold:
                        classification = self.llm_classifier.classify(pages_text)
                    date_conf = metadata.confidence.get("document_date", 0)
                    sender_conf = metadata.confidence.get("sender_name", 0)
                    if (
                        date_conf < self.settings.llm_confidence_threshold
                        or sender_conf < self.settings.llm_confidence_threshold
                    ):
                        metadata = self.llm_extractor.extract_metadata(pages_text, classification.doc_type)

                search_text = self._build_search_text(group.title, metadata, pages_text)
                document_date = None
                if metadata.document_date:
                    try:
                        document_date = datetime.fromisoformat(metadata.document_date)
                    except ValueError:
                        document_date = None

                logical_doc = {
                    "source_file_id": source_files_repo._oid(source_file_id),
                    "page_ids": [pages_repo._oid(page_id) for page_id in group.page_ids],
                    "title": group.title,
                    "grouping_confidence": group.confidence,
                    "doc_type": classification.doc_type,
                    "document_date": document_date,
                    "sender_name": metadata.sender_name,
                    "sender_normalized": metadata.sender_normalized,
                    "extra_fields": metadata.extra_fields,
                    "confidence": {
                        "doc_type": classification.confidence,
                        **metadata.confidence,
                        "grouping": group.confidence,
                    },
                    "search_text": search_text,
                }
                logical_document_id = await logical_documents_repo.insert_logical_document(
                    self.db.logical_documents,
                    logical_doc,
                )
                await pages_repo.assign_logical_document(
                    self.db.pages,
                    group.page_ids,
                    logical_document_id,
                )

                progress = 55 + int(((group_index + 1) / max(len(groups), 1)) * 40)
                await jobs_repo.update_job(
                    self.db.processing_jobs,
                    job_id,
                    progress_pct=progress,
                )

            await source_files_repo.update_source_file_status(
                self.db.source_files,
                source_file_id,
                "processed",
            )
            await jobs_repo.update_job(
                self.db.processing_jobs,
                job_id,
                status="completed",
                progress_pct=100,
                completed=True,
            )
        except Exception as exc:
            await source_files_repo.update_source_file_status(
                self.db.source_files,
                source_file_id,
                "failed",
            )
            await jobs_repo.update_job(
                self.db.processing_jobs,
                job_id,
                status="failed",
                error=str(exc),
                completed=True,
            )
            raise

    def _build_search_text(
        self,
        title: str | None,
        metadata,
        pages_text: list[str],
    ) -> str:
        parts = [
            title or "",
            metadata.sender_name or "",
            metadata.sender_normalized or "",
            "\n".join(pages_text),
        ]
        return "\n".join(part for part in parts if part).strip()
