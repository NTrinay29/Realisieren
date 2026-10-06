"""Shared HTTP/session utilities for the scraping assignment."""

from __future__ import annotations

import logging
import time
from typing import Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class BaseScraper:
    """Reusable HTTP client with retries, timeout, and polite request delay."""

    def __init__(self, timeout: int = 10, delay: float = 0.5) -> None:
        self.timeout = timeout
        self.delay = delay
        self.session = self._create_session()

    @staticmethod
    def _create_session() -> requests.Session:
        session = requests.Session()
        session.headers.update(
            {"User-Agent": "ScrapingAssignment/1.0 (learning project)"}
        )
        retries = Retry(
            total=3,
            connect=3,
            read=3,
            status=3,
            backoff_factor=1.0,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=frozenset({"GET"}),
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retries)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def get(self, url: str) -> Optional[requests.Response]:
        """Fetch a URL, returning None after a logged request failure."""
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            response.encoding = "utf-8"
            logger.info("Fetched %s (%s)", url, response.status_code)
            return response
        except requests.RequestException as exc:
            logger.error("Failed to fetch %s: %s", url, exc)
            return None

    def pause(self) -> None:
        time.sleep(self.delay)
