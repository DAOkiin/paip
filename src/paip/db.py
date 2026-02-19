from __future__ import annotations

import logging
from datetime import date, datetime, timezone
from typing import Any

from sqlalchemy import (
    JSON,
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    create_engine,
    select,
)
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship

from .models import Event, EventClaim, HistoryRecord, MonitorSpec, SearchHit

SCHEMA_VERSION = 2
QUERY_LOGGER = logging.getLogger("paip.query")


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _log_query(query_id: str, **fields: Any) -> None:
    parts = [f"query_id={query_id}"]
    for key, value in fields.items():
        parts.append(f"{key}={value!r}")
    QUERY_LOGGER.info(" ".join(parts))


class Base(DeclarativeBase):
    pass


class MonitorRow(Base):
    __tablename__ = "monitors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    city: Mapped[str] = mapped_column(String(255), nullable=False)
    topic: Mapped[str] = mapped_column(String(255), nullable=False)
    query: Mapped[str] = mapped_column(String(1024), nullable=False)
    interval_min: Mapped[int] = mapped_column(Integer, nullable=False)
    tg_chat_id: Mapped[str] = mapped_column(String(128), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

    runs: Mapped[list["RunRow"]] = relationship(back_populates="monitor")


class RunRow(Base):
    __tablename__ = "runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    monitor_id: Mapped[int] = mapped_column(ForeignKey("monitors.id"), nullable=False)
    trigger: Mapped[str] = mapped_column(String(32), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="running")
    fetched_sources: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    claims_extracted: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    new_events: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    updated_events: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    duplicates: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    unsupported_sources: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)

    monitor: Mapped[MonitorRow] = relationship(back_populates="runs")


class SourceHitRow(Base):
    __tablename__ = "source_hits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("runs.id"), nullable=False)
    monitor_id: Mapped[int] = mapped_column(ForeignKey("monitors.id"), nullable=False)
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    title: Mapped[str] = mapped_column(String(1024), nullable=False)
    snippet: Mapped[str] = mapped_column(Text, nullable=False, default="")
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    source: Mapped[str] = mapped_column(String(128), nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)


class EventClaimRow(Base):
    __tablename__ = "event_claims"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("runs.id"), nullable=False)
    monitor_id: Mapped[int] = mapped_column(ForeignKey("monitors.id"), nullable=False)
    source_hit_id: Mapped[int | None] = mapped_column(ForeignKey("source_hits.id"), nullable=True)
    source_url: Mapped[str] = mapped_column(String(2048), nullable=False, default="")
    source_name: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    title: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    city: Mapped[str | None] = mapped_column(String(255), nullable=True)
    venue: Mapped[str | None] = mapped_column(String(512), nullable=True)
    start_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    extracted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    event_key: Mapped[str | None] = mapped_column(String(64), nullable=True)
    validation_status: Mapped[str] = mapped_column(String(32), nullable=False, default="valid")
    validation_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)


class EventRow(Base):
    __tablename__ = "events"
    __table_args__ = (UniqueConstraint("monitor_id", "event_key", name="uq_monitor_event_key"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    monitor_id: Mapped[int] = mapped_column(ForeignKey("monitors.id"), nullable=False)
    event_key: Mapped[str] = mapped_column(String(64), nullable=False)
    title: Mapped[str] = mapped_column(String(1024), nullable=False)
    city: Mapped[str] = mapped_column(String(255), nullable=False)
    venue: Mapped[str] = mapped_column(String(512), nullable=False)
    start_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    source_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    source_name: Mapped[str] = mapped_column(String(255), nullable=False)
    extracted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)


class NotificationRow(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("runs.id"), nullable=False)
    monitor_id: Mapped[int] = mapped_column(ForeignKey("monitors.id"), nullable=False)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"), nullable=False)
    channel: Mapped[str] = mapped_column(String(64), nullable=False, default="telegram")
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    reason: Mapped[str] = mapped_column(String(512), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)


Index("idx_runs_monitor_started", RunRow.monitor_id, RunRow.started_at)
Index("idx_source_hits_monitor_created", SourceHitRow.monitor_id, SourceHitRow.created_at)
Index("idx_events_monitor_created", EventRow.monitor_id, EventRow.created_at)
Index("idx_events_monitor_source", EventRow.monitor_id, EventRow.source_url)
Index("idx_notifications_monitor_created", NotificationRow.monitor_id, NotificationRow.created_at)


class Store:
    def __init__(self, db_url: str):
        self.engine: Engine = create_engine(
            db_url,
            future=True,
            connect_args={"check_same_thread": False},
        )
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        _log_query(
            "Schema.EnsureVersion",
            dialect=self.engine.dialect.name,
            target_schema_version=SCHEMA_VERSION,
        )
        if self.engine.dialect.name != "sqlite":
            Base.metadata.create_all(self.engine)
            return

        with self.engine.begin() as conn:
            version = int(conn.exec_driver_sql("PRAGMA user_version").scalar_one())
            if version != SCHEMA_VERSION:
                for table in (
                    "notifications",
                    "events",
                    "event_claims",
                    "source_hits",
                    "canonical_items",
                    "raw_hits",
                    "runs",
                    "monitors",
                ):
                    conn.exec_driver_sql(f"DROP TABLE IF EXISTS {table}")
                Base.metadata.create_all(conn)
                conn.exec_driver_sql(f"PRAGMA user_version = {SCHEMA_VERSION}")
                return
            Base.metadata.create_all(conn)

    def add_monitor(self, spec: MonitorSpec) -> MonitorSpec:
        _log_query(
            "Monitor.Create",
            city=spec.city,
            topic=spec.topic,
            interval_min=spec.interval_min,
            enabled=spec.enabled,
        )
        row = MonitorRow(
            title=spec.title,
            city=spec.city,
            topic=spec.topic,
            query=spec.query,
            interval_min=spec.interval_min,
            tg_chat_id=spec.tg_chat_id,
            enabled=spec.enabled,
        )
        with Session(self.engine) as session:
            session.add(row)
            session.commit()
            session.refresh(row)
        return MonitorSpec(
            id=row.id,
            title=row.title,
            city=row.city,
            topic=row.topic,
            query=row.query,
            interval_min=row.interval_min,
            tg_chat_id=row.tg_chat_id,
            enabled=row.enabled,
        )

    def list_monitors(
        self,
        enabled_only: bool = False,
        limit: int = 200,
        offset: int = 0,
    ) -> list[MonitorSpec]:
        limit = max(1, limit)
        offset = max(0, offset)
        _log_query("Monitor.List", enabled_only=enabled_only, limit=limit, offset=offset)
        stmt = select(MonitorRow).order_by(MonitorRow.id)
        if enabled_only:
            stmt = stmt.where(MonitorRow.enabled.is_(True))
        stmt = stmt.limit(limit).offset(offset)
        with Session(self.engine) as session:
            rows = session.scalars(stmt).all()
        return [
            MonitorSpec(
                id=row.id,
                title=row.title,
                city=row.city,
                topic=row.topic,
                query=row.query,
                interval_min=row.interval_min,
                tg_chat_id=row.tg_chat_id,
                enabled=row.enabled,
            )
            for row in rows
        ]

    def get_monitor(self, monitor_id: int) -> MonitorSpec | None:
        _log_query("Monitor.GetById", monitor_id=monitor_id)
        with Session(self.engine) as session:
            row = session.get(MonitorRow, monitor_id)
            if row is None:
                return None
            return MonitorSpec(
                id=row.id,
                title=row.title,
                city=row.city,
                topic=row.topic,
                query=row.query,
                interval_min=row.interval_min,
                tg_chat_id=row.tg_chat_id,
                enabled=row.enabled,
            )

    def start_run(self, monitor_id: int, trigger: str) -> int:
        _log_query("Run.Start", monitor_id=monitor_id, trigger=trigger)
        row = RunRow(monitor_id=monitor_id, trigger=trigger, status="running")
        with Session(self.engine) as session:
            session.add(row)
            session.commit()
            session.refresh(row)
            return row.id

    def finish_run(
        self,
        run_id: int,
        *,
        status: str,
        fetched_sources: int,
        claims_extracted: int,
        new_events: int,
        updated_events: int,
        duplicates: int,
        unsupported_sources: int,
        error: str | None,
    ) -> None:
        _log_query(
            "Run.Finish",
            run_id=run_id,
            status=status,
            fetched_sources=fetched_sources,
            claims_extracted=claims_extracted,
            new_events=new_events,
            updated_events=updated_events,
            duplicates=duplicates,
            unsupported_sources=unsupported_sources,
            error=error,
        )
        with Session(self.engine) as session:
            row = session.get(RunRow, run_id)
            if row is None:
                return
            row.status = status
            row.fetched_sources = fetched_sources
            row.claims_extracted = claims_extracted
            row.new_events = new_events
            row.updated_events = updated_events
            row.duplicates = duplicates
            row.unsupported_sources = unsupported_sources
            row.error = error
            row.finished_at = now_utc()
            session.commit()

    def add_source_hit(
        self,
        run_id: int,
        monitor_id: int,
        hit: SearchHit,
        payload: dict[str, Any],
    ) -> int:
        _log_query(
            "SourceHit.Create",
            run_id=run_id,
            monitor_id=monitor_id,
            source=hit.source,
            url=hit.url,
        )
        row = SourceHitRow(
            run_id=run_id,
            monitor_id=monitor_id,
            url=hit.url,
            title=hit.title,
            snippet=hit.snippet,
            published_at=hit.published_at,
            source=hit.source,
            payload=payload,
        )
        with Session(self.engine) as session:
            session.add(row)
            session.commit()
            session.refresh(row)
            return row.id

    def add_event_claim(self, claim: EventClaim, *, validation_status: str = "valid") -> int:
        _log_query(
            "EventClaim.Create",
            run_id=claim.run_id,
            monitor_id=claim.monitor_id,
            source_url=claim.source_url,
            validation_status=validation_status,
        )
        row = EventClaimRow(
            run_id=claim.run_id,
            monitor_id=claim.monitor_id,
            source_hit_id=claim.source_hit_id,
            source_url=claim.source_url,
            source_name=claim.source_name,
            title=claim.title,
            city=claim.city,
            venue=claim.venue,
            start_at=claim.start_at,
            start_date=claim.start_date,
            extracted_at=claim.extracted_at,
            confidence=claim.confidence,
            event_key=claim.event_key,
            validation_status=validation_status,
            payload=_to_jsonable(claim.raw_payload),
        )
        with Session(self.engine) as session:
            session.add(row)
            session.commit()
            session.refresh(row)
            return row.id

    def add_invalid_event_claim(
        self,
        *,
        run_id: int,
        monitor_id: int,
        source_hit_id: int | None,
        payload: dict[str, Any],
        error: str,
    ) -> int:
        _log_query(
            "EventClaim.CreateInvalid",
            run_id=run_id,
            monitor_id=monitor_id,
            source_hit_id=source_hit_id,
            error=error,
        )
        row = EventClaimRow(
            run_id=run_id,
            monitor_id=monitor_id,
            source_hit_id=source_hit_id,
            source_url=str(payload.get("source_url") or ""),
            source_name=str(payload.get("source_name") or ""),
            title=_as_optional_text(payload.get("title")),
            city=_as_optional_text(payload.get("city")),
            venue=_as_optional_text(payload.get("venue")),
            start_at=payload.get("start_at") if isinstance(payload.get("start_at"), datetime) else None,
            start_date=payload.get("start_date") if isinstance(payload.get("start_date"), date) else None,
            extracted_at=(
                payload.get("extracted_at") if isinstance(payload.get("extracted_at"), datetime) else None
            ),
            confidence=_as_optional_float(payload.get("confidence")),
            event_key=_as_optional_text(payload.get("event_key")),
            validation_status="invalid",
            validation_error=error,
            payload=_to_jsonable(payload),
        )
        with Session(self.engine) as session:
            session.add(row)
            session.commit()
            session.refresh(row)
            return row.id

    def get_event_by_key(self, monitor_id: int, event_key: str) -> Event | None:
        _log_query("Event.GetByKey", monitor_id=monitor_id, event_key=event_key)
        stmt = (
            select(EventRow)
            .where(EventRow.monitor_id == monitor_id)
            .where(EventRow.event_key == event_key)
            .limit(1)
        )
        with Session(self.engine) as session:
            row = session.scalar(stmt)
        if row is None:
            return None
        return _row_to_event(row)

    def get_event_by_source_url(self, monitor_id: int, source_url: str) -> Event | None:
        _log_query(
            "Event.GetLatestBySourceUrl",
            monitor_id=monitor_id,
            source_url=source_url,
        )
        stmt = (
            select(EventRow)
            .where(EventRow.monitor_id == monitor_id)
            .where(EventRow.source_url == source_url)
            .order_by(EventRow.updated_at.desc())
            .limit(1)
        )
        with Session(self.engine) as session:
            row = session.scalar(stmt)
        if row is None:
            return None
        return _row_to_event(row)

    def create_event(self, claim: EventClaim) -> Event:
        if claim.start_date is None:
            raise ValueError("Claim start_date is required to create event")
        _log_query(
            "Event.Create",
            monitor_id=claim.monitor_id,
            event_key=claim.event_key,
            source_url=claim.source_url,
        )
        row = EventRow(
            monitor_id=claim.monitor_id,
            event_key=claim.event_key,
            title=claim.title,
            city=claim.city,
            venue=claim.venue,
            start_at=claim.start_at,
            start_date=claim.start_date,
            source_url=claim.source_url,
            source_name=claim.source_name,
            extracted_at=claim.extracted_at,
            confidence=claim.confidence,
        )
        with Session(self.engine) as session:
            session.add(row)
            session.commit()
            session.refresh(row)
            return _row_to_event(row)

    def update_event_from_claim(self, event_id: int, claim: EventClaim) -> tuple[Event, bool]:
        _log_query(
            "Event.UpdateFromClaim",
            event_id=event_id,
            monitor_id=claim.monitor_id,
            event_key=claim.event_key,
        )
        with Session(self.engine) as session:
            row = session.get(EventRow, event_id)
            if row is None:
                raise ValueError(f"Event {event_id} not found")

            changed = False
            for attr, value in (
                ("event_key", claim.event_key),
                ("title", claim.title),
                ("city", claim.city),
                ("venue", claim.venue),
                ("start_at", claim.start_at),
                ("start_date", claim.start_date),
                ("source_url", claim.source_url),
                ("source_name", claim.source_name),
            ):
                if getattr(row, attr) != value:
                    setattr(row, attr, value)
                    changed = True

            if changed:
                row.extracted_at = claim.extracted_at
                row.confidence = claim.confidence
                row.updated_at = now_utc()
            session.commit()
            session.refresh(row)
            return _row_to_event(row), changed

    def add_notification(
        self,
        *,
        run_id: int,
        monitor_id: int,
        event_id: int,
        channel: str,
        payload: dict[str, Any],
        status: str,
        error: str | None,
        reason: str,
    ) -> int:
        _log_query(
            "Notification.Create",
            run_id=run_id,
            monitor_id=monitor_id,
            event_id=event_id,
            status=status,
            reason=reason,
        )
        row = NotificationRow(
            run_id=run_id,
            monitor_id=monitor_id,
            event_id=event_id,
            channel=channel,
            payload=payload,
            status=status,
            error=error,
            reason=reason,
        )
        with Session(self.engine) as session:
            session.add(row)
            session.commit()
            session.refresh(row)
            return row.id

    def get_history(self, monitor_id: int, limit: int) -> list[HistoryRecord]:
        limit = max(1, limit)
        _log_query(
            "Notification.GetHistoryByMonitor",
            monitor_id=monitor_id,
            limit=limit,
        )
        stmt = (
            select(NotificationRow, EventRow)
            .join(EventRow, NotificationRow.event_id == EventRow.id)
            .where(NotificationRow.monitor_id == monitor_id)
            .order_by(NotificationRow.created_at.desc())
            .limit(limit)
        )
        with Session(self.engine) as session:
            rows = session.execute(stmt).all()

        return [
            HistoryRecord(
                created_at=n.created_at,
                source_name=e.source_name,
                source_url=e.source_url,
                reason=n.reason,
                status=n.status,
                title=e.title,
                city=e.city,
                venue=e.venue,
                start_date=e.start_date,
                error=n.error,
            )
            for n, e in rows
        ]

    def list_runs(self, monitor_id: int, limit: int = 200, offset: int = 0) -> list[RunRow]:
        limit = max(1, limit)
        offset = max(0, offset)
        _log_query("Run.ListByMonitor", monitor_id=monitor_id, limit=limit, offset=offset)
        stmt = (
            select(RunRow)
            .where(RunRow.monitor_id == monitor_id)
            .order_by(RunRow.id)
            .limit(limit)
            .offset(offset)
        )
        with Session(self.engine) as session:
            return session.scalars(stmt).all()

    def list_notifications(
        self,
        monitor_id: int,
        limit: int = 200,
        offset: int = 0,
    ) -> list[NotificationRow]:
        limit = max(1, limit)
        offset = max(0, offset)
        _log_query("Notification.ListByMonitor", monitor_id=monitor_id, limit=limit, offset=offset)
        stmt = (
            select(NotificationRow)
            .where(NotificationRow.monitor_id == monitor_id)
            .order_by(NotificationRow.id)
            .limit(limit)
            .offset(offset)
        )
        with Session(self.engine) as session:
            return session.scalars(stmt).all()

    def list_events(self, monitor_id: int, limit: int = 20) -> list[Event]:
        limit = max(1, limit)
        _log_query("Event.ListByMonitor", monitor_id=monitor_id, limit=limit)
        stmt = (
            select(EventRow)
            .where(EventRow.monitor_id == monitor_id)
            .order_by(EventRow.updated_at.desc())
            .limit(limit)
        )
        with Session(self.engine) as session:
            rows = session.scalars(stmt).all()
        return [_row_to_event(row) for row in rows]


def _row_to_event(row: EventRow) -> Event:
    return Event(
        id=row.id,
        monitor_id=row.monitor_id,
        event_key=row.event_key,
        title=row.title,
        city=row.city,
        venue=row.venue,
        start_at=row.start_at,
        start_date=row.start_date,
        source_url=row.source_url,
        source_name=row.source_name,
        extracted_at=row.extracted_at,
        confidence=row.confidence,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def _as_optional_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _as_optional_float(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value))
    except ValueError:
        return None


def _to_jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _to_jsonable(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_to_jsonable(v) for v in value]
    if isinstance(value, tuple):
        return [_to_jsonable(v) for v in value]
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    return value
