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

### 3. Quick NEPSE Index Check
Check the current NEPSE benchmark index, change, and market summary with one command:

```bash
python3 scripts/nepse_point.py
```

Example output:
```
NEPSE Index: 2,711.76
  ▼ -12.27 (-0.45%)
  High: 2,729.60  |  Low: 2,705.04
  52W High: 3,002.08  |  52W Low: 2,487.18
  As of: 2026-06-15T15:29:07.53

Market is CLOSED
  Turnover: NPR 4.41B
  Volume: 10,739,998 shares
  Transactions: 51,702

Top Gainers
  Symbol              LTP     Change  %Change
  SOPL             611.40     +79.70  +14.99%
  APHL             523.90     +68.30  +14.99%
  SPHL             633.00     +29.10   +4.82%
  NICAD85/86     1,217.90     +48.90   +4.18%
  SYPNL          1,463.00     +58.00   +4.13%

Top Losers
  Symbol              LTP     Change  %Change
  GRDBL          1,113.00     -96.00   -7.94%
  RAWA             500.00     -38.00   -7.06%
  CFCL             620.00     -39.00   -5.92%
  NRIC             999.00     -43.00   -4.13%
  NFS              606.00     -21.90   -3.49%

Top by Turnover
  Symbol                 Turnover      Price
  AKJCL            388,506,473.30     397.00
  NBBD2085         270,458,382.90   1,158.70
  LSL              228,887,240.70     219.50
  SYPNL            209,045,886.60   1,463.00
  RSML             162,458,794.30   3,460.00
```

### 4. Historical Results
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