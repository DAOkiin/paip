from __future__ import annotations

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, Field, model_validator


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


class EventClaim(BaseModel):
    id: int | None = None
    run_id: int
    monitor_id: int
    source_hit_id: int | None = None
    source_url: str = Field(min_length=1)
    source_name: str = Field(min_length=1)
    title: str = Field(min_length=1)
    city: str = Field(min_length=1)
    venue: str = Field(min_length=1)
    start_at: datetime | None = None
    start_date: date | None = None
    extracted_at: datetime
    confidence: float = Field(ge=0.0, le=1.0)
    raw_payload: dict[str, Any] = Field(default_factory=dict)
    event_key: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_dates(self) -> "EventClaim":
        if self.start_at is None and self.start_date is None:
            raise ValueError("Either start_at or start_date must be provided")
        if self.start_date is None and self.start_at is not None:
            self.start_date = self.start_at.date()
        return self


class Event(BaseModel):
    id: int | None = None
    monitor_id: int
    event_key: str
    title: str
    city: str
    venue: str
    start_at: datetime | None = None
    start_date: date
    source_url: str
    source_name: str
    extracted_at: datetime
    confidence: float = Field(ge=0.0, le=1.0)
    created_at: datetime | None = None
    updated_at: datetime | None = None


class RunResult(BaseModel):
    run_id: int
    fetched_sources: int = 0
    claims_extracted: int = 0
    new_events: int = 0
    updated_events: int = 0
    duplicates: int = 0
    unsupported_sources: int = 0
    status: str
    error: str | None = None


class HistoryRecord(BaseModel):
    created_at: datetime
    source_name: str
    source_url: str
    reason: str
    status: str
    title: str
    city: str
    venue: str
    start_date: date
    error: str | None = None
