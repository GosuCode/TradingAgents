# TradingAgents Features

A reference of what this project provides. For setup and usage, see [README.md](README.md). For NEPSE-specific details, see [NEPSE_INTEGRATION.md](NEPSE_INTEGRATION.md).

---

## Multi-agent framework

- LangGraph-based pipeline with specialized LLM agents
- Modular analyst selection (enable/disable individual analysts)
- Configurable debate depth (`max_debate_rounds`, `max_risk_discuss_rounds`)
- Dual-model setup: deep-think LLM for reasoning, quick-think LLM for lighter tasks
- Structured output for key agents (Research Manager, Trader, Portfolio Manager, Sentiment Analyst)
- Signal extraction from final decision (5-tier rating: Buy → Sell)
- Python API via `TradingAgentsGraph.propagate(ticker, date)`
- Programmatic and CLI entry points

---

## Agent pipeline

| Stage | Agents | Role |
|-------|--------|------|
| Analysts | Market, Sentiment, News, Fundamentals | Collect data and write section reports |
| Research | Bull, Bear, Research Manager | Debate thesis; manager picks direction |
| Trading | Trader | Turn research into an investment plan |
| Risk | Aggressive, Neutral, Conservative | Challenge the plan from three risk profiles |
| Portfolio | Portfolio Manager | Final Buy / Overweight / Hold / Underweight / Sell decision |

Optional **crypto** pipeline (`asset_type="crypto"`) with crypto-aware instrument context.

---

## Data sources

Per-category vendor configuration (`data_vendors`, `tool_vendors`):

| Category | Vendors | Tools |
|----------|---------|-------|
| Stock prices | yfinance, alpha_vantage, **nepse** | OHLCV history |
| Technical indicators | yfinance, alpha_vantage, **nepse** | MACD, RSI, Bollinger, SMA/EMA, ATR, … |
| Fundamentals | yfinance, alpha_vantage | Financials, balance sheet, cash flow, income statement |
| News | yfinance, alpha_vantage, nepse (stub) | Ticker news, global/macro news |
| Macro | fred | Rates, inflation, labor, growth (requires `FRED_API_KEY`) |
| Prediction markets | polymarket | Event probabilities (keyless) |

**Sentiment sources** (Sentiment Analyst): Yahoo Finance news headlines, StockTwits cashtag stream, Reddit posts.

**Data caching** under `~/.tradingagents/cache/` (OHLCV CSV, NEPSE history, etc.).

---

## Markets

- **Global (yfinance):** US, HK (`.HK`), Tokyo (`.T`), London (`.L`), India (`.NS`, `.BO`), Canada (`.TO`), Australia (`.AX`), China A-shares (`.SS`, `.SZ`), crypto (`BTC-USD`, …)
- **NEPSE:** Nepal Stock Exchange via `nepse-scraper` (`--vendor nepse`)
- **Instrument identity:** deterministic ticker → company/asset lookup before agents run
- **Regional alpha benchmarks:** auto-mapped per exchange suffix (e.g. `^N225` for `.T`, SPY for US); NEPSE Index for NEPSE runs

---

## NEPSE

- Full analysis pipeline with NEPSE OHLCV and technical indicators
- NEPSE Index benchmark for outcome tracking
- Outcome tracking with T+2 settlement and trading-session counting (Sun–Thu)
- CLI: `--vendor nepse` auto-sets benchmark
- Web API: live index, gainers, losers, turnover, market summary
- Script: `scripts/nepse_point.py` for a quick index snapshot
- Example: `examples/nepse_analysis.py`

**NEPSE limitations:** no news API; no portfolio simulator; outcome resolution on re-run, not batch backtest.

---

## LLM providers

| Provider | Notes |
|----------|-------|
| OpenAI | GPT-5.x family, Responses API |
| Google | Gemini, thinking level config |
| Anthropic | Claude, effort config |
| xAI | Grok |
| DeepSeek | |
| Qwen / Qwen-CN | International and China endpoints |
| GLM / GLM-CN | Zhipu, international and China |
| MiniMax / MiniMax-CN | |
| OpenRouter | |
| Mistral, Kimi, Groq, NVIDIA | OpenAI-compatible |
| Ollama | Local models, remote via `OLLAMA_BASE_URL` |
| Azure OpenAI | Enterprise |
| AWS Bedrock | Optional extra install |
| OpenAI-compatible | Any custom endpoint (vLLM, LM Studio, …) |

Configurable via CLI, `default_config.py`, or `TRADINGAGENTS_*` environment variables.

---

## CLI

```bash
tradingagents analyze              # interactive prompts
python3 -m cli.main --ticker …     # direct flags
```

| Flag | Purpose |
|------|---------|
| `--ticker` / `-t` | Symbol to analyze |
| `--date` / `-d` | Analysis date (`YYYY-MM-DD`) |
| `--vendor` | Data vendor (`yfinance`, `alpha_vantage`, `nepse`) |
| `--checkpoint` | Resume interrupted runs |
| `--clear-checkpoints` | Reset saved graph state |

Interactive setup: analyst selection, research depth, LLM provider/model, output language, data vendor.

**Output:** `~/.tradingagents/logs/<TICKER>/<DATE>/` — `complete_report.md`, `reports/*.md`, `message_tool.log`, strategy state JSON.

---

## Web interface

Docker Compose stack: **frontend** (React), **backend** (FastAPI), **worker** (Celery), **Redis**.

| Page / API | Purpose |
|------------|---------|
| Dashboard | NEPSE index, gainers, losers, turnover, summary |
| Analysis | Submit ticker + date + vendor; stream progress |
| Reports | Browse past analysis reports |
| Settings | View LLM and data vendor config |
| `GET /api/nepse/*` | Index, gainers, losers, turnover, summary |
| `POST /api/analysis` | Queue analysis job |
| `WS /api/analysis/ws/{task_id}` | Live progress stream |
| `GET /api/reports` | List saved reports |

---

## Memory and outcome tracking

**Decision log** (always on): append-only markdown at `~/.tradingagents/memory/trading_memory.md`.

1. Each run stores a **pending** decision entry.
2. On the next run for the same ticker, the framework fetches realized returns, computes alpha vs benchmark, and writes an LLM **reflection**.
3. Past decisions and reflections are injected into the Portfolio Manager prompt.

| Market | Return source | Benchmark | Settlement |
|--------|---------------|-----------|------------|
| yfinance | Yahoo Finance | SPY or regional index | Same-day entry |
| NEPSE | nepse_scraper | NEPSE Index | T+2, 5 trading sessions |

Config: `outcome_holding_days`, `outcome_settlement_days`, `memory_log_max_entries`, `TRADINGAGENTS_MEMORY_LOG_PATH`.

---

## Reliability and validation

- **Checkpoint resume:** LangGraph SqliteSaver per ticker; opt-in via `--checkpoint`
- **Verified market snapshot:** deterministic OHLCV + indicators the Market Analyst must cite (#830)
- **Look-ahead bias prevention:** price data filtered to on-or-before analysis date
- **Ticker path safety:** sanitized file paths for results and cache
- **Symbol normalization:** broker symbols (e.g. `XAUUSD` → `GC=F`) for identity and returns

---

## Configuration

- Central defaults in `tradingagents/default_config.py`
- Env overrides: `TRADINGAGENTS_LLM_PROVIDER`, `TRADINGAGENTS_RESULTS_DIR`, `TRADINGAGENTS_CACHE_DIR`, `TRADINGAGENTS_TEMPERATURE`, `TRADINGAGENTS_BENCHMARK_TICKER`, …
- Per-category and per-tool data vendor routing
- Output language for reports and final decision (debate stays English)
- Analyst concurrency limit
- Temperature and provider-specific reasoning/thinking controls

---

## Deployment

- `pip install .` — package + CLI entry point `tradingagents`
- Docker Compose for CLI-only or full web stack
- Ollama profile for local LLM in Docker
- `.env` / `.env.enterprise` for API keys

---

## Not included

- Live order execution or brokerage integration
- Full portfolio backtester (no fees, slippage, circuit limits, position sizing)
- Batch outcome resolution across all tickers (per-ticker on re-run only)
- Guaranteed reproducible LLM output (non-deterministic by design)
- Financial advice — research framework only
