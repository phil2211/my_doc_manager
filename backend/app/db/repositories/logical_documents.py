from __future__ import annotations

import re
from datetime import datetime
from typing import Any

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection


def _oid(value: str | ObjectId) -> ObjectId:
    return value if isinstance(value, ObjectId) else ObjectId(value)


async def insert_logical_document(collection: AsyncIOMotorCollection, doc: dict[str, Any]) -> str:
    result = await collection.insert_one(doc)
    return str(result.inserted_id)


async def update_logical_document(
    collection: AsyncIOMotorCollection,
    logical_document_id: str,
    update_fields: dict[str, Any],
) -> None:
    await collection.update_one({"_id": _oid(logical_document_id)}, {"$set": update_fields})


async def get_logical_document(
    collection: AsyncIOMotorCollection,
    logical_document_id: str,
) -> dict[str, Any] | None:
    return await collection.find_one({"_id": _oid(logical_document_id)})


async def list_distinct_sender_names(
    collection: AsyncIOMotorCollection,
    *,
    limit: int = 200,
) -> list[str]:
    pipeline = [
        {"$match": {"sender_name": {"$exists": True, "$nin": [None, ""]}}},
        {"$group": {"_id": "$sender_name"}},
        {"$sort": {"_id": 1}},
        {"$limit": limit},
    ]
    cursor = collection.aggregate(pipeline)
    results = await cursor.to_list(length=limit)
    return [str(item["_id"]) for item in results if item.get("_id")]


async def search_logical_documents(
    collection: AsyncIOMotorCollection,
    *,
    doc_type: str | None = None,
    sender_prefix: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    query: str | None = None,
    skip: int = 0,
    limit: int = 50,
) -> tuple[list[dict[str, Any]], int]:
    mongo_query: dict[str, Any] = {}
    if doc_type:
        mongo_query["doc_type"] = doc_type
    if sender_prefix:
        mongo_query["sender_normalized"] = {
            "$regex": f"^{re.escape(sender_prefix)}",
            "$options": "i",
        }
    if date_from or date_to:
        date_filter: dict[str, Any] = {}
        if date_from:
            date_filter["$gte"] = date_from
        if date_to:
            date_filter["$lte"] = date_to
        mongo_query["document_date"] = date_filter

    projection: dict[str, Any] | None = None
    sort: list[tuple[str, Any]] = [("document_date", -1)]

    if query:
        mongo_query["$text"] = {"$search": query}
        projection = {"score": {"$meta": "textScore"}}
        sort = [("score", {"$meta": "textScore"})]

    total = await collection.count_documents(mongo_query)
    cursor = collection.find(mongo_query, projection).sort(sort).skip(skip).limit(limit)
    items = await cursor.to_list(length=limit)
    return items, total
