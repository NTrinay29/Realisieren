# AI_USAGE.md

## Tool used

**ChatGPT (OpenAI)**

## How it was used

AI assistance was used to:

- translate the assignment requirements into a modular project structure
- design the shared HTTP/session helper
- draft source-specific Requests + BeautifulSoup scraper modules
- design cleaning, validation, and duplicate-detection functions
- draft unit tests for the processing layer
- improve README documentation and error-handling structure
- review the pipeline against the assignment checklist

## Representative prompts

1. "Build a Python ETL project for Books to Scrape and Quotes to Scrape using Requests and BeautifulSoup, with dynamic next-link pagination."
2. "Add reusable cleaning functions for whitespace, price, ratings, tags, and URLs, keeping them separate from scraping."
3. "Implement duplicate detection using normalized identifying fields and a hash, plus unit tests for capitalization and whitespace differences."
4. "Review the project against the assignment requirements for validation, logging, output reconciliation, and reproducibility."

## AI-assisted areas

AI-assisted implementation includes:

- `scrapers/base_scraper.py`
- `scrapers/books_scraper.py`
- `scrapers/quotes_scraper.py`
- `processing/cleaning.py`
- `processing/validation.py`
- `processing/deduplication.py`
- `main.py`
- unit tests
- documentation

## Review and verification

The implementation was reviewed against the supplied assignment/reference documents. In particular, the final design keeps scraping separate from processing, follows `li.next > a`, leaves non-applicable fields empty instead of inventing data, returns validation reasons, and uses the specified duplicate-identification rules.

The code was also checked with offline unit tests. The execution environment used for preparing this submission did not have direct outbound DNS/network access, so the live scraping step could not be executed here. No fake scraped output was generated to hide that limitation.

Before submission, run `python main.py` from a machine with internet access and verify that:

- both sources appear in `output/final_dataset.csv`
- the final row count matches `summary_report.json`
- prices are numeric
- ratings are within 1–5
- `logs/scraper.log` contains page-level progress
- `pytest -q` passes

## Incorrect/incomplete AI suggestions discovered

No AI-generated suggestion was knowingly left unverified as a factual scraping result. The live dataset was not fabricated when network access was unavailable during preparation.
