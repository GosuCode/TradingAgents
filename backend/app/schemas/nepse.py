from pydantic import BaseModel


class IndexEntry(BaseModel):
    name: str
    close: float
    current_value: float
    high: float
    low: float
    previous_close: float
    change: float
    per_change: float
    fifty_two_week_high: float
    fifty_two_week_low: float
    generated_time: str


class IndexResponse(BaseModel):
    success: bool
    data: IndexEntry | None = None
    error: str | None = None


class TopStockItem(BaseModel):
    symbol: str
    security_name: str
    ltp: float | None = None
    point_change: float | None = None
    percentage_change: float | None = None
    turnover: float | None = None
    closing_price: float | None = None


class TopStocksResponse(BaseModel):
    success: bool
    data: list[TopStockItem] = []
    error: str | None = None


class SummaryItem(BaseModel):
    detail: str
    value: float


class SummaryResponse(BaseModel):
    success: bool
    data: list[SummaryItem] = []
    error: str | None = None
