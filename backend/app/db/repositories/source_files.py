from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection


def _oid(value: str | ObjectId) -> ObjectId:
    return value if isinstance(value, ObjectId) else ObjectId(value)


async def find_by_sha256(collection: AsyncIOMotorCollection, sha256: str) -> dict[str, Any] | None:
    return await collection.find_one({"sha256": sha256})


async def insert_source_file(
    collection: AsyncIOMotorCollection,
    *,
    filename: str,
    storage_path: str,
    sha256: str,
    status: str = "uploaded",
) -> str:
    doc = {
        "filename": filename,
        "storage_path": storage_path,
        "sha256": sha256,
        "uploaded_at": datetime.now(timezone.utc),
        "status": status,
    }
    result = await collection.insert_one(doc)
    return str(result.inserted_id)


async def get_source_file(collection: AsyncIOMotorCollection, source_file_id: str) -> dict[str, Any] | None:
    return await collection.find_one({"_id": _oid(source_file_id)})


async def update_source_file_status(
    collection: AsyncIOMotorCollection,
    source_file_id: str,
    status: str,
) -> None:
    await collection.update_one({"_id": _oid(source_file_id)}, {"$set": {"status": status}})
