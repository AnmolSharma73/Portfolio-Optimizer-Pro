"""
Portfolio Optimizer Pro — Data Processor.

Provides static utility methods for computing returns, covariance
matrices, handling missing data, aligning DataFrames, and computing
rolling statistics.
"""

from __future__ import annotations

from typing import List, Literal

import numpy as np
import pandas as pd


class DataProcessor:
    """Pure-computation helpers for transforming price / return data.

    Every method is a ``@staticmethod`` — no instance state is needed.
    """

    # ── Returns ───────────────────────────────────────────────────────────

    @staticmethod
    def calculate_returns(
        prices: pd.DataFrame,
        method: Literal["simple", "log"] = "simple",
    ) -> pd.DataFrame:
        """Compute period-over-period returns from a price DataFrame.

        Parameters
        ----------
        prices : pd.DataFrame
            DataFrame of (adjusted) close prices.
        method : ``"simple"`` | ``"log"``
            ``"simple"`` → arithmetic percentage change.
            ``"log"``    → continuously-compounded (log) returns.

        Returns
        -------
        pd.DataFrame
            Returns DataFrame with the first row (``NaN``) dropped.

        Raises
        ------
        ValueError
            If *method* is not recognised.
        """
        if prices.empty:
            return pd.DataFrame()

        if method == "simple":
            return prices.pct_change().dropna()
        elif method == "log":
            return np.log(prices / prices.shift(1)).dropna()
        else:
            raise ValueError(
                f"Unknown return method '{method}'. Use 'simple' or 'log'."
            )

    # ── Annualised returns ────────────────────────────────────────────────

    @staticmethod
    def calculate_annualized_returns(
        returns: pd.DataFrame,
        trading_days: int = 252,
    ) -> pd.Series:
        """Annualise mean daily returns.

        Parameters
        ----------
        returns : pd.DataFrame
            Daily returns.
        trading_days : int
            Number of trading days per year.

        Returns
        -------
        pd.Series
            Annualised mean return per asset.
        """
        if returns.empty:
            return pd.Series(dtype=float)
        return returns.mean() * trading_days

    # ── Covariance matrix ─────────────────────────────────────────────────

    @staticmethod
    def calculate_covariance_matrix(
        returns: pd.DataFrame,
        method: Literal["sample", "ledoit_wolf"] = "sample",
        trading_days: int = 252,
    ) -> pd.DataFrame:
        """Compute an annualised covariance matrix.

        Parameters
        ----------
        returns : pd.DataFrame
            Daily returns.
        method : ``"sample"`` | ``"ledoit_wolf"``
            ``"sample"``       → standard sample covariance.
            ``"ledoit_wolf"``  → Ledoit-Wolf shrinkage estimator
            (via ``pypfopt.risk_models.CovarianceShrinkage`` if available,
            otherwise falls back to ``sklearn``).
        trading_days : int
            Annualisation factor.

        Returns
        -------
        pd.DataFrame
            Annualised covariance matrix.
        """
        if returns.empty:
            return pd.DataFrame()

        if method == "sample":
            return returns.cov() * trading_days

        elif method == "ledoit_wolf":
            try:
                # Prefer pypfopt's implementation (handles annualisation)
                from pypfopt.risk_models import CovarianceShrinkage

                # CovarianceShrinkage expects *prices*, but we already have
                # returns.  We can reconstruct a pseudo-price series or use
                # sklearn directly.  Using sklearn for correctness:
                raise ImportError("prefer sklearn path for returns input")
            except (ImportError, Exception):
                pass

            try:
                from sklearn.covariance import LedoitWolf

                lw = LedoitWolf().fit(returns.dropna())
                cov = pd.DataFrame(
                    lw.covariance_,
                    index=returns.columns,
                    columns=returns.columns,
                )
                return cov * trading_days
            except ImportError:
                # Ultimate fallback: sample covariance
                return returns.cov() * trading_days
        else:
            raise ValueError(
                f"Unknown covariance method '{method}'. "
                "Use 'sample' or 'ledoit_wolf'."
            )

    # ── Missing data ──────────────────────────────────────────────────────

    @staticmethod
    def handle_missing_data(
        df: pd.DataFrame,
        method: str = "ffill",
    ) -> pd.DataFrame:
        """Fill or remove missing data.

        Strategy: forward-fill → backward-fill → drop columns that
        still contain any ``NaN`` values.

        Parameters
        ----------
        df : pd.DataFrame
            Raw data potentially containing gaps.
        method : str
            Kept for API flexibility (currently only ``"ffill"``
            strategy is used).

        Returns
        -------
        pd.DataFrame
            Cleaned DataFrame.
        """
        if df.empty:
            return df

        cleaned = df.ffill().bfill()

        # Drop columns that *still* have NaN (e.g. entirely empty columns)
        cols_with_nan = cleaned.columns[cleaned.isna().any()].tolist()
        if cols_with_nan:
            cleaned = cleaned.drop(columns=cols_with_nan)

        return cleaned

    # ── Data alignment ────────────────────────────────────────────────────

    @staticmethod
    def align_data(dataframes: List[pd.DataFrame]) -> List[pd.DataFrame]:
        """Align multiple DataFrames to a common DatetimeIndex.

        Only dates present in **all** DataFrames are retained (inner join).

        Parameters
        ----------
        dataframes : list[pd.DataFrame]
            DataFrames to align.

        Returns
        -------
        list[pd.DataFrame]
            Aligned DataFrames sharing the same index.
        """
        if not dataframes:
            return []

        # Build the common index via successive intersection
        common_index = dataframes[0].index
        for df in dataframes[1:]:
            common_index = common_index.intersection(df.index)

        return [df.loc[common_index] for df in dataframes]

    # ── Rolling returns ───────────────────────────────────────────────────

    @staticmethod
    def calculate_rolling_returns(
        prices: pd.DataFrame,
        window: int = 252,
    ) -> pd.DataFrame:
        """Compute rolling annualised returns.

        Uses the simple growth formula:
        ``(price_t / price_{t-window}) - 1``

        Parameters
        ----------
        prices : pd.DataFrame
            Close prices.
        window : int
            Rolling window in trading days.

        Returns
        -------
        pd.DataFrame
            Rolling annualised returns (``NaN`` for the first
            *window* rows).
        """
        if prices.empty:
            return pd.DataFrame()

        return (prices / prices.shift(window)) - 1
