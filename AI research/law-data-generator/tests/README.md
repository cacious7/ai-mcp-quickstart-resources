# Tests Directory

This directory contains comprehensive unit tests for the Zambian Law Scraper project.

## Test Isolation

All test files are configured with proper test isolation to prevent polluting the main `lawdata/` directory:

- Each test class has `setUp()` and `tearDown()` methods
- Tests use temporary directories (`tempfile.mkdtemp()`)
- The `DATA_DIR` and `CHECKPOINT_FILE` variables are temporarily overridden during tests
- Temporary directories are automatically cleaned up after each test

## Test Files

- `test_zambian_law_scraper_unittest.py` - Main scraper functionality tests
- `test_parliament_scraper_unittest.py` - Parliament of Zambia fetcher tests
- `test_blackhall_scraper_unittest.py` - Blackhall's Laws of Zambia fetcher tests
- `test_judiciary_scraper_unittest.py` - Judiciary of Zambia fetcher tests
- `test_globalex_scraper_unittest.py` - GlobaLex fetcher tests
- `test_loc_scraper_unittest.py` - Law Library of Congress fetcher tests
- `test_hrc_scraper_unittest.py` - Zambia Human Rights Commission fetcher tests
- `test_law_accuracy.py` - Law accuracy validation tests
- `test_law_accuracy_realpdf_unittest.py` - Real PDF accuracy tests

## Running Tests

### Run all tests:
```bash
python -m pytest tests/ -v
```

### Run specific test file:
```bash
python -m pytest tests/test_globalex_scraper_unittest.py -v
```

### Run specific test method:
```bash
python -m pytest tests/test_globalex_scraper_unittest.py::TestGlobalexScraper::test_fetch_globalex_reference_detail_html -v
```

### Run with short traceback:
```bash
python -m pytest tests/ -v --tb=short
```

## Test Coverage

The tests cover:
- HTML parsing and content extraction
- PDF downloading and text extraction
- Network error handling
- Pagination handling
- Metadata extraction (title, year, citations, related files)
- Duplicate detection and semantic comparison
- Checkpointing functionality
- All 7 source fetchers (ZambiaLII, Parliament, Blackhall, Judiciary, LoC, GlobaLex, HRC)

## Test Data Isolation Verification

After running tests, verify that the main `lawdata/` directory remains empty:
```bash
ls lawdata/
# Should be empty or not exist
```

This confirms that test isolation is working properly and tests are not creating persistent data in the main application directory.
