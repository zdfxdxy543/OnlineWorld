from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class DatabaseSessionManager:
    database_url: str

    def describe(self) -> dict[str, str]:
        return {
            "database_url": self.database_url,
            "status": "configured",
            "mode": "placeholder",
        }
