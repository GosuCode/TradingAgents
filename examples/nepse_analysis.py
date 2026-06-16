"""
NEPSE Analysis - Same pattern as main.py

To analyze any NEPSE stock, just change:
1. data_vendors from "yfinance" to "nepse"
2. The ticker symbol to a NEPSE symbol (e.g., NABIL, HBL, CYCL, MEN)
"""

from dotenv import load_dotenv

from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.graph.trading_graph import TradingAgentsGraph

load_dotenv()

config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "openrouter"
config["deep_think_llm"] = "anthropic/claude-3.5-haiku"
config["quick_think_llm"] = "anthropic/claude-3.5-haiku"
config["max_debate_rounds"] = 1
config["backend_url"] = "https://openrouter.ai/api/v1"

# Use NEPSE instead of yfinance - everything else stays the same!
config["data_vendors"] = {
    "core_stock_apis": "nepse",
    "technical_indicators": "nepse",
    "fundamental_data": "nepse",
    "news_data": "nepse",
}

ta = TradingAgentsGraph(debug=True, config=config)

# Analyze any NEPSE symbol - just change the ticker!
# Options: NABIL, HBL, EBL, NMB, MEN, CYCL, NIFRA, etc.
_, decision = ta.propagate("CYCL", "2026-05-09")
print(decision)
