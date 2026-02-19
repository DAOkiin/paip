from __future__ import annotations

import hashlib
import re
from datetime import date
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


_IGNORED_QUERY_PREFIXES = ("utm_", "fbclid", "gclid")


def canonicalize_url(url: str) -> str:
    split = urlsplit(url.strip())
    query_pairs = [
        (k, v)
        for k, v in parse_qsl(split.query, keep_blank_values=True)
        if not any(k.startswith(prefix) for prefix in _IGNORED_QUERY_PREFIXES)
    ]
    normalized = urlunsplit(
        (
            split.scheme.lower(),
            split.netloc.lower(),
            split.path or "/",
            urlencode(sorted(query_pairs)),
            "",
        )
    )
    return normalized


def normalize_text(value: str) -> str:
    lowered = value.casefold().strip()
    compact = re.sub(r"[^\w\s]", " ", lowered)
    return re.sub(r"\s+", " ", compact).strip()


def build_event_key(*, title: str, city: str, venue: str, start_date: date) -> str:
    normalized = "|".join(
        [
            normalize_text(title),
            normalize_text(city),
            normalize_text(venue),
            start_date.isoformat(),
        ]
    )
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def dedup_key(canonical_url: str) -> str:
    return hashlib.sha256(canonical_url.encode("utf-8")).hexdigest()
