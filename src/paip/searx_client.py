from __future__ import annotations

from datetime import datetime
from typing import Any

import httpx

from .models import SearchHit


class SearxClient:
    def __init__(self, base_url: str, api_key: str | None = None, timeout_sec: float = 20.0):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout_sec = timeout_sec

    def search(self, query: str, limit: int = 20) -> list[SearchHit]:
        params = {
            "q": query,
            "format": "json",
        }
        headers: dict[str, str] = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
            headers["X-API-Key"] = self.api_key

        with httpx.Client(timeout=self.timeout_sec, follow_redirects=True) as client:
            response = client.get(f"{self.base_url}/search", params=params, headers=headers)
            response.raise_for_status()
            payload = response.json()

        raw_results: list[dict[str, Any]] = payload.get("results", [])[:limit]
        normalized: list[SearchHit] = []
        for item in raw_results:
            url = item.get("url")
            title = item.get("title") or "(untitled)"
            if not url:
                continue
            normalized.append(
                SearchHit(
                    url=str(url),
                    title=str(title),
                    snippet=str(item.get("content") or ""),
                    published_at=_parse_datetime(item.get("publishedDate")),
                    source=str(item.get("engine") or "searxng"),
                )
            )
        return normalized


def _parse_datetime(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
    return None
