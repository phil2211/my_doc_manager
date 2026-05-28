from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, UploadFile
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.client import get_database
from app.db.repositories import processing_jobs as jobs_repo
from app.db.repositories import source_files as source_files_repo
from app.schemas.documents import JobStatusResponse, UploadResponse
from app.services.ingest import get_pdf_path, save_upload_and_create_records
from app.services.pipeline import ProcessingPipeline

router = APIRouter(prefix="/api/v1/files", tags=["files"])


async def get_db() -> AsyncIOMotorDatabase:
    return get_database()


@router.post("", response_model=UploadResponse)
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile,
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> UploadResponse:
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    source_file_id, job_id, duplicate = await save_upload_and_create_records(db, file)
    source_file = await source_files_repo.get_source_file(db.source_files, source_file_id)
    if source_file is None:
        raise HTTPException(status_code=500, detail="Failed to store uploaded file")

    if not duplicate:
        pipeline = ProcessingPipeline(db)
        background_tasks.add_task(
            pipeline.run,
            source_file_id,
            job_id,
            get_pdf_path(source_file),
        )

    return UploadResponse(
        source_file_id=source_file_id,
        job_id=job_id,
        filename=source_file["filename"],
        duplicate=duplicate,
    )


@router.get("/{source_file_id}/status", response_model=JobStatusResponse)
async def get_file_status(
    source_file_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> JobStatusResponse:
    job = await jobs_repo.get_job_by_source_file(db.processing_jobs, source_file_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobStatusResponse(
        id=str(job["_id"]),
        source_file_id=str(job["source_file_id"]),
        status=job["status"],
        progress_pct=job["progress_pct"],
        error=job.get("error"),
        started_at=job["started_at"],
        completed_at=job.get("completed_at"),
    )
