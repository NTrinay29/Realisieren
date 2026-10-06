from processing.validation import validate_record


def valid_record():
    return {
        "source": "Books to Scrape",
        "source_url": "https://books.toscrape.com/catalogue/example_1/index.html",
        "name_or_title": "Example",
        "price": 10.5,
        "rating": 4,
    }


def test_valid_record_has_no_problems():
    assert validate_record(valid_record()) == []


def test_invalid_record_returns_reasons():
    record = valid_record()
    record.update({"source": "Unknown", "source_url": "bad", "name_or_title": "", "price": -1, "rating": 6})
    problems = validate_record(record)
    assert set(problems) == {"unknown_source", "missing_name", "invalid_url", "invalid_price", "invalid_rating"}
