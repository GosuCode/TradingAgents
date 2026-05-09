"""
NEPSE Stock Analysis - Lightweight Version
Uses TradingAgents data infrastructure with direct analysis
"""

from tradingagents.dataflows.config import set_config
from tradingagents.dataflows.interface import route_to_vendor

from dotenv import load_dotenv
import pandas as pd
from io import StringIO

load_dotenv()

set_config({
    "data_vendors": {
        "core_stock_apis": "nepse",
        "technical_indicators": "nepse",
    }
})

def analyze_stock(symbol: str, days: int = 60):
    end_date = "2026-05-09"
    start_date = "2026-03-10"

    print("="*60)
    print(f"NEPSE STOCK ANALYSIS: {symbol}")
    print("="*60)

    data = route_to_vendor("get_stock_data", symbol, start_date, end_date)

    lines = data.strip().split('\n')
    data_lines = [l for l in lines if l and not l.startswith('#')]

    df = pd.read_csv(StringIO('\n'.join(data_lines)))
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')

    df['sma_10'] = df['close'].rolling(window=10).mean()
    df['sma_20'] = df['close'].rolling(window=20).mean()
    df['sma_50'] = df['close'].rolling(window=50).mean()

    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))

    df['volume_sma'] = df['volume'].rolling(window=20).mean()
    df['vol_ratio'] = df['volume'] / df['volume_sma']

    df['returns'] = df['close'].pct_change()
    df['volatility'] = df['returns'].rolling(window=20).std() * (252**0.5)

    print("\n📊 PRICE DATA (Last 10 days)")
    print("-"*60)
    recent = df.tail(10)[['date', 'open', 'high', 'low', 'close', 'volume']].copy()
    recent['date'] = recent['date'].dt.strftime('%Y-%m-%d')
    print(recent.to_string(index=False))

    latest = df.iloc[-1]
    prev_10 = df.iloc[-11] if len(df) > 10 else df.iloc[0]

    print("\n📈 TECHNICAL INDICATORS")
    print("-"*60)
    print(f"Current Close:    NPR {latest['close']:.2f}")
    print(f"10-Day SMA:        NPR {latest['sma_10']:.2f}" if pd.notna(latest['sma_10']) else "10-Day SMA:       N/A")
    print(f"20-Day SMA:        NPR {latest['sma_20']:.2f}" if pd.notna(latest['sma_20']) else "20-Day SMA:       N/A")
    print(f"50-Day SMA:        NPR {latest['sma_50']:.2f}" if pd.notna(latest['sma_50']) else "50-Day SMA:       N/A")
    print(f"RSI(14):           {latest['rsi']:.2f}")
    print(f"Volatility(20d):   {latest['volatility']*100:.2f}%")

    print("\n📉 TREND ANALYSIS")
    print("-"*60)
    if latest['close'] > latest['sma_20']:
        trend = "🟢 BULLISH"
    elif latest['close'] < latest['sma_20']:
        trend = "🔴 BEARISH"
    else:
        trend = "🟡 NEUTRAL"
    print(f"Trend:             {trend}")

    if latest['rsi'] > 70:
        rsi_zone = "🔴 OVERBOUGHT"
    elif latest['rsi'] < 30:
        rsi_zone = "🟢 OVERSOLD"
    else:
        rsi_zone = "🟡 NEUTRAL"
    print(f"RSI Zone:          {rsi_zone} ({latest['rsi']:.1f})")

    if latest['vol_ratio'] > 1.5:
        vol_status = "🔴 HIGH"
    elif latest['vol_ratio'] < 0.5:
        vol_status = "🟢 LOW"
    else:
        vol_status = "🟡 NORMAL"
    print(f"Volume Status:     {vol_status} ({latest['vol_ratio']:.1f}x avg)")

    price_change = (latest['close'] - prev_10['close']) / prev_10['close'] * 100
    print(f"10-Day Change:     {price_change:+.2f}%")

    print("\n🎯 TRADING SIGNALS")
    print("-"*60)
    signals = []
    if latest['close'] > latest['sma_20']:
        signals.append("✓ Above 20 SMA (Bullish)")
    else:
        signals.append("✗ Below 20 SMA (Bearish)")

    if latest['rsi'] < 30:
        signals.append("✓ RSI Oversold (Buy Signal)")
    elif latest['rsi'] > 70:
        signals.append("✗ RSI Overbought (Sell Signal)")

    if latest['close'] > latest['sma_50']:
        signals.append("✓ Above 50 SMA (Bullish)")
    else:
        signals.append("✗ Below 50 SMA (Bearish)")

    for s in signals:
        print(f"  {s}")

    print("\n" + "="*60)
    print("💡 RECOMMENDATION")
    print("="*60)

    bullish = sum(1 for s in signals if "✓" in s)
    bearish = sum(1 for s in signals if "✗" in s)

    if bullish > bearish + 1:
        action = "🟢 BUY"
        reason = "Multiple bullish indicators"
    elif bearish > bullish + 1:
        action = "🔴 SELL"
        reason = "Multiple bearish indicators"
    elif latest['rsi'] < 35:
        action = "🟡 BUY"
        reason = "RSI oversold, potential bounce"
    elif latest['rsi'] > 65:
        action = "🟡 SELL"
        reason = "RSI overbought, potential pullback"
    else:
        action = "⚪ HOLD"
        reason = "Mixed signals, wait for clarity"

    print(f"\nAction: {action}")
    print(f"Reason: {reason}")

    support = latest['close'] * 0.95
    resistance = latest['close'] * 1.05
    print(f"\nSupport Level:  NPR {support:.2f}")
    print(f"Resistance:     NPR {resistance:.2f}")

    print("\n" + "="*60)
    return action, reason

if __name__ == "__main__":
    action, reason = analyze_stock("CYCL")
    print(f"\nFinal: {action} - {reason}")