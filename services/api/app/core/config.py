from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache

from app import __version__


def _split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


@dataclass(frozen=True)
class Settings:
    app_env: str
    api_host: str
    api_port: int
    cors_origins: list[str]
    database_url: str
    llm_provider: str
    llm_api_key: str
    llm_model: str
    version: str = __version__


@lru_cache
def get_settings() -> Settings:
    return Settings(
        app_env=os.getenv("APP_ENV", "local"),
        api_host=os.getenv("API_HOST", "127.0.0.1"),
        api_port=int(os.getenv("API_PORT", "8000")),
        cors_origins=_split_csv(os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")),
        database_url=os.getenv("DATABASE_URL", "sqlite:///./simhire.db"),
        llm_provider=os.getenv("LLM_PROVIDER", "mock"),
        llm_api_key=os.getenv("LLM_API_KEY", ""),
        llm_model=os.getenv("LLM_MODEL", ""),
    )
