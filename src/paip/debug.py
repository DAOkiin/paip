from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path

from .config import Settings
from .db import Store


def main() -> None:
    parser = argparse.ArgumentParser(prog="python -m paip.debug")
    parser.add_argument("--monitor-id", type=int, default=1)
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--telegram-preview", action="store_true")
    parser.add_argument("--run-id", type=int, default=None)
    args = parser.parse_args()

    settings = Settings.from_env()
    # Keep debug commands aligned with runtime schema version.
    Store(settings.db_url)
    db_path = Path(settings.db_path)
    print(f"DB: {db_path}")
    if not db_path.exists():
        print("Database file not found")
        return

    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    print("\ncounts:")
    for table in ("runs", "source_hits", "event_claims", "events", "notifications"):
        cnt = cur.execute(f"select count(*) from {table}").fetchone()[0]
        print(f"  {table}: {cnt}")

    print(f"\nlast runs for monitor_id={args.monitor_id}:")
    runs = cur.execute(
        """
        select
          id,
          trigger,
          started_at,
          finished_at,
          status,
          fetched_sources,
          claims_extracted,
          new_events,
          updated_events,
          duplicates,
          unsupported_sources,
          error
        from runs
        where monitor_id = ?
        order by id desc
        limit ?
        """,
        (args.monitor_id, args.limit),
    ).fetchall()
    if not runs:
        print("  no runs")
    else:
        for row in runs:
            data = dict(row)
            print(
                "  run_id={id} trigger={trigger} status={status} fetched={fetched_sources} "
                "claims={claims_extracted} new={new_events} upd={updated_events} dup={duplicates} "
                "unsupported={unsupported_sources} started={started_at} error={error}".format(**data)
            )

    print(f"\nlast events for monitor_id={args.monitor_id}:")
    events = cur.execute(
        """
        select id, title, city, venue, start_date, source_name, source_url, updated_at
        from events
        where monitor_id = ?
        order by updated_at desc
        limit ?
        """,
        (args.monitor_id, args.limit),
    ).fetchall()
    if not events:
        print("  no events")
    else:
        for row in events:
            data = dict(row)
            print(
                "  event_id={id} date={start_date} title={title} city={city} venue={venue} "
                "source={source_name} url={source_url} updated={updated_at}".format(**data)
            )

    print(f"\nlast notifications for monitor_id={args.monitor_id}:")
    notifications = cur.execute(
        """
        select n.id, n.run_id, n.status, n.reason, n.error, n.created_at, e.title as event_title
        from notifications n
        join events e on e.id = n.event_id
        where n.monitor_id = ?
        order by n.id desc
        limit ?
        """,
        (args.monitor_id, args.limit),
    ).fetchall()
    if not notifications:
        print("  no notifications")
    else:
        for row in notifications:
            data = dict(row)
            print(
                "  notif_id={id} run_id={run_id} status={status} reason={reason} title={event_title} "
                "created={created_at} error={error}".format(**data)
            )

    if args.telegram_preview:
        _print_telegram_preview(cur, monitor_id=args.monitor_id, limit=args.limit, run_id=args.run_id)

    con.close()


def _print_telegram_preview(
    cur: sqlite3.Cursor,
    *,
    monitor_id: int,
    limit: int,
    run_id: int | None,
) -> None:
    print("\ntelegram preview:")
    if run_id is None:
        run_row = cur.execute(
            """
            select run_id
            from notifications
            where monitor_id = ?
            order by id desc
            limit 1
            """,
            (monitor_id,),
        ).fetchone()
        if run_row is None:
            print("  no notifications to preview")
            return
        run_id = int(run_row["run_id"])

    rows = cur.execute(
        """
        select id, run_id, status, error, payload
        from notifications
        where monitor_id = ? and run_id = ?
        order by id asc
        limit ?
        """,
        (monitor_id, run_id, limit),
    ).fetchall()
    if not rows:
        print(f"  no notifications for run_id={run_id}")
        return

    print(f"  run_id={run_id}, messages={len(rows)}")
    for idx, row in enumerate(rows, 1):
        payload = row["payload"]
        if isinstance(payload, str):
            try:
                payload = json.loads(payload)
            except json.JSONDecodeError:
                payload = {"message": payload}
        if not isinstance(payload, dict):
            payload = {"message": str(payload)}
        message = payload.get("message") or "<empty message>"
        print(f"\n  #{idx} notif_id={row['id']} status={row['status']} error={row['error']}")
        for line in str(message).splitlines():
            print(f"    {line}")


if __name__ == "__main__":
    main()
