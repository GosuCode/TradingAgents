# NEPSE Integration Opportunities

What would improve NEPSE mode beyond price + technicals. See [NEPSE_LIMITATIONS.md](NEPSE_LIMITATIONS.md) for current gaps.

---

## Highest impact

**NEPSE disclosures** — `nepse_scraper` already has company disclosures, notices, and ticker info. Use these for the fundamentals analyst instead of missing Yahoo-style financials (dividends, rights, AGMs, regulatory filings).

**Nepal macro** — Replace US FRED data with a small NRB/CBS snippet: policy rate, inflation, USD/NPR, remittance trends. More relevant for banks, MFIs, and consumption-linked stocks.

**Local financial news** — Merolagani, ShareSansar, Bizmandu, Arthik Abhiyan, plus NEPSE circulars. Fills the empty news/sentiment layer better than StockTwits or Reddit.

**Sector context** — NEPSE is sector-heavy (banks, MFIs, hydropower, insurance). Sector indices, peer comparison, and regulator context (NRB for banks, etc.) from existing scraper endpoints.

---

## Medium impact

- **Market regime data** — top gainers/losers, turnover, market summary as context for agents
- **Fix index pagination** — full NEPSE Index history for reliable outcome tracking
- **Circuit bands** — daily price limits from NEPSE data for honest tradeability notes
- **Behavioral signals** — volume/turnover spikes when social text isn't available

---

## Lower priority

- Annual report PDF parsing (hard; start with disclosure metadata only)
- Nepali-language news (if `output_language` is Nepali)
- Batch outcome resolver across tickers
- yfinance / Polymarket / US prediction markets — low NEPSE relevance

---

## Target stack

```
Prices + indicators     ← already works
Disclosures + notices   ← fundamentals + news substitute
NRB macro snippet       ← macro context
Local headlines         ← news + sentiment
Sector index + peers    ← research + benchmark
```

NEPSE mode should behave as a **disclosure & sector analyst**, not a US 10-K clone.

---

## Constraints

- No official NEPSE fundamentals/news API — scraping and disclosures are the realistic path
- Respect rate limits and terms on third-party sites
- Empty tool stubs hurt more than partial but honest data
