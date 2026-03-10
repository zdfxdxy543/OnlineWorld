from __future__ import annotations

import os
from dataclasses import dataclass


def _parse_origins(value: str | None) -> tuple[str, ...]:
    if not value:
        return (
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        )

    return tuple(origin.strip() for origin in value.split(",") if origin.strip())


@dataclass(frozen=True)
class Settings:
    app_name: str = "OnlineWorld Backend"
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    api_prefix: str = "/api/v1"
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./onlineworld.db")
    llm_provider: str = os.getenv("LLM_PROVIDER", "mock")
    llm_model: str = os.getenv("LLM_MODEL", "story-seed-v1")
    cors_origins: tuple[str, ...] = _parse_origins(os.getenv("CORS_ORIGINS"))


def get_settings() -> Settings:
    return Settings()
