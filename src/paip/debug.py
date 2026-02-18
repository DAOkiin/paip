from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

from .config import Settings


def main() -> None:
    parser = argparse.ArgumentParser(prog="python -m paip.debug")
    parser.add_argument("--monitor-id", type=int, default=1)
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args()

    settings = Settings.from_env()
    db_path = Path(settings.db_path)
    print(f"DB: {db_path}")
    if not db_path.exists():
        print("Database file not found")
        return

    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    print("\ncounts:")
    for table in ("runs", "raw_hits", "canonical_items", "notifications"):
        cnt = cur.execute(f"select count(*) from {table}").fetchone()[0]
        print(f"  {table}: {cnt}")

    print(f"\nlast runs for monitor_id={args.monitor_id}:")
    runs = cur.execute(
        """
        select id, trigger, started_at, finished_at, status, fetched, new_items, duplicates, error
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
                "  run_id={id} trigger={trigger} status={status} fetched={fetched} new={new_items} "
                "dup={duplicates} started={started_at} error={error}".format(**data)
            )

    print(f"\nlast notifications for monitor_id={args.monitor_id}:")
    notifications = cur.execute(
        """
        select id, run_id, status, reason, error, created_at
        from notifications
        where monitor_id = ?
        order by id desc
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
                "  notif_id={id} run_id={run_id} status={status} created={created_at} "
                "reason={reason} error={error}".format(**data)
            )

    con.close()


if __name__ == "__main__":
    main()
