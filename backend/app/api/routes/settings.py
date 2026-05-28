from __future__ import annotations

from fastapi import APIRouter

from app.core.config import get_settings
from app.schemas.documents import SettingsResponse, SettingsUpdateRequest

router = APIRouter(prefix="/api/v1/settings", tags=["settings"])

_runtime_settings = {}


@router.get("", response_model=SettingsResponse)
async def get_settings_endpoint() -> SettingsResponse:
    settings = get_settings()
    overrides = _runtime_settings
    return SettingsResponse(
        llm_enabled=overrides.get("llm_enabled", settings.llm_enabled),
        llm_base_url=overrides.get("llm_base_url", settings.llm_base_url),
        llm_model=overrides.get("llm_model", settings.llm_model),
        llm_confidence_threshold=overrides.get(
            "llm_confidence_threshold",
            settings.llm_confidence_threshold,
        ),
        ocr_dpi=overrides.get("ocr_dpi", settings.ocr_dpi),
    )


@router.put("", response_model=SettingsResponse)
async def update_settings_endpoint(payload: SettingsUpdateRequest) -> SettingsResponse:
    settings = get_settings()
    updates = payload.model_dump(exclude_none=True)
    _runtime_settings.update(updates)

    for key, value in updates.items():
        if hasattr(settings, key):
            object.__setattr__(settings, key, value)

    return await get_settings_endpoint()
