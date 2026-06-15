import os
from celery import Celery

from backend.app.config import settings

celery_app = Celery(
    "tradingagents",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kathmandu",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)


from backend.app.tasks import analysis_runner  # noqa: F401


def get_task_status(task_id: str) -> dict | None:
    """Fetch task result/status from Celery backend."""
    result = celery_app.AsyncResult(task_id)
    if result.state == "PENDING":
        return {"status": "queued", "progress": 0, "message": "Waiting to start"}
    elif result.state == "STARTED":
        meta = result.info or {}
        return {"status": "running", "progress": meta.get("progress", 0), "message": meta.get("message", "")}
    elif result.state == "SUCCESS":
        return {"status": "completed", "progress": 100, "message": "Analysis complete", "data": result.result}
    elif result.state == "FAILURE":
        return {"status": "failed", "progress": 0, "message": str(result.info or "Unknown error")}
    else:
        return {"status": result.state.lower(), "progress": 0, "message": ""}
