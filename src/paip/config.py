from __future__ import annotations

import os
from pathlib import Path

from pydantic import BaseModel, Field, ValidationError, field_validator


class Settings(BaseModel):
    db_path: str = Field(default="./tmp/paip.db")
    searxng_base_url: str | None = None
    searxng_api_key: str | None = None
    telegram_bot_token: str | None = None
    log_level: str = "INFO"

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, value: str) -> str:
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        level = value.upper()
        if level not in allowed:
            raise ValueError(f"Unsupported log level: {value}")
        return level

    @property
    def db_url(self) -> str:
        return f"sqlite:///{self.db_path}"

    def ensure_dirs(self) -> None:
        db_file = Path(self.db_path)
        if db_file.parent and not db_file.parent.exists():
            db_file.parent.mkdir(parents=True, exist_ok=True)

    @classmethod
    def from_env(cls) -> "Settings":
        data = {
            "db_path": os.getenv("PAIP_DB_PATH", "./tmp/paip.db"),
            "searxng_base_url": os.getenv("SEARXNG_BASE_URL"),
            "searxng_api_key": os.getenv("SEARXNG_API_KEY"),
            "telegram_bot_token": os.getenv("TELEGRAM_BOT_TOKEN"),
            "log_level": os.getenv("PAIP_LOG_LEVEL", "INFO"),
        }
        try:
            settings = cls(**data)
        except ValidationError as exc:
            raise SystemExit(str(exc)) from exc
        settings.ensure_dirs()
        return settings
