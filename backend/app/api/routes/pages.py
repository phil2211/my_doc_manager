from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.client import get_database
from app.db.repositories import pages as pages_repo

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
