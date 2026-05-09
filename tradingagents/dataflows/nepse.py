from typing import Annotated
from datetime import datetime, timedelta

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

def get_stock_data(
    symbol: Annotated[str, "NEPSE stock symbol (e.g., 'NABIL', 'NIFRA', 'MEN')"],
    start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
    end_date: Annotated[str, "End date in yyyy-mm-dd format"],
) -> str:
    """
    Get OHLCV stock data for a NEPSE-listed company using nepse_scraper.
    NEPSE uses company codes like NABIL, NIFRA, HBL, MEN, etc.
    """
    if not NEPSE_SCRAPER_AVAILABLE:
        return "Error: nepse_scraper not installed. Run: pip install nepse-scraper"

    if not PANDAS_AVAILABLE:
        return "Error: pandas not installed. Run: pip install pandas"

    try:
        scraper = NepseScraper(verify_ssl=False)
        result = scraper.get_ticker_price_history(
            ticker=symbol.upper().strip(),
            start_date=start_date,
            end_date=end_date
        )

        df = _parse_price_history(result)

        if df.empty:
            return f"No data found for '{symbol.upper()}' on NEPSE between {start_date} and {end_date}"

        numeric_cols = ["open", "high", "low", "close", "volume"]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = df[col].round(2)

        header = f"# NEPSE stock data for {symbol.upper()} from {start_date} to {end_date}\n"
        header += f"# Total records: {len(df)}\n"
        header += f"# Data retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        return header + df.to_csv(index=False)

    except Exception as e:
        return f"Error fetching NEPSE data for {symbol}: {str(e)}"

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
    symbol: Annotated[str, "NEPSE stock symbol (e.g., 'NABIL', 'NIFRA', 'MEN')"],
    days: Annotated[int, "Number of days to look back"] = 30,
) -> str:
    """Get price history for last N days for a NEPSE stock."""
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    return get_stock_data(symbol, start_date, end_date)

def get_news(
    ticker: Annotated[str, "NEPSE stock symbol"],
    start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
    end_date: Annotated[str, "End date in yyyy-mm-dd format"],
) -> str:
    """Get news for a NEPSE stock. Note: News data not available for NEPSE."""
    return "News data is not available for NEPSE-listed stocks. NEPSE does not provide a public news API. Please rely on technical and fundamental analysis of price data."

def get_global_news(
    curr_date: Annotated[str, "Current date"] = None,
    look_back_days: Annotated[int, "Number of days"] = 7,
    limit: Annotated[int, "Max articles"] = 5,
) -> str:
    """Get global/market news. Note: Not available for NEPSE."""
    return "Global news data is not available through NEPSE. News aggregation requires external sources not integrated with this NEPSE adapter."