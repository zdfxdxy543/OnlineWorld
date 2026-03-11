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


def _parse_probability(value: str | None, *, default: float) -> float:
    if value is None:
        return default
    try:
        parsed = float(value)
    except ValueError:
        return default
    return max(0.0, min(1.0, parsed))


@dataclass(frozen=True)
class Settings:
    app_name: str = "OnlineWorld Backend"
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    api_prefix: str = "/api/v1"
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./onlineworld.db")
    llm_provider: str = os.getenv("LLM_PROVIDER", "siliconflow")
    llm_model: str = os.getenv("LLM_MODEL", "story-seed-v1")
    siliconflow_api_key: str = os.getenv("SILICONFLOW_API_KEY", "sk-vxnqqulpbrduxkhpxmsfebvhyvwdxjebofqcjtdsjrggebvv")
    siliconflow_base_url: str = os.getenv("SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1")
    siliconflow_planner_model: str = os.getenv("SILICONFLOW_PLANNER_MODEL", "Pro/deepseek-ai/DeepSeek-V3.2")
    scheduler_new_actor_probability: float = _parse_probability(
        os.getenv("SCHEDULER_NEW_ACTOR_PROBABILITY"), default=0.30
    )
    cors_origins: tuple[str, ...] = _parse_origins(os.getenv("CORS_ORIGINS"))


def get_settings() -> Settings:
    return Settings()
