from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.documents import router as documents_router
from app.api.routes.files import router as files_router
from app.api.routes.pages import router as pages_router
from app.api.routes.settings import router as settings_router
from app.core.config import get_settings
from app.db.client import close_client, get_database
from app.db.indexes import ensure_indexes


@asynccontextmanager
async def lifespan(app: FastAPI):
    db = get_database()
    await ensure_indexes(db)
    yield
    await close_client()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="PDF Scan Metadata Manager", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(files_router)
    app.include_router(documents_router)
    app.include_router(pages_router)
    app.include_router(settings_router)

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
