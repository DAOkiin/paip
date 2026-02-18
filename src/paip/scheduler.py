from __future__ import annotations

import logging
import time
from datetime import datetime, timezone

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler

from .config import Settings
from .db import Store
from .notifier import TelegramNotifier
from .pipeline import run_monitor
from .searx_client import SearxClient

LOGGER = logging.getLogger(__name__)


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
    monitors = store.list_monitors(enabled_only=True)
    for monitor in monitors:
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
    monitors = store.list_monitors(enabled_only=True)
    for monitor in monitors:
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
