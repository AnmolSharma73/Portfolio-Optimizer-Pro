"""
Markowitz Mean-Variance Optimizer
=================================

Implements classic Markowitz portfolio optimization using pypfopt's
EfficientFrontier solver.  Supports max-Sharpe, min-volatility,
target-return, target-risk, and equal-weight strategies.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional, Tuple

import numpy as np
import pandas as pd
from pypfopt import EfficientFrontier, objective_functions
from pypfopt.exceptions import OptimizationError

logger = logging.getLogger(__name__)


class MarkowitzOptimizer:
    """Mean-variance portfolio optimizer backed by *pypfopt*.

    Parameters
    ----------
    returns : pd.Series
        Annualized expected returns per asset (index = ticker).
    cov_matrix : pd.DataFrame
        Annualized covariance matrix (tickers × tickers).
    risk_free_rate : float, optional
        Annualized risk-free rate (default ``0.05``).
    """

    def __init__(
        self,
        returns: pd.Series,
        cov_matrix: pd.DataFrame,
        risk_free_rate: float = 0.05,
    ) -> None:
        if returns.empty or cov_matrix.empty:
            raise ValueError("Returns and covariance matrix must not be empty.")
        if not cov_matrix.shape[0] == cov_matrix.shape[1] == len(returns):
            raise ValueError(
                f"Dimension mismatch: returns has {len(returns)} assets but "
                f"covariance matrix is {cov_matrix.shape}."
            )

        self.returns: pd.Series = returns
        self.cov_matrix: pd.DataFrame = cov_matrix
        self.risk_free_rate: float = risk_free_rate
        self.tickers: list[str] = list(returns.index)
        self.n_assets: int = len(self.tickers)

    # ------------------------------------------------------------------
    # Public optimisation methods
    # ------------------------------------------------------------------

    def optimize_max_sharpe(
        self,
        weight_bounds: Tuple[float, float] = (0, 1),
        sector_mapper: Optional[Dict[str, str]] = None,
        sector_upper: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """Maximise the Sharpe ratio.

        Parameters
        ----------
        weight_bounds : tuple, optional
            (min, max) weight per asset.
        sector_mapper : dict, optional
            Map ``{ticker: sector}`` for sector constraints.
        sector_upper : dict, optional
            Map ``{sector: max_allocation}``.

        Returns
        -------
        dict
            ``{'weights', 'expected_return', 'volatility', 'sharpe_ratio'}``
        """
        if self.n_assets == 1:
            return self._single_asset_result()

        ef = EfficientFrontier(
            self.returns,
            self.cov_matrix,
            weight_bounds=weight_bounds,
        )

        # Optional sector constraints
        if sector_mapper and sector_upper:
            ef.add_sector_constraints(sector_mapper, sector_upper)

        try:
            ef.max_sharpe(risk_free_rate=self.risk_free_rate)
        except OptimizationError as exc:
            logger.warning("Max-Sharpe optimisation failed: %s", exc)
            return self.optimize_equal_weight()

        return self._format_result(ef)

    def optimize_min_volatility(
        self,
        weight_bounds: Tuple[float, float] = (0, 1),
    ) -> Dict[str, Any]:
        """Find the minimum-volatility portfolio.

        Returns
        -------
        dict
            ``{'weights', 'expected_return', 'volatility', 'sharpe_ratio'}``
        """
        if self.n_assets == 1:
            return self._single_asset_result()

        ef = EfficientFrontier(
            self.returns,
            self.cov_matrix,
            weight_bounds=weight_bounds,
        )

        try:
            ef.min_volatility()
        except OptimizationError as exc:
            logger.warning("Min-volatility optimisation failed: %s", exc)
            return self.optimize_equal_weight()

        return self._format_result(ef)

    def optimize_target_return(
        self,
        target_return: float,
        weight_bounds: Tuple[float, float] = (0, 1),
    ) -> Dict[str, Any]:
        """Find the portfolio that achieves *target_return* with minimum risk.

        Parameters
        ----------
        target_return : float
            Desired annualized portfolio return.

        Returns
        -------
        dict
            ``{'weights', 'expected_return', 'volatility', 'sharpe_ratio'}``
        """
        if self.n_assets == 1:
            return self._single_asset_result()

        ef = EfficientFrontier(
            self.returns,
            self.cov_matrix,
            weight_bounds=weight_bounds,
        )

        try:
            ef.efficient_return(target_return=target_return)
        except (OptimizationError, ValueError) as exc:
            logger.warning("Target-return optimisation failed: %s", exc)
            return self.optimize_equal_weight()

        return self._format_result(ef)

    def optimize_target_risk(
        self,
        target_risk: float,
        weight_bounds: Tuple[float, float] = (0, 1),
    ) -> Dict[str, Any]:
        """Find the portfolio that achieves *target_risk* with maximum return.

        Parameters
        ----------
        target_risk : float
            Desired annualized portfolio volatility.

        Returns
        -------
        dict
            ``{'weights', 'expected_return', 'volatility', 'sharpe_ratio'}``
        """
        if self.n_assets == 1:
            return self._single_asset_result()

        ef = EfficientFrontier(
            self.returns,
            self.cov_matrix,
            weight_bounds=weight_bounds,
        )

        try:
            ef.efficient_risk(target_volatility=target_risk)
        except (OptimizationError, ValueError) as exc:
            logger.warning("Target-risk optimisation failed: %s", exc)
            return self.optimize_equal_weight()

        return self._format_result(ef)

    def optimize_equal_weight(self) -> Dict[str, Any]:
        """Return a naïve 1/N equal-weight portfolio with calculated metrics.

        Returns
        -------
        dict
            ``{'weights', 'expected_return', 'volatility', 'sharpe_ratio'}``
        """
        weights = np.array([1.0 / self.n_assets] * self.n_assets)
        expected_return = float(weights @ self.returns.values)
        volatility = float(
            np.sqrt(weights @ self.cov_matrix.values @ weights)
        )
        sharpe = (
            (expected_return - self.risk_free_rate) / volatility
            if volatility > 0
            else 0.0
        )

        return {
            "weights": dict(zip(self.tickers, weights.tolist())),
            "expected_return": expected_return,
            "volatility": volatility,
            "sharpe_ratio": sharpe,
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _format_result(self, ef: EfficientFrontier) -> Dict[str, Any]:
        """Extract cleaned weights and performance metrics from *ef*.

        Parameters
        ----------
        ef : pypfopt.EfficientFrontier
            Solved EfficientFrontier instance.

        Returns
        -------
        dict
            ``{'weights', 'expected_return', 'volatility', 'sharpe_ratio'}``
        """
        cleaned = ef.clean_weights()
        perf = ef.portfolio_performance(
            verbose=False, risk_free_rate=self.risk_free_rate
        )
        expected_return, volatility, sharpe = perf

        return {
            "weights": dict(cleaned),
            "expected_return": float(expected_return),
            "volatility": float(volatility),
            "sharpe_ratio": float(sharpe),
        }

    def _single_asset_result(self) -> Dict[str, Any]:
        """Handle the degenerate single-asset case."""
        ticker = self.tickers[0]
        ret = float(self.returns.iloc[0])
        vol = float(np.sqrt(self.cov_matrix.iloc[0, 0]))
        sharpe = (ret - self.risk_free_rate) / vol if vol > 0 else 0.0

        return {
            "weights": {ticker: 1.0},
            "expected_return": ret,
            "volatility": vol,
            "sharpe_ratio": sharpe,
        }
