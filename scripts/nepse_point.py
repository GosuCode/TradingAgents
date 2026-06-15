#!/usr/bin/env python3
"""Display the current NEPSE index (benchmark point) from nepalstock.com."""

import urllib3
import warnings
from datetime import datetime, timezone, timedelta

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings("ignore", category=urllib3.exceptions.InsecureRequestWarning)


def main():
    try:
        from nepse_scraper import NepseScraper
    except ImportError:
        print("Error: nepse-scraper not installed. Run: pip install nepse-scraper")
        return 1

    scraper = NepseScraper(verify_ssl=False)
    data = scraper.get_nepse_index()

    if not data or not isinstance(data, list):
        print("No index data available. Market may be closed.")
        return 1

    nepse_entry = next((e for e in data if e.get("index") == "NEPSE Index"), None)
    if not nepse_entry:
        print("NEPSE Index entry not found in response.")
        return 1

    current = nepse_entry.get("currentValue", 0)
    prev_close = nepse_entry.get("close", 0)
    change = current - prev_close
    per_change = (change / prev_close * 100) if prev_close else 0
    ts = nepse_entry.get("generatedTime", datetime.now(timezone(timedelta(hours=5.45))).isoformat())

    arrow = "\u25b2" if change >= 0 else "\u25bc"
    color = "\033[32m" if change >= 0 else "\033[31m"
    reset = "\033[0m"

    print(f"NEPSE Index: {current:,.2f}")
    print(f"  {color}{arrow} {change:+,.2f} ({per_change:+.2f}%){reset}")
    print(f"  High: {nepse_entry.get('high', 0):,.2f}  |  Low: {nepse_entry.get('low', 0):,.2f}")
    print(f"  52W High: {nepse_entry.get('fiftyTwoWeekHigh', 0):,.2f}  |  52W Low: {nepse_entry.get('fiftyTwoWeekLow', 0):,.2f}")
    print(f"  As of: {ts}")
    print(f"\nMarket is {'OPEN' if scraper.is_market_open() else 'CLOSED'}")

    summary = scraper.get_market_summary()
    if summary and isinstance(summary, list):
        smap = {e["detail"]: e["value"] for e in summary if "detail" in e and "value" in e}
        turnover = smap.get("Total Turnover Rs:", 0)
        print(f"  Turnover: NPR {turnover / 1e9:,.2f}B")
        print(f"  Volume: {smap.get('Total Traded Shares', 0):,.0f} shares")
        print(f"  Transactions: {smap.get('Total Transactions', 0):,.0f}")

    print()
    _print_top_stocks(scraper)


def _print_top_stocks(scraper):
    gainers = scraper.get_top_stocks("top_gainer")
    if gainers:
        print("Top Gainers")
        print(f"  {'Symbol':<12} {'LTP':>10} {'Change':>10} {'%Change':>8}")
        for s in gainers[:5]:
            sym = s.get("symbol", "")
            ltp = s.get("ltp", 0)
            chg = s.get("pointChange", 0)
            pct = s.get("percentageChange", 0)
            print(f"  {sym:<12} {ltp:>10,.2f} {chg:>+10,.2f} {pct:>+7.2f}%")
        print()

    losers = scraper.get_top_stocks("top_loser")
    if losers:
        print("Top Losers")
        print(f"  {'Symbol':<12} {'LTP':>10} {'Change':>10} {'%Change':>8}")
        for s in losers[:5]:
            sym = s.get("symbol", "")
            ltp = s.get("ltp", 0)
            chg = s.get("pointChange", 0)
            pct = s.get("percentageChange", 0)
            print(f"  {sym:<12} {ltp:>10,.2f} {chg:>+10,.2f} {pct:>+7.2f}%")
        print()

    turnovers = scraper.get_top_stocks("top_turnover")
    if turnovers:
        print("Top by Turnover")
        print(f"  {'Symbol':<12} {'Turnover':>18} {'Price':>10}")
        for s in turnovers[:5]:
            sym = s.get("symbol", "")
            t = s.get("turnover", 0)
            price = s.get("closingPrice", 0)
            print(f"  {sym:<12} {t:>18,.2f} {price:>10,.2f}")


if __name__ == "__main__":
    exit(main())
