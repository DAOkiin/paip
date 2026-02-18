from __future__ import annotations

import hashlib
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


def dedup_key(canonical_url: str) -> str:
    return hashlib.sha256(canonical_url.encode("utf-8")).hexdigest()
