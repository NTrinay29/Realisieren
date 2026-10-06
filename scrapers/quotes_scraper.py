"""Quotes to Scrape source scraper."""

from __future__ import annotations

import logging
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)

BASE_URL = "https://quotes.toscrape.com/"


class QuotesScraper(BaseScraper):
    source_name = "Quotes to Scrape"

    def scrape(self) -> list[dict]:
        url = BASE_URL
        records: list[dict] = []
        page_number = 1

        while url:
            logger.info("Quotes page %d: %s", page_number, url)
            response = self.get(url)
            if response is None:
                logger.error("Stopping Quotes to Scrape after page failure: %s", url)
                break

            soup = BeautifulSoup(response.text, "lxml")
            for quote in soup.select("div.quote"):
                try:
                    records.append(self._parse_quote(quote, url))
                except Exception as exc:
                    logger.warning("Skipping malformed quote on %s: %s", url, exc)

            next_link = soup.select_one("li.next > a")
            url = urljoin(url, next_link["href"]) if next_link and next_link.get("href") else None
            page_number += 1
            if url:
                self.pause()

        logger.info("Quotes scrape complete: %d records", len(records))
        return records

    def _parse_quote(self, quote, page_url: str) -> dict:
        text = quote.select_one("span.text")
        author = quote.select_one("small.author")
        author_link = quote.select_one('a[href^="/author/"]')
        tags = [tag.get_text(" ", strip=True) for tag in quote.select("a.tag")]

        if not text or not author:
            raise ValueError("quote text or author is missing")

        author_url = urljoin(page_url, author_link["href"]) if author_link and author_link.get("href") else page_url

        return {
            "source": self.source_name,
            "source_url": page_url,
            "name_or_title": text.get_text(" ", strip=True),
            "category": None,
            "price": None,
            "rating": None,
            "author": author.get_text(" ", strip=True),
            "tags": tags,
            "description": None,
            "author_url": author_url,
        }
