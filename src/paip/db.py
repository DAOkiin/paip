from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
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

from .models import CanonicalItem, HistoryRecord, MonitorSpec, SearchHit



def now_utc() -> datetime:
    return datetime.now(timezone.utc)


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
    fetched: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    new_items: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    duplicates: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)

    monitor: Mapped[MonitorRow] = relationship(back_populates="runs")


class RawHitRow(Base):
    __tablename__ = "raw_hits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("runs.id"), nullable=False)
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    title: Mapped[str] = mapped_column(String(1024), nullable=False)
    snippet: Mapped[str] = mapped_column(Text, nullable=False, default="")
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    source: Mapped[str] = mapped_column(String(128), nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)


class CanonicalItemRow(Base):
    __tablename__ = "canonical_items"
    __table_args__ = (
        UniqueConstraint("monitor_id", "canonical_url", name="uq_monitor_canonical_url"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    monitor_id: Mapped[int] = mapped_column(ForeignKey("monitors.id"), nullable=False)
    canonical_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    title: Mapped[str] = mapped_column(String(1024), nullable=False)
    snippet: Mapped[str] = mapped_column(Text, nullable=False)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    source: Mapped[str] = mapped_column(String(128), nullable=False)
    dedup_key: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)


class NotificationRow(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("runs.id"), nullable=False)
    monitor_id: Mapped[int] = mapped_column(ForeignKey("monitors.id"), nullable=False)
    canonical_item_id: Mapped[int] = mapped_column(ForeignKey("canonical_items.id"), nullable=False)
    channel: Mapped[str] = mapped_column(String(64), nullable=False, default="telegram")
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    reason: Mapped[str] = mapped_column(String(512), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)


Index("idx_canonical_monitor_created", CanonicalItemRow.monitor_id, CanonicalItemRow.created_at)
Index("idx_notifications_monitor_created", NotificationRow.monitor_id, NotificationRow.created_at)


class Store:
    def __init__(self, db_url: str):
        self.engine: Engine = create_engine(
            db_url,
            future=True,
            connect_args={"check_same_thread": False},
        )
        Base.metadata.create_all(self.engine)

    def add_monitor(self, spec: MonitorSpec) -> MonitorSpec:
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

    def list_monitors(self, enabled_only: bool = False) -> list[MonitorSpec]:
        stmt = select(MonitorRow).order_by(MonitorRow.id)
        if enabled_only:
            stmt = stmt.where(MonitorRow.enabled.is_(True))
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
        fetched: int,
        new_items: int,
        duplicates: int,
        error: str | None,
    ) -> None:
        with Session(self.engine) as session:
            row = session.get(RunRow, run_id)
            if row is None:
                return
            row.status = status
            row.fetched = fetched
            row.new_items = new_items
            row.duplicates = duplicates
            row.error = error
            row.finished_at = now_utc()
            session.commit()

    def add_raw_hit(self, run_id: int, hit: SearchHit, payload: dict[str, Any]) -> int:
        row = RawHitRow(
            run_id=run_id,
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

    def has_canonical(self, monitor_id: int, canonical_url: str) -> bool:
        stmt = (
            select(CanonicalItemRow.id)
            .where(CanonicalItemRow.monitor_id == monitor_id)
            .where(CanonicalItemRow.canonical_url == canonical_url)
            .limit(1)
        )
        with Session(self.engine) as session:
            return session.scalar(stmt) is not None

    def add_canonical_item(self, item: CanonicalItem) -> CanonicalItem:
        row = CanonicalItemRow(
            monitor_id=item.monitor_id,
            canonical_url=item.canonical_url,
            title=item.title,
            snippet=item.snippet,
            published_at=item.published_at,
            source=item.source,
            dedup_key=item.dedup_key,
        )
        with Session(self.engine) as session:
            session.add(row)
            session.commit()
            session.refresh(row)
        item.id = row.id
        item.created_at = row.created_at
        return item

    def add_notification(
        self,
        *,
        run_id: int,
        monitor_id: int,
        canonical_item_id: int,
        channel: str,
        payload: dict[str, Any],
        status: str,
        error: str | None,
        reason: str,
    ) -> int:
        row = NotificationRow(
            run_id=run_id,
            monitor_id=monitor_id,
            canonical_item_id=canonical_item_id,
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
        stmt = (
            select(NotificationRow, CanonicalItemRow)
            .join(CanonicalItemRow, NotificationRow.canonical_item_id == CanonicalItemRow.id)
            .where(NotificationRow.monitor_id == monitor_id)
            .order_by(NotificationRow.created_at.desc())
            .limit(limit)
        )
        with Session(self.engine) as session:
            rows = session.execute(stmt).all()

        return [
            HistoryRecord(
                created_at=n.created_at,
                source=c.source,
                reason=n.reason,
                status=n.status,
                title=c.title,
                canonical_url=c.canonical_url,
                error=n.error,
            )
            for n, c in rows
        ]

    def list_runs(self, monitor_id: int) -> list[RunRow]:
        stmt = select(RunRow).where(RunRow.monitor_id == monitor_id).order_by(RunRow.id)
        with Session(self.engine) as session:
            return session.scalars(stmt).all()

    def list_notifications(self, monitor_id: int) -> list[NotificationRow]:
        stmt = (
            select(NotificationRow)
            .where(NotificationRow.monitor_id == monitor_id)
            .order_by(NotificationRow.id)
        )
        with Session(self.engine) as session:
            return session.scalars(stmt).all()
