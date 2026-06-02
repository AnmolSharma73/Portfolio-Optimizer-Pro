"""
Monte Carlo Portfolio Simulator
================================

Generates thousands of random portfolios via Dirichlet-sampled weights
and identifies optimal portfolios.  Also provides Geometric Brownian
Motion simulation for projecting future portfolio value paths.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class MonteCarloSimulator:
    """Monte Carlo simulator for portfolio analysis.

    Parameters
    ----------
    returns : pd.Series
        Annualized expected returns per asset (index = ticker).
    cov_matrix : pd.DataFrame
        Annualized covariance matrix (tickers × tickers).
    risk_free_rate : float, optional
        Annualized risk-free rate (default ``0.05``).
    num_simulations : int, optional
        Number of random portfolios to generate (default ``10_000``).
    """

    def __init__(
        self,
        returns: pd.Series,
        cov_matrix: pd.DataFrame,
        risk_free_rate: float = 0.05,
        num_simulations: int = 10_000,
    ) -> None:
        if returns.empty or cov_matrix.empty:
            raise ValueError("Returns and covariance matrix must not be empty.")

        self.returns: pd.Series = returns
        self.cov_matrix: pd.DataFrame = cov_matrix
        self.risk_free_rate: float = risk_free_rate
        self.num_simulations: int = max(num_simulations, 100)
        self.tickers: List[str] = list(returns.index)
        self.n_assets: int = len(self.tickers)

        # Precompute numpy arrays for vectorised math
        self._mu: np.ndarray = returns.values.astype(np.float64)
        self._cov: np.ndarray = cov_matrix.values.astype(np.float64)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run_simulation(self, seed: Optional[int] = None) -> Dict[str, Any]:
        """Run Monte Carlo simulation over random portfolios.

        Parameters
        ----------
        seed : int, optional
            Random seed for reproducibility.

        Returns
        -------
        dict
            ``{'returns': np.array, 'volatilities': np.array,
              'sharpe_ratios': np.array,
              'weights': np.array(n_sim, n_assets),
              'tickers': list}``
        """
        rng = np.random.default_rng(seed)

        # Dirichlet(1, ..., 1) gives uniform distribution over the simplex
        weights = rng.dirichlet(
            alpha=np.ones(self.n_assets), size=self.num_simulations
        )  # shape: (n_sim, n_assets)

        # Vectorised portfolio metrics ----------------------------------
        # Expected return for each portfolio: (n_sim,)
        port_returns = weights @ self._mu

        # Volatility for each portfolio: sqrt(w Σ w^T)
        # (n_sim, n_assets) @ (n_assets, n_assets) -> (n_sim, n_assets)
        cov_dot = weights @ self._cov
        # Element-wise multiply and sum across assets -> variance per portfolio
        port_variances = np.einsum("ij,ij->i", cov_dot, weights)
        port_volatilities = np.sqrt(port_variances)

        # Sharpe ratios
        with np.errstate(divide="ignore", invalid="ignore"):
            port_sharpes = np.where(
                port_volatilities > 0,
                (port_returns - self.risk_free_rate) / port_volatilities,
                0.0,
            )

        return {
            "returns": port_returns,
            "volatilities": port_volatilities,
            "sharpe_ratios": port_sharpes,
            "weights": weights,
            "tickers": self.tickers,
        }

    def get_optimal_portfolios(
        self, results: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Dict[str, Any]]:
        """Identify the max-Sharpe and min-volatility portfolios from
        simulation results.

        Parameters
        ----------
        results : dict, optional
            Output of :meth:`run_simulation`.  If ``None``, a new
            simulation is run.

        Returns
        -------
        dict
            ``{'max_sharpe': {'weights': dict, 'return': float,
              'volatility': float, 'sharpe': float},
              'min_volatility': {...}}``
        """
        if results is None:
            results = self.run_simulation()

        max_sharpe_idx = int(np.argmax(results["sharpe_ratios"]))
        min_vol_idx = int(np.argmin(results["volatilities"]))

        tickers = results["tickers"]

        def _portfolio_at(idx: int) -> Dict[str, Any]:
            w = results["weights"][idx]
            return {
                "weights": dict(zip(tickers, w.tolist())),
                "return": float(results["returns"][idx]),
                "volatility": float(results["volatilities"][idx]),
                "sharpe": float(results["sharpe_ratios"][idx]),
            }

        return {
            "max_sharpe": _portfolio_at(max_sharpe_idx),
            "min_volatility": _portfolio_at(min_vol_idx),
        }

    def simulate_future_prices(
        self,
        current_prices: pd.Series,
        weights: Dict[str, float],
        days: int = 252,
        num_paths: int = 1_000,
        seed: Optional[int] = None,
    ) -> np.ndarray:
        """Project future portfolio value using Geometric Brownian Motion.

        For each path the daily log-return is sampled from a multivariate
        normal and the per-asset price paths are combined according to the
        portfolio weights.

        Parameters
        ----------
        current_prices : pd.Series
            Most recent closing price per asset (index = ticker).
        weights : dict
            Portfolio weights ``{ticker: weight}``.
        days : int, optional
            Number of trading days to simulate (default ``252``).
        num_paths : int, optional
            Number of Monte Carlo paths (default ``1_000``).
        seed : int, optional
            Random seed for reproducibility.

        Returns
        -------
        np.ndarray
            Shape ``(num_paths, days)`` – cumulative portfolio value
            (starting at 1.0) for each path.
        """
        rng = np.random.default_rng(seed)

        # Align tickers
        aligned_tickers = [t for t in self.tickers if t in weights]
        if not aligned_tickers:
            raise ValueError("No matching tickers between weights and data.")

        w = np.array([weights[t] for t in aligned_tickers], dtype=np.float64)
        w = w / w.sum()  # ensure normalised

        # Daily drift and covariance
        idx = [self.tickers.index(t) for t in aligned_tickers]
        mu_daily = self._mu[idx] / 252.0
        cov_daily = self._cov[np.ix_(idx, idx)] / 252.0

        n_assets_used = len(aligned_tickers)

        # Sample daily log-returns: (num_paths, days, n_assets)
        daily_log_returns = rng.multivariate_normal(
            mean=mu_daily - 0.5 * np.diag(cov_daily),  # drift adjustment for GBM
            cov=cov_daily,
            size=(num_paths, days),
        )  # shape: (num_paths, days, n_assets)

        # Cumulative asset prices relative to day-0 price
        # exp of cumulative sum of log-returns along the time axis
        cum_log_returns = np.cumsum(daily_log_returns, axis=1)
        asset_growth = np.exp(cum_log_returns)  # (num_paths, days, n_assets)

        # Weighted portfolio value at each time step
        # (num_paths, days, n_assets) @ (n_assets,) -> (num_paths, days)
        portfolio_value = asset_growth @ w

        return portfolio_value
