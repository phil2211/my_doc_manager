from __future__ import annotations

import hashlib
from pathlib import Path

from fastapi import UploadFile
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.config import get_settings
from app.db.repositories import processing_jobs as jobs_repo
from app.db.repositories import source_files as source_files_repo
from app.services.pdf_utils import ensure_storage_dir


async def save_upload_and_create_records(
    db: AsyncIOMotorDatabase,
    upload: UploadFile,
) -> tuple[str, str, bool]:
    content = await upload.read()
    sha256 = hashlib.sha256(content).hexdigest()
    filename = upload.filename or "upload.pdf"

    existing = await source_files_repo.find_by_sha256(db.source_files, sha256)
    if existing:
        job = await jobs_repo.get_job_by_source_file(db.source_files, str(existing["_id"]))
        if job:
            return str(existing["_id"]), str(job["_id"]), True
        job_id = await jobs_repo.create_job(db.processing_jobs, str(existing["_id"]))
        return str(existing["_id"]), job_id, True

    source_file_id = await source_files_repo.insert_source_file(
        db.source_files,
        filename=filename,
        storage_path="",
        sha256=sha256,
    )
    storage_dir = ensure_storage_dir(source_file_id)
    pdf_path = storage_dir / "original.pdf"
    pdf_path.write_bytes(content)

    await source_files_repo.update_source_file_status(
        db.source_files,
        source_file_id,
        "uploaded",
    )
    await db.source_files.update_one(
        {"_id": source_files_repo._oid(source_file_id)},
        {"$set": {"storage_path": str(pdf_path)}},
    )

    job_id = await jobs_repo.create_job(db.processing_jobs, source_file_id)
    return source_file_id, job_id, False


def get_pdf_path(source_file: dict) -> Path:
    return Path(source_file["storage_path"])
