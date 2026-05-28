from __future__ import annotations

from pathlib import Path

import fitz
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, Response
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.client import get_database
from app.db.repositories import pages as pages_repo
from app.db.repositories import source_files as source_files_repo
from app.services.ingest import get_pdf_path
from app.services.pdf_utils import render_page_to_image

PREVIEW_DPI = 150

router = APIRouter(prefix="/api/v1/pages", tags=["pages"])


async def get_db() -> AsyncIOMotorDatabase:
    return get_database()


@router.get("/{page_id}/thumbnail")
async def get_page_thumbnail(
    page_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    page = await db.pages.find_one({"_id": pages_repo._oid(page_id)})
    if page is None:
        raise HTTPException(status_code=404, detail="Page not found")

    thumbnail_path = page.get("thumbnail_path")
    if not thumbnail_path or not Path(thumbnail_path).exists():
        raise HTTPException(status_code=404, detail="Thumbnail not found")

    return FileResponse(path=thumbnail_path, media_type="image/png")


@router.get("/{page_id}/preview")
async def get_page_preview(
    page_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    page = await db.pages.find_one({"_id": pages_repo._oid(page_id)})
    if page is None:
        raise HTTPException(status_code=404, detail="Page not found")

    source_file = await source_files_repo.get_source_file(
        db.source_files,
        str(page["source_file_id"]),
    )
    if source_file is None:
        raise HTTPException(status_code=404, detail="Source file not found")

    pdf_path = get_pdf_path(source_file)
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="PDF not found")

    page_number = int(page["page_number"])
    doc = fitz.open(pdf_path)
    try:
        if page_number < 1 or page_number > len(doc):
            raise HTTPException(status_code=404, detail="Page not found in PDF")
        image_bytes = render_page_to_image(doc[page_number - 1], PREVIEW_DPI)
    finally:
        doc.close()

    return Response(content=image_bytes, media_type="image/png")
