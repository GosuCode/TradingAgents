# NEPSE Limitations

What works, what doesn't, and what to expect when using `--vendor nepse`. See [NEPSE_INTEGRATION.md](NEPSE_INTEGRATION.md) for setup.

---

## Broken

**Fundamentals analyst (historical)** — Now resolved. `get_fundamentals` returns company profile + key stats from the NEPSE API (sector, market cap, listed shares, 52w range, etc.). `get_balance_sheet`, `get_cashflow`, and `get_income_statement` return matching disclosures from `nepse_scraper.get_company_disclosures()` when available.

Coverage depends on what the company has filed through NEPSE's disclosure system — no structured financial statements like yfinance's 10-K, but real company-submitted documents.

---

## Empty or useless

| Feature                | Behavior                                     |
| ---------------------- | -------------------------------------------- |
| News / global news     | Real data from NEPSE disclosures + exchange messages |
| Sentiment — StockTwits | US cashtags; NEPSE symbols rarely have posts         |
| Sentiment — Reddit     | US subreddits only; no NEPSE coverage                |
| FRED macro             | US indicators (Fed, CPI, etc.), not Nepal            |
| NRB macro              | NEPSE market trend table; NRB rates attempt scrape   |
| Polymarket             | Global/US events, not NEPSE-specific         |

Agents still run using price, sector, and technical data, but news and social layers add little.

---

## Partially working

**Outcome tracking** — Uses NEPSE prices and NEPSE Index alpha with T+2 settlement. Limitations:

- Resolves only when you **re-run the same ticker** (not batch)
- Needs enough trading sessions after the decision date; very recent entries stay pending
- NEPSE Index history is **paginated** (20 rows per API page); older pending entries may fail to resolve or get wrong alpha
- Close-based only — no circuit limits, fees, slippage, or position sizing

**Data reliability** — Depends on `nepse-scraper` and nepalstock.com; API outages and `verify_ssl=False` can cause intermittent failures.

---

## Works well

- Market analyst (OHLCV, verified snapshot, technical indicators)
- Instrument identity (company name, sector from NEPSE API)
- Full pipeline (research debate → trader → risk → portfolio manager)
- Memory log and reflections (when returns resolve)
- Checkpoint/resume

---

## Practical takeaway

NEPSE mode is best treated as a **technical + disclosure-based decision tool**, not a full fundamental/news/social stack. The `fundamental_data: "nepse"` gap has been closed: fundamentals now return company profile and disclosure-matched entries, though structured 10-K-style statements are not available.
