from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection


def _oid(value: str | ObjectId) -> ObjectId:
    return value if isinstance(value, ObjectId) else ObjectId(value)


async def create_job(collection: AsyncIOMotorCollection, source_file_id: str) -> str:
    doc = {
        "source_file_id": _oid(source_file_id),
        "status": "pending",
        "progress_pct": 0,
        "error": None,
        "started_at": datetime.now(timezone.utc),
        "completed_at": None,
    }
    result = await collection.insert_one(doc)
    return str(result.inserted_id)


async def get_job(collection: AsyncIOMotorCollection, job_id: str) -> dict[str, Any] | None:
    return await collection.find_one({"_id": _oid(job_id)})


async def get_job_by_source_file(
    collection: AsyncIOMotorCollection,
    source_file_id: str,
) -> dict[str, Any] | None:
    return await collection.find_one({"source_file_id": _oid(source_file_id)}, sort=[("started_at", -1)])


async def update_job(
    collection: AsyncIOMotorCollection,
    job_id: str,
    *,
    status: str | None = None,
    progress_pct: int | None = None,
    error: str | None = None,
    completed: bool = False,
) -> None:
    update: dict[str, Any] = {}
    if status is not None:
        update["status"] = status
    if progress_pct is not None:
        update["progress_pct"] = progress_pct
    if error is not None:
        update["error"] = error
    if completed:
        update["completed_at"] = datetime.now(timezone.utc)
    if update:
        await collection.update_one({"_id": _oid(job_id)}, {"$set": update})
