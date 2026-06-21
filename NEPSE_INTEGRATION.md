# NEPSE Integration

TradingAgents uses `nepse-scraper` for Nepal Stock Exchange data. Set `--vendor nepse` (or the config below) — everything else works the same as the yfinance path.

## Install

```bash
pip install nepse-scraper pandas stockstats
```

## CLI

```bash
python3 -m cli.main --ticker CYCL --vendor nepse
python3 -m cli.main --ticker CYCL --vendor nepse --date 2026-05-09
python3 -m cli.main --ticker CYCL --vendor nepse --checkpoint   # resume on crash
```

| Option            | Description                        |
| ----------------- | ---------------------------------- |
| `--ticker` / `-t` | NEPSE symbol (CYCL, NABIL, HBL, …) |
| `--date` / `-d`   | Analysis date (`YYYY-MM-DD`)       |
| `--vendor`        | Set to `nepse`                     |
| `--checkpoint`    | Save graph state for resume        |

## Python

```python
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.graph.trading_graph import TradingAgentsGraph

config = DEFAULT_CONFIG.copy()
config["data_vendors"] = {
    "core_stock_apis": "nepse",
    "technical_indicators": "nepse",
    "fundamental_data": "nepse",
    "news_data": "nepse",
}
config["benchmark_ticker"] = "NEPSE Index"  # auto-set by CLI when --vendor nepse

ta = TradingAgentsGraph(config=config)
_, decision = ta.propagate("CYCL", "2026-05-09")
```

See `examples/nepse_analysis.py` for a full example.

## Outcome tracking

After each run, the decision is logged as **pending**. On the next run for the same ticker, the framework:

1. Fetches returns from NEPSE (not yfinance)
2. Computes alpha vs the NEPSE Index
3. Writes an LLM reflection into the memory log
4. Injects past reflections into future analyses

NEPSE-specific behavior:

- **Benchmark:** NEPSE Index (via `nepse_scraper`)
- **T+2 settlement:** entry at close 2 trading sessions after the decision date
- **Holding period:** 5 trading sessions after entry (Sun–Thu calendar)
- **Too recent:** skipped until enough sessions exist; retried on the next run

Config (defaults shown):

```python
config["outcome_holding_days"] = 5       # sessions held after settlement
config["outcome_settlement_days"] = 2    # T+2
config["memory_log_path"] = "~/.tradingagents/memory/trading_memory.md"
```

This is **not** a portfolio simulator — no position sizing, fees, slippage, or circuit-limit modeling.

## Output

Results are saved under `~/.tradingagents/logs/<TICKER>/<DATE>/`:

```
complete_report.md
reports/           # per-section markdown
message_tool.log
```

## NEPSE index snapshot

```bash
python3 scripts/nepse_point.py
```

## Limitations

- No news API for NEPSE (social/news analysts have limited data)
- Outcome resolution is per-ticker on re-run, not batch backtest
- Circuit limits and full settlement rules are not simulated
