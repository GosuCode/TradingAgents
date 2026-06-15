import json
import uuid
from datetime import datetime

import redis as sync_redis
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException

from backend.app.celery_app import get_task_status, celery_app
from backend.app.config import settings
from backend.app.schemas.analysis import AnalysisRequest, AnalysisStatus, AnalysisReport
from backend.app.tasks.analysis_runner import run_analysis

router = APIRouter(prefix="/api/analysis", tags=["Analysis"])

REDIS_CLIENT = sync_redis.from_url(settings.redis_url)
PUBSUB_CHANNEL = "analysis:progress:{}"


@router.post("")
def start_analysis(body: AnalysisRequest) -> AnalysisStatus:
    task = run_analysis.delay(
        ticker=body.ticker,
        date=body.date,
        vendor=body.vendor,
        llm_provider=body.llm_provider,
        deep_think_llm=body.deep_think_llm,
        quick_think_llm=body.quick_think_llm,
    )
    return AnalysisStatus(
        task_id=task.id,
        status="queued",
        ticker=body.ticker,
        created_at=datetime.now().isoformat(),
    )


@router.get("/{task_id}/status")
def get_status(task_id: str) -> AnalysisStatus:
    status = get_task_status(task_id)
    if status is None:
        raise HTTPException(status_code=404, detail="Task not found")
    data = status.get("data", {}) or {}
    return AnalysisStatus(
        task_id=task_id,
        status=status["status"],
        progress=status["progress"],
        message=status["message"],
        ticker=data.get("ticker", ""),
        created_at="",
        error=status.get("message") if status["status"] == "failed" else None,
    )


@router.get("/{task_id}/report")
def get_report(task_id: str) -> AnalysisReport:
    status = get_task_status(task_id)
    if status is None:
        raise HTTPException(status_code=404, detail="Task not found")
    if status["status"] != "completed":
        raise HTTPException(status_code=400, detail="Analysis not yet completed")
    data = status.get("data", {}) or {}
    return AnalysisReport(
        task_id=task_id,
        ticker=data.get("ticker", ""),
        date=data.get("date", ""),
        decision=data.get("decision", ""),
        rating=data.get("rating", ""),
        summary=data.get("summary", ""),
        created_at=data.get("date", ""),
    )


@router.websocket("/ws/{task_id}")
async def ws_analysis(websocket: WebSocket, task_id: str):
    await websocket.accept()

    pubsub = REDIS_CLIENT.pubsub()
    channel = PUBSUB_CHANNEL.format(task_id)
    pubsub.subscribe(channel)

    try:
        while True:
            msg = pubsub.get_message(timeout=1.0)
            if msg and msg["type"] == "message":
                data = json.loads(msg["data"])
                await websocket.send_json(data)

            # Check for client disconnect
            try:
                await websocket.receive_text()
            except WebSocketDisconnect:
                break
    except WebSocketDisconnect:
        pass
    finally:
        pubsub.unsubscribe(channel)
        pubsub.close()
