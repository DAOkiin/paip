from __future__ import annotations

from datetime import datetime, timezone

from paip.config import Settings
from paip.db import Store
from paip.models import MonitorSpec, SearchHit
from paip.notifier import NotificationAttempt
from paip.pipeline import run_monitor
from paip.scheduler import run_scheduler_once_for_tests


class FakeSearxClient:
    def __init__(self, hits: list[SearchHit]):
        self._hits = hits

    def search(self, query: str, limit: int = 20) -> list[SearchHit]:
        return self._hits[:limit]


class BrokenSearxClient:
    def search(self, query: str, limit: int = 20) -> list[SearchHit]:
        raise RuntimeError("searx timeout")


class FakeNotifier:
    def __init__(self, fail: bool = False):
        self.fail = fail
        self.messages: list[tuple[str, str]] = []

    def send_message(self, chat_id: str, text: str) -> NotificationAttempt:
        self.messages.append((chat_id, text))
        if self.fail:
            return NotificationAttempt(status="failed", error="telegram down")
        return NotificationAttempt(status="sent")


def _make_store_and_settings(tmp_path):
    settings = Settings(
        db_path=str(tmp_path / "paip.db"),
        searxng_base_url="http://searx.local",
        telegram_bot_token="token",
    )
    settings.ensure_dirs()
    return Store(settings.db_url), settings


def _add_monitor(store: Store) -> MonitorSpec:
    return store.add_monitor(
        MonitorSpec(
            title="Bangkok events",
            city="Bangkok",
            topic="tech",
            query="events",
            interval_min=1,
            tg_chat_id="123456",
            enabled=True,
        )
    )


def _hit(url: str, title: str = "Event") -> SearchHit:
    return SearchHit(
        url=url,
        title=title,
        snippet="snippet",
        published_at=datetime.now(timezone.utc),
        source="searxng",
    )


def test_add_and_list_monitor(tmp_path):
    store, _ = _make_store_and_settings(tmp_path)
    created = _add_monitor(store)

    monitors = store.list_monitors()
    assert len(monitors) == 1
    assert monitors[0].id == created.id
    assert monitors[0].city == "Bangkok"


def test_manual_run_and_exact_dedup(tmp_path):
    store, settings = _make_store_and_settings(tmp_path)
    monitor = _add_monitor(store)
    hits = [_hit("https://example.com/a"), _hit("https://example.com/b")]

    notifier = FakeNotifier()
    result1 = run_monitor(
        store,
        settings,
        monitor.id or 0,
        trigger="manual",
        searx_client=FakeSearxClient(hits),
        notifier=notifier,
    )
    assert result1.status == "completed"
    assert result1.new_items == 2

    result2 = run_monitor(
        store,
        settings,
        monitor.id or 0,
        trigger="manual",
        searx_client=FakeSearxClient(hits),
        notifier=notifier,
    )
    assert result2.status == "completed"
    assert result2.new_items == 0
    assert result2.duplicates == 2

    notifications = store.list_notifications(monitor.id or 0)
    assert len(notifications) == 2


def test_scheduler_trigger_creates_interval_run(tmp_path):
    store, settings = _make_store_and_settings(tmp_path)
    monitor = _add_monitor(store)

    run_scheduler_once_for_tests(
        store,
        settings,
        wait_seconds=0.4,
        searx_client=FakeSearxClient([_hit("https://example.com/scheduled")]),
        notifier=FakeNotifier(),
    )

    runs = store.list_runs(monitor.id or 0)
    assert runs
    assert runs[-1].trigger == "interval"
    assert runs[-1].status == "completed"


def test_searx_error_sets_failed_run(tmp_path):
    store, settings = _make_store_and_settings(tmp_path)
    monitor = _add_monitor(store)

    result = run_monitor(
        store,
        settings,
        monitor.id or 0,
        trigger="manual",
        searx_client=BrokenSearxClient(),
        notifier=FakeNotifier(),
    )

    assert result.status == "failed"
    assert "searx timeout" in (result.error or "")
    runs = store.list_runs(monitor.id or 0)
    assert runs[-1].status == "failed"


def test_telegram_error_is_recorded_but_run_completes(tmp_path):
    store, settings = _make_store_and_settings(tmp_path)
    monitor = _add_monitor(store)

    result = run_monitor(
        store,
        settings,
        monitor.id or 0,
        trigger="manual",
        searx_client=FakeSearxClient([_hit("https://example.com/new")]),
        notifier=FakeNotifier(fail=True),
    )

    assert result.status == "completed"
    notifications = store.list_notifications(monitor.id or 0)
    assert notifications[-1].status == "failed"
    assert notifications[-1].error == "telegram down"


def test_history_contains_source_time_reason(tmp_path):
    store, settings = _make_store_and_settings(tmp_path)
    monitor = _add_monitor(store)

    run_monitor(
        store,
        settings,
        monitor.id or 0,
        trigger="manual",
        searx_client=FakeSearxClient([_hit("https://example.com/history")]),
        notifier=FakeNotifier(),
    )

    history = store.get_history(monitor.id or 0, limit=10)
    assert history
    first = history[0]
    assert first.source == "searxng"
    assert first.reason
    assert first.created_at
