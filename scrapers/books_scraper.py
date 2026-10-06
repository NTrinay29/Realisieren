"""Books to Scrape source scraper."""

from __future__ import annotations

import logging
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)

BASE_URL = "https://books.toscrape.com/"


class BooksScraper(BaseScraper):
    source_name = "Books to Scrape"

    def scrape(self) -> list[dict]:
        url = BASE_URL
        records: list[dict] = []
        page_number = 1

        while url:
            logger.info("Books page %d: %s", page_number, url)
            response = self.get(url)
            if response is None:
                logger.error("Stopping Books to Scrape after page failure: %s", url)
                break

            soup = BeautifulSoup(response.text, "lxml")
            for article in soup.select("article.product_pod"):
                try:
                    record = self._parse_book(article, url)
                    records.append(record)
                except Exception as exc:  # defensive: one malformed item must not stop a page
                    logger.warning("Skipping malformed book on %s: %s", url, exc)

            next_link = soup.select_one("li.next > a")
            url = urljoin(url, next_link["href"]) if next_link and next_link.get("href") else None
            page_number += 1
            if url:
                self.pause()

        logger.info("Books scrape complete: %d records", len(records))
        return records

    def _parse_book(self, article, page_url: str) -> dict:
        link = article.select_one("h3 > a")
        price = article.select_one("p.price_color")
        rating = article.select_one("p.star-rating")

        if not link or not link.get("href"):
            raise ValueError("book link is missing")

        return {
            "source": self.source_name,
            "source_url": urljoin(page_url, link["href"]),
            "name_or_title": link.get("title") or link.get_text(" ", strip=True),
            "category": None,
            "price": price.get_text(" ", strip=True) if price else None,
            "rating": " ".join(rating.get("class", [])) if rating else None,
            "author": None,
            "tags": None,
            "description": None,
        }
