from __future__ import annotations

from typing import Any

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection


def _oid(value: str | ObjectId) -> ObjectId:
    return value if isinstance(value, ObjectId) else ObjectId(value)


async def insert_page(collection: AsyncIOMotorCollection, page_doc: dict[str, Any]) -> str:
    result = await collection.insert_one(page_doc)
    return str(result.inserted_id)


async def insert_pages(collection: AsyncIOMotorCollection, page_docs: list[dict[str, Any]]) -> list[str]:
    if not page_docs:
        return []
    result = await collection.insert_many(page_docs)
    return [str(page_id) for page_id in result.inserted_ids]


async def get_pages_by_source_file(
    collection: AsyncIOMotorCollection,
    source_file_id: str,
) -> list[dict[str, Any]]:
    cursor = collection.find({"source_file_id": _oid(source_file_id)}).sort("page_number", 1)
    return await cursor.to_list(length=10000)


async def get_pages_by_logical_document(
    collection: AsyncIOMotorCollection,
    logical_document_id: str,
) -> list[dict[str, Any]]:
    cursor = collection.find({"logical_document_id": _oid(logical_document_id)}).sort("page_number", 1)
    return await cursor.to_list(length=1000)


async def update_page(
    collection: AsyncIOMotorCollection,
    page_id: str,
    update_fields: dict[str, Any],
) -> None:
    await collection.update_one({"_id": _oid(page_id)}, {"$set": update_fields})


async def assign_logical_document(
    collection: AsyncIOMotorCollection,
    page_ids: list[str],
    logical_document_id: str,
) -> None:
    await collection.update_many(
        {"_id": {"$in": [_oid(page_id) for page_id in page_ids]}},
        {"$set": {"logical_document_id": _oid(logical_document_id)}},
    )
