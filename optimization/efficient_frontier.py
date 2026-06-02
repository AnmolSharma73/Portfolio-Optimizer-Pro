"""
Efficient Frontier Calculator
==============================

Sweeps the mean-variance efficient frontier by varying target returns
between the minimum and maximum feasible values.  Also identifies key
portfolios (max Sharpe, min volatility, equal weight).
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
from pypfopt import EfficientFrontier
from pypfopt.exceptions import OptimizationError

from .markowitz import MarkowitzOptimizer

logger = logging.getLogger(__name__)


class EfficientFrontierCalculator:
    """Compute the efficient frontier for a set of assets.

    Parameters
    ----------
    returns : pd.Series
        Annualized expected returns per asset (index = ticker).
    cov_matrix : pd.DataFrame
        Annualized covariance matrix (tickers × tickers).
    risk_free_rate : float, optional
        Annualized risk-free rate (default ``0.05``).
    num_portfolios : int, optional
        Number of target-return points along the frontier (default ``100``).
    """

    def __init__(
        self,
        returns: pd.Series,
        cov_matrix: pd.DataFrame,
        risk_free_rate: float = 0.05,
        num_portfolios: int = 100,
    ) -> None:
        if returns.empty or cov_matrix.empty:
            raise ValueError("Returns and covariance matrix must not be empty.")

        self.returns: pd.Series = returns
        self.cov_matrix: pd.DataFrame = cov_matrix
        self.risk_free_rate: float = risk_free_rate
        self.num_portfolios: int = max(num_portfolios, 10)
        self.tickers: List[str] = list(returns.index)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def compute_frontier(self) -> Dict[str, List[Any]]:
        """Sweep the efficient frontier by varying target returns.

        Returns
        -------
        dict
            ``{'returns': [...], 'volatilities': [...],
              'sharpe_ratios': [...], 'weights': [dict, ...]}``
        """
        # Determine feasible return range via min-vol and max-return portfolios
        min_ret = self._min_feasible_return()
        max_ret = self._max_feasible_return()

        if min_ret is None or max_ret is None or min_ret >= max_ret:
            logger.warning(
                "Cannot determine feasible return range (min=%.4f, max=%.4f). "
                "Returning empty frontier.",
                min_ret or 0,
                max_ret or 0,
            )
            return {
                "returns": [],
                "volatilities": [],
                "sharpe_ratios": [],
                "weights": [],
            }

        target_returns = np.linspace(min_ret, max_ret, self.num_portfolios)

        frontier_returns: List[float] = []
        frontier_vols: List[float] = []
        frontier_sharpes: List[float] = []
        frontier_weights: List[Dict[str, float]] = []

        for target in target_returns:
            try:
                ef = EfficientFrontier(
                    self.returns,
                    self.cov_matrix,
                    weight_bounds=(0, 1),
                )
                ef.efficient_return(target_return=float(target))
                cleaned = ef.clean_weights()
                perf = ef.portfolio_performance(
                    verbose=False, risk_free_rate=self.risk_free_rate
                )
                exp_ret, vol, sharpe = perf

                frontier_returns.append(float(exp_ret))
                frontier_vols.append(float(vol))
                frontier_sharpes.append(float(sharpe))
                frontier_weights.append(dict(cleaned))
            except (OptimizationError, ValueError) as exc:
                logger.debug(
                    "Skipping target return %.4f: %s", target, exc
                )
                continue

        return {
            "returns": frontier_returns,
            "volatilities": frontier_vols,
            "sharpe_ratios": frontier_sharpes,
            "weights": frontier_weights,
        }

    def get_key_portfolios(self) -> Dict[str, Dict[str, Any]]:
        """Return the three key reference portfolios.

        Returns
        -------
        dict
            ``{'max_sharpe': {...}, 'min_volatility': {...},
              'equal_weight': {...}}``
        """
        opt = MarkowitzOptimizer(
            self.returns, self.cov_matrix, self.risk_free_rate
        )
        return {
            "max_sharpe": opt.optimize_max_sharpe(),
            "min_volatility": opt.optimize_min_volatility(),
            "equal_weight": opt.optimize_equal_weight(),
        }

    def get_frontier_data(self) -> pd.DataFrame:
        """Return frontier as a tidy DataFrame for plotting.

        Returns
        -------
        pd.DataFrame
            Columns: ``['Return', 'Volatility', 'Sharpe']``.
        """
        frontier = self.compute_frontier()

        if not frontier["returns"]:
            return pd.DataFrame(columns=["Return", "Volatility", "Sharpe"])

        return pd.DataFrame(
            {
                "Return": frontier["returns"],
                "Volatility": frontier["volatilities"],
                "Sharpe": frontier["sharpe_ratios"],
            }
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _min_feasible_return(self) -> Optional[float]:
        """Return the expected return of the minimum-volatility portfolio."""
        try:
            ef = EfficientFrontier(
                self.returns,
                self.cov_matrix,
                weight_bounds=(0, 1),
            )
            ef.min_volatility()
            perf = ef.portfolio_performance(verbose=False)
            return float(perf[0])
        except (OptimizationError, ValueError) as exc:
            logger.warning("Could not compute min-return bound: %s", exc)
            return None

    def _max_feasible_return(self) -> Optional[float]:
        """Return the maximum single-asset return (upper bound)."""
        try:
            return float(self.returns.max())
        except Exception as exc:  # pragma: no cover
            logger.warning("Could not compute max-return bound: %s", exc)
            return None
