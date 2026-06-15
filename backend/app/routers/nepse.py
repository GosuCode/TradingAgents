import logging
import urllib3
import warnings
from fastapi import APIRouter, Query

from backend.app.schemas.nepse import (
    IndexResponse, IndexEntry,
    TopStocksResponse, TopStockItem,
    SummaryResponse, SummaryItem,
)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings("ignore", category=urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/nepse", tags=["NEPSE"])


def _get_scraper():
    from nepse_scraper import NepseScraper
    return NepseScraper(verify_ssl=False)


@router.get("/index")
def get_index() -> IndexResponse:
    try:
        scraper = _get_scraper()
        data = scraper.get_nepse_index()
        if not data or not isinstance(data, list):
            return IndexResponse(success=False, error="No index data available")
        entry = next((e for e in data if e.get("index") == "NEPSE Index"), None)
        if not entry:
            return IndexResponse(success=False, error="NEPSE Index not found")
        current = entry.get("currentValue", 0)
        prev_close = entry.get("close", 0)
        return IndexResponse(success=True, data=IndexEntry(
            name="NEPSE Index",
            close=entry.get("close", 0),
            current_value=current,
            high=entry.get("high", 0),
            low=entry.get("low", 0),
            previous_close=entry.get("previousClose", 0),
            change=current - prev_close,
            per_change=((current - prev_close) / prev_close * 100) if prev_close else 0,
            fifty_two_week_high=entry.get("fiftyTwoWeekHigh", 0),
            fifty_two_week_low=entry.get("fiftyTwoWeekLow", 0),
            generated_time=entry.get("generatedTime", ""),
        ))
    except Exception as e:
        logger.exception("Failed to fetch NEPSE index")
        return IndexResponse(success=False, error=str(e))


@router.get("/gainers")
def get_gainers(limit: int = Query(5, ge=1, le=20)) -> TopStocksResponse:
    try:
        scraper = _get_scraper()
        data = scraper.get_top_stocks("top_gainer")
        items = [
            TopStockItem(
                symbol=s.get("symbol", ""),
                security_name=s.get("securityName", ""),
                ltp=s.get("ltp", 0),
                point_change=s.get("pointChange", 0),
                percentage_change=s.get("percentageChange", 0),
            )
            for s in (data or [])[:limit]
        ]
        return TopStocksResponse(success=True, data=items)
    except Exception as e:
        logger.exception("Failed to fetch gainers")
        return TopStocksResponse(success=False, error=str(e))


@router.get("/losers")
def get_losers(limit: int = Query(5, ge=1, le=20)) -> TopStocksResponse:
    try:
        scraper = _get_scraper()
        data = scraper.get_top_stocks("top_loser")
        items = [
            TopStockItem(
                symbol=s.get("symbol", ""),
                security_name=s.get("securityName", ""),
                ltp=s.get("ltp", 0),
                point_change=s.get("pointChange", 0),
                percentage_change=s.get("percentageChange", 0),
            )
            for s in (data or [])[:limit]
        ]
        return TopStocksResponse(success=True, data=items)
    except Exception as e:
        logger.exception("Failed to fetch losers")
        return TopStocksResponse(success=False, error=str(e))


@router.get("/turnover")
def get_turnover(limit: int = Query(5, ge=1, le=20)) -> TopStocksResponse:
    try:
        scraper = _get_scraper()
        data = scraper.get_top_stocks("top_turnover")
        items = [
            TopStockItem(
                symbol=s.get("symbol", ""),
                security_name=s.get("securityName", ""),
                turnover=s.get("turnover", 0),
                closing_price=s.get("closingPrice", 0),
            )
            for s in (data or [])[:limit]
        ]
        return TopStocksResponse(success=True, data=items)
    except Exception as e:
        logger.exception("Failed to fetch turnover")
        return TopStocksResponse(success=False, error=str(e))


@router.get("/summary")
def get_summary() -> SummaryResponse:
    try:
        scraper = _get_scraper()
        data = scraper.get_market_summary()
        if not data or not isinstance(data, list):
            return SummaryResponse(success=False, error="No summary data")
        items = [
            SummaryItem(detail=e["detail"], value=e["value"])
            for e in data if "detail" in e and "value" in e
        ]
        return SummaryResponse(success=True, data=items)
    except Exception as e:
        logger.exception("Failed to fetch summary")
        return SummaryResponse(success=False, error=str(e))
