from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    mongodb_uri: str = "mongodb://admin:changeme@localhost:27017/my_doc_manager?authSource=admin"
    mongodb_db_name: str = "my_doc_manager"
    file_storage_path: str = "./data/files"
    ocr_dpi: int = 300
    scanned_text_threshold: int = 50
    llm_enabled: bool = False
    llm_base_url: str = "http://localhost:11434/v1"
    llm_model: str = "llama3.2"
    llm_api_key: str = "ollama"
    llm_confidence_threshold: float = 0.6
    cors_origins: str = "http://localhost:5173"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
