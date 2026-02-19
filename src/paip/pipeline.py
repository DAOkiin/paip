from __future__ import annotations

import logging
from datetime import date, datetime, timezone
from typing import Any

from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

from .config import Settings
from .db import Store
from .extractors import ExtractorRegistry
from .models import Event, EventClaim, RunResult
from .notifier import TelegramNotifier
from .searx_client import SearxClient
from .utils import build_event_key, canonicalize_url

LOGGER = logging.getLogger(__name__)


def run_monitor(
    store: Store,
    settings: Settings,
    monitor_id: int,
    *,
    trigger: str,
    searx_client: SearxClient | None = None,
    notifier: TelegramNotifier | None = None,
    extractor_registry: ExtractorRegistry | None = None,
) -> RunResult:
    monitor = store.get_monitor(monitor_id)
    if monitor is None:
        return RunResult(run_id=0, status="failed", error=f"Monitor {monitor_id} not found")
    if not monitor.enabled:
        return RunResult(run_id=0, status="failed", error=f"Monitor {monitor_id} is disabled")

    run_id = store.start_run(monitor_id, trigger)
    fetched_sources = 0
    claims_extracted = 0
    new_events = 0
    updated_events = 0
    duplicates = 0
    unsupported_sources = 0

    try:
        if searx_client is None:
            if not settings.searxng_base_url:
                raise RuntimeError("SEARXNG_BASE_URL is required")
            searx_client = SearxClient(settings.searxng_base_url, settings.searxng_api_key)
        if notifier is None:
            notifier = TelegramNotifier(settings.telegram_bot_token)
        if extractor_registry is None:
            extractor_registry = ExtractorRegistry()

        hits = searx_client.search(monitor.effective_query)
        fetched_sources = len(hits)

        for hit in hits:
            source_hit_id = store.add_source_hit(
                run_id,
                monitor_id,
                hit,
                payload=hit.model_dump(mode="json"),
            )
            extractor = extractor_registry.match(hit.url)
            if extractor is None:
                unsupported_sources += 1
                continue

            try:
                raw_claims = extractor.extract(hit, monitor)
            except Exception as exc:  # noqa: BLE001
                LOGGER.warning(
                    "extractor failed for monitor=%s url=%s error=%s",
                    monitor_id,
                    hit.url,
                    exc,
                )
                store.add_invalid_event_claim(
                    run_id=run_id,
                    monitor_id=monitor_id,
                    source_hit_id=source_hit_id,
                    payload={
                        "source_url": canonicalize_url(hit.url),
                        "source_name": hit.source,
                        "title": hit.title,
                        "raw_error": str(exc),
                    },
                    error=f"extractor_error: {exc}",
                )
                continue

            for raw_claim in raw_claims:
                claims_extracted += 1
                candidate = _prepare_claim_candidate(
                    raw_claim=raw_claim,
                    run_id=run_id,
                    monitor_id=monitor_id,
                    source_hit_id=source_hit_id,
                    fallback_source_url=hit.url,
                    fallback_source_name=hit.source,
                    fallback_city=monitor.city,
                )

                try:
                    claim = EventClaim.model_validate(candidate)
                except ValidationError as exc:
                    store.add_invalid_event_claim(
                        run_id=run_id,
                        monitor_id=monitor_id,
                        source_hit_id=source_hit_id,
                        payload=candidate,
                        error=str(exc),
                    )
                    continue

                store.add_event_claim(claim)

                resolution, event = _resolve_event(store, claim)
                if resolution == "duplicate":
                    duplicates += 1
                    continue

                if event.id is None:
                    raise RuntimeError("Resolved event has no id")

                reason = "new_event" if resolution == "new" else "event_updated"
                message = _format_message(event, reason=reason, monitor_title=monitor.title)
                attempt = notifier.send_message(monitor.tg_chat_id, message)
                if attempt.status == "failed":
                    LOGGER.warning(
                        "telegram delivery failed for monitor=%s event=%s error=%s",
                        monitor_id,
                        event.id,
                        attempt.error,
                    )
                    print(message)

                store.add_notification(
                    run_id=run_id,
                    monitor_id=monitor_id,
                    event_id=event.id,
                    channel="telegram",
                    payload={
                        "chat_id": monitor.tg_chat_id,
                        "message": message,
                        "event": event.model_dump(mode="json"),
                    },
                    status=attempt.status,
                    error=attempt.error,
                    reason=reason,
                )

                if resolution == "new":
                    new_events += 1
                else:
                    updated_events += 1

        store.finish_run(
            run_id,
            status="completed",
            fetched_sources=fetched_sources,
            claims_extracted=claims_extracted,
            new_events=new_events,
            updated_events=updated_events,
            duplicates=duplicates,
            unsupported_sources=unsupported_sources,
            error=None,
        )
        return RunResult(
            run_id=run_id,
            fetched_sources=fetched_sources,
            claims_extracted=claims_extracted,
            new_events=new_events,
            updated_events=updated_events,
            duplicates=duplicates,
            unsupported_sources=unsupported_sources,
            status="completed",
        )

    except Exception as exc:  # noqa: BLE001
        store.finish_run(
            run_id,
            status="failed",
            fetched_sources=fetched_sources,
            claims_extracted=claims_extracted,
            new_events=new_events,
            updated_events=updated_events,
            duplicates=duplicates,
            unsupported_sources=unsupported_sources,
            error=str(exc),
        )
        LOGGER.exception("monitor run failed: monitor_id=%s run_id=%s", monitor_id, run_id)
        return RunResult(
            run_id=run_id,
            fetched_sources=fetched_sources,
            claims_extracted=claims_extracted,
            new_events=new_events,
            updated_events=updated_events,
            duplicates=duplicates,
            unsupported_sources=unsupported_sources,
            status="failed",
            error=str(exc),
        )


def _prepare_claim_candidate(
    *,
    raw_claim: dict[str, Any],
    run_id: int,
    monitor_id: int,
    source_hit_id: int,
    fallback_source_url: str,
    fallback_source_name: str,
    fallback_city: str,
) -> dict[str, Any]:
    candidate = dict(raw_claim)

    source_url = str(candidate.get("source_url") or fallback_source_url)
    source_name = str(candidate.get("source_name") or fallback_source_name)
    title = str(candidate.get("title") or "").strip()
    city = str(candidate.get("city") or fallback_city).strip()
    venue = str(candidate.get("venue") or "").strip()

    start_at, start_date = _coerce_start_fields(candidate)
    if start_date is None and start_at is not None:
        start_date = start_at.date()

    event_key = candidate.get("event_key")
    if not event_key and title and city and venue and start_date is not None:
        event_key = build_event_key(
            title=title,
            city=city,
            venue=venue,
            start_date=start_date,
        )

    return {
        "run_id": run_id,
        "monitor_id": monitor_id,
        "source_hit_id": source_hit_id,
        "source_url": canonicalize_url(source_url),
        "source_name": source_name,
        "title": title,
        "city": city,
        "venue": venue,
        "start_at": start_at,
        "start_date": start_date,
        "extracted_at": candidate.get("extracted_at") or datetime.now(timezone.utc),
        "confidence": candidate.get("confidence") if candidate.get("confidence") is not None else 0.0,
        "raw_payload": candidate.get("raw_payload")
        if isinstance(candidate.get("raw_payload"), dict)
        else candidate,
        "event_key": event_key or "",
    }


def _coerce_start_fields(candidate: dict[str, Any]) -> tuple[datetime | None, date | None]:
    start_at_raw = candidate.get("start_at")
    start_date_raw = candidate.get("start_date")

    start_at: datetime | None
    start_date: date | None

    if isinstance(start_at_raw, datetime):
        start_at = start_at_raw
    elif isinstance(start_at_raw, str):
        start_at = _parse_datetime(start_at_raw)
    else:
        start_at = None

    if isinstance(start_date_raw, date) and not isinstance(start_date_raw, datetime):
        start_date = start_date_raw
    elif isinstance(start_date_raw, datetime):
        start_date = start_date_raw.date()
    elif isinstance(start_date_raw, str):
        start_date = _parse_date(start_date_raw)
    else:
        start_date = None

    return start_at, start_date


def _parse_datetime(value: str) -> datetime | None:
    text = value.strip()
    if not text:
        return None
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None


def _parse_date(value: str) -> date | None:
    text = value.strip()
    if not text:
        return None
    try:
        return date.fromisoformat(text)
    except ValueError:
        return None


def _resolve_event(store: Store, claim: EventClaim) -> tuple[str, Event]:
    existing_by_key = store.get_event_by_key(claim.monitor_id, claim.event_key)
    if existing_by_key is not None:
        if existing_by_key.id is None:
            raise RuntimeError("existing event has no id")
        event, changed = store.update_event_from_claim(existing_by_key.id, claim)
        return ("updated", event) if changed else ("duplicate", event)

    existing_by_source = store.get_event_by_source_url(claim.monitor_id, claim.source_url)
    if existing_by_source is not None:
        if existing_by_source.id is None:
            raise RuntimeError("existing event has no id")
        try:
            event, changed = store.update_event_from_claim(existing_by_source.id, claim)
        except IntegrityError:
            conflict = store.get_event_by_key(claim.monitor_id, claim.event_key)
            if conflict is None:
                raise
            return "duplicate", conflict
        return ("updated", event) if changed else ("duplicate", event)

    return "new", store.create_event(claim)


def _format_message(event: Event, *, reason: str, monitor_title: str) -> str:
    date_label = event.start_date.isoformat()
    return (
        f"[PAIP] {reason}\n"
        f"Monitor: {monitor_title}\n"
        f"Title: {event.title}\n"
        f"City: {event.city}\n"
        f"Venue: {event.venue}\n"
        f"Date: {date_label}\n"
        f"Source: {event.source_name}\n"
        f"URL: {event.source_url}"
    )
