import json
import os
import time
from datetime import datetime

import redis as sync_redis

from backend.app.celery_app import celery_app
from backend.app.config import settings

REDIS_CLIENT = sync_redis.from_url(settings.redis_url)
PUBSUB_CHANNEL = "analysis:progress:{}"


def _publish(task_id: str, msg: dict):
    """Publish a progress message to Redis pub/sub."""
    channel = PUBSUB_CHANNEL.format(task_id)
    REDIS_CLIENT.publish(channel, json.dumps(msg))


def _update_meta(task_id: str, **kwargs):
    """Update Celery task metadata (for polling)."""
    celery_app.backend.store_result(task_id, kwargs, state="STARTED")


@celery_app.task(bind=True, max_retries=0)
def run_analysis(self, ticker: str, date: str | None, vendor: str, llm_provider: str,
                 deep_think_llm: str | None, quick_think_llm: str | None):
    task_id = self.request.id
    _publish(task_id, {"type": "log", "data": f"Starting analysis for {ticker}..."})
    _update_meta(task_id, progress=5, message="Initializing agents...")

    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    try:
        from tradingagents.default_config import DEFAULT_CONFIG
        from tradingagents.graph.trading_graph import TradingAgentsGraph

        config = DEFAULT_CONFIG.copy()
        config["llm_provider"] = llm_provider
        if vendor:
            config["data_vendors"] = {
                "core_stock_apis": vendor,
                "technical_indicators": vendor,
                "fundamental_data": vendor,
                "news_data": vendor,
            }
        if deep_think_llm:
            config["deep_think_llm"] = deep_think_llm
        if quick_think_llm:
            config["quick_think_llm"] = quick_think_llm

        _publish(task_id, {"type": "log", "data": f"Config loaded. Building graph..."})
        _update_meta(task_id, progress=15, message="Building agent graph...")

        graph = TradingAgentsGraph(config=config, debug=True)

        _publish(task_id, {"type": "log", "data": f"Starting propagation for {ticker} on {date}..."})
        _update_meta(task_id, progress=25, message=f"Running analyst team for {ticker}...")

        final_state, decision = graph.propagate(ticker, date)

        _publish(task_id, {"type": "log", "data": f"Analysis complete. Decision: {decision}"})
        _update_meta(task_id, progress=100, message="Analysis complete")

        rating = ""
        summary = ""
        if isinstance(final_state, dict):
            pm = final_state.get("final_trade_decision", "")
            if isinstance(pm, dict):
                rating = pm.get("rating", "")
                summary = pm.get("executive_summary", "")
            elif isinstance(pm, str):
                from tradingagents.graph.signal_processing import SignalProcessor
                sp = SignalProcessor()
                rating = sp.process_signal(pm)

        result = {
            "decision": str(decision),
            "rating": rating,
            "summary": summary,
            "ticker": ticker,
            "date": date,
        }

        _publish(task_id, {"type": "complete", "data": result})
        return result

    except Exception as e:
        _publish(task_id, {"type": "error", "data": str(e)})
        _update_meta(task_id, progress=0, message=f"Failed: {str(e)}")
        raise
