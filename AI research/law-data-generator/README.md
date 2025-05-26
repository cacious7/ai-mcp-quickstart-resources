# Zambian Law Scraper

This project is a Python-based tool to collect, structure, and store Zambian law data from multiple authoritative sources. It is designed for resumable, incremental scraping and outputs each law as a JSON file in the `lawdata/` folder.

## Features
- Scrapes from multiple legitimate sources (ZambiaLII, Parliament of Zambia, Blackhall’s Laws of Zambia, Judiciary of Zambia, Law Library of Congress, GlobaLex, Zambia Human Rights Commission, and more)
- Saves each law as a structured JSON file
- Checkpointing for resumability (safe to stop and restart)
- Extensible: add new sources easily

## Usage
1. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
2. Run the scraper:
   ```powershell
   python zambian_law_scraper.py
   ```
3. JSON files will be saved in the `lawdata/` folder.

## Folder Structure
- `zambian_law_scraper.py` — Main script
- `lawdata/` — Output folder for law JSON files
- `tests/` — Comprehensive unit tests with proper test isolation
- `requirements.txt` — Python dependencies
- `.github/copilot-instructions.md` — Copilot custom instructions

## Testing
Run the comprehensive test suite:
```powershell
python -m pytest tests/ -v
```

All tests use proper isolation and do not pollute the main `lawdata/` directory. See `tests/README.md` for detailed testing information.

## Notes
- Respect robots.txt and terms of use for each source.
- Extend the script to add more sources as needed.
