"""NEPSE outcome tracking for memory/reflection Phase B."""

from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from tradingagents.dataflows.nepse import (
    NEPSE_BENCHMARK_LABEL,
    _compute_session_return,
    fetch_nepse_returns,
)
from tradingagents.graph.trading_graph import TradingAgentsGraph


def _sessions(closes: list[float], start: str = "2026-05-01") -> pd.DataFrame:
    """Build aligned session rows (daily for test simplicity)."""
    dates = pd.date_range(start, periods=len(closes), freq="D")
    return pd.DataFrame({"date": dates, "close_stock": closes, "close_index": [100.0 + i for i in range(len(closes))]})


class TestComputeSessionReturn:
    def test_full_holding_period(self):
        # settlement=2 → entry at session T+2 (idx 2 = 102), exit 5 sessions later (idx 7 = 107)
        sessions = _sessions([100, 101, 102, 103, 104, 105, 106, 107, 108])
        raw, days = _compute_session_return(sessions, "close_stock", settlement_days=2, holding_days=5)
        assert raw == pytest.approx((107 - 102) / 102)
        assert days == 5

    def test_too_recent_returns_none(self):
        sessions = _sessions([100, 101, 102, 103, 104, 105, 106])  # need idx 7
        raw, days = _compute_session_return(sessions, "close_stock", settlement_days=2, holding_days=5)
        assert raw is None and days is None

    def test_zero_entry_price_returns_none(self):
        sessions = _sessions([0, 0, 0, 100, 110, 120, 130, 140])
        raw, days = _compute_session_return(sessions, "close_stock", settlement_days=2, holding_days=3)
        assert raw is None and days is None


class TestFetchNepseReturns:
    def test_returns_raw_alpha_and_days(self):
        stock_df = pd.DataFrame({
            "date": pd.date_range("2026-05-01", periods=10, freq="D"),
            "close": [100.0, 101, 102, 103, 104, 105, 106, 107, 108, 109],
        })
        index_df = pd.DataFrame({
            "date": pd.date_range("2026-05-01", periods=10, freq="D"),
            "close": [2700.0 + i for i in range(10)],
        })

        with patch("tradingagents.dataflows.nepse._fetch_nepse_price_df", return_value=stock_df), \
             patch("tradingagents.dataflows.nepse._fetch_nepse_index_df", return_value=index_df):
            raw, alpha, days = fetch_nepse_returns("CYCL", "2026-05-01", holding_days=5, settlement_days=2)

        assert days == 5
        assert raw is not None and alpha is not None
        # entry idx 2 = 102, exit idx 7 = 107
        assert raw == pytest.approx((107 - 102) / 102)
        bench_ret = (2707.0 - 2702.0) / 2702.0
        assert alpha == pytest.approx(raw - bench_ret)

    def test_too_recent_returns_none(self):
        stock_df = pd.DataFrame({
            "date": pd.date_range("2026-06-15", periods=3, freq="D"),
            "close": [100.0, 101, 102],
        })
        index_df = pd.DataFrame({
            "date": pd.date_range("2026-06-15", periods=3, freq="D"),
            "close": [2700.0, 2701, 2702],
        })

        with patch("tradingagents.dataflows.nepse._fetch_nepse_price_df", return_value=stock_df), \
             patch("tradingagents.dataflows.nepse._fetch_nepse_index_df", return_value=index_df):
            raw, alpha, days = fetch_nepse_returns("CYCL", "2026-06-15", holding_days=5, settlement_days=2)

        assert raw is None and alpha is None and days is None


class TestTradingGraphNepseRouting:
    def test_resolve_benchmark_nepse_vendor(self):
        mock_graph = MagicMock(spec=TradingAgentsGraph)
        mock_graph.config = {
            "benchmark_ticker": None,
            "data_vendors": {"core_stock_apis": "nepse"},
            "benchmark_map": {"": "SPY"},
        }
        assert TradingAgentsGraph._resolve_benchmark(mock_graph, "CYCL") == NEPSE_BENCHMARK_LABEL

    def test_resolve_benchmark_explicit_overrides_nepse(self):
        mock_graph = MagicMock(spec=TradingAgentsGraph)
        mock_graph.config = {
            "benchmark_ticker": "Custom Index",
            "data_vendors": {"core_stock_apis": "nepse"},
        }
        assert TradingAgentsGraph._resolve_benchmark(mock_graph, "CYCL") == "Custom Index"

    def test_fetch_returns_routes_to_nepse(self):
        mock_graph = MagicMock(spec=TradingAgentsGraph)
        mock_graph.config = {
            "data_vendors": {"core_stock_apis": "nepse"},
            "outcome_holding_days": 5,
            "outcome_settlement_days": 2,
        }

        with patch("tradingagents.dataflows.nepse.fetch_nepse_returns", return_value=(0.05, 0.02, 5)) as mock_fetch:
            raw, alpha, days = TradingAgentsGraph._fetch_returns(
                mock_graph, "CYCL", "2026-05-01", benchmark=NEPSE_BENCHMARK_LABEL,
            )

        mock_fetch.assert_called_once_with("CYCL", "2026-05-01", 5, 2)
        assert raw == 0.05 and alpha == 0.02 and days == 5

    def test_fetch_returns_yfinance_when_not_nepse(self):
        with patch("tradingagents.dataflows.nepse.fetch_nepse_returns") as mock_nepse, \
             patch("yfinance.Ticker") as mock_ticker_cls:
            def _make_ticker(sym):
                m = MagicMock()
                m.history.return_value = pd.DataFrame({"Close": [100.0, 102, 104, 106, 108, 110]})
                return m
            mock_ticker_cls.side_effect = _make_ticker

            raw, alpha, days = TradingAgentsGraph._fetch_returns(
                None, "NVDA", "2026-01-05", holding_days=5, benchmark="SPY",
            )

        mock_nepse.assert_not_called()
        assert raw is not None and days == 5
