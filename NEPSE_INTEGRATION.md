# TradingAgents NEPSE Integration

## Installation

```bash
pip install nepse-scraper pandas stockstats
```

## CLI Usage

```bash
python3 -m cli.main --ticker CYCL --vendor nepse
```

### Options

| Option | Short | Description |
|--------|-------|-------------|
| `--ticker` | `-t` | NEPSE symbol (CYCL, NABIL, HBL, etc.) |
| `--date` | `-d` | Analysis date (YYYY-MM-DD) |
| `--vendor` | | Data source: `nepse`, `yfinance`, `alpha_vantage` |
| `--checkpoint` | | Save state for crash recovery |

## Features

### 1. Live Analysis (CLI)
Analyze stocks in real-time with AI agents.

```bash
python3 -m cli.main --ticker CYCL --vendor nepse
```

### 2. Checkpoint/Resume
Save progress and resume if interrupted.

```bash
# Enable checkpointing
python3 -m cli.main --ticker CYCL --vendor nepse --checkpoint
 
# Clear checkpoints
python3 -m cli.main --ticker CYCL --vendor nepse --clear-checkpoints
```

### 3. Historical Results
All past analyses saved automatically.

```
~/.tradingagents/logs/<TICKER>/<DATE>/
├── complete_report.md      # Full analysis
├── 1_analysts/           # Market, sentiment, news, fundamentals
├── 2_research/           # Bull/Bear debate
├── 3_trading/            # Investment plan
├── 4_risk/               # Risk evaluation
├── 5_portfolio/           # Final decision
└── message_tool.log      # Full conversation
```

View past results:
```bash
cat ~/.tradingagents/logs/CYCL/2026-05-09/complete_report.md
```

## Backtesting

Test TradingAgents decisions on historical data.

```bash
python3 examples/backtest.py CYCL 2026-01-01 2026-05-09
```

### Custom Backtest

```python
from examples.backtest import run_backtest

run_backtest(
    ticker="CYCL",
    start_date="2026-01-01",
    end_date="2026-05-09",
    interval_days=30,
    initial_capital=100000.0
)
```

Output:
```
BACKTEST SUMMARY
==================
Ticker: CYCL
Period: 2026-01-01 to 2026-05-09
Initial Capital: NPR 100,000.00
Final Capital: NPR 110,000.00
Return: 10.00%

Decision breakdown:
  BUY: 5
  SELL: 1
  HOLD: 4
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
print(decision)
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
| MFIL | Mahuli Microfinance |

## Notes

- News data not available for NEPSE
- Uses `nepse-scraper` for real-time data
- Same interface as `yfinance` - just change vendor config