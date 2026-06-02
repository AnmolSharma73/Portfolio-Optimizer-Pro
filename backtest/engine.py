"""
Backtesting engine for portfolio simulation.

Provides a robust framework for simulating portfolio performance over
historical price data, including periodic rebalancing, transaction cost
modelling, and comprehensive performance reporting.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from risk.metrics import RiskMetrics


class BacktestEngine:
    """Simulate a portfolio strategy over historical price data.

    The engine tracks share-level positions, rebalances at a configurable
    frequency, deducts realistic transaction costs on each rebalance, and
    produces detailed performance analytics.

    Parameters
    ----------
    prices : pd.DataFrame
        Adjusted-close prices with a ``DatetimeIndex`` and one column per
        ticker.
    weights : dict
        Target allocation expressed as ``{ticker: weight}``.  Weights are
        automatically normalised to sum to 1.0; tickers absent from
        *prices* are silently dropped.
    initial_capital : float, optional
        Starting portfolio value in currency units (default ``100_000``).
    rebalance_freq : int, optional
        Number of trading days between rebalances (default ``21`` ≈ 1 month).
    transaction_cost : float, optional
        Proportional cost applied to turnover on each rebalance
        (default ``0.001`` = 10 bps).
    """

    def __init__(
        self,
        prices: pd.DataFrame,
        weights: dict,
        initial_capital: float = 100_000,
        rebalance_freq: int = 21,
        transaction_cost: float = 0.001,
    ) -> None:
        self.prices: pd.DataFrame = prices.copy()
        self._raw_weights: dict = dict(weights)
        self.initial_capital: float = initial_capital
        self.rebalance_freq: int = rebalance_freq
        self.transaction_cost: float = transaction_cost

        # --- Resolve valid tickers & normalise weights -------------------
        valid_tickers: List[str] = [
            t for t in self._raw_weights if t in self.prices.columns
        ]
        if not valid_tickers:
            raise ValueError(
                "None of the tickers in 'weights' are present in the price data."
            )
        self.tickers: List[str] = valid_tickers
        raw_sum: float = sum(self._raw_weights[t] for t in self.tickers)
        if raw_sum <= 0:
            raise ValueError("Sum of valid weights must be positive.")
        self.weights: Dict[str, float] = {
            t: self._raw_weights[t] / raw_sum for t in self.tickers
        }

        # Keep only relevant columns & forward-fill NaNs
        self.prices = self.prices[self.tickers].ffill()

        # Placeholder for results
        self._results: Optional[Dict[str, Any]] = None

    # ------------------------------------------------------------------
    # Core simulation
    # ------------------------------------------------------------------

    def run_backtest(self) -> dict:
        """Execute the portfolio simulation.

        Returns
        -------
        dict
            ``portfolio_values`` – ``pd.Series`` of daily portfolio value,
            ``returns`` – ``pd.Series`` of daily portfolio returns,
            ``trades`` – list of dicts recording each rebalance event,
            ``total_costs`` – cumulative transaction costs incurred.
        """
        prices: pd.DataFrame = self.prices
        dates: pd.DatetimeIndex = prices.index  # type: ignore[assignment]
        n_days: int = len(dates)

        if n_days < 2:
            raise ValueError("Need at least 2 days of price data to run a backtest.")

        # --- Initial allocation ------------------------------------------
        portfolio_value: float = self.initial_capital
        # Allocate shares on day 0
        day0_prices: pd.Series = prices.iloc[0]
        shares: Dict[str, float] = {}
        for ticker in self.tickers:
            alloc: float = portfolio_value * self.weights[ticker]
            shares[ticker] = alloc / day0_prices[ticker] if day0_prices[ticker] > 0 else 0.0

        portfolio_values: List[float] = [portfolio_value]
        trades: List[Dict[str, Any]] = []
        total_costs: float = 0.0
        last_rebalance_day: int = 0

        # --- Day-by-day simulation ---------------------------------------
        for day_idx in range(1, n_days):
            current_prices: pd.Series = prices.iloc[day_idx]

            # Mark-to-market
            portfolio_value = sum(
                shares[t] * current_prices[t] for t in self.tickers
            )

            # --- Rebalance check -----------------------------------------
            if (day_idx - last_rebalance_day) >= self.rebalance_freq:
                # Current weights (pre-rebalance)
                current_weights: Dict[str, float] = {}
                for t in self.tickers:
                    current_weights[t] = (
                        (shares[t] * current_prices[t]) / portfolio_value
                        if portfolio_value > 0
                        else 0.0
                    )

                # Turnover = sum of absolute weight changes
                turnover: float = sum(
                    abs(self.weights[t] - current_weights[t]) for t in self.tickers
                )
                cost: float = self.transaction_cost * turnover * portfolio_value
                total_costs += cost

                # Deduct cost, then reallocate
                portfolio_value -= cost
                new_shares: Dict[str, float] = {}
                for t in self.tickers:
                    alloc = portfolio_value * self.weights[t]
                    price_t: float = current_prices[t]
                    new_shares[t] = alloc / price_t if price_t > 0 else 0.0

                trades.append(
                    {
                        "date": dates[day_idx],
                        "day_index": day_idx,
                        "portfolio_value_pre": portfolio_value + cost,
                        "portfolio_value_post": portfolio_value,
                        "turnover": turnover,
                        "cost": cost,
                        "weights_before": dict(current_weights),
                        "weights_after": dict(self.weights),
                    }
                )

                shares = new_shares
                last_rebalance_day = day_idx

            portfolio_values.append(portfolio_value)

        # --- Build result series -----------------------------------------
        pv_series: pd.Series = pd.Series(portfolio_values, index=dates, name="portfolio_value")
        returns_series: pd.Series = pv_series.pct_change().fillna(0.0)
        returns_series.name = "daily_return"

        self._results = {
            "portfolio_values": pv_series,
            "returns": returns_series,
            "trades": trades,
            "total_costs": total_costs,
        }
        return self._results

    # ------------------------------------------------------------------
    # Benchmark comparison
    # ------------------------------------------------------------------

    def compare_with_benchmark(self, benchmark_prices: pd.Series) -> dict:
        """Compare portfolio performance against a benchmark.

        Parameters
        ----------
        benchmark_prices : pd.Series
            Price series for the benchmark instrument, indexed by date.

        Returns
        -------
        dict
            ``portfolio`` – portfolio value series,
            ``benchmark`` – benchmark value series normalised to the same
            initial capital,
            ``excess_returns`` – daily excess return series.
        """
        if self._results is None:
            self.run_backtest()
        assert self._results is not None  # for type-checker

        portfolio_values: pd.Series = self._results["portfolio_values"]

        # Align benchmark to portfolio dates
        bench: pd.Series = benchmark_prices.reindex(portfolio_values.index).ffill().bfill()
        # Normalise to same initial capital
        bench_normalised: pd.Series = bench / bench.iloc[0] * self.initial_capital
        bench_normalised.name = "benchmark_value"

        portfolio_returns: pd.Series = portfolio_values.pct_change().fillna(0.0)
        benchmark_returns: pd.Series = bench_normalised.pct_change().fillna(0.0)
        excess: pd.Series = portfolio_returns - benchmark_returns
        excess.name = "excess_return"

        return {
            "portfolio": portfolio_values,
            "benchmark": bench_normalised,
            "excess_returns": excess,
        }

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------

    def generate_report(self) -> dict:
        """Produce a comprehensive performance report.

        Returns
        -------
        dict
            All metrics from :class:`RiskMetrics` plus high-level portfolio
            statistics such as total return, final value, and cost summary.
        """
        if self._results is None:
            self.run_backtest()
        assert self._results is not None

        returns: pd.Series = self._results["returns"]
        pv: pd.Series = self._results["portfolio_values"]

        # Risk metrics via RiskMetrics helper
        risk_report: dict = RiskMetrics.get_all_metrics(returns)

        # Augment with backtest-specific stats
        risk_report.update(
            {
                "initial_capital": self.initial_capital,
                "final_value": float(pv.iloc[-1]),
                "total_return_pct": float((pv.iloc[-1] / pv.iloc[0] - 1) * 100),
                "total_costs": self._results["total_costs"],
                "num_rebalances": len(self._results["trades"]),
            }
        )
        return risk_report

    # ------------------------------------------------------------------
    # Calendar return breakdowns
    # ------------------------------------------------------------------

    def get_annual_returns(self) -> pd.DataFrame:
        """Calculate annual returns from daily portfolio returns.

        Returns
        -------
        pd.DataFrame
            Columns ``['Year', 'Return']`` with one row per calendar year.
        """
        if self._results is None:
            self.run_backtest()
        assert self._results is not None

        daily: pd.Series = self._results["returns"]
        annual: pd.Series = daily.groupby(daily.index.year).apply(  # type: ignore[arg-type]
            lambda x: (1 + x).prod() - 1
        )
        df: pd.DataFrame = annual.reset_index()
        df.columns = ["Year", "Return"]
        return df

    def get_monthly_returns(self) -> pd.DataFrame:
        """Calculate monthly returns and return a year × month pivot table.

        Returns
        -------
        pd.DataFrame
            Rows = calendar year, columns = month (1–12), values = monthly
            return computed as ``(1 + daily_return).prod() - 1``.
        """
        if self._results is None:
            self.run_backtest()
        assert self._results is not None

        daily: pd.Series = self._results["returns"]
        year: pd.Series = daily.index.year  # type: ignore[attr-defined]
        month: pd.Series = daily.index.month  # type: ignore[attr-defined]

        monthly: pd.Series = daily.groupby([year, month]).apply(
            lambda x: (1 + x).prod() - 1
        )
        monthly.index.names = ["Year", "Month"]
        pivot: pd.DataFrame = monthly.reset_index().pivot(
            index="Year", columns="Month", values=monthly.name or 0
        )
        # Ensure all 12 months present
        for m in range(1, 13):
            if m not in pivot.columns:
                pivot[m] = np.nan
        pivot = pivot[list(range(1, 13))]
        return pivot
