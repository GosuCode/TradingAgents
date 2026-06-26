# NEPSE Limitations

What works, what doesn't, and what to expect when using `--vendor nepse`. See [NEPSE_INTEGRATION.md](NEPSE_INTEGRATION.md) for setup.

---

## Broken

**Fundamentals analyst** — The CLI sets `fundamental_data: "nepse"`, but no NEPSE vendor exists for `get_fundamentals`, `get_balance_sheet`, `get_cashflow`, or `get_income_statement`. Tool calls raise a `ValueError`. The analyst may report failure or improvise without real financial statements.

Neither yfinance nor Alpha Vantage covers NEPSE fundamentals, so this analyst is degraded for NEPSE regardless of vendor.

---

## Empty or useless

| Feature                | Behavior                                     |
| ---------------------- | -------------------------------------------- |
| News / global news     | Static “not available” stub                  |
| Sentiment — StockTwits | US cashtags; NEPSE symbols rarely have posts |
| Sentiment — Reddit     | US subreddits only; no NEPSE coverage        |
| FRED macro             | US indicators (Fed, CPI, etc.), not Nepal    |
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

NEPSE mode is best treated as a **technical + multi-agent decision tool**, not a full fundamental/news/social stack. The main config bug is `fundamental_data: "nepse"` — that vendor does not exist yet.
