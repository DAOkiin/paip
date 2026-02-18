from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class MonitorSpec(BaseModel):
    id: int | None = None
    title: str
    city: str
    topic: str
    query: str
    interval_min: int = Field(ge=1)
    tg_chat_id: str
    enabled: bool = True

    @property
    def effective_query(self) -> str:
        parts = [self.query.strip(), self.city.strip(), self.topic.strip()]
        return " ".join(part for part in parts if part)


class SearchHit(BaseModel):
    url: str
    title: str
    snippet: str = ""
    published_at: datetime | None = None
    source: str = "searxng"


class CanonicalItem(BaseModel):
    id: int | None = None
    monitor_id: int
    canonical_url: str
    title: str
    snippet: str
    published_at: datetime | None = None
    dedup_key: str
    source: str
    created_at: datetime | None = None


class RunResult(BaseModel):
    run_id: int
    fetched: int = 0
    new_items: int = 0
    duplicates: int = 0
    status: str
    error: str | None = None


class HistoryRecord(BaseModel):
    created_at: datetime
    source: str
    reason: str
    status: str
    title: str
    canonical_url: str
    error: str | None = None
