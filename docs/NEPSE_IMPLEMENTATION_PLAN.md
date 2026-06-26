# NEPSE Implementation Plan

Fill the gaps in the NEPSE vendor stack. Based on audit at `docs/NEPSE_LIMITATIONS.md` and `interface.py:106-172`.

**Status: ✅ Complete** — All phases implemented and verified.

---

## Phase 1 — Fundamentals from NEPSE disclosures (high ROI, low effort)

**Problem:** `fundamental_data: "nepse"` in config raises `ValueError` because no NEPSE vendor is registered for `get_fundamentals`, `get_balance_sheet`, `get_cashflow`, or `get_income_statement` in `interface.py:120-135`.

**Solution:** `nepse_scraper` already has `get_ticker_info()` (used by `agent_utils.py:110`) and `get_company_disclosures()`. Wrap them for the four fundamental tools.

### Files to change

#### `tradingagents/dataflows/nepse.py` — add four functions

```python
def get_fundamentals(
    ticker: Annotated[str, "NEPSE stock symbol"],
    curr_date: Annotated[str, "Current date YYYY-mm-dd"] = None,
) -> str:
    """Return NEPSE company profile + key stats from ticker_info."""
    # Call scraper.get_ticker_info(ticker)
    # Return formatted markdown with:
    #   - company name, sector, instrument type
    #   - listed shares, paid-up capital
    #   - high/low prices, last traded price, volume
    # Follow the markdown pattern from get_nepse_top_gainers (line 485)

def get_balance_sheet(
    ticker: Annotated[str, "NEPSE stock symbol"],
    curr_date: Annotated[str, "Current date YYYY-mm-dd"] = None,
) -> str:
    """Return recent disclosures tagged as balance-sheet relevant."""
    # Call scraper.get_company_disclosures(ticker)
    # Filter/format disclosures with "balance sheet" or "financial statement" in title
    # Return markdown list of disclosure titles + dates

def get_cashflow(
    ticker: Annotated[str, "NEPSE stock symbol"],
    curr_date: Annotated[str, "Current date YYYY-mm-dd"] = None,
) -> str:
    """Return cash flow related disclosures."""
    # Same as get_balance_sheet but filter for cash-flow keywords

def get_income_statement(
    ticker: Annotated[str, "NEPSE stock symbol"],
    curr_date: Annotated[str, "Current date YYYY-mm-dd"] = None,
) -> str:
    """Return income/profit related disclosures."""
    # Same pattern, filter for "income", "profit", "result"
```

**Pattern to follow:** `get_nepse_top_gainers` (lines 460-487) for guard clauses and markdown formatting. `agent_utils.py:105-129` shows the `scraper.get_ticker_info()` parsing pattern.

#### `tradingagents/dataflows/interface.py` — register vendors

- Import the four new functions at line 21-30:
  ```python
  from .nepse import (
      get_balance_sheet as get_nepse_balance_sheet,
      get_cashflow as get_nepse_cashflow,
      get_fundamentals as get_nepse_fundamentals,
      get_global_news as get_nepse_global_news,
      get_income_statement as get_nepse_income_statement,
      ...
  )
  ```
- Add `"nepse"` keys to `VENDOR_METHODS` blocks at lines 120-135:
  ```python
  "get_fundamentals": {
      "alpha_vantage": ...,
      "yfinance": ...,
      "nepse": get_nepse_fundamentals,
  },
  # Same for get_balance_sheet, get_cashflow, get_income_statement
  ```

### Acceptance

- `--vendor nepse` no longer raises `ValueError` for the fundamentals analyst
- `get_fundamentals(NABIL)` returns company name, sector, listed shares
- `get_balance_sheet(NABIL)` returns relevant disclosure entries

---

## Phase 2 — News from NEPSE notices (low effort)

**Problem:** Current `get_news()` and `get_global_news()` in `nepse.py:585-600` return static "not available" stubs.

**Solution:** `nepse_scraper.get_notices()` returns regulatory/company notices. Replace the stubs.

### `tradingagents/dataflows/nepse.py` — replace stubs

```python
def get_news(
    ticker: Annotated[str, "NEPSE stock symbol"],
    start_date: Annotated[str, "Start date YYYY-mm-dd"],
    end_date: Annotated[str, "End date YYYY-mm-dd"],
) -> str:
    """Return NEPSE notices relevant to ticker."""
    # Call scraper.get_notices()
    # Filter by ticker mention + date range
    # Return formatted markdown list

def get_global_news(
    curr_date: str = None,
    look_back_days: int = 7,
    limit: int = 5,
) -> str:
    """Return recent NEPSE-wide notices (regulatory, market-wide)."""
    # Call scraper.get_notices()
    # Filter for market-wide notices (no specific ticker)
    # Return top N entries
```

**Pattern to follow:** `yahoo_finance_news.py` for date filtering logic, native `nepse.py` guard clauses for error handling.

---

## Phase 3 — Nepal macro from NRB (medium effort)

**Problem:** `macro_data: "nepse"` is not registered; FRED data is US-only and irrelevant for NEPSE.

**Solution:** New module `tradingagents/dataflows/nrb.py` scraping Nepal Rastra Bank published rates.

### New file: `tradingagents/dataflows/nrb.py`

```python
def get_macro_data(
    curr_date: str = None,
    look_back_days: int = 30,
    limit: int = 5,
) -> str:
    """Return key Nepal macro indicators."""
    # Sources:
    #   - NRB policy rate (from nrb.org.np or nepse_scraper)
    #   - USD/NPR exchange rate
    #   - CPI inflation (NRB published)
    #   - Remittance data (NRB quarterly)
    # Return markdown with current values + recent trend
```

**Pattern to follow:** `fred.py` (standalone vendor, markdown output).

### `tradingagents/dataflows/interface.py` — register

- Import and add `"nrb"` to `VENDOR_METHODS["get_macro_indicators"]`
- Add `"nrb"` to `VENDOR_LIST`

---

## Phase 4 — Default config fix

**Problem:** `default_config.py:131` sets `"fundamental_data": "yfinance"`, but CLI `--vendor nepse` and example configs set it to `"nepse"` which breaks because no NEPSE fundamentals vendor exists.

**Fix after Phase 1:** No config change needed — the vendor key `"nepse"` will resolve correctly once registered in `interface.py`.

---

## File change summary

| File | Change |
|---|---|
| `tradingagents/dataflows/nepse.py` | Add 4 fundamental functions; replace 2 news stubs |
| `tradingagents/dataflows/interface.py` | Import + register new functions in `VENDOR_METHODS` |
| `tradingagents/dataflows/nrb.py` | New file: Nepal macro data |
| `tradingagents/dataflows/interface.py` | Register `"nrb"` for `get_macro_indicators` |

## Order of implementation

1. **Phase 1** (fundamentals) — unblocks the `ValueError`, highest user-facing impact
2. **Phase 2** (news) — fills empty stubs with real data, same file
3. **Phase 3** (macro) — standalone new module, lowest risk
