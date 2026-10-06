"""Duplicate detection using normalized fingerprints."""

from __future__ import annotations

import hashlib
import re


def _normalize_key_part(value) -> str:
    text = str(value or "").lower()
    text = re.sub(r"[^\w\s]", "", text)
    return " ".join(text.split())


def make_fingerprint(record: dict) -> str:
    if record.get("source") == "Books to Scrape":
        key = f"{record.get('source')} {record.get('name_or_title')}"
    else:
        key = (
            f"{record.get('source')} {record.get('author')} "
            f"{str(record.get('name_or_title') or '')[:50]}"
        )
    normalized = _normalize_key_part(key)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def find_duplicates(records: list[dict]) -> tuple[list[dict], list[dict]]:
    seen: set[str] = set()
    unique: list[dict] = []
    duplicates: list[dict] = []

    for record in records:
        fingerprint = make_fingerprint(record)
        if fingerprint in seen:
            duplicates.append(record)
        else:
            unique.append(record)
            seen.add(fingerprint)

    return unique, duplicates
