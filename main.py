"""Entry point for the multi-source scraping ETL pipeline."""

from __future__ import annotations

import csv
import json
import logging
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from processing.cleaning import clean_record
from processing.deduplication import find_duplicates
from processing.validation import validate_record
from scrapers.books_scraper import BooksScraper
from scrapers.quotes_scraper import QuotesScraper

ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "output"
LOG_DIR = ROOT / "logs"
LOG_FILE = LOG_DIR / "scraper.log"
CSV_FILE = OUTPUT_DIR / "final_dataset.csv"
SUMMARY_FILE = OUTPUT_DIR / "summary_report.json"

FIELDNAMES = [
    "source",
    "source_url",
    "name_or_title",
    "category",
    "price",
    "rating",
    "author",
    "tags",
    "description",
    "scraped_at",
]


def configure_logging() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setFormatter(formatter)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


def process_source(scraper, source_name: str, scraped_at: str) -> tuple[list[dict], dict]:
    logger = logging.getLogger(__name__)
    raw_records = scraper.scrape()
    cleaned_records: list[dict] = []
    rejection_counts: Counter[str] = Counter()
    rejected_records = 0

    for raw in raw_records:
        raw["scraped_at"] = scraped_at
        cleaned = clean_record(raw)
        problems = validate_record(cleaned)
        if problems:
            rejected_records += 1
            for reason in problems:
                rejection_counts[reason] += 1
            logger.warning(
                "Rejected record from %s: %s",
                source_name,
                ", ".join(problems),
            )
            continue
        cleaned_records.append(cleaned)

    return cleaned_records, {
        "scraped": len(raw_records),
        "cleaned": len(cleaned_records),
        "rejected": rejected_records,
        "rejected_by_reason": dict(rejection_counts),
    }


def write_csv(records: list[dict]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with CSV_FILE.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)


def write_summary(summary: dict) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    SUMMARY_FILE.write_text(json.dumps(summary, indent=2), encoding="utf-8")


def main() -> int:
    configure_logging()
    logger = logging.getLogger(__name__)
    start = time.perf_counter()
    start_dt = datetime.now(timezone.utc)
    scraped_at = start_dt.isoformat()

    all_records: list[dict] = []
    per_source: dict[str, dict] = {}

    scrapers = [
        (BooksScraper(), "Books to Scrape"),
        (QuotesScraper(), "Quotes to Scrape"),
    ]

    for scraper, source_name in scrapers:
        try:
            records, metrics = process_source(scraper, source_name, scraped_at)
            all_records.extend(records)
            per_source[source_name] = metrics
        except Exception:
            logger.exception("Unexpected failure while processing %s", source_name)
            per_source[source_name] = {
                "scraped": 0,
                "cleaned": 0,
                "rejected": 0,
                "rejected_by_reason": {"source_failure": 1},
            }

    unique_records, duplicate_records = find_duplicates(all_records)
    logger.info("Duplicates detected: %d", len(duplicate_records))

    write_csv(unique_records)
    end_dt = datetime.now(timezone.utc)
    duration = time.perf_counter() - start

    summary = {
        "run": {
            "start_time_utc": start_dt.isoformat(),
            "end_time_utc": end_dt.isoformat(),
            "duration_seconds": round(duration, 3),
        },
        "sources": per_source,
        "duplicates": len(duplicate_records),
        "final_record_count": len(unique_records),
        "reconciliation": {
            "cleaned_total": sum(item["cleaned"] for item in per_source.values()),
            "rejected_total": sum(item["rejected"] for item in per_source.values()),
            "duplicates_total": len(duplicate_records),
            "final_total": len(unique_records),
        },
    }
    write_summary(summary)
    logger.info("Pipeline complete: %d final records", len(unique_records))
    logger.info("CSV: %s", CSV_FILE)
    logger.info("Summary: %s", SUMMARY_FILE)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
