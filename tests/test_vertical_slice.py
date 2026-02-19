from __future__ import annotations

import logging
from datetime import date, datetime, timezone

from paip.config import Settings
from paip.db import Store
from paip.extractors import ExtractorRegistry, StaticHtmlEventbriteExtractor
from paip.models import EventClaim, MonitorSpec, SearchHit
from paip.notifier import NotificationAttempt
from paip.pipeline import run_monitor
from paip.scheduler import run_scheduler_once_for_tests
from paip.utils import build_event_key, normalize_text


class FakeSearxClient:
    def __init__(self, hits: list[SearchHit]):
        self._hits = hits

    def search(self, query: str, limit: int = 20) -> list[SearchHit]:  # noqa: ARG002
        return self._hits[:limit]


class BrokenSearxClient:
    def search(self, query: str, limit: int = 20) -> list[SearchHit]:  # noqa: ARG002
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


class URLMappedExtractor:
    name = "url_mapped"

    def __init__(self, claims_by_url: dict[str, list[dict]]):
        self.claims_by_url = claims_by_url

    def supports(self, url: str) -> bool:
        return url in self.claims_by_url

    def extract(self, hit: SearchHit, monitor: MonitorSpec) -> list[dict]:  # noqa: ARG002
        return [dict(item) for item in self.claims_by_url.get(hit.url, [])]


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


def _claim(
    *,
    source_url: str,
    title: str = "Bangkok AI Meetup",
    city: str = "Bangkok",
    venue: str = "True Digital Park",
    start_date: date = date(2026, 3, 1),
) -> dict:
    return {
        "source_url": source_url,
        "source_name": "eventbrite.com",
        "title": title,
        "city": city,
        "venue": venue,
        "start_date": start_date,
        "extracted_at": datetime.now(timezone.utc),
        "confidence": 0.9,
        "raw_payload": {"test": True},
    }


def test_normalize_text_and_event_key_stable():
    assert normalize_text("  Bangkok,  AI Meetup!!  ") == "bangkok ai meetup"
    key1 = build_event_key(
        title="Bangkok AI Meetup",
        city="Bangkok",
        venue="True Digital Park",
        start_date=date(2026, 3, 1),
    )
    key2 = build_event_key(
        title="bangkok   ai meetup",
        city="BANGKOK",
        venue="True Digital Park",
        start_date=date(2026, 3, 1),
    )
    assert key1 == key2


def test_event_claim_requires_start_field():
    payload = {
        "run_id": 1,
        "monitor_id": 1,
        "source_url": "https://example.com/event",
        "source_name": "example.com",
        "title": "Event",
        "city": "Bangkok",
        "venue": "Venue",
        "extracted_at": datetime.now(timezone.utc),
        "confidence": 0.8,
        "raw_payload": {},
        "event_key": "k",
    }
    try:
        EventClaim.model_validate(payload)
        assert False, "EventClaim without start should fail"
    except Exception as exc:  # noqa: BLE001
        assert "start_at or start_date" in str(exc)


def test_eventbrite_extractor_parses_valid_page():
    html = """
    <html><head>
    <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@type": "Event",
      "name": "Bangkok AI Meetup",
      "startDate": "2026-03-05T19:00:00+07:00",
      "url": "https://www.eventbrite.com/e/bangkok-ai-meetup",
      "location": {
        "@type": "Place",
        "name": "True Digital Park",
        "address": {"@type": "PostalAddress", "addressLocality": "Bangkok"}
      }
    }
    </script>
    </head><body></body></html>
    """
    extractor = StaticHtmlEventbriteExtractor(html)
    monitor = MonitorSpec(
        title="Bangkok events",
        city="Bangkok",
        topic="tech",
        query="events",
        interval_min=10,
        tg_chat_id="1",
    )
    claims = extractor.extract(_hit("https://www.eventbrite.com/e/bangkok-ai-meetup"), monitor)
    assert len(claims) == 1
    claim = claims[0]
    assert claim["title"] == "Bangkok AI Meetup"
    assert claim["city"] == "Bangkok"
    assert claim["venue"] == "True Digital Park"
    assert claim["start_date"] == date(2026, 3, 5)


def test_eventbrite_extractor_ignores_broken_jsonld():
    html = """
    <html><head>
    <script type="application/ld+json">{ not valid json }</script>
    <script type="application/ld+json">{"@type": "Organization", "name": "No Event"}</script>
    </head><body></body></html>
    """
    extractor = StaticHtmlEventbriteExtractor(html)
    monitor = MonitorSpec(
        title="Bangkok events",
        city="Bangkok",
        topic="tech",
        query="events",
        interval_min=10,
        tg_chat_id="1",
    )
    claims = extractor.extract(_hit("https://www.eventbrite.com/e/no-event"), monitor)
    assert claims == []


def test_add_and_list_monitor(tmp_path):
    store, _ = _make_store_and_settings(tmp_path)
    created = _add_monitor(store)

    monitors = store.list_monitors()
    assert len(monitors) == 1
    assert monitors[0].id == created.id
    assert monitors[0].city == "Bangkok"


def test_list_monitors_supports_pagination(tmp_path):
    store, _ = _make_store_and_settings(tmp_path)
    created = [_add_monitor(store) for _ in range(5)]
    expected_ids = [monitor.id for monitor in created if monitor.id is not None]

    page1 = store.list_monitors(limit=2, offset=0)
    page2 = store.list_monitors(limit=2, offset=2)
    page3 = store.list_monitors(limit=2, offset=4)

    assert [m.id for m in page1] == expected_ids[:2]
    assert [m.id for m in page2] == expected_ids[2:4]
    assert [m.id for m in page3] == expected_ids[4:5]


def test_list_runs_and_notifications_support_pagination(tmp_path):
    store, _ = _make_store_and_settings(tmp_path)
    monitor = _add_monitor(store)
    monitor_id = monitor.id or 0

    seed_run = store.start_run(monitor_id, "manual")
    start_date = date(2026, 3, 1)
    claim = EventClaim.model_validate(
        {
            "run_id": seed_run,
            "monitor_id": monitor_id,
            "source_hit_id": None,
            "source_url": "https://events.local/pagination-seed",
            "source_name": "events.local",
            "title": "Pagination Event",
            "city": "Bangkok",
            "venue": "Venue",
            "start_date": start_date,
            "extracted_at": datetime.now(timezone.utc),
            "confidence": 0.9,
            "raw_payload": {},
            "event_key": build_event_key(
                title="Pagination Event",
                city="Bangkok",
                venue="Venue",
                start_date=start_date,
            ),
        }
    )
    event = store.create_event(claim)
    event_id = event.id or 0

    for idx in range(5):
        run_id = store.start_run(monitor_id, "manual")
        store.add_notification(
            run_id=run_id,
            monitor_id=monitor_id,
            event_id=event_id,
            channel="telegram",
            payload={"idx": idx},
            status="sent",
            error=None,
            reason="new_event",
        )

    all_runs = store.list_runs(monitor_id, limit=20, offset=0)
    all_notifications = store.list_notifications(monitor_id, limit=20, offset=0)

    runs_page1 = store.list_runs(monitor_id, limit=2, offset=0)
    runs_page2 = store.list_runs(monitor_id, limit=2, offset=2)
    notifications_page1 = store.list_notifications(monitor_id, limit=2, offset=0)
    notifications_page2 = store.list_notifications(monitor_id, limit=2, offset=2)

    assert [row.id for row in runs_page1] == [row.id for row in all_runs[:2]]
    assert [row.id for row in runs_page2] == [row.id for row in all_runs[2:4]]
    assert [row.id for row in notifications_page1] == [row.id for row in all_notifications[:2]]
    assert [row.id for row in notifications_page2] == [row.id for row in all_notifications[2:4]]


def test_query_id_logs_are_emitted_for_store_operations(caplog, tmp_path):
    caplog.set_level(logging.INFO, logger="paip.query")
    store, _ = _make_store_and_settings(tmp_path)
    monitor = _add_monitor(store)
    monitor_id = monitor.id or 0

    store.list_monitors(limit=10, offset=0)
    run_id = store.start_run(monitor_id, "manual")
    store.list_runs(monitor_id, limit=10, offset=0)
    store.finish_run(
        run_id,
        status="completed",
        fetched_sources=0,
        claims_extracted=0,
        new_events=0,
        updated_events=0,
        duplicates=0,
        unsupported_sources=0,
        error=None,
    )

    assert "query_id=Monitor.Create" in caplog.text
    assert "query_id=Monitor.List" in caplog.text
    assert "query_id=Run.Start" in caplog.text
    assert "query_id=Run.ListByMonitor" in caplog.text
    assert "query_id=Run.Finish" in caplog.text


def test_pipeline_unsupported_source_does_not_fail(tmp_path):
    store, settings = _make_store_and_settings(tmp_path)
    monitor = _add_monitor(store)

    supported = "https://supported.local/events/1"
    unsupported = "https://unsupported.local/page/1"
    hits = [_hit(supported), _hit(unsupported)]

    result = run_monitor(
        store,
        settings,
        monitor.id or 0,
        trigger="manual",
        searx_client=FakeSearxClient(hits),
        notifier=FakeNotifier(),
        extractor_registry=ExtractorRegistry([URLMappedExtractor({supported: [_claim(source_url=supported)]})]),
    )

    assert result.status == "completed"
    assert result.new_events == 1
    assert result.unsupported_sources == 1


def test_pipeline_rerun_same_events_creates_duplicates(tmp_path):
    store, settings = _make_store_and_settings(tmp_path)
    monitor = _add_monitor(store)
    url = "https://events.local/meetup-1"

    notifier = FakeNotifier()
    result1 = run_monitor(
        store,
        settings,
        monitor.id or 0,
        trigger="manual",
        searx_client=FakeSearxClient([_hit(url)]),
        notifier=notifier,
        extractor_registry=ExtractorRegistry([URLMappedExtractor({url: [_claim(source_url=url)]})]),
    )
    assert result1.new_events == 1
    assert result1.duplicates == 0

    result2 = run_monitor(
        store,
        settings,
        monitor.id or 0,
        trigger="manual",
        searx_client=FakeSearxClient([_hit(url)]),
        notifier=notifier,
        extractor_registry=ExtractorRegistry([URLMappedExtractor({url: [_claim(source_url=url)]})]),
    )
    assert result2.new_events == 0
    assert result2.updated_events == 0
    assert result2.duplicates == 1


def test_pipeline_change_in_date_or_venue_updates_event(tmp_path):
    store, settings = _make_store_and_settings(tmp_path)
    monitor = _add_monitor(store)
    url = "https://events.local/meetup-update"

    run_monitor(
        store,
        settings,
        monitor.id or 0,
        trigger="manual",
        searx_client=FakeSearxClient([_hit(url)]),
        notifier=FakeNotifier(),
        extractor_registry=ExtractorRegistry(
            [URLMappedExtractor({url: [_claim(source_url=url, venue="Venue A", start_date=date(2026, 3, 1))]})]
        ),
    )

    result = run_monitor(
        store,
        settings,
        monitor.id or 0,
        trigger="manual",
        searx_client=FakeSearxClient([_hit(url)]),
        notifier=FakeNotifier(),
        extractor_registry=ExtractorRegistry(
            [URLMappedExtractor({url: [_claim(source_url=url, venue="Venue B", start_date=date(2026, 3, 2))]})]
        ),
    )

    assert result.new_events == 0
    assert result.updated_events == 1
    events = store.list_events(monitor.id or 0)
    assert len(events) == 1
    assert events[0].venue == "Venue B"
    assert events[0].start_date == date(2026, 3, 2)


def test_invalid_claim_is_not_persisted_as_event(tmp_path):
    store, settings = _make_store_and_settings(tmp_path)
    monitor = _add_monitor(store)
    url = "https://events.local/bad-claim"

    result = run_monitor(
        store,
        settings,
        monitor.id or 0,
        trigger="manual",
        searx_client=FakeSearxClient([_hit(url)]),
        notifier=FakeNotifier(),
        extractor_registry=ExtractorRegistry(
            [
                URLMappedExtractor(
                    {
                        url: [
                            {
                                "source_url": url,
                                "source_name": "events.local",
                                "title": "Broken Event",
                                "city": "Bangkok",
                                "start_date": date(2026, 3, 1),
                                "confidence": 0.8,
                            }
                        ]
                    }
                )
            ]
        ),
    )

    assert result.status == "completed"
    assert result.new_events == 0
    assert store.list_events(monitor.id or 0) == []


def test_scheduler_trigger_creates_interval_run(tmp_path):
    store, settings = _make_store_and_settings(tmp_path)
    monitor = _add_monitor(store)

    run_scheduler_once_for_tests(
        store,
        settings,
        wait_seconds=0.4,
        searx_client=FakeSearxClient([]),
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
    url = "https://events.local/tg-fail"

    result = run_monitor(
        store,
        settings,
        monitor.id or 0,
        trigger="manual",
        searx_client=FakeSearxClient([_hit(url)]),
        notifier=FakeNotifier(fail=True),
        extractor_registry=ExtractorRegistry([URLMappedExtractor({url: [_claim(source_url=url)]})]),
    )

    assert result.status == "completed"
    notifications = store.list_notifications(monitor.id or 0)
    assert notifications[-1].status == "failed"
    assert notifications[-1].error == "telegram down"


def test_history_contains_event_level_reason_and_source(tmp_path):
    store, settings = _make_store_and_settings(tmp_path)
    monitor = _add_monitor(store)
    url = "https://events.local/history"

    run_monitor(
        store,
        settings,
        monitor.id or 0,
        trigger="manual",
        searx_client=FakeSearxClient([_hit(url)]),
        notifier=FakeNotifier(),
        extractor_registry=ExtractorRegistry([URLMappedExtractor({url: [_claim(source_url=url)]})]),
    )

    history = store.get_history(monitor.id or 0, limit=10)
    assert history
    first = history[0]
    assert first.source_name == "eventbrite.com"
    assert first.reason == "new_event"
    assert first.title == "Bangkok AI Meetup"
    assert first.start_date == date(2026, 3, 1)
