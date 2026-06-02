"""
Black-Litterman Optimizer
=========================

Implements the Black-Litterman asset allocation model, which blends
market-implied equilibrium returns with subjective investor views
to produce posterior return estimates.  Uses ``pypfopt`` for both the
BL model and the final mean-variance optimisation step.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

import numpy as np
import pandas as pd
from pypfopt import BlackLittermanModel, EfficientFrontier
from pypfopt.exceptions import OptimizationError

logger = logging.getLogger(__name__)


class BlackLittermanOptimizer:
    """Black-Litterman portfolio optimizer.

    Parameters
    ----------
    returns : pd.Series
        Annualized expected returns per asset (index = ticker).
    cov_matrix : pd.DataFrame
        Annualized covariance matrix (tickers × tickers).
    market_caps : pd.Series or dict, optional
        Market capitalisation per asset.  If ``None``, equal market caps
        are assumed.
    risk_free_rate : float, optional
        Annualized risk-free rate (default ``0.05``).
    risk_aversion : float, optional
        Market risk-aversion parameter δ (default ``2.5``).
    """

    def __init__(
        self,
        returns: pd.Series,
        cov_matrix: pd.DataFrame,
        market_caps: Optional[pd.Series | Dict[str, float]] = None,
        risk_free_rate: float = 0.05,
        risk_aversion: float = 2.5,
    ) -> None:
        if returns.empty or cov_matrix.empty:
            raise ValueError("Returns and covariance matrix must not be empty.")

        self.returns: pd.Series = returns
        self.cov_matrix: pd.DataFrame = cov_matrix
        self.risk_free_rate: float = risk_free_rate
        self.risk_aversion: float = risk_aversion
        self.tickers: list[str] = list(returns.index)
        self.n_assets: int = len(self.tickers)

        # Market caps
        if market_caps is None:
            self.market_caps: pd.Series = pd.Series(
                1.0 / self.n_assets, index=self.tickers
            )
        elif isinstance(market_caps, dict):
            self.market_caps = pd.Series(market_caps).reindex(self.tickers).fillna(
                1.0 / self.n_assets
            )
        else:
            self.market_caps = market_caps.reindex(self.tickers).fillna(
                1.0 / self.n_assets
            )

        # Internal state set by set_views / compute_posterior_returns
        self._P: Optional[np.ndarray] = None
        self._Q: Optional[np.ndarray] = None
        self._posterior_returns: Optional[pd.Series] = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def compute_equilibrium_returns(self) -> pd.Series:
        """Compute market-implied (prior) equilibrium returns.

        Uses the reverse-optimisation formula:

            π = δ · Σ · w_mkt

        where ``w_mkt`` are the market-capitalisation weights.

        Returns
        -------
        pd.Series
            Equilibrium excess returns per asset.
        """
        w_mkt = self.market_caps / self.market_caps.sum()
        cov = self.cov_matrix.values.astype(np.float64)
        pi = self.risk_aversion * cov @ w_mkt.values

        return pd.Series(pi, index=self.tickers, name="equilibrium_return")

    def set_views(self, views_dict: Dict[str, float]) -> None:
        """Set absolute investor views.

        Parameters
        ----------
        views_dict : dict
            ``{ticker: expected_return}`` – each entry represents an
            absolute view (e.g., ``{'AAPL': 0.10}`` means "AAPL will
            return 10 %").

        Notes
        -----
        Only tickers present in the universe are kept.  Views on unknown
        tickers are silently ignored.
        """
        # Filter to known tickers
        valid_views = {t: v for t, v in views_dict.items() if t in self.tickers}

        if not valid_views:
            logger.warning(
                "No valid views provided (tickers not in universe). "
                "Posterior returns will equal the prior."
            )
            self._P = None
            self._Q = None
            return

        n_views = len(valid_views)
        P = np.zeros((n_views, self.n_assets))
        Q = np.zeros(n_views)

        for i, (ticker, view_return) in enumerate(valid_views.items()):
            j = self.tickers.index(ticker)
            P[i, j] = 1.0
            Q[i] = view_return

        self._P = P
        self._Q = Q
        # Invalidate cached posterior
        self._posterior_returns = None

        logger.info("Set %d absolute view(s): %s", n_views, valid_views)

    def compute_posterior_returns(self, tau: float = 0.05) -> pd.Series:
        """Blend equilibrium returns with investor views.

        If no views have been set, the posterior equals the prior
        (equilibrium returns).

        Parameters
        ----------
        tau : float, optional
            Scalar indicating uncertainty of the prior (default ``0.05``).

        Returns
        -------
        pd.Series
            Posterior (blended) expected returns per asset.
        """
        pi = self.compute_equilibrium_returns()

        if self._P is None or self._Q is None:
            self._posterior_returns = pi
            return pi

        try:
            bl = BlackLittermanModel(
                cov_matrix=self.cov_matrix,
                pi=pi,
                P=self._P,
                Q=self._Q,
                tau=tau,
            )
            posterior = bl.bl_returns()
            self._posterior_returns = posterior
            return posterior
        except Exception as exc:
            logger.warning(
                "Black-Litterman posterior computation failed (%s). "
                "Falling back to equilibrium returns.",
                exc,
            )
            self._posterior_returns = pi
            return pi

    def optimize(
        self,
        views_dict: Optional[Dict[str, float]] = None,
        tau: float = 0.05,
        weight_bounds: tuple = (0, 1),
    ) -> Dict[str, Any]:
        """Run the full Black-Litterman pipeline and optimise.

        1. Set views (if provided).
        2. Compute posterior returns.
        3. Run max-Sharpe optimisation on the posterior.

        Parameters
        ----------
        views_dict : dict, optional
            Absolute views ``{ticker: expected_return}``.
        tau : float, optional
            Prior uncertainty scalar (default ``0.05``).
        weight_bounds : tuple, optional
            (min, max) weight per asset.

        Returns
        -------
        dict
            ``{'weights': dict, 'expected_return': float,
              'volatility': float, 'sharpe_ratio': float,
              'posterior_returns': dict, 'equilibrium_returns': dict}``
        """
        if views_dict is not None:
            self.set_views(views_dict)

        posterior = self.compute_posterior_returns(tau=tau)
        equilibrium = self.compute_equilibrium_returns()

        # Single-asset shortcut
        if self.n_assets == 1:
            ticker = self.tickers[0]
            ret = float(posterior.iloc[0])
            vol = float(np.sqrt(self.cov_matrix.iloc[0, 0]))
            sharpe = (ret - self.risk_free_rate) / vol if vol > 0 else 0.0
            return {
                "weights": {ticker: 1.0},
                "expected_return": ret,
                "volatility": vol,
                "sharpe_ratio": sharpe,
                "posterior_returns": posterior.to_dict(),
                "equilibrium_returns": equilibrium.to_dict(),
            }

        # Build efficient frontier with posterior returns
        try:
            ef = EfficientFrontier(
                posterior,
                self.cov_matrix,
                weight_bounds=weight_bounds,
            )
            ef.max_sharpe(risk_free_rate=self.risk_free_rate)
            cleaned = ef.clean_weights()
            perf = ef.portfolio_performance(
                verbose=False, risk_free_rate=self.risk_free_rate
            )
            exp_ret, vol, sharpe = perf
        except (OptimizationError, ValueError) as exc:
            logger.warning(
                "BL max-Sharpe optimisation failed (%s). "
                "Falling back to equal weights.",
                exc,
            )
            w = np.ones(self.n_assets) / self.n_assets
            exp_ret = float(w @ posterior.values)
            vol = float(np.sqrt(w @ self.cov_matrix.values @ w))
            sharpe = (
                (exp_ret - self.risk_free_rate) / vol if vol > 0 else 0.0
            )
            cleaned = dict(zip(self.tickers, w.tolist()))

        return {
            "weights": dict(cleaned),
            "expected_return": float(exp_ret),
            "volatility": float(vol),
            "sharpe_ratio": float(sharpe),
            "posterior_returns": posterior.to_dict(),
            "equilibrium_returns": equilibrium.to_dict(),
        }
