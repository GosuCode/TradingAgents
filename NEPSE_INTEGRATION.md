# TradingAgents NEPSE (Nepal Stock Exchange) Integration

<p align="center">
  <img src="assets/TauricResearch.png" style="width: 60%; height: auto;">
</p>

<div align="center">
  <a href="https://www.nepalstock.com" target="_blank"><img alt="NEPSE" src="https://img.shields.io/badge/NEPSE-Nepal%20Stock%20Exchange-2E7D32?style=flat-square&logo=ledger"/></a>
  <a href="https://discord.com/invite/hk9PGKShPK" target="_blank"><img alt="Discord" src="https://img.shields.io/badge/Discord-TradingResearch-7289da?logo=discord&logoColor=white&color=7289da"/></a>
  <a href="https://github.com/TauricResearch/TradingAgents" target="_blank"><img alt="GitHub" src="https://img.shields.io/badge/GitHub-TradingAgents-181717?style=flat-square&logo=github"/></a>
</div>

---

## Table of Contents

- [Quick Start](#quick-start)
- [How to Analyze Any NEPSE Symbol](#how-to-analyze-any-nepse-symbol)
- [Overview](#overview)
- [What is NEPSE?](#what-is-nepse)
- [Installation](#installation)
- [NEPSE Data Adapter Setup](#nepse-data-adapter-setup)
- [Configuration](#configuration)
- [Usage](#usage)
- [Available Functions](#available-functions)
- [NEPSE Stock Symbols](#nepse-stock-symbols)
- [Example Scripts](#example-scripts)
- [Troubleshooting](#troubleshooting)
- [Technical Details](#technical-details)
- [Contributing](#contributing)

---

## Quick Start

### Analyze any NEPSE symbol in 3 steps:

```bash
# 1. Navigate to project directory
cd /path/to/TradingAgents

# 2. Run the lightweight analysis script with your desired symbol
python examples/nepse_analysis_light.py MEN

# 3. That's it! See detailed technical analysis instantly
```

---

## How to Analyze Any NEPSE Symbol

### Method 1: Lightweight Analysis (Fast, No API credits needed)

```bash
# Analyze any symbol by passing it as argument
python examples/nepse_analysis_light.py NABIL    # Nabil Bank
python examples/nepse_analysis_light.py HBL       # Himalayan Bank
python examples/nepse_analysis_light.py MEN      # Mountain Energy Nepal
python examples/nepse_analysis_light.py CYCL     # Nepal Cyclist Laghubitta
python examples/nepse_analysis_light.py NIFRA    # Nepal Infrastructure Bank

# View help
python examples/nepse_analysis_light.py --help
```

### Method 2: Full TradingAgents Analysis (AI-powered multi-agent)

```bash
# 1. Edit examples/nepse_analysis_cycl.py and change the symbol
# Line 44: _, decision = ta.propagate("CYCL", "2026-05-09")
# Change "CYCL" to your desired symbol

# 2. Run
python examples/nepse_analysis_cycl.py
```

### Method 3: Interactive Mode

```bash
# Launch the TradingAgents CLI
tradingagents

# Note: Configure NEPSE as data source when prompted
```

### Method 4: Custom Python Script

```python
from tradingagents.dataflows.config import set_config
from tradingagents.dataflows.interface import route_to_vendor

# Configure for NEPSE
set_config({
    "data_vendors": {
        "core_stock_apis": "nepse",
    }
})

# Analyze any symbol
symbol = "NABIL"  # Change this to any NEPSE symbol
end_date = "2026-05-09"
start_date = "2026-03-10"

data = route_to_vendor("get_stock_data", symbol, start_date, end_date)
print(data)
```

### Method 5: Get List of Available Symbols

```python
from tradingagents.dataflows.nepse import get_nepse_top_gainers

# Get current trading symbols (top gainers shows active symbols)
gainers = get_nepse_top_gainers()
print(gainers)
```

---

## Overview

This document describes the NEPSE (Nepal Stock Exchange) integration for the TradingAgents framework. It allows users to analyze and trade NEPSE-listed stocks using the same multi-agent LLM framework that works with global markets.

## What is NEPSE?

NEPSE (Nepal Stock Exchange) is the only stock exchange in Nepal, operating under the Nepal Securities Board. It facilitates trading of:
- Commercial banks
- Development banks
- Hydropower companies
- Corporate bonds
- Mutual funds
- Insurance companies

### Key Characteristics

| Aspect | Details |
|--------|---------|
| Trading Hours | Sunday-Thursday, 11:00 AM - 3:00 PM NPT |
| Settlement | T+2 (Trade + 2 business days) |
| Currency | Nepalese Rupee (NPR) |
| Index | NEPSE Sensitive Index (NEPSE Index) |
| Exchange Code | NEPALI (for international reference) |

---

## Installation

### Prerequisites

1. Python 3.10 or higher
2. pip or conda
3. Git
4. API keys for LLM providers (OpenAI, Anthropic, Google, etc.) - optional for lightweight analysis

### Step 1: Clone TradingAgents

```bash
git clone https://github.com/TauricResearch/TradingAgents.git
cd TradingAgents
```

### Step 2: Create Virtual Environment

```bash
# Using conda
conda create -n tradingagents python=3.13
conda activate tradingagents

# Or using venv
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

### Step 3: Install Core Dependencies

```bash
pip install .
```

### Step 4: Install NEPSE Dependencies

```bash
pip install nepse-scraper pandas
```

> **Note**: The `nepse-scraper` package fetches real-time data from nepalstock.com. It requires SSL verification to be disabled due to certificate issues on the NEPSE website.

---

## NEPSE Data Adapter Setup

The NEPSE adapter is pre-installed at `tradingagents/dataflows/nepse.py`. It uses the `nepse-scraper` package to fetch live data from NEPSE.

### Files Modified/Created

| File | Description |
|------|-------------|
| `tradingagents/dataflows/nepse.py` | NEPSE data source adapter |
| `tradingagents/dataflows/interface.py` | Updated to route to NEPSE vendor |
| `examples/nepse_analysis_light.py` | Lightweight analysis script |
| `examples/nepse_analysis_cycl.py` | Full TradingAgents example |

### Understanding the Adapter

```
┌─────────────────────────────────────────────────────────┐
│                  TradingAgents Framework                  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│   ┌─────────────────┐     ┌─────────────────────────┐  │
│   │   Interface     │────▶│  Vendor Routing         │  │
│   │   (route_to     │     │  ┌─────────┐ ┌────────┐ │  │
│   │    _vendor)     │     │  │yfinance │ │  NEPSE │ │  │
│   └─────────────────┘     │  └─────────┘ └────────┘ │  │
│                            └─────────────────────────┘  │
│                                         │                │
│                            ┌────────────┴───────────┐   │
│                            │                         │   │
│                    ┌───────▼──────┐          ┌──────▼──┐ │
│                    │  nepse_scraper│          │ yfinance│ │
│                    │              │          │         │ │
│                    │   nepalstock.com         │         │ │
│                    └──────────────┘          └─────────┘ │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Configuration

### Method 1: Using set_config() in Python

```python
from tradingagents.dataflows.interface import set_config

set_config({
    "data_vendors": {
        "core_stock_apis": "nepse",
        "technical_indicators": "nepse",
        "fundamental_data": "nepse",
        "news_data": "nepse",
    }
})
```

### Method 2: Environment Variables

```bash
export TRADINGAGENTS_DATA_VENDOR_CORE="nepse"
export TRADINGAGENTS_DATA_VENDOR_TECHNICAL="nepse"
```

### Method 3: CLI Configuration

When using the CLI, select NEPSE-compatible settings or modify the configuration file at `~/.tradingagents/config.json`.

---

## Usage

### Basic Python Usage

```python
from tradingagents.dataflows.nepse import get_stock_data, get_nepse_summary

# Get historical data for a stock
data = get_stock_data(
    symbol="NABIL",
    start_date="2026-01-01",
    end_date="2026-05-09"
)
print(data)

# Get market summary
summary = get_nepse_summary()
print(summary)
```

### Using with TradingAgents

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.dataflows.interface import set_config

# Configure for NEPSE
set_config({
    "data_vendors": {
        "core_stock_apis": "nepse",
    }
})

# Initialize TradingAgents
ta = TradingAgentsGraph(debug=True)

# Run analysis on a NEPSE stock
_, decision = ta.propagate("NABIL", "2026-05-09")
print(decision)
```

### CLI Usage

```bash
# Launch interactive CLI
tradingagents

# Or run directly
python -m cli.main

# Analyze a NEPSE stock with checkpoint enabled
tradingagents analyze --ticker NABIL --date 2026-05-09 --checkpoint
```

---

## Available Functions

### Core Data Functions

| Function | Description | Parameters |
|----------|-------------|------------|
| `get_stock_data` | Get OHLCV data for a stock | `symbol`, `start_date`, `end_date` |
| `get_nepse_price_history` | Get last N days of data | `symbol`, `days` (default: 30) |
| `get_nepse_summary` | Get market summary | None |
| `get_nepse_top_gainers` | Top gaining stocks | `date` (optional) |
| `get_nepse_top_losers` | Top losing stocks | `date` (optional) |
| `get_nepse_index` | NEPSE Sensitive Index | `date` (optional) |
| `get_news` | News for stock (NEPSE: not available) | `ticker`, `start_date`, `end_date` |
| `get_global_news` | Global news (NEPSE: not available) | `curr_date`, `look_back_days`, `limit` |

### Example Output

```csv
# NEPSE stock data for MEN from 2026-05-01 to 2026-05-09
# Total records: 8
# Data retrieved on: 2026-05-09 10:28:03

date,open,high,low,close,volume,symbol
2026-05-04,570.0,622.0,570.0,577.9,53954,MEN
2026-05-05,577.9,584.8,571.0,579.0,40179,MEN
2026-05-06,581.0,587.0,579.3,583.0,32249,MEN
2026-05-07,580.0,590.0,576.9,589.0,35558,MEN
2026-05-08,598.0,598.9,585.0,590.0,18171,MEN
```

---

## NEPSE Stock Symbols

### Banks

| Symbol | Company Name |
|--------|--------------|
| NABIL | Nabil Bank Limited |
| EBL | Everest Bank Limited |
| HBL | Himalayan Bank Limited |
| NMB | NMB Bank Limited |
| SBL | Standard Chartered Bank Nepal |
| NICA | NIC Asia Bank Limited |
| CZBIL | CZ Bank Limited |

### Hydropower Companies

| Symbol | Company Name |
|--------|--------------|
| MEN | Mountain Energy Nepal Limited |
| NIFRA | Nepal Infrastructure Bank |
| KFL | Kalika Power Company Limited |
| AKPL | Arun Kabeli Power Limited |
| HPPL | Himshikhar Power Limited |

### Microfinance (Laghubitta)

| Symbol | Company Name |
|--------|--------------|
| CYCL | Nepal Cyclist Laghubitta Bittiya Sanstha |
| MSBB | Muktinath Bikas Bank |
| SLBS | Sufi Mikro Laghubitta Bittiya Sanstha |
| NMFBS | National Microfinance Bittiya Sanstha |

### Insurance Companies

| Symbol | Company Name |
|--------|--------------|
| NLIC | Nepal Life Insurance Company |
| LICN | Life Insurance Corporation Nepal |
| UNL | Union Insurance Company |

### Other Companies

| Symbol | Company Name |
|--------|--------------|
| NOC | Nepal Oil Corporation |
| GPI | General Insurance Nepal |
| HPL | Hydroelectricity Company Limited |

> **Note**: This is a partial list. For complete symbol listings, visit [nepalstock.com](https://www.nepalstock.com) or use `get_nepse_top_gainers()` to see current trading symbols.

---

## Example Scripts

### Example 1: Lightweight Analysis (Recommended for quick checks)

```python
# examples/nepse_analysis_light.py
from tradingagents.dataflows.config import set_config
from tradingagents.dataflows.interface import route_to_vendor

set_config({
    "data_vendors": {
        "core_stock_apis": "nepse",
    }
})

# Get data
data = route_to_vendor("get_stock_data", "NABIL", "2026-03-10", "2026-05-09")
print(data)
```

Run:
```bash
python examples/nepse_analysis_light.py NABIL
```

### Example 2: Full TradingAgents with OpenRouter

```python
# examples/nepse_analysis_cycl.py
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.dataflows.config import set_config

config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "openrouter"
config["deep_think_llm"] = "anthropic/claude-3.5-haiku"
config["quick_think_llm"] = "anthropic/claude-3.5-haiku"
config["backend_url"] = "https://openrouter.ai/api/v1"
config["data_vendors"] = {
    "core_stock_apis": "nepse",
}

ta = TradingAgentsGraph(debug=True, config=config)
_, decision = ta.propagate("CYCL", "2026-05-09")
print(decision)
```

Run:
```bash
python examples/nepse_analysis_cycl.py
```

### Example 3: Custom Analysis Script

```python
# my_nepse_analysis.py
import sys
from tradingagents.dataflows.config import set_config
from tradingagents.dataflows.interface import route_to_vendor
import pandas as pd

set_config({"data_vendors": {"core_stock_apis": "nepse"}})

symbol = sys.argv[1] if len(sys.argv) > 1 else "NABIL"
data = route_to_vendor("get_stock_data", symbol, "2026-03-10", "2026-05-09")
print(data)
```

Run:
```bash
python my_nepse_analysis.py NABIL
python my_nepse_analysis.py HBL
python my_nepse_analysis.py MEN
```

---

## Troubleshooting

### Common Issues

#### 1. nepse-scraper not installed

```bash
pip install nepse-scraper
```

#### 2. SSL Certificate Warnings

These warnings are normal and expected. The `nepse-scraper` disables SSL verification due to certificate issues on nepalstock.com. This is handled automatically.

```
InsecureRequestWarning: Unverified HTTPS request
```

To suppress these warnings in your script:

```python
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
```

#### 3. No data found for symbol

- Verify the symbol is correct (uppercase)
- Check if the company is still listed on NEPSE
- Try a different date range

```python
from tradingagents.dataflows.nepse import get_nepse_top_gainers

# Get current trading symbols
gainers = get_nepse_top_gainers()
print(gainers)
```

#### 4. Rate Limiting

NEPSE may rate-limit requests. The adapter includes built-in delays, but if you encounter issues:

```python
import time
time.sleep(1)  # Add delay between requests
```

#### 5. Connection Errors

If you get connection errors, check your internet connection and try again later. NEPSE servers may be unavailable during:
- Non-trading hours
- System maintenance
- High traffic periods

#### 6. API Credits Exhausted (for full TradingAgents)

If you see "This request requires more credits" error:
- Upgrade your OpenRouter credits at https://openrouter.ai/settings/credits
- Or use the lightweight analysis script which doesn't require LLM API

---

## Technical Details

### Data Flow Architecture

```
User Request
     │
     ▼
┌────────────────────┐
│  route_to_vendor   │
│   (interface.py)   │
└────────┬───────────┘
         │
    ┌────▼────┐
    │ Category │
    │ Config  │
    └────┬────┘
         │
    ┌────▼────────┐
    │ NEPSE Vendor │
    └────┬─────────┘
         │
    ┌────▼─────────────┐
    │  nepse.py        │
    │ (Data Adapter)    │
    └────┬─────────────┘
         │
    ┌────▼──────────────┐
    │  NepseScraper     │
    │ (nepse-scraper)   │
    └────┬──────────────┘
         │
    ┌────▼─────────────┐
    │  nepalstock.com  │
    │   (NEPSE API)    │
    └──────────────────┘
```

### Response Format

The NEPSE adapter returns data in CSV format, compatible with other TradingAgents data sources:

```csv
# Header with metadata
# NEPSE stock data for <SYMBOL> from <START> to <END>
# Total records: <COUNT>
# Data retrieved on: <TIMESTAMP>

date,open,high,low,close,volume,symbol
YYYY-MM-DD,<open>,<high>,<low>,<close>,<volume>,<symbol>
```

### Error Handling

All functions return error messages as strings rather than raising exceptions, ensuring graceful handling in the agent workflow:

```python
result = get_stock_data("INVALID", "2026-01-01", "2026-05-09")
# Returns: "No data found for 'INVALID' on NEPSE between 2026-01-01 and 2026-05-09"
```

---

## Contributing

Contributions to improve the NEPSE integration are welcome! Areas for contribution:

- Additional data functions
- Improved error handling
- Technical indicator support for NEPSE
- Fundamental data integration
- Documentation improvements

To contribute:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

For questions or discussions, join our [Discord community](https://discord.com/invite/hk9PGKShPK).

---

## References

- [TradingAgents GitHub](https://github.com/TauricResearch/TradingAgents)
- [NEPSE Official Website](https://www.nepalstock.com)
- [nepse-scraper Package](https://pypi.org/project/nepse-scraper/)
- [NEPSE API Documentation](https://www.nepalstock.com/api)

---

<div align="center">

**TradingAgents NEPSE Integration** | Part of the [Tauric Research](https://tauric.ai/) Open-Source Framework

*Disclaimer: This integration is for research and educational purposes. Trading decisions should be made with caution and proper financial advice.*

</div>