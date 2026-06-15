from pydantic import BaseModel
from datetime import datetime


class AnalysisRequest(BaseModel):
    ticker: str
    date: str | None = None
    vendor: str = "nepse"
    llm_provider: str = "openrouter"
    deep_think_llm: str | None = None
    quick_think_llm: str | None = None


class AnalysisStatus(BaseModel):
    task_id: str
    status: str  # queued | running | completed | failed
    progress: int = 0
    message: str = ""
    ticker: str = ""
    created_at: str = ""
    completed_at: str | None = None
    error: str | None = None


class AnalysisReport(BaseModel):
    task_id: str
    ticker: str
    date: str
    decision: str
    rating: str
    summary: str
    reports: dict[str, str] = {}
    created_at: str
