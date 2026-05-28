from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.validators import apply_collection_validators


async def ensure_indexes(db: AsyncIOMotorDatabase) -> None:
    await db.source_files.create_index("sha256", unique=True)
    await db.processing_jobs.create_index([("source_file_id", 1), ("status", 1)])
    await db.pages.create_index([("source_file_id", 1), ("page_number", 1)], unique=True)
    await db.pages.create_index("logical_document_id")
    await db.logical_documents.create_index([("doc_type", 1), ("document_date", -1)])
    await db.logical_documents.create_index([("sender_normalized", 1), ("document_date", -1)])
    await db.logical_documents.create_index([("source_file_id", 1)])
    await db.logical_documents.create_index([("search_text", "text")])

    await apply_collection_validators(db)
