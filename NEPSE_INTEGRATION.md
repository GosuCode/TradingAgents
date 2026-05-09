# TradingAgents NEPSE Integration

## Quick Start

```bash
# Analyze any NEPSE stock via CLI
python -m cli.main --ticker CYCL --vendor nepse
python -m cli.main --ticker NABIL --vendor nepse
python -m cli.main --ticker HBL --vendor nepse
python -m cli.main --ticker MEN --vendor nepse
```

## CLI Options

```bash
python -m cli.main [OPTIONS]

Options:
  --ticker, -t TEXT    Ticker symbol (e.g., CYCL, NABIL, NVDA)
  --date, -d TEXT      Analysis date (YYYY-MM-DD)
  --vendor TEXT        Data vendor: yfinance, alpha_vantage, nepse
  --checkpoint         Enable checkpoint/resume
```

## Python Usage

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

config = DEFAULT_CONFIG.copy()
config["data_vendors"] = {
    "core_stock_apis": "nepse",
    "technical_indicators": "nepse",
}

ta = TradingAgentsGraph(debug=True, config=config)
_, decision = ta.propagate("CYCL", "2026-05-09")
```

## Installation

```bash
pip install nepse-scraper pandas stockstats
```

## Popular NEPSE Symbols

| Symbol | Company |
|--------|---------|
| NABIL | Nabil Bank |
| HBL | Himalayan Bank |
| EBL | Everest Bank |
| NMB | NMB Bank |
| MEN | Mountain Energy Nepal |
| CYCL | Nepal Cyclist Laghubitta |
| NIFRA | Nepal Infrastructure Bank |

## Notes

- News data not available for NEPSE
- Uses `nepse-scraper` package for data
- Works same as `yfinance` vendor - just change config to `"nepse"`

## Results

Analysis reports are saved to:
```
~/.tradingagents/logs/<TICKER>/<DATE>/
```

Example:
```
~/.tradingagents/logs/CYCL/2026-05-09/
├── complete_report.md      # Full analysis
├── 1_analysts/             # Market, sentiment, news, fundamentals
├── 2_research/             # Investment plan
├── 3_trading/              # Trader plan
├── 4_risk/                 # Risk analysis
├── 5_portfolio/            # Final decision
└── message_tool.log        # All chat/tool calls
```
