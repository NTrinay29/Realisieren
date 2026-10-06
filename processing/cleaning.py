"""Pure data-cleaning helpers."""

from __future__ import annotations

import re
from typing import Any, Optional
from urllib.parse import urljoin

RATING_MAP = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}
BASE_URLS = {
    "Books to Scrape": "https://books.toscrape.com/",
    "Quotes to Scrape": "https://quotes.toscrape.com/",
}


def clean_text(value: Any) -> Optional[str]:
    if value is None:
        return None
    text = " ".join(str(value).replace("\xa0", " ").split())
    return text or None


def strip_quotes(value: Any) -> Optional[str]:
    text = clean_text(value)
    if text is None:
        return None
    return text.strip("“”\"'") or None


def clean_price(raw: Any) -> Optional[float]:
    if raw is None:
        return None
    match = re.search(r"\d+(?:\.\d+)?", str(raw).replace(",", ""))
    return float(match.group()) if match else None


def clean_rating(raw: Any) -> Optional[int]:
    for word in clean_text(raw).lower().split() if clean_text(raw) else []:
        if word in RATING_MAP:
            return RATING_MAP[word]
    return None


def clean_tags(raw: Any) -> Optional[str]:
    if raw is None:
        return None
    if isinstance(raw, str):
        tags = [part.strip() for part in raw.split(";")]
    else:
        tags = [str(part).strip() for part in raw]
    tags = sorted({tag.lower() for tag in tags if tag})
    return ";".join(tags) or None


def normalize_url(value: Any, base_url: Optional[str] = None) -> Optional[str]:
    if value is None:
        return None
    value = str(value).strip()
    if not value:
        return None
    if value.startswith(("http://", "https://")):
        return value
    if base_url:
        absolute = urljoin(base_url, value)
        return absolute if absolute.startswith(("http://", "https://")) else None
    return None


def clean_record(raw: dict) -> dict:
    source = raw.get("source")
    cleaned = {
        "source": clean_text(source),
        "source_url": normalize_url(raw.get("source_url"), BASE_URLS.get(source)),
        "name_or_title": clean_text(raw.get("name_or_title")),
        "category": clean_text(raw.get("category")),
        "price": clean_price(raw.get("price")),
        "rating": clean_rating(raw.get("rating")),
        "author": clean_text(raw.get("author")),
        "tags": clean_tags(raw.get("tags")),
        "description": clean_text(raw.get("description")),
        "scraped_at": raw.get("scraped_at"),
    }
    if source == "Quotes to Scrape":
        cleaned["name_or_title"] = strip_quotes(raw.get("name_or_title"))
    return cleaned
