"""
NEPSE Stock Analysis using TradingAgents Framework
Analyzes CYCL (Nepal Cyclist Laghubitta Bittiya Sanstha)
"""

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.dataflows.config import set_config

from dotenv import load_dotenv
import os

load_dotenv()

config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "openrouter"
config["deep_think_llm"] = "anthropic/claude-3.5-haiku"
config["quick_think_llm"] = "anthropic/claude-3.5-haiku"
config["max_debate_rounds"] = 1
config["backend_url"] = "https://openrouter.ai/api/v1"
config["max_tokens"] = 2048

config["data_vendors"] = {
    "core_stock_apis": "nepse",
    "technical_indicators": "nepse",
    "fundamental_data": "nepse",
    "news_data": "nepse",
}

config["output_language"] = "English"

print("="*60)
print("NEPSE STOCK ANALYSIS - CYCL (TradingAgents Framework)")
print("="*60)
print(f"LLM Provider: OpenRouter")
print(f"Model: {config['deep_think_llm']}")
print(f"Data Source: NEPSE (nepalstock.com)")
print()

ta = TradingAgentsGraph(debug=True, config=config)

print("Running multi-agent analysis...")
print("-"*40)
_, decision = ta.propagate("CYCL", "2026-05-09")

print("\n" + "="*60)
print("TRADING DECISION FOR CYCL")
print("="*60)
print(decision)