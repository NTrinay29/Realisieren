# Multi-Source Web Scraping & Data Consolidation

## Overview

This project implements the Realisieren Technologies Python web-scraping assignment as a small ETL pipeline:

**Scrape → Clean → Validate → Deduplicate → Consolidate → Save**

The two public practice sources are:

- Books to Scrape — `https://books.toscrape.com/`
- Quotes to Scrape — `https://quotes.toscrape.com/`

The implementation follows the site's `Next` link rather than hard-coding page numbers, and keeps source-specific parsing separate from generic processing.

## Requirements

- Python 3.10, 3.11, or 3.12
- Internet connection
- `requests`
- `beautifulsoup4`
- `lxml`
- `pytest` for tests

## Setup

macOS/Linux:

```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Windows:

```powershell
py -3.11 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Run

From the project root:

```bash
python main.py
```

The command creates:

- `output/final_dataset.csv`
- `output/summary_report.json`
- `logs/scraper.log`

## Source exploration

### Books to Scrape

The listing page uses `article.product_pod` for a book. The full title is stored in the `title` attribute of `h3 > a`; price is in `p.price_color`; the rating is represented by a class such as `Three`; and the product URL is the `href` of `h3 > a`. Pagination uses `li.next > a`.

### Quotes to Scrape

A quote is represented by `div.quote`. The quote text is in `span.text`, the author is in `small.author`, tags are `a.tag`, and pagination uses `li.next > a`.

These observations match the assignment reference and are kept in the source scraper modules.

## Data model

| Column | Books | Quotes |
|---|---|---|
| `source` | Books to Scrape | Quotes to Scrape |
| `source_url` | Book detail URL | Page URL where quote appeared |
| `name_or_title` | Book title | Quote text |
| `category` | Empty in the default run | Empty |
| `price` | Numeric price | Empty |
| `rating` | Integer 1–5 | Empty |
| `author` | Empty | Author name |
| `tags` | Empty | Lowercase, sorted, semicolon-separated |
| `description` | Empty in the default run | Empty |
| `scraped_at` | UTC timestamp | UTC timestamp |

### Category and description limitation

The assignment notes that category and description are not available on the book listing page. This implementation deliberately leaves them empty rather than inventing values. If desired, a future version can make a detail-page request for every book, while retaining the required request delay.

## Pagination

Both scrapers start from their home page and repeatedly inspect `li.next > a`. The relative `href` is converted to an absolute URL using `urllib.parse.urljoin`. When no next link exists, pagination stops.

No page count is hard-coded.

## HTTP reliability

A shared `BaseScraper` uses a `requests.Session`, a descriptive User-Agent, a 10-second timeout, retries for HTTP 429/500/502/503/504, and a 0.5-second pause between pages. A failed source is logged and does not prevent the other source from being attempted.

## Cleaning

Cleaning is implemented as pure functions in `processing/cleaning.py`:

- whitespace and non-breaking-space normalization
- quote-mark removal
- currency-to-float conversion
- word-rating-to-integer conversion
- lowercase/sort/join tag normalization
- URL normalization

## Validation

`processing/validation.py` checks:

- source is one of the two expected values
- `name_or_title` is present
- source URL looks like an HTTP(S) URL
- price is numeric and non-negative when present
- rating is an integer from 1 to 5 when present

Validation returns reason codes so the summary can show why records were rejected.

## Deduplication

The pipeline removes duplicate records before writing the CSV.

- Books: `source + title`
- Quotes: `source + author + first 50 characters of quote text`

The identifying text is lowercased, punctuation is removed, whitespace is collapsed, and the normalized key is SHA-256 hashed. This makes differences such as capitalization and extra spaces equivalent.

The real practice sites are expected to contain unique items, so a normal run may report zero duplicates. Unit tests deliberately create duplicates to prove the logic.

## Logging

`main.py` configures logging to both the terminal and `logs/scraper.log`.

- `INFO`: page progress and successful fetches
- `WARNING`: rejected/malformed records
- `ERROR`: failed requests and source-level failures

## Output and reconciliation

The JSON summary records per-source scraped, cleaned, and rejected counts, rejection reasons, duplicate count, final row count, and execution timing. The final row count is also recorded separately for easy comparison with the CSV.

## Tests

Run:

```bash
pytest -q
```

Tests cover text/price/rating/tag cleaning, validation, and duplicate detection.

## Assumptions and limitations

1. Only the two provided practice websites are scraped.
2. The scraper does not bypass authentication, CAPTCHAs, robots restrictions, or access controls.
3. Category and description remain empty unless a future detail-page enrichment stage is added.
4. The quote `source_url` is the page where the quote was found; the author URL is intentionally not used as the standardized source URL.
5. A source that fails after retries is logged and the pipeline continues with the other source.

## AI usage

See `AI_USAGE.md`. AI assistance was used for implementation planning, code generation/refactoring, and test design. The submitted code should be reviewed and understood by the candidate before submission.
