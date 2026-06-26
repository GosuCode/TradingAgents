"""Nepal macro-economic data vendor.

Fetches Nepal-specific macro context from NEPSE market data and NRB
(Nepal Rastra Bank) published statistics. Used by the news analyst to
ground macro commentary in actual numbers rather than headlines alone.

NRB data sources (no official API — scraped from public HTML pages):
  - Policy rates: https://www.nrb.org.np/cmfm_rates/policy_rates
  - Forex rates:  https://www.nrb.org.np/forex/
"""

import logging
import re
from datetime import datetime, timedelta

import requests
from lxml import html

from .errors import NoMarketDataError

logger = logging.getLogger(__name__)

REQUEST_TIMEOUT = 30
MAX_ROWS = 40
DEFAULT_LOOKBACK_DAYS = 90

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
}

_NRB_POLICY_RATES_URL = "https://www.nrb.org.np/cmfm_rates/policy_rates"
_NRB_FOREX_URL = "https://www.nrb.org.np/forex/"


def _parse_table_rows(table_html: str) -> list[list[str]]:
    """Parse an HTML table into rows of stripped cell text."""
    tree = html.fromstring(table_html)
    rows = []
    for tr in tree.xpath(".//tr"):
        cells = [re.sub(r"\s+", " ", td.text_content()).strip() for td in tr.xpath(".//td")]
        if cells:
            rows.append(cells)
    return rows


def _fetch_page_tables(url: str) -> list[str]:
    """Fetch a URL and return its <table> elements as HTML strings.

    NRB pages return HTTP 404 but deliver valid content in the body, so
    we cannot use ``raise_for_status()`` here — a non-2xx status is
    expected for ``policy_rates`` and ``forex`` pages.
    """
    try:
        resp = requests.get(url, headers=_HEADERS, timeout=REQUEST_TIMEOUT)
        # Accept any status — NRB pages serve content even with 404
        if not resp.ok and not resp.text:
            return []
    except Exception:
        return []
    tables = re.findall(r"<table[^>]*>.*?</table>", resp.text, re.DOTALL)
    return tables


def _fetch_nrb_policy_rates() -> dict[str, str] | None:
    """Scrape NRB policy rates page for current policy rate, SLF, SDF, CRR.

    Returns dict like::
        {
            "policy_rate": "4.25",
            "slf": "5.75",
            "sdf": "2.75",
            "crr": "4.00",
        }
    """
    tables = _fetch_page_tables(_NRB_POLICY_RATES_URL)
    if not tables:
        return None

    result: dict[str, str] = {}

    # Policy rates (Table 0): Ceiling Rate, Policy Rate, Floor Rate
    if len(tables) >= 1:
        rows = _parse_table_rows(tables[0])
        for row in rows:
            text = " ".join(row).lower()
            if "policy rate" in text or "overnight repo" in text:
                for cell in row:
                    val = re.search(r"\d+\.\d+", cell)
                    if val:
                        result["policy_rate"] = val.group(0)
                        break
            elif "standing liquidity" in text or "ceiling" in text:
                for cell in row:
                    val = re.search(r"\d+\.\d+", cell)
                    if val:
                        result["slf"] = val.group(0)
                        break
            elif "standing deposit" in text or "floor" in text:
                for cell in row:
                    val = re.search(r"\d+\.\d+", cell)
                    if val:
                        result["sdf"] = val.group(0)
                        break

    # CRR (Table 1)
    if len(tables) >= 2:
        rows = _parse_table_rows(tables[1])
        for row in rows:
            text = " ".join(row).lower()
            if "commercial" in text or "bank" in text:
                for cell in row:
                    val = re.search(r"\d+\.\d+", cell)
                    if val:
                        result["crr"] = val.group(0)
                        break
                break

    return result if result else None


def _fetch_nrb_forex() -> dict[str, dict[str, str]] | None:
    """Scrape NRB forex page for major exchange rates.

    Returns dict like::
        {
            "USD": {"buy": "150.74", "sell": "151.34"},
            "EUR": {"buy": "171.24", "sell": "171.92"},
            "GBP": {"buy": "198.70", "sell": "199.49"},
            "INR": {"buy": "160.00", "sell": "160.15"},
        }
    """
    tables = _fetch_page_tables(_NRB_FOREX_URL)
    if not tables:
        return None

    result: dict[str, dict[str, str]] = {}
    currency_alias = {"usd": "USD", "eur": "EUR", "gbp": "GBP", "inr": "INR",
                      "chf": "CHF", "aud": "AUD", "cad": "CAD", "sgd": "SGD",
                      "jpy": "JPY", "cny": "CNY", "sar": "SAR", "qar": "QAR",
                      "thb": "THB", "aed": "AED", "myr": "MYR", "krw": "KRW",
                      "sek": "SEK", "dkk": "DKK", "hkd": "HKD", "kwd": "KWD",
                      "bhd": "BHD", "omr": "OMR"}

    for table_html in tables:
        rows = _parse_table_rows(table_html)
        for row in rows:
            if len(row) < 4:
                continue
            raw_currency = row[0].strip().lower()
            currency = None
            for key in currency_alias:
                if key in raw_currency:
                    currency = currency_alias[key]
                    break
            if not currency:
                continue
            # Table structure: Currency (Unit) | Unit | Buy | Sell
            buy = row[2].strip() if len(row) > 2 else ""
            sell = row[3].strip() if len(row) > 3 else ""
            result[currency] = {"buy": buy, "sell": sell}

    return result if result else None


def _fetch_nepse_market_trend(days: int) -> list[dict]:
    """Return recent NEPSE daily market summaries as a list of dicts."""
    try:
        from nepse_scraper import NepseScraper

        scraper = NepseScraper(verify_ssl=False)
        hist = scraper.get_market_summary_history()
        if not isinstance(hist, list):
            return []
        cutoff = datetime.today() - timedelta(days=days)
        recent = []
        for row in hist:
            try:
                dt = datetime.strptime(row.get("businessDate", ""), "%Y-%m-%d")
                if dt >= cutoff:
                    recent.append(row)
            except (ValueError, TypeError):
                continue
        return recent[-MAX_ROWS:]
    except Exception:
        return []


def _format_market_trend_table(rows: list[dict]) -> str:
    """Format market history as a markdown table."""
    if not rows:
        return ""
    lines = [
        "| Date | Turnover (NPR) | Shares Traded | Transactions | Scrips |",
        "|------|---------------|--------------|-------------|--------|",
    ]
    for r in rows:
        lines.append(
            f"| {r.get('businessDate', '')} "
            f"| {r.get('totalTurnover', 0):,.0f} "
            f"| {r.get('totalTradedShares', 0):,} "
            f"| {r.get('totalTransactions', 0):,} "
            f"| {r.get('tradedScrips', 0)} |"
        )
    return "\n".join(lines)


def _fetch_sectors() -> list[dict]:
    """Return the list of NEPSE sectors with regulatory bodies."""
    try:
        from nepse_scraper import NepseScraper

        scraper = NepseScraper(verify_ssl=False)
        raw = scraper.get_sectors()
        if isinstance(raw, dict):
            raw = raw.get("sectors", [])
        if isinstance(raw, list):
            return [s for s in raw if s.get("sectorDescription")]
        return []
    except Exception:
        return []


def _format_sector_table(sectors: list[dict]) -> str:
    """Format sector list as a markdown table."""
    if not sectors:
        return ""
    lines = [
        "| Sector | Regulatory Body |",
        "|--------|----------------|",
    ]
    for s in sectors:
        lines.append(
            f"| {s.get('sectorDescription', '')} "
            f"| {s.get('regulatoryBody', '')} |"
        )
    return "\n".join(lines)


def get_macro_data(
    curr_date: str = None,
    look_back_days: int = None,
    limit: int = 5,
) -> str:
    """
    Get Nepal macro-economic indicators.

    Returns:
      - NRB policy rates (policy rate, SLF, SDF, CRR)
      - NRB foreign exchange rates (USD, EUR, GBP, INR, …)
      - NEPSE daily market trend (turnover, volume)
      - NEPSE sector composition and regulatory bodies
    """
    if look_back_days is None:
        look_back_days = DEFAULT_LOOKBACK_DAYS

    sections = ["# Nepal Macro Indicators"]

    # --- NRB policy rates ---
    rates = _fetch_nrb_policy_rates()
    if rates:
        lines = ["## NRB Policy Rates", ""]
        lines.append(f"| Metric | Rate |")
        lines.append(f"|--------|------|")
        lines.append(f"| Policy Rate (Overnight Repo) | {rates.get('policy_rate', 'N/A')}% |")
        lines.append(f"| Standing Liquidity Facility (Ceiling) | {rates.get('slf', 'N/A')}% |")
        lines.append(f"| Standing Deposit Facility (Floor) | {rates.get('sdf', 'N/A')}% |")
        lines.append(f"| Cash Reserve Ratio (Commercial Banks) | {rates.get('crr', 'N/A')}% |")
        sections.append("\n".join(lines))
    else:
        sections.append(
            "## NRB Policy Rates\nCould not fetch. "
            "Check https://www.nrb.org.np/cmfm_rates/policy_rates"
        )

    # --- NRB forex ---
    forex = _fetch_nrb_forex()
    if forex:
        major = ["USD", "EUR", "GBP", "INR"]
        lines = ["## NRB Foreign Exchange Rates", ""]
        lines.append("| Currency | Buy (NPR) | Sell (NPR) |")
        lines.append("|----------|-----------|------------|")
        for ccy in major:
            if ccy in forex:
                lines.append(f"| {ccy} | {forex[ccy]['buy']} | {forex[ccy]['sell']} |")
        # Add any other currencies found
        others = [c for c in sorted(forex) if c not in major]
        for ccy in others:
            lines.append(f"| {ccy} | {forex[ccy]['buy']} | {forex[ccy]['sell']} |")
        sections.append("\n".join(lines))
    else:
        sections.append(
            "## NRB Foreign Exchange Rates\nCould not fetch. "
            "Check https://www.nrb.org.np/forex/"
        )

    # --- Market-level trend ---
    rows = _fetch_nepse_market_trend(look_back_days)
    if rows:
        sections.append("## NEPSE Market Trend (Daily)")
        sections.append(_format_market_trend_table(rows))
    else:
        sections.append("## NEPSE Market Trend\nNo recent market summary available.")

    # --- Sectors ---
    sectors = _fetch_sectors()
    if sectors:
        sections.append("## NEPSE Sectors & Regulators")
        sections.append(_format_sector_table(sectors))

    return "\n\n".join(sections) + "\n"
