"""
Risk Parity Optimizer
=====================

Constructs a portfolio where every asset contributes equally to total
portfolio risk.  Uses ``scipy.optimize.minimize`` with a custom
objective that penalises deviations from equal risk contribution.
"""

from __future__ import annotations

import logging
from typing import Any, Dict

import numpy as np
import pandas as pd
from scipy.optimize import minimize

logger = logging.getLogger(__name__)


class RiskParityOptimizer:
    """Equal-risk-contribution (risk parity) portfolio optimizer.

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

        self.returns: pd.Series = returns
        self.cov_matrix: pd.DataFrame = cov_matrix
        self.risk_free_rate: float = risk_free_rate
        self.tickers: list[str] = list(returns.index)
        self.n_assets: int = len(self.tickers)

        # Numpy arrays for fast computation
        self._mu: np.ndarray = returns.values.astype(np.float64)
        self._cov: np.ndarray = cov_matrix.values.astype(np.float64)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def optimize(self) -> Dict[str, Any]:
        """Solve for risk-parity weights.

        Returns
        -------
        dict
            ``{'weights': dict, 'expected_return': float,
              'volatility': float, 'sharpe_ratio': float,
              'risk_contributions': dict}``
        """
        # Single-asset trivial case
        if self.n_assets == 1:
            return self._single_asset_result()

        # Initial guess: equal weight
        w0 = np.ones(self.n_assets) / self.n_assets

        # Constraints: weights sum to 1
        constraints = {"type": "eq", "fun": lambda w: np.sum(w) - 1.0}

        # Bounds: all weights >= 0
        bounds = tuple((0.0, 1.0) for _ in range(self.n_assets))

        result = minimize(
            self._objective,
            w0,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
            options={"maxiter": 1_000, "ftol": 1e-12},
        )

        if not result.success:
            logger.warning(
                "Risk-parity optimisation did not converge: %s. "
                "Using best iterate.",
                result.message,
            )

        weights = result.x
        weights = np.maximum(weights, 0.0)  # clip tiny negatives
        weights /= weights.sum()  # re-normalise

        # Compute portfolio metrics
        expected_return = float(weights @ self._mu)
        volatility = float(np.sqrt(weights @ self._cov @ weights))
        sharpe = (
            (expected_return - self.risk_free_rate) / volatility
            if volatility > 0
            else 0.0
        )
        risk_contribs = self._risk_contribution(weights)

        return {
            "weights": dict(zip(self.tickers, weights.tolist())),
            "expected_return": expected_return,
            "volatility": volatility,
            "sharpe_ratio": sharpe,
            "risk_contributions": dict(
                zip(self.tickers, risk_contribs.tolist())
            ),
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _risk_contribution(self, weights: np.ndarray) -> np.ndarray:
        """Calculate the marginal risk contribution per asset.

        The risk contribution of asset *i* is defined as:

            RC_i = w_i * (Σ w)_i / σ_p

        where σ_p = sqrt(w^T Σ w).

        Parameters
        ----------
        weights : np.ndarray
            Portfolio weight vector (n_assets,).

        Returns
        -------
        np.ndarray
            Risk contribution per asset (sums to 1.0 when normalised).
        """
        sigma_w = self._cov @ weights  # (n_assets,)
        portfolio_var = weights @ sigma_w
        portfolio_vol = np.sqrt(portfolio_var)

        if portfolio_vol < 1e-12:
            return np.ones(self.n_assets) / self.n_assets

        # Marginal risk contribution (fraction of total vol)
        marginal_rc = weights * sigma_w / portfolio_vol
        # Normalise so contributions sum to 1
        total_rc = marginal_rc.sum()
        if total_rc > 0:
            marginal_rc /= total_rc

        return marginal_rc

    def _objective(self, weights: np.ndarray) -> float:
        """Risk-parity objective: minimise SSE between actual and target
        (equal) risk contributions.

        Parameters
        ----------
        weights : np.ndarray
            Candidate weight vector.

        Returns
        -------
        float
            Sum of squared deviations from equal risk contribution.
        """
        sigma_w = self._cov @ weights
        portfolio_var = weights @ sigma_w

        if portfolio_var < 1e-16:
            return 0.0

        portfolio_vol = np.sqrt(portfolio_var)

        # Absolute risk contribution per asset
        rc = weights * sigma_w / portfolio_vol

        # Target: each asset contributes equally
        target_rc = portfolio_vol / self.n_assets

        # Sum of squared differences
        return float(np.sum((rc - target_rc) ** 2))

    def _single_asset_result(self) -> Dict[str, Any]:
        """Handle the degenerate single-asset case."""
        ticker = self.tickers[0]
        ret = float(self._mu[0])
        vol = float(np.sqrt(self._cov[0, 0]))
        sharpe = (ret - self.risk_free_rate) / vol if vol > 0 else 0.0

        return {
            "weights": {ticker: 1.0},
            "expected_return": ret,
            "volatility": vol,
            "sharpe_ratio": sharpe,
            "risk_contributions": {ticker: 1.0},
        }
