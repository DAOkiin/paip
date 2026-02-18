from __future__ import annotations

import argparse
import json
import logging
import sys

from .config import Settings
from .db import Store
from .models import MonitorSpec
from .pipeline import run_monitor
from .scheduler import run_scheduler


def main() -> None:
    args = _build_parser().parse_args()
    settings = Settings.from_env()
    logging.basicConfig(
        level=getattr(logging, settings.log_level),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    store = Store(settings.db_url)

    if args.command == "monitor":
        if args.monitor_command == "add":
            spec = MonitorSpec(
                title=args.title,
                city=args.city,
                topic=args.topic,
                query=args.query,
                interval_min=args.interval_min,
                tg_chat_id=args.chat_id,
                enabled=True,
            )
            created = store.add_monitor(spec)
            print(f"Created monitor id={created.id}")
            return

        if args.monitor_command == "list":
            monitors = store.list_monitors()
            if not monitors:
                print("No monitors")
                return
            for monitor in monitors:
                print(
                    f"id={monitor.id} title={monitor.title!r} city={monitor.city!r} "
                    f"topic={monitor.topic!r} interval_min={monitor.interval_min} enabled={monitor.enabled}"
                )
            return

    if args.command == "run":
        if args.run_command == "once":
            result = run_monitor(store, settings, args.monitor_id, trigger="manual")
            print(json.dumps(result.model_dump(), ensure_ascii=False))
            if result.status != "completed":
                raise SystemExit(1)
            return

        if args.run_command == "scheduler":
            print("Starting scheduler (UTC). Press Ctrl+C to stop.")
            run_scheduler(store, settings)
            return

    if args.command == "history":
        history = store.get_history(args.monitor_id, args.limit)
        if not history:
            print("No history")
            return
        for row in history:
            print(
                f"[{row.created_at.isoformat()}] status={row.status} source={row.source} "
                f"title={row.title!r} reason={row.reason!r} url={row.canonical_url}"
                + (f" error={row.error!r}" if row.error else "")
            )
        return

    raise SystemExit("Unsupported command")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="paip")
    subparsers = parser.add_subparsers(dest="command", required=True)

    monitor_parser = subparsers.add_parser("monitor")
    monitor_sub = monitor_parser.add_subparsers(dest="monitor_command", required=True)

    monitor_add = monitor_sub.add_parser("add")
    monitor_add.add_argument("--title", required=True)
    monitor_add.add_argument("--city", required=True)
    monitor_add.add_argument("--topic", required=True)
    monitor_add.add_argument("--query", required=True)
    monitor_add.add_argument("--interval-min", type=int, required=True)
    monitor_add.add_argument("--chat-id", required=True)

    monitor_sub.add_parser("list")

    run_parser = subparsers.add_parser("run")
    run_sub = run_parser.add_subparsers(dest="run_command", required=True)

    run_once = run_sub.add_parser("once")
    run_once.add_argument("--monitor-id", type=int, required=True)

    run_sub.add_parser("scheduler")

    history = subparsers.add_parser("history")
    history.add_argument("--monitor-id", type=int, required=True)
    history.add_argument("--limit", type=int, default=20)

    return parser


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Stopped", file=sys.stderr)
        raise SystemExit(130)
