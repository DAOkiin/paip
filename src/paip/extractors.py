from __future__ import annotations

import json
import re
from datetime import date, datetime, timezone
from typing import Any, Iterable, Iterator, Protocol
from urllib.parse import urlsplit

import httpx

from .models import MonitorSpec, SearchHit
from .utils import canonicalize_url


_JSON_LD_SCRIPT_RE = re.compile(
    r"<script[^>]+type=[\"']application/ld\+json[\"'][^>]*>(.*?)</script>",
    re.IGNORECASE | re.DOTALL,
)


class SourceExtractor(Protocol):
    name: str

    def supports(self, url: str) -> bool:
        ...

    def extract(self, hit: SearchHit, monitor: MonitorSpec) -> list[dict[str, Any]]:
        ...


class ExtractorRegistry:
    def __init__(self, extractors: Iterable[SourceExtractor] | None = None):
        self._extractors = list(extractors or [EventbriteExtractor()])

    def match(self, url: str) -> SourceExtractor | None:
        for extractor in self._extractors:
            if extractor.supports(url):
                return extractor
        return None


class EventbriteExtractor:
    name = "eventbrite_jsonld"

    def __init__(self, timeout_sec: float = 20.0):
        self.timeout_sec = timeout_sec

    def supports(self, url: str) -> bool:
        host = urlsplit(url).netloc.casefold()
        return "eventbrite." in host

    def extract(self, hit: SearchHit, monitor: MonitorSpec) -> list[dict[str, Any]]:
        html = self._fetch_html(hit.url)
        claims: list[dict[str, Any]] = []
        for block in _iter_json_ld_documents(html):
            for event_obj in _iter_event_objects(block):
                claims.append(_event_object_to_claim(event_obj, hit, monitor))
        return claims

    def _fetch_html(self, url: str) -> str:
        with httpx.Client(timeout=self.timeout_sec, follow_redirects=True) as client:
            response = client.get(url)
            response.raise_for_status()
            return response.text


class StaticHtmlEventbriteExtractor(EventbriteExtractor):
    """Test helper extractor that avoids network calls."""

    def __init__(self, html: str):
        super().__init__(timeout_sec=0.1)
        self._html = html

    def _fetch_html(self, url: str) -> str:  # noqa: ARG002
        return self._html


def _iter_json_ld_documents(html: str) -> Iterator[Any]:
    for match in _JSON_LD_SCRIPT_RE.finditer(html):
        script_content = (match.group(1) or "").strip()
        if not script_content:
            continue
        try:
            yield json.loads(script_content)
        except json.JSONDecodeError:
            continue


def _iter_event_objects(payload: Any) -> Iterator[dict[str, Any]]:
    if isinstance(payload, list):
        for item in payload:
            yield from _iter_event_objects(item)
        return

    if not isinstance(payload, dict):
        return

    type_value = payload.get("@type")
    if _is_event_type(type_value):
        yield payload

    graph = payload.get("@graph")
    if isinstance(graph, list):
        for item in graph:
            yield from _iter_event_objects(item)

    for value in payload.values():
        if isinstance(value, (dict, list)):
            yield from _iter_event_objects(value)


def _is_event_type(type_value: Any) -> bool:
    if isinstance(type_value, str):
        return type_value.casefold() == "event"
    if isinstance(type_value, list):
        return any(isinstance(item, str) and item.casefold() == "event" for item in type_value)
    return False


def _event_object_to_claim(
    event_obj: dict[str, Any],
    hit: SearchHit,
    monitor: MonitorSpec,
) -> dict[str, Any]:
    start_at, start_date = _parse_start_values(event_obj.get("startDate"))
    location = event_obj.get("location")
    source_url = _coerce_source_url(event_obj.get("url"), fallback=hit.url)
    source_name = _source_name_from_url(source_url, fallback=hit.source)

    return {
        "source_url": source_url,
        "source_name": source_name,
        "title": _clean_text(event_obj.get("name")) or hit.title,
        "city": _extract_city(location) or monitor.city,
        "venue": _extract_venue(location),
        "start_at": start_at,
        "start_date": start_date,
        "extracted_at": datetime.now(timezone.utc),
        "confidence": 0.9,
        "raw_payload": {
            "extractor": "eventbrite_jsonld",
            "event": event_obj,
            "hit": hit.model_dump(mode="json"),
        },
    }


def _parse_start_values(raw_value: Any) -> tuple[datetime | None, date | None]:
    if raw_value is None:
        return None, None

    if isinstance(raw_value, datetime):
        return raw_value, raw_value.date()

    if isinstance(raw_value, date):
        return None, raw_value

    if not isinstance(raw_value, str):
        return None, None

    value = raw_value.strip()
    if not value:
        return None, None

    if "T" not in value:
        try:
            return None, date.fromisoformat(value)
        except ValueError:
            return None, None

    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None, None
    return dt, dt.date()


def _extract_city(location: Any) -> str:
    if isinstance(location, list):
        for item in location:
            city = _extract_city(item)
            if city:
                return city
        return ""

    if not isinstance(location, dict):
        return ""

    address = location.get("address")
    if isinstance(address, dict):
        for key in ("addressLocality", "addressRegion"):
            value = _clean_text(address.get(key))
            if value:
                return value

    return ""


def _extract_venue(location: Any) -> str:
    if isinstance(location, list):
        for item in location:
            venue = _extract_venue(item)
            if venue:
                return venue
        return ""

    if not isinstance(location, dict):
        return ""

    name = _clean_text(location.get("name"))
    if name:
        return name

    address = location.get("address")
    if isinstance(address, dict):
        for key in ("name", "streetAddress", "addressLocality"):
            value = _clean_text(address.get(key))
            if value:
                return value

    return ""


def _coerce_source_url(raw_url: Any, *, fallback: str) -> str:
    value = str(raw_url or fallback).strip()
    if not value:
        value = fallback
    try:
        return canonicalize_url(value)
    except Exception:  # noqa: BLE001
        return fallback


def _source_name_from_url(url: str, *, fallback: str) -> str:
    host = urlsplit(url).netloc
    return host or fallback


def _clean_text(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    return " ".join(text.split())
