import logging
import os
import time
from datetime import datetime, timedelta
from typing import Annotated

import pandas as pd

from .errors import NoMarketDataError

logger = logging.getLogger(__name__)

# In-memory session cache for get_stock_data
_in_memory_cache: dict[tuple[str, str, str], tuple[float, str]] = {}
_IN_MEMORY_TTL_SECS = 3600  # 1 hour

_DISK_CACHE_MAX_AGE = timedelta(hours=24)

NEPSE_INDEX_ID = 58
NEPSE_BENCHMARK_LABEL = "NEPSE Index"

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    from nepse_scraper import NepseScraper
    NEPSE_SCRAPER_AVAILABLE = True
except ImportError:
    NEPSE_SCRAPER_AVAILABLE = False

try:
    from stockstats import wrap
    STOCKSTATS_AVAILABLE = True
except ImportError:
    STOCKSTATS_AVAILABLE = False


def _fetch_and_cache_nepse(
    symbol: str,
    start_str: str,
    end_str: str,
    cache_file: str,
) -> pd.DataFrame:
    """Fetch NEPSE data and save to disk cache. Returns DataFrame with lowercase columns."""
    scraper = NepseScraper(verify_ssl=False)
    raw = scraper.get_ticker_price_history(
        ticker=symbol.upper().strip(),
        start_date=start_str,
        end_date=end_str,
    )
    df = _parse_price_history(raw)
    if df.empty or "close" not in df.columns:
        raise NoMarketDataError(symbol, symbol, f"NEPSE returned no rows for {symbol}")
    os.makedirs(os.path.dirname(cache_file), exist_ok=True)
    df.to_csv(cache_file, index=False, encoding="utf-8")
    return df


def get_stock_data(
    symbol: Annotated[str, "NEPSE stock symbol (e.g., 'NABIL', 'NIFRA', 'MEN')"],
    start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
    end_date: Annotated[str, "End date in yyyy-mm-dd format"],
) -> str:
    """
    Get OHLCV stock data for a NEPSE-listed company using nepse_scraper.
    NEPSE uses company codes like NABIL, NIFRA, HBL, MEN, etc.

    Uses a two-layer cache:
      1. In-memory (per session, 1-hour TTL)
      2. Broad-window disk cache (5 years, 24-hour staleness)
    """
    if not NEPSE_SCRAPER_AVAILABLE:
        return "Error: nepse_scraper not installed. Run: pip install nepse-scraper"
    if not PANDAS_AVAILABLE:
        return "Error: pandas not installed. Run: pip install pandas"

    from tradingagents.dataflows.config import get_config
    from tradingagents.dataflows.utils import safe_ticker_component

    safe_sym = safe_ticker_component(symbol.upper().strip())

    # --- Layer 1: In-memory cache ---
    key = (safe_sym, start_date, end_date)
    now = time.time()
    cached_entry = _in_memory_cache.get(key)
    if cached_entry is not None:
        ts, cached_result = cached_entry
        if now - ts < _IN_MEMORY_TTL_SECS:
            return cached_result

    # --- Layer 2: Broad-window disk cache ---
    config = get_config()
    today = pd.Timestamp.today()
    window_start = today - pd.DateOffset(years=5)
    window_start_str = window_start.strftime("%Y-%m-%d")
    window_end_str = (today + pd.Timedelta(days=1)).strftime("%Y-%m-%d")

    cache_file = os.path.join(
        config["data_cache_dir"],
        f"{safe_sym}-NEPSE-full.csv",
    )

    df = None
    cache_hit = os.path.exists(cache_file)

    if cache_hit:
        try:
            cached_df = pd.read_csv(cache_file, on_bad_lines="skip", encoding="utf-8")
            if not cached_df.empty and "close" in cached_df.columns:
                file_age = timedelta(seconds=time.time() - os.path.getmtime(cache_file))
                if file_age < _DISK_CACHE_MAX_AGE:
                    df = cached_df
                else:
                    # Stale cache: try to refresh, fall back on failure
                    try:
                        df = _fetch_and_cache_nepse(symbol, window_start_str, window_end_str, cache_file)
                    except Exception:
                        logger.warning("NEPSE API fetch failed, using stale cache for %s", symbol)
                        df = cached_df
        except Exception as e:
            logger.warning("Failed to read NEPSE cache for %s: %s", symbol, e)

    if df is None:
        try:
            df = _fetch_and_cache_nepse(symbol, window_start_str, window_end_str, cache_file)
        except NoMarketDataError:
            return f"No data found for '{symbol.upper()}' on NEPSE"
        except Exception as e:
            return f"Error fetching NEPSE data for {symbol}: {str(e)}"

    # Normalise dates and filter to requested range
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    req_start = pd.to_datetime(start_date)
    req_end = pd.to_datetime(end_date)
    filtered = df[(df["date"] >= req_start) & (df["date"] <= req_end)].copy()

    if filtered.empty:
        return f"No data found for '{symbol.upper()}' on NEPSE between {start_date} and {end_date}"

    numeric_cols = ["open", "high", "low", "close", "volume"]
    for col in numeric_cols:
        if col in filtered.columns:
            filtered[col] = filtered[col].round(2)

    header = f"# NEPSE stock data for {symbol.upper()} from {start_date} to {end_date}\n"
    header += f"# Total records: {len(filtered)}\n"
    header += f"# Data retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

    result = header + filtered.to_csv(index=False)

    # Store in in-memory cache
    _in_memory_cache[key] = (time.time(), result)

    return result


def get_stock_stats_indicators_window(
    symbol: Annotated[str, "ticker symbol of the company"],
    indicator: Annotated[str, "technical indicator to get the analysis and report of"],
    curr_date: Annotated[
        str, "The current trading date you are trading on, YYYY-mm-dd"
    ],
    look_back_days: Annotated[int, "how many days to look back"],
) -> str:
    """
    Get technical indicator data for NEPSE stock using stockstats.
    """
    best_ind_params = {
        "close_50_sma": (
            "50 SMA: A medium-term trend indicator. "
            "Usage: Identify trend direction and serve as dynamic support/resistance. "
            "Tips: It lags price; combine with faster indicators for timely signals."
        ),
        "close_200_sma": (
            "200 SMA: A long-term trend benchmark. "
            "Usage: Confirm overall market trend and identify golden/death cross setups. "
            "Tips: It reacts slowly; best for strategic trend confirmation rather than frequent trading entries."
        ),
        "close_10_ema": (
            "10 EMA: A responsive short-term average. "
            "Usage: Capture quick shifts in momentum and potential entry points. "
            "Tips: Prone to noise in choppy markets; use alongside longer averages for filtering false signals."
        ),
        "macd": (
            "MACD: Computes momentum via differences of EMAs. "
            "Usage: Look for crossovers and divergence as signals of trend changes. "
            "Tips: Confirm with other indicators in low-volatility or sideways markets."
        ),
        "macds": (
            "MACD Signal: An EMA smoothing of the MACD line. "
            "Usage: Use crossovers with the MACD line to trigger trades. "
            "Tips: Should be part of a broader strategy to avoid false positives."
        ),
        "macdh": (
            "MACD Histogram: Shows the gap between the MACD line and its signal. "
            "Usage: Visualize momentum strength and spot divergence early. "
            "Tips: Can be volatile; complement with additional filters in fast-moving markets."
        ),
        "rsi": (
            "RSI: Measures momentum to flag overbought/oversold conditions. "
            "Usage: Apply 70/30 thresholds and watch for divergence to signal reversals. "
            "Tips: In strong trends, RSI may remain extreme; always cross-check with trend analysis."
        ),
        "boll": (
            "Bollinger Middle: A 20 SMA serving as the basis for Bollinger Bands. "
            "Usage: Acts as a dynamic benchmark for price movement. "
            "Tips: Combine with the upper and lower bands to effectively spot breakouts or reversals."
        ),
        "boll_ub": (
            "Bollinger Upper Band: Typically 2 standard deviations above the middle line. "
            "Usage: Signals potential overbought conditions and breakout zones. "
            "Tips: Confirm signals with other tools; prices may ride the band in strong trends."
        ),
        "boll_lb": (
            "Bollinger Lower Band: Typically 2 standard deviations below the middle line. "
            "Usage: Indicates potential oversold conditions. "
            "Tips: Use additional analysis to avoid false reversal signals."
        ),
        "atr": (
            "ATR: Averages true range to measure volatility. "
            "Usage: Set stop-loss levels and adjust position sizes based on current market volatility. "
            "Tips: It's a reactive measure, so use it as part of a broader risk management strategy."
        ),
        "vwma": (
            "VWMA: A moving average weighted by volume. "
            "Usage: Confirm trends by integrating price action with volume data. "
            "Tips: Watch for skewed results from volume spikes; use in combination with other volume analyses."
        ),
        "mfi": (
            "MFI: The Money Flow Index is a momentum indicator that uses both price and volume to measure buying and selling pressure. "
            "Usage: Identify overbought (>80) or oversold (<20) conditions and confirm the strength of trends or reversals. "
            "Tips: Use alongside RSI or MACD to confirm signals; divergence between price and MFI can indicate potential reversals."
        ),
    }

    if indicator not in best_ind_params:
        return f"Indicator {indicator} is not supported. Please choose from: {list(best_ind_params.keys())}"

    if not STOCKSTATS_AVAILABLE:
        return "Error: stockstats not installed. Run: pip install stockstats"

    end_date = curr_date
    curr_date_dt = datetime.strptime(curr_date, "%Y-%m-%d")
    before = curr_date_dt - timedelta(days=look_back_days)

    try:
        indicator_data = _get_indicator_bulk(symbol, indicator, curr_date)

        current_dt = curr_date_dt
        ind_string = ""

        while current_dt >= before:
            date_str = current_dt.strftime('%Y-%m-%d')

            if date_str in indicator_data:
                indicator_value = indicator_data[date_str]
            else:
                indicator_value = "N/A: Not a trading day (weekend or holiday)"

            ind_string += f"{date_str}: {indicator_value}\n"
            current_dt = current_dt - timedelta(days=1)

        result_str = (
            f"## {indicator} values from {before.strftime('%Y-%m-%d')} to {end_date}:\n\n"
            + ind_string
            + "\n\n"
            + best_ind_params.get(indicator, "No description available.")
        )

        return result_str

    except Exception as e:
        return f"Error getting indicator data for {indicator}: {str(e)}"


def _get_indicator_bulk(
    symbol: Annotated[str, "ticker symbol of the company"],
    indicator: Annotated[str, "technical indicator to calculate"],
    curr_date: Annotated[str, "current date for reference"]
) -> dict:
    """
    Bulk calculation of stock stats indicators for NEPSE.
    """
    data = _load_nepse_ohlcv(symbol, curr_date)
    df = wrap(data)
    df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")

    df[indicator]

    result_dict = {}
    for _, row in df.iterrows():
        date_str = row["Date"]
        indicator_value = row[indicator]

        if pd.isna(indicator_value):
            result_dict[date_str] = "N/A"
        else:
            result_dict[date_str] = str(indicator_value)

    return result_dict


def _load_nepse_ohlcv(symbol: str, end_date: str) -> pd.DataFrame:
    """
    Load NEPSE OHLCV data for use with stockstats.
    """
    if not PANDAS_AVAILABLE or not NEPSE_SCRAPER_AVAILABLE:
        raise ImportError("pandas and nepse-scraper are required")

    from dateutil.relativedelta import relativedelta

    end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    start_dt = end_dt - relativedelta(days=120)

    start_date = start_dt.strftime("%Y-%m-%d")

    scraper = NepseScraper(verify_ssl=False)
    result = scraper.get_ticker_price_history(
        ticker=symbol.upper().strip(),
        start_date=start_date,
        end_date=end_date
    )

    df = _parse_price_history(result)

    if df.empty:
        raise ValueError(f"No data available for {symbol}")

    df = df.rename(columns={
        'date': 'Date',
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'volume': 'Volume'
    })

    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date')

    return df


def load_nepse_ohlcv(symbol: str, curr_date: str) -> pd.DataFrame:
    """Fetch NEPSE OHLCV data with caching, filtered to prevent look-ahead bias.

    Mirrors ``stockstats_utils.load_ohlcv()`` but uses the NEPSE API instead of
    yfinance. Returns a DataFrame with columns ``Date``, ``Open``, ``High``,
    ``Low``, ``Close``, ``Volume`` (uppercase, matching the yfinance convention)
    or raises ``NoMarketDataError`` when no data is available.
    """
    if not NEPSE_SCRAPER_AVAILABLE:
        raise NoMarketDataError(
            symbol, symbol,
            "nepse_scraper not installed. Run: pip install nepse-scraper",
        )
    if not PANDAS_AVAILABLE:
        raise NoMarketDataError(symbol, symbol, "pandas not installed")

    from tradingagents.dataflows.config import get_config
    from tradingagents.dataflows.utils import safe_ticker_component

    config = get_config()
    curr_date_dt = pd.to_datetime(curr_date)
    today_date = pd.Timestamp.today()
    start_date = today_date - pd.DateOffset(years=5)
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = (today_date + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
    safe_sym = safe_ticker_component(symbol.upper())

    os.makedirs(config["data_cache_dir"], exist_ok=True)
    cache_file = os.path.join(
        config["data_cache_dir"],
        f"{safe_sym}-NEPSE-data-{start_str}-{end_str}.csv",
    )

    data = None
    if os.path.exists(cache_file):
        cached = pd.read_csv(cache_file, on_bad_lines="skip", encoding="utf-8")
        if not cached.empty and "Close" in cached.columns:
            data = cached

    if data is None:
        scraper = NepseScraper(verify_ssl=False)
        raw = scraper.get_ticker_price_history(
            ticker=symbol.upper().strip(),
            start_date=start_str,
            end_date=end_str,
        )
        df = _parse_price_history(raw)
        if df.empty or "close" not in df.columns:
            raise NoMarketDataError(
                symbol, symbol, f"NEPSE returned no rows for {symbol}",
            )
        # Rename lowercase columns to uppercase to match the yfinance convention.
        df = df.rename(columns={
            "date": "Date",
            "open": "Open",
            "high": "High",
            "low": "Low",
            "close": "Close",
            "volume": "Volume",
        })
        df = df.drop(columns=[c for c in ["symbol"] if c in df.columns], errors="ignore")
        df.to_csv(cache_file, index=False, encoding="utf-8")
        data = df

    # Clean & normalise (mirrors _clean_dataframe from stockstats_utils).
    data["Date"] = pd.to_datetime(data["Date"], errors="coerce")
    data = data.dropna(subset=["Date"])
    price_cols = [c for c in ["Open", "High", "Low", "Close", "Volume"] if c in data.columns]
    data[price_cols] = data[price_cols].apply(pd.to_numeric, errors="coerce")
    data = data.dropna(subset=["Close"])
    data[price_cols] = data[price_cols].ffill().bfill()

    # Filter to curr_date to prevent look-ahead bias.
    data = data[data["Date"] <= curr_date_dt]

    if data.empty:
        raise NoMarketDataError(
            symbol, symbol, f"No NEPSE rows on or before {curr_date} for {symbol}",
        )
    return data


def _parse_price_history(data) -> pd.DataFrame:
    """Parse nepse_scraper response into a DataFrame."""
    if isinstance(data, dict):
        content = data.get('content', [])
    elif isinstance(data, list):
        content = data
    else:
        return pd.DataFrame()

    if not content:
        return pd.DataFrame()

    records = []
    for item in content:
        records.append({
            'date': item.get('businessDate', ''),
            'open': item.get('openPrice', 0),
            'high': item.get('highPrice', 0),
            'low': item.get('lowPrice', 0),
            'close': item.get('closePrice', 0),
            'volume': item.get('totalTradedQuantity', 0),
            'symbol': item.get('security', {}).get('symbol', '') if isinstance(item.get('security'), dict) else '',
        })

    df = pd.DataFrame(records)
    if 'date' in df.columns:
        df = df.sort_values('date')
    return df


def get_nepse_top_gainers(
    date: Annotated[str, "Date in yyyy-mm-dd format"] = None,
) -> str:
    """Get top gaining stocks on NEPSE for a given date."""
    if not NEPSE_SCRAPER_AVAILABLE:
        return "Error: nepse_scraper not installed. Run: pip install nepse-scraper"
    if not PANDAS_AVAILABLE:
        return "Error: pandas not installed. Run: pip install pandas"

    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')

    try:
        scraper = NepseScraper(verify_ssl=False)
        gainers = scraper.get_top_gainers(date=date)

        if gainers is None:
            return f"No gainer data for {date}"

        if isinstance(gainers, dict):
            gainers = pd.DataFrame(gainers.get('content', []))

        if gainers.empty:
            return f"No gainer data for {date}"

        return f"# NEPSE Top Gainers for {date}\n\n{gainers.to_string(index=False)}"
    except Exception as e:
        return f"Error fetching gainers: {str(e)}"


def get_nepse_top_losers(
    date: Annotated[str, "Date in yyyy-mm-dd format"] = None,
) -> str:
    """Get top losing stocks on NEPSE for a given date."""
    if not NEPSE_SCRAPER_AVAILABLE:
        return "Error: nepse_scraper not installed. Run: pip install nepse-scraper"
    if not PANDAS_AVAILABLE:
        return "Error: pandas not installed. Run: pip install pandas"

    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')

    try:
        scraper = NepseScraper(verify_ssl=False)
        losers = scraper.get_top_losers(date=date)

        if losers is None:
            return f"No loser data for {date}"

        if isinstance(losers, dict):
            losers = pd.DataFrame(losers.get('content', []))

        if losers.empty:
            return f"No loser data for {date}"

        return f"# NEPSE Top Losers for {date}\n\n{losers.to_string(index=False)}"
    except Exception as e:
        return f"Error fetching losers: {str(e)}"


def get_nepse_summary() -> str:
    """Get NEPSE market summary (total volume, turnover, etc.)."""
    if not NEPSE_SCRAPER_AVAILABLE:
        return "Error: nepse_scraper not installed. Run: pip install nepse-scraper"
    if not PANDAS_AVAILABLE:
        return "Error: pandas not installed. Run: pip install pandas"

    try:
        scraper = NepseScraper(verify_ssl=False)
        summary = scraper.get_market_summary()

        if summary is None:
            return "No summary data available"

        if isinstance(summary, dict):
            summary = pd.DataFrame([summary])

        if summary.empty:
            return "No summary data available"

        return f"# NEPSE Market Summary ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})\n\n{summary.to_string(index=False)}"
    except Exception as e:
        return f"Error fetching summary: {str(e)}"


def get_nepse_index(
    date: Annotated[str, "Date in yyyy-mm-dd format"] = None,
) -> str:
    """Get NEPSE sensitive index data for a given date."""
    if not NEPSE_SCRAPER_AVAILABLE:
        return "Error: nepse_scraper not installed. Run: pip install nepse-scraper"
    if not PANDAS_AVAILABLE:
        return "Error: pandas not installed. Run: pip install pandas"

    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')

    try:
        scraper = NepseScraper(verify_ssl=False)
        index_data = scraper.get_sensitive_index(date=date)

        if index_data is None:
            return f"No index data for {date}"

        if isinstance(index_data, dict):
            index_data = pd.DataFrame([index_data])

        if index_data.empty:
            return f"No index data for {date}"

        return f"# NEPSE Sensitive Index for {date}\n\n{index_data.to_string(index=False)}"
    except Exception as e:
        return f"Error fetching index: {str(e)}"


def get_nepse_price_history(
    symbol: Annotated[str, "NEPSE stock symbol"],
    days: Annotated[int, "Number of days to look back"] = 30,
) -> str:
    """Get price history for last N days for a NEPSE stock."""
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    return get_stock_data(symbol, start_date, end_date)


# --- Fundamentals (from NEPSE ticker info + disclosures) ---


def _get_ticker_info_or_error(ticker: str) -> dict:
    """Return ticker_info dict or raise NoMarketDataError."""
    if not NEPSE_SCRAPER_AVAILABLE:
        raise NoMarketDataError(ticker, ticker, "nepse_scraper not installed")
    try:
        scraper = NepseScraper(verify_ssl=False)
        info = scraper.get_ticker_info(ticker.upper().strip())
        if not info:
            raise NoMarketDataError(ticker, ticker, "no ticker info returned")
        return info
    except NoMarketDataError:
        raise
    except Exception as e:
        raise NoMarketDataError(ticker, ticker, str(e)) from e


def get_fundamentals(
    ticker: Annotated[str, "NEPSE stock symbol"],
    curr_date: Annotated[str, "Current date YYYY-mm-dd"] = None,
) -> str:
    """
    Get company fundamentals for a NEPSE-listed stock from the NEPSE API.
    Returns company profile, key statistics, and market data.
    """
    if not PANDAS_AVAILABLE:
        return "Error: pandas not installed. Run: pip install pandas"

    info = _get_ticker_info_or_error(ticker)
    sym = ticker.upper().strip()
    sec = info.get("security", {})
    company = sec.get("companyId", {}) if isinstance(sec.get("companyId"), dict) else {}
    sector_master = company.get("sectorMaster", {}) if isinstance(company.get("sectorMaster"), dict) else {}
    trade = info.get("securityDailyTradeDto", {})

    lines = [f"# NEPSE fundamentals for {sym}", ""]
    lines.append(f"**Company:** {sec.get('securityName', 'N/A')}")
    lines.append(f"**Sector:** {sector_master.get('sectorDescription', 'N/A')}")
    lines.append(f"**Instrument Type:** {(sec.get('instrumentType') or {}).get('description', 'N/A')}")
    lines.append(f"**ISIN:** {sec.get('isin', 'N/A')}")
    lines.append(f"**Listing Date:** {sec.get('listingDate', 'N/A')}")
    lines.append(f"**Face Value:** NPR {sec.get('faceValue', 'N/A')}")
    lines.append(f"**Listed Shares:** {info.get('stockListedShares', 'N/A')}")
    lines.append(f"**Paid-up Capital:** NPR {info.get('paidUpCapital', 'N/A')}")
    lines.append(f"**Market Capitalization:** NPR {info.get('marketCapitalization', 'N/A')}")
    lines.append(f"**Public Shares:** {info.get('publicShares', 'N/A')} ({info.get('publicPercentage', 'N/A')}%)")
    lines.append(f"**Promoter Shares:** {info.get('promoterShares', 'N/A')} ({info.get('promoterPercentage', 'N/A')}%)")
    lines.append(f"**52-Week High:** NPR {trade.get('fiftyTwoWeekHigh', 'N/A')}")
    lines.append(f"**52-Week Low:** NPR {trade.get('fiftyTwoWeekLow', 'N/A')}")
    lines.append(f"**Last Traded Price:** NPR {trade.get('lastTradedPrice', 'N/A')}")
    lines.append(f"**Previous Close:** NPR {trade.get('previousClose', 'N/A')}")
    lines.append(f"**Open Price:** NPR {trade.get('openPrice', 'N/A')}")
    lines.append(f"**High Price:** NPR {trade.get('highPrice', 'N/A')}")
    lines.append(f"**Low Price:** NPR {trade.get('lowPrice', 'N/A')}")
    lines.append(f"**Volume:** {trade.get('totalTradeQuantity', 'N/A')}")
    lines.append(f"**Trades:** {trade.get('totalTrades', 'N/A')}")
    lines.append(f"**Share Group:** {(sec.get('shareGroupId') or {}).get('description', 'N/A')}")
    lines.append(f"**Regulatory Body:** {sector_master.get('regulatoryBody', 'N/A')}")
    lines.append(f"**Website:** {company.get('companyWebsite', 'N/A')}")

    return "\n".join(lines) + "\n"


def _ticker_from_headline(headline: str) -> str | None:
    """Extract ticker symbol from headline brackets, e.g. ``[NABIL]``."""
    import re
    m = re.findall(r"\[(\w+)\]", headline)
    return m[-1].upper().strip() if m else None


def _filter_disclosures_by_ticker(ticker: str) -> list:
    """Filter company disclosures for a specific ticker.

    Bypasses ``NepseScraper.get_company_disclosures()`` because that method
    reads ``response.json().get('news', [])`` while the actual response key
    is ``companyNews``, so the library call always returns an empty list.
    We hit the endpoint directly instead. Ticker matching uses the ``[TICKER]``
    bracket in the headline since the NEPSE API puts the symbol there
    (e.g. ``Appointment of Acting CEO [NMIC]``) while ``newsSource`` is
    unreliable free text.
    """
    if not NEPSE_SCRAPER_AVAILABLE:
        return []
    try:
        scraper = NepseScraper(verify_ssl=False)
        endpoint = scraper.endpoints.get("disclosure")
        if not endpoint:
            return []
        resp = scraper.session.get(endpoint["api"])
        data = resp.json()
        items = data.get("companyNews", [])
        sym = ticker.upper().strip()
        return [
            d for d in items
            if _ticker_from_headline(d.get("newsHeadline", "")) == sym
        ]
    except Exception:
        return []


def _format_disclosures(disclosures: list, title: str) -> str:
    """Format a list of disclosure dicts into markdown."""
    if not disclosures:
        return f"# {title}\n\nNo disclosures found.\n"
    lines = [f"# {title}", f"Total: {len(disclosures)}", ""]
    for d in disclosures:
        headline = d.get("newsHeadline", "Untitled")
        body = d.get("newsBody", "")
        date = d.get("addedDate", "").split("T")[0] if d.get("addedDate") else ""
        source = d.get("newsSource", "")
        lines.append(f"### {headline}")
        lines.append(f"**Date:** {date} | **Source:** {source}")
        if body:
            import re
            clean = re.sub(r"<[^>]+>", "", body).strip()
            if clean:
                lines.append(f"> {clean[:500]}")
        lines.append("")
    return "\n".join(lines)


def get_balance_sheet(
    ticker: Annotated[str, "NEPSE stock symbol"],
    curr_date: Annotated[str, "Current date YYYY-mm-dd"] = None,
) -> str:
    """
    Get balance sheet related disclosures for a NEPSE-listed stock.
    Returns company disclosures matching balance-sheet keywords.
    """
    if not NEPSE_SCRAPER_AVAILABLE:
        return "Error: nepse_scraper not installed. Run: pip install nepse-scraper"
    if not PANDAS_AVAILABLE:
        return "Error: pandas not installed. Run: pip install pandas"

    keywords = {"balance sheet", "financial statement", "financial position", "statement of affairs"}
    items = _filter_disclosures_by_ticker(ticker)
    matched = [d for d in items if any(k in (d.get("newsHeadline", "") + d.get("newsBody", "")).lower() for k in keywords)]
    return _format_disclosures(matched, f"NEPSE balance sheet disclosures for {ticker.upper()}")


def get_cashflow(
    ticker: Annotated[str, "NEPSE stock symbol"],
    curr_date: Annotated[str, "Current date YYYY-mm-dd"] = None,
) -> str:
    """
    Get cash flow related disclosures for a NEPSE-listed stock.
    Returns company disclosures matching cash-flow keywords.
    """
    if not NEPSE_SCRAPER_AVAILABLE:
        return "Error: nepse_scraper not installed. Run: pip install nepse-scraper"
    if not PANDAS_AVAILABLE:
        return "Error: pandas not installed. Run: pip install pandas"

    keywords = {"cash flow", "cashflow"}
    items = _filter_disclosures_by_ticker(ticker)
    matched = [d for d in items if any(k in (d.get("newsHeadline", "") + d.get("newsBody", "")).lower() for k in keywords)]
    return _format_disclosures(matched, f"NEPSE cash flow disclosures for {ticker.upper()}")


def get_income_statement(
    ticker: Annotated[str, "NEPSE stock symbol"],
    curr_date: Annotated[str, "Current date YYYY-mm-dd"] = None,
) -> str:
    """
    Get income statement related disclosures for a NEPSE-listed stock.
    Returns company disclosures matching income/profit keywords.
    """
    if not NEPSE_SCRAPER_AVAILABLE:
        return "Error: nepse_scraper not installed. Run: pip install nepse-scraper"
    if not PANDAS_AVAILABLE:
        return "Error: pandas not installed. Run: pip install pandas"

    keywords = {"income", "profit", "result", "financial performance", "revenue", "earnings"}
    items = _filter_disclosures_by_ticker(ticker)
    matched = [d for d in items if any(k in (d.get("newsHeadline", "") + d.get("newsBody", "")).lower() for k in keywords)]
    return _format_disclosures(matched, f"NEPSE income statement disclosures for {ticker.upper()}")


# --- News (from NEPSE company disclosures + notices) ---


def get_news(
    ticker: Annotated[str, "NEPSE stock symbol"],
    start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
    end_date: Annotated[str, "End date in yyyy-mm-dd format"],
) -> str:
    """
    Get news/disclosures for a NEPSE-listed stock from the NEPSE API.
    Returns company announcements and regulatory filings.
    """
    if not NEPSE_SCRAPER_AVAILABLE:
        return "Error: nepse_scraper not installed. Run: pip install nepse-scraper"

    items = _filter_disclosures_by_ticker(ticker)
    if not items:
        return f"# NEPSE news for {ticker.upper()}\n\nNo news found.\n"

    start_dt = pd.to_datetime(start_date) if start_date else None
    end_dt = pd.to_datetime(end_date) if end_date else None

    filtered = []
    for d in items:
        added = d.get("addedDate", "")
        if added:
            dt = pd.to_datetime(added.split("T")[0], errors="coerce")
            if pd.isna(dt):
                continue
            if start_dt and dt < start_dt:
                continue
            if end_dt and dt > end_dt:
                continue
            filtered.append(d)

    if not filtered:
        return f"# NEPSE news for {ticker.upper()}\n\nNo news found between {start_date} and {end_date}.\n"

    lines = [f"# NEPSE news for {ticker.upper()}", f"Period: {start_date} to {end_date}", f"Total: {len(filtered)}", ""]
    for d in filtered:
        headline = d.get("newsHeadline", "Untitled")
        body = d.get("newsBody", "")
        date = d.get("addedDate", "").split("T")[0] if d.get("addedDate") else ""
        lines.append(f"### {headline}")
        lines.append(f"**Date:** {date}")
        if body:
            import re
            clean = re.sub(r"<[^>]+>", "", body).strip()
            if clean:
                lines.append(f"> {clean[:500]}")
        lines.append("")
    return "\n".join(lines)


def get_global_news(
    curr_date: Annotated[str, "Current date"] = None,
    look_back_days: Annotated[int, "Number of days"] = 7,
    limit: Annotated[int, "Max articles"] = 5,
) -> str:
    """
    Get market-wide news and notices from NEPSE.
    Includes exchange messages and regulatory notices.
    """
    if not NEPSE_SCRAPER_AVAILABLE:
        return "Error: nepse_scraper not installed. Run: pip install nepse-scraper"

    items = []
    try:
        scraper = NepseScraper(verify_ssl=False)
        # Get exchange messages from the disclosure endpoint
        endpoint = scraper.endpoints.get("disclosure")
        if endpoint:
            resp = scraper.session.get(endpoint["api"])
            data = resp.json()
            items = data.get("exchangeMessages", [])
    except Exception:
        pass

    if not items:
        return "# NEPSE market news\n\nNo market-wide news available.\n"

    if curr_date:
        ref_dt = pd.to_datetime(curr_date)
        cutoff = ref_dt - pd.Timedelta(days=look_back_days)
    else:
        cutoff = pd.Timestamp.today() - pd.Timedelta(days=look_back_days)

    filtered = []
    for d in items:
        added = None
        for field in ("modifiedDate", "addedDate", "approvedDate"):
            val = d.get(field)
            if val:
                added = val
                break
        if added:
            dt = pd.to_datetime(added.split("T")[0], errors="coerce")
            if not pd.isna(dt) and dt >= cutoff:
                filtered.append(d)

    filtered = filtered[:limit]

    if not filtered:
        return "# NEPSE market news\n\nNo recent market-wide news.\n"

    lines = ["# NEPSE market news", f"Last {look_back_days} days", ""]
    for d in filtered:
        body = d.get("messageBody", "")
        date = d.get("modifiedDate", "").split("T")[0] if d.get("modifiedDate") else ""
        lines.append(f"**Date:** {date}")
        if body:
            import re
            clean = re.sub(r"<[^>]+>", "", body).strip()
            if clean:
                lines.append(f"> {clean[:1000]}")
        lines.append("")
    return "\n".join(lines)


# --- Outcome tracking (memory/reflection Phase B) ---


def _parse_index_history(data) -> pd.DataFrame:
    """Parse nepse_scraper index history into a normalized DataFrame."""
    if isinstance(data, dict):
        content = data.get("content", [])
    elif isinstance(data, list):
        content = data
    else:
        return pd.DataFrame()

    if not content:
        return pd.DataFrame()

    records = []
    for item in content:
        records.append({
            "date": item.get("businessDate", ""),
            "close": item.get("closingIndex", 0),
        })

    df = pd.DataFrame(records)
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.dropna(subset=["date"]).sort_values("date")
    return df


def _fetch_nepse_price_df(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    """Fetch OHLCV for ``symbol`` between ``start_date`` and ``end_date``."""
    if not NEPSE_SCRAPER_AVAILABLE or not PANDAS_AVAILABLE:
        raise ImportError("nepse-scraper and pandas are required for NEPSE returns")

    scraper = NepseScraper(verify_ssl=False)
    raw = scraper.get_ticker_price_history(
        ticker=symbol.upper().strip(),
        start_date=start_date,
        end_date=end_date,
    )
    df = _parse_price_history(raw)
    if df.empty:
        return df
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"]).sort_values("date")
    return df


def _fetch_nepse_index_df(start_date: str, end_date: str) -> pd.DataFrame:
    """Fetch NEPSE Index closing levels between ``start_date`` and ``end_date``."""
    if not NEPSE_SCRAPER_AVAILABLE or not PANDAS_AVAILABLE:
        raise ImportError("nepse-scraper and pandas are required for NEPSE returns")

    scraper = NepseScraper(verify_ssl=False)
    raw = scraper.get_indices_history(NEPSE_INDEX_ID, start_date, end_date)
    return _parse_index_history(raw)


def _compute_session_return(
    sessions: pd.DataFrame,
    close_col: str,
    settlement_days: int,
    holding_days: int,
) -> tuple[float | None, int | None]:
    """Return (pct_change, holding_days) over aligned trading sessions.

    Entry is at the close ``settlement_days`` sessions after ``trade_date``
    (T+2 settlement when ``settlement_days`` is 2). Exit is ``holding_days``
    sessions after entry. Returns ``(None, None)`` when data is not yet
    available (too recent).
    """
    exit_idx = settlement_days + holding_days
    if len(sessions) <= exit_idx:
        return None, None

    entry_close = float(sessions.iloc[settlement_days][close_col])
    exit_close = float(sessions.iloc[exit_idx][close_col])
    if entry_close <= 0:
        return None, None

    ret = (exit_close - entry_close) / entry_close
    return float(ret), holding_days


def fetch_nepse_returns(
    ticker: str,
    trade_date: str,
    holding_days: int = 5,
    settlement_days: int = 2,
) -> tuple[float | None, float | None, int | None]:
    """Fetch raw and alpha return for a NEPSE ticker vs the NEPSE Index.

    Uses nepse_scraper (not yfinance). Counts **trading sessions** (Sun–Thu),
    not calendar days. ``settlement_days`` models T+2: entry is at the close
    ``settlement_days`` sessions after ``trade_date``; exit is ``holding_days``
    sessions later.

    Returns ``(raw_return, alpha_return, actual_holding_days)`` or
    ``(None, None, None)`` when price data is unavailable or too recent.
    """
    if not NEPSE_SCRAPER_AVAILABLE or not PANDAS_AVAILABLE:
        logger.warning("nepse-scraper or pandas unavailable; cannot resolve NEPSE outcome")
        return None, None, None

    try:
        start_dt = datetime.strptime(trade_date, "%Y-%m-%d")
        total_sessions = holding_days + settlement_days
        # NEPSE trades Sun–Thu; add buffer for Fri/Sat and holidays.
        calendar_buffer = total_sessions * 2 + 14
        end_str = (start_dt + timedelta(days=calendar_buffer)).strftime("%Y-%m-%d")

        stock_df = _fetch_nepse_price_df(ticker, trade_date, end_str)
        index_df = _fetch_nepse_index_df(trade_date, end_str)

        if stock_df.empty or index_df.empty:
            return None, None, None

        trade_dt = pd.to_datetime(trade_date)
        stock_df = stock_df[stock_df["date"] >= trade_dt][["date", "close"]]
        index_df = index_df[index_df["date"] >= trade_dt][["date", "close"]]

        aligned = pd.merge(stock_df, index_df, on="date", suffixes=("_stock", "_index"))
        aligned = aligned.sort_values("date").reset_index(drop=True)

        if aligned.empty:
            return None, None, None

        raw, days = _compute_session_return(
            aligned, "close_stock", settlement_days, holding_days,
        )
        if raw is None:
            return None, None, None

        bench_ret, _ = _compute_session_return(
            aligned, "close_index", settlement_days, holding_days,
        )
        if bench_ret is None:
            return None, None, None

        alpha = raw - bench_ret
        return raw, alpha, days

    except Exception as e:
        logger.warning(
            "Could not resolve NEPSE outcome for %s on %s (will retry next run): %s",
            ticker, trade_date, e,
        )
        return None, None, None
