from __future__ import annotations

import logging

from .config import Settings
from .db import Store
from .models import CanonicalItem, RunResult
from .notifier import TelegramNotifier
from .searx_client import SearxClient
from .utils import canonicalize_url, dedup_key

LOGGER = logging.getLogger(__name__)


def run_monitor(
    store: Store,
    settings: Settings,
    monitor_id: int,
    *,
    trigger: str,
    searx_client: SearxClient | None = None,
    notifier: TelegramNotifier | None = None,
) -> RunResult:
    monitor = store.get_monitor(monitor_id)
    if monitor is None:
        return RunResult(run_id=0, status="failed", error=f"Monitor {monitor_id} not found")
    if not monitor.enabled:
        return RunResult(run_id=0, status="failed", error=f"Monitor {monitor_id} is disabled")

    run_id = store.start_run(monitor_id, trigger)
    fetched = 0
    new_items = 0
    duplicates = 0

    try:
        if searx_client is None:
            if not settings.searxng_base_url:
                raise RuntimeError("SEARXNG_BASE_URL is required")
            searx_client = SearxClient(settings.searxng_base_url, settings.searxng_api_key)
        if notifier is None:
            notifier = TelegramNotifier(settings.telegram_bot_token)

        hits = searx_client.search(monitor.effective_query)
        fetched = len(hits)

        for hit in hits:
            store.add_raw_hit(run_id, hit, payload=hit.model_dump(mode="json"))
            c_url = canonicalize_url(hit.url)
            if store.has_canonical(monitor_id, c_url):
                duplicates += 1
                continue

            item = store.add_canonical_item(
                CanonicalItem(
                    monitor_id=monitor_id,
                    canonical_url=c_url,
                    title=hit.title,
                    snippet=hit.snippet,
                    published_at=hit.published_at,
                    dedup_key=dedup_key(c_url),
                    source=hit.source,
                )
            )
            if item.id is None:
                raise RuntimeError("Canonical item was not persisted")
            reason = (
                f"New result for monitor '{monitor.title}' "
                f"(city={monitor.city}, topic={monitor.topic})"
            )
            message = _format_message(item.title, item.source, item.canonical_url, reason)
            attempt = notifier.send_message(monitor.tg_chat_id, message)
            if attempt.status == "failed":
                LOGGER.warning(
                    "telegram delivery failed for monitor=%s item=%s error=%s",
                    monitor_id,
                    item.id,
                    attempt.error,
                )
                print(message)

            store.add_notification(
                run_id=run_id,
                monitor_id=monitor_id,
                canonical_item_id=item.id,
                channel="telegram",
                payload={
                    "chat_id": monitor.tg_chat_id,
                    "message": message,
                    "item": item.model_dump(mode="json"),
                },
                status=attempt.status,
                error=attempt.error,
                reason=reason,
            )
            new_items += 1

        store.finish_run(
            run_id,
            status="completed",
            fetched=fetched,
            new_items=new_items,
            duplicates=duplicates,
            error=None,
        )
        return RunResult(
            run_id=run_id,
            fetched=fetched,
            new_items=new_items,
            duplicates=duplicates,
            status="completed",
        )

    except Exception as exc:  # noqa: BLE001
        store.finish_run(
            run_id,
            status="failed",
            fetched=fetched,
            new_items=new_items,
            duplicates=duplicates,
            error=str(exc),
        )
        LOGGER.exception("monitor run failed: monitor_id=%s run_id=%s", monitor_id, run_id)
        return RunResult(
            run_id=run_id,
            fetched=fetched,
            new_items=new_items,
            duplicates=duplicates,
            status="failed",
            error=str(exc),
        )


def _format_message(title: str, source: str, canonical_url: str, reason: str) -> str:
    return (
        f"[PAIP] New event\n"
        f"Title: {title}\n"
        f"Source: {source}\n"
        f"URL: {canonical_url}\n"
        f"Reason: {reason}"
    )
