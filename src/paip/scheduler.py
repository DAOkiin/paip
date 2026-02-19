from __future__ import annotations

import logging
import time
from collections.abc import Iterator
from datetime import datetime, timezone

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler

from .config import Settings
from .db import Store
from .models import MonitorSpec
from .notifier import TelegramNotifier
from .pipeline import run_monitor
from .searx_client import SearxClient

LOGGER = logging.getLogger(__name__)
MONITOR_PAGE_SIZE = 200


def run_scheduler(
    store: Store,
    settings: Settings,
    *,
    searx_client: SearxClient | None = None,
    notifier: TelegramNotifier | None = None,
) -> None:
    scheduler = BlockingScheduler(timezone="UTC")
    _register_interval_jobs(
        scheduler,
        store,
        settings,
        searx_client=searx_client,
        notifier=notifier,
    )
    LOGGER.info("scheduler started with %s jobs", len(scheduler.get_jobs()))
    scheduler.start()


def run_scheduler_once_for_tests(
    store: Store,
    settings: Settings,
    *,
    wait_seconds: float = 0.5,
    searx_client: SearxClient | None = None,
    notifier: TelegramNotifier | None = None,
) -> None:
    scheduler = BackgroundScheduler(timezone="UTC")
    for monitor in _iter_enabled_monitors(store, page_size=MONITOR_PAGE_SIZE):
        scheduler.add_job(
            run_monitor,
            trigger="date",
            run_date=datetime.now(timezone.utc),
            kwargs={
                "store": store,
                "settings": settings,
                "monitor_id": monitor.id,
                "trigger": "interval",
                "searx_client": searx_client,
                "notifier": notifier,
            },
            id=f"monitor-once-{monitor.id}",
            replace_existing=True,
        )
    scheduler.start()
    time.sleep(wait_seconds)
    scheduler.shutdown(wait=True)


def _register_interval_jobs(
    scheduler: BlockingScheduler,
    store: Store,
    settings: Settings,
    *,
    searx_client: SearxClient | None = None,
    notifier: TelegramNotifier | None = None,
) -> None:
    for monitor in _iter_enabled_monitors(store, page_size=MONITOR_PAGE_SIZE):
        scheduler.add_job(
            run_monitor,
            trigger="interval",
            minutes=monitor.interval_min,
            kwargs={
                "store": store,
                "settings": settings,
                "monitor_id": monitor.id,
                "trigger": "interval",
                "searx_client": searx_client,
                "notifier": notifier,
            },
            id=f"monitor-{monitor.id}",
            replace_existing=True,
            coalesce=True,
            max_instances=1,
        )


def _iter_enabled_monitors(store: Store, *, page_size: int) -> Iterator[MonitorSpec]:
    offset = 0
    while True:
        batch = store.list_monitors(enabled_only=True, limit=page_size, offset=offset)
        if not batch:
            return
        for monitor in batch:
            yield monitor
        if len(batch) < page_size:
            return
        offset += page_size
