import os
from pathlib import Path

from fastapi import APIRouter, HTTPException

from tradingagents.dataflows.config import get_config

router = APIRouter(prefix="/api/reports", tags=["Reports"])


def _results_dir() -> Path:
    return Path(get_config()["results_dir"])


@router.get("")
def list_reports():
    """List all available ticker/date report directories."""
    base = _results_dir()
    if not base.is_dir():
        return []

    entries = []
    for ticker_dir in sorted(base.iterdir()):
        if not ticker_dir.is_dir():
            continue
        ticker = ticker_dir.name
        for date_dir in sorted(ticker_dir.iterdir(), reverse=True):
            if not date_dir.is_dir():
                continue
            reports_dir = date_dir / "reports"
            if not reports_dir.is_dir():
                continue
            sections = sorted(
                ({"name": p.stem.replace("_", " ").title(), "file": p.name}
                 for p in reports_dir.iterdir()
                 if p.suffix.lower() == ".md"),
                key=lambda s: s["name"],
            )
            if sections:
                entries.append({
                    "ticker": ticker,
                    "date": date_dir.name,
                    "sections": sections,
                })
    return entries


@router.get("/{ticker}/{date}")
def get_report(ticker: str, date: str):
    """Return all report sections for a ticker/date as markdown content."""
    reports_dir = _results_dir() / ticker / date / "reports"
    if not reports_dir.is_dir():
        raise HTTPException(status_code=404, detail="Report not found")

    sections = []
    for p in sorted(reports_dir.iterdir()):
        if p.suffix.lower() != ".md":
            continue
        try:
            content = p.read_text(encoding="utf-8")
        except Exception:
            content = ""
        sections.append({
            "name": p.stem.replace("_", " ").title(),
            "file": p.name,
            "content": content,
        })

    if not sections:
        raise HTTPException(status_code=404, detail="No report sections found")

    return {
        "ticker": ticker,
        "date": date,
        "sections": sections,
    }
