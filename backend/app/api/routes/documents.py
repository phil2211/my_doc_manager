from __future__ import annotations

from datetime import datetime, time, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.client import get_database
from app.db.repositories import logical_documents as logical_documents_repo
from app.db.repositories import pages as pages_repo
from app.db.repositories import source_files as source_files_repo
from app.schemas.documents import (
    DocumentListItem,
    DocumentMetadataResponse,
    DocumentMetadataUpdateRequest,
    DocumentSearchResponse,
    LogicalDocumentResponse,
    PageResponse,
)

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])


async def get_db() -> AsyncIOMotorDatabase:
    return get_database()


async def _logical_document_response(
    document: dict,
    db: AsyncIOMotorDatabase,
) -> LogicalDocumentResponse:
    document_id = str(document["_id"])
    pages = await pages_repo.get_pages_by_logical_document(db.pages, document_id)
    page_responses = [
        PageResponse(
            id=str(page["_id"]),
            page_number=page["page_number"],
            thumbnail_path=page.get("thumbnail_path"),
            is_scanned=page.get("is_scanned", False),
            text_content=page.get("text_content", ""),
            ocr_confidence=page.get("ocr_confidence"),
        )
        for page in pages
    ]

    metadata = DocumentMetadataResponse(
        doc_type=document.get("doc_type"),
        document_date=document.get("document_date"),
        sender_name=document.get("sender_name"),
        sender_normalized=document.get("sender_normalized"),
        confidence=document.get("confidence", {}),
        extra_fields=document.get("extra_fields", {}),
    )

    return LogicalDocumentResponse(
        id=document_id,
        source_file_id=str(document["source_file_id"]),
        page_ids=[str(page_id) for page_id in document.get("page_ids", [])],
        title=document.get("title"),
        grouping_confidence=document.get("grouping_confidence"),
        metadata=metadata,
        pages=page_responses,
    )


@router.get("", response_model=DocumentSearchResponse)
async def search_documents(
    doc_type: str | None = None,
    sender: str | None = Query(default=None, description="Sender prefix match"),
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    q: str | None = Query(default=None, description="Full-text search query"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> DocumentSearchResponse:
    items, total = await logical_documents_repo.search_logical_documents(
        db.logical_documents,
        doc_type=doc_type,
        sender_prefix=sender,
        date_from=date_from,
        date_to=date_to,
        query=q,
        skip=skip,
        limit=limit,
    )

    response_items = [
        DocumentListItem(
            id=str(item["_id"]),
            source_file_id=str(item["source_file_id"]),
            title=item.get("title"),
            doc_type=item.get("doc_type"),
            document_date=item.get("document_date"),
            sender_name=item.get("sender_name"),
            sender_normalized=item.get("sender_normalized"),
            page_count=len(item.get("page_ids", [])),
            score=item.get("score"),
        )
        for item in items
    ]
    return DocumentSearchResponse(items=response_items, total=total)


@router.get("/{document_id}", response_model=LogicalDocumentResponse)
async def get_document(
    document_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> LogicalDocumentResponse:
    document = await logical_documents_repo.get_logical_document(db.logical_documents, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    return await _logical_document_response(document, db)


@router.patch("/{document_id}", response_model=LogicalDocumentResponse)
async def update_document_metadata(
    document_id: str,
    payload: DocumentMetadataUpdateRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> LogicalDocumentResponse:
    document = await logical_documents_repo.get_logical_document(db.logical_documents, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    changes = payload.model_dump(exclude_unset=True)
    update_fields: dict[str, object] = {}
    if "doc_type" in changes:
        update_fields["doc_type"] = changes["doc_type"]
    if "document_date" in changes:
        raw_date = changes["document_date"]
        if raw_date is None:
            update_fields["document_date"] = None
        else:
            update_fields["document_date"] = datetime.combine(
                raw_date,
                time.min,
                tzinfo=timezone.utc,
            )

    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields to update")

    await logical_documents_repo.update_logical_document(
        db.logical_documents,
        document_id,
        update_fields,
    )

    updated = await logical_documents_repo.get_logical_document(db.logical_documents, document_id)
    assert updated is not None
    return await _logical_document_response(updated, db)


@router.get("/{document_id}/file")
async def get_document_file(
    document_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    document = await logical_documents_repo.get_logical_document(db.logical_documents, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    source_file = await source_files_repo.get_source_file(
        db.source_files,
        str(document["source_file_id"]),
    )
    if source_file is None:
        raise HTTPException(status_code=404, detail="Source file not found")

    return FileResponse(
        path=source_file["storage_path"],
        media_type="application/pdf",
        filename=source_file["filename"],
    )
