from processing.deduplication import find_duplicates


def test_duplicates_ignore_case_and_spaces():
    base = {"source": "Books to Scrape", "author": None}
    records = [
        {**base, "name_or_title": "Example Book Title"},
        {**base, "name_or_title": "  Example Book Title "},
        {**base, "name_or_title": "EXAMPLE BOOK TITLE"},
    ]
    unique, dupes = find_duplicates(records)
    assert len(unique) == 1
    assert len(dupes) == 2


def test_quote_duplicate_uses_source_author_and_first_50_chars():
    base = {"source": "Quotes to Scrape", "author": "Author"}
    first = {**base, "name_or_title": "A quote with identical leading content that continues beyond fifty characters."}
    second = {**base, "name_or_title": "A quote with identical leading content that continues beyond fifty characters, but differs later."}
    unique, dupes = find_duplicates([first, second])
    assert len(unique) == 1
    assert len(dupes) == 1
