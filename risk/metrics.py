"""
Risk Metrics Module
===================

Comprehensive collection of portfolio risk and performance metrics.
All methods are static and operate on pandas Series of returns.
"""

import numpy as np
import pandas as pd
from scipy import stats


class RiskMetrics:
    """
    A collection of static methods for computing portfolio risk and
    performance metrics.

    All methods accept daily return series (as ``pd.Series``) and,
    where applicable, annualise results using the supplied
    ``trading_days`` parameter (default **252**).

    Default risk-free rate: **0.05** (5 % annualised).
    """

    # ------------------------------------------------------------------
    # Core return / volatility helpers
    # ------------------------------------------------------------------

    @staticmethod
    def annualized_return(
        returns: pd.Series,
        trading_days: int = 252,
    ) -> float:
        """Compute the annualised arithmetic mean return.

        Parameters
        ----------
        returns : pd.Series
            Daily simple returns.
        trading_days : int, optional
            Number of trading days per year, by default 252.

        Returns
        -------
        float
            Annualised return.
        """
        try:
            if returns.empty:
                return 0.0
            return float(returns.mean() * trading_days)
        except Exception:
            return 0.0

    @staticmethod
    def annualized_volatility(
        returns: pd.Series,
        trading_days: int = 252,
    ) -> float:
        """Compute annualised volatility (standard deviation).

        Parameters
        ----------
        returns : pd.Series
            Daily simple returns.
        trading_days : int, optional
            Number of trading days per year, by default 252.

        Returns
        -------
        float
            Annualised volatility.
        """
        try:
            if returns.empty:
                return 0.0
            return float(returns.std() * np.sqrt(trading_days))
        except Exception:
            return 0.0

    @staticmethod
    def sharpe_ratio(
        returns: pd.Series,
        risk_free_rate: float = 0.05,
        trading_days: int = 252,
    ) -> float:
        """Compute the annualised Sharpe ratio.

        Parameters
        ----------
        returns : pd.Series
            Daily simple returns.
        risk_free_rate : float, optional
            Annualised risk-free rate, by default 0.05.
        trading_days : int, optional
            Number of trading days per year, by default 252.

        Returns
        -------
        float
            Sharpe ratio.
        """
        try:
            ann_ret = RiskMetrics.annualized_return(returns, trading_days)
            ann_vol = RiskMetrics.annualized_volatility(returns, trading_days)
            if ann_vol == 0.0:
                return 0.0
            return float((ann_ret - risk_free_rate) / ann_vol)
        except Exception:
            return 0.0

    @staticmethod
    def sortino_ratio(
        returns: pd.Series,
        risk_free_rate: float = 0.05,
        trading_days: int = 252,
    ) -> float:
        """Compute the annualised Sortino ratio.

        Uses downside deviation (standard deviation of negative returns
        only) instead of total volatility.

        Parameters
        ----------
        returns : pd.Series
            Daily simple returns.
        risk_free_rate : float, optional
            Annualised risk-free rate, by default 0.05.
        trading_days : int, optional
            Number of trading days per year, by default 252.

        Returns
        -------
        float
            Sortino ratio.
        """
        try:
            if returns.empty:
                return 0.0
            ann_ret = RiskMetrics.annualized_return(returns, trading_days)
            negative_returns = returns[returns < 0]
            if negative_returns.empty:
                return 0.0
            downside_dev = float(negative_returns.std() * np.sqrt(trading_days))
            if downside_dev == 0.0:
                return 0.0
            return float((ann_ret - risk_free_rate) / downside_dev)
        except Exception:
            return 0.0

    @staticmethod
    def calmar_ratio(
        returns: pd.Series,
        trading_days: int = 252,
    ) -> float:
        """Compute the Calmar ratio (annualised return / |max drawdown|).

        Parameters
        ----------
        returns : pd.Series
            Daily simple returns.
        trading_days : int, optional
            Number of trading days per year, by default 252.

        Returns
        -------
        float
            Calmar ratio.
        """
        try:
            ann_ret = RiskMetrics.annualized_return(returns, trading_days)
            mdd = RiskMetrics.max_drawdown(returns)
            if mdd == 0.0:
                return 0.0
            return float(ann_ret / abs(mdd))
        except Exception:
            return 0.0

    # ------------------------------------------------------------------
    # Drawdown metrics
    # ------------------------------------------------------------------

    @staticmethod
    def max_drawdown(returns: pd.Series) -> float:
        """Compute the maximum drawdown (peak-to-trough decline).

        Parameters
        ----------
        returns : pd.Series
            Daily simple returns.

        Returns
        -------
        float
            Maximum drawdown as a *negative* value (e.g. -0.25 for 25 %).
        """
        try:
            if returns.empty:
                return 0.0
            dd_series = RiskMetrics.drawdown_series(returns)
            return float(dd_series.min())
        except Exception:
            return 0.0

    @staticmethod
    def drawdown_series(returns: pd.Series) -> pd.Series:
        """Compute the full drawdown time series.

        Parameters
        ----------
        returns : pd.Series
            Daily simple returns.

        Returns
        -------
        pd.Series
            Drawdown series where each value is the decline from the
            running peak (non-positive values).
        """
        try:
            if returns.empty:
                return pd.Series(dtype=float)
            cumulative = (1 + returns).cumprod()
            running_max = cumulative.cummax()
            drawdown = (cumulative - running_max) / running_max
            return drawdown
        except Exception:
            return pd.Series(dtype=float)

    # ------------------------------------------------------------------
    # Value-at-Risk & Expected Shortfall
    # ------------------------------------------------------------------

    @staticmethod
    def value_at_risk(
        returns: pd.Series,
        confidence: float = 0.95,
        method: str = "historical",
    ) -> float:
        """Compute Value-at-Risk (VaR) at the given confidence level.

        Parameters
        ----------
        returns : pd.Series
            Daily simple returns.
        confidence : float, optional
            Confidence level (e.g. 0.95 for 95 %), by default 0.95.
        method : str, optional
            ``'historical'`` – uses empirical percentile.
            ``'parametric'`` – assumes normal distribution and uses
            ``mean - z * std`` (via ``scipy.stats.norm.ppf``).

        Returns
        -------
        float
            VaR value (typically negative, representing the loss
            threshold).
        """
        try:
            if returns.empty:
                return 0.0
            if method == "historical":
                return float(np.percentile(returns, (1 - confidence) * 100))
            elif method == "parametric":
                mu = returns.mean()
                sigma = returns.std()
                if sigma == 0.0:
                    return 0.0
                z = stats.norm.ppf(1 - confidence)
                return float(mu + z * sigma)
            else:
                raise ValueError(
                    f"Unknown VaR method '{method}'. "
                    "Use 'historical' or 'parametric'."
                )
        except Exception:
            return 0.0

    @staticmethod
    def conditional_var(
        returns: pd.Series,
        confidence: float = 0.95,
    ) -> float:
        """Compute Conditional VaR (Expected Shortfall / CVaR).

        The mean of all returns that fall below the VaR threshold.

        Parameters
        ----------
        returns : pd.Series
            Daily simple returns.
        confidence : float, optional
            Confidence level, by default 0.95.

        Returns
        -------
        float
            CVaR (expected shortfall).
        """
        try:
            if returns.empty:
                return 0.0
            var = RiskMetrics.value_at_risk(returns, confidence, method="historical")
            tail = returns[returns <= var]
            if tail.empty:
                return float(var)
            return float(tail.mean())
        except Exception:
            return 0.0

    # ------------------------------------------------------------------
    # Benchmark-relative metrics
    # ------------------------------------------------------------------

    @staticmethod
    def beta(
        returns: pd.Series,
        benchmark_returns: pd.Series,
    ) -> float:
        """Compute portfolio beta relative to a benchmark.

        Parameters
        ----------
        returns : pd.Series
            Portfolio daily returns.
        benchmark_returns : pd.Series
            Benchmark daily returns.

        Returns
        -------
        float
            Portfolio beta.
        """
        try:
            aligned = pd.concat(
                [returns, benchmark_returns], axis=1, join="inner"
            ).dropna()
            if aligned.empty or len(aligned) < 2:
                return 0.0
            port = aligned.iloc[:, 0]
            bench = aligned.iloc[:, 1]
            cov_matrix = np.cov(port, bench)
            bench_var = cov_matrix[1, 1]
            if bench_var == 0.0:
                return 0.0
            return float(cov_matrix[0, 1] / bench_var)
        except Exception:
            return 0.0

    @staticmethod
    def alpha(
        returns: pd.Series,
        benchmark_returns: pd.Series,
        risk_free_rate: float = 0.05,
        trading_days: int = 252,
    ) -> float:
        """Compute Jensen's alpha.

        ``alpha = ann_return - (rf + beta * (benchmark_ann_return - rf))``

        Parameters
        ----------
        returns : pd.Series
            Portfolio daily returns.
        benchmark_returns : pd.Series
            Benchmark daily returns.
        risk_free_rate : float, optional
            Annualised risk-free rate, by default 0.05.
        trading_days : int, optional
            Number of trading days per year, by default 252.

        Returns
        -------
        float
            Jensen's alpha (annualised).
        """
        try:
            ann_ret = RiskMetrics.annualized_return(returns, trading_days)
            bench_ann_ret = RiskMetrics.annualized_return(
                benchmark_returns, trading_days
            )
            port_beta = RiskMetrics.beta(returns, benchmark_returns)
            return float(
                ann_ret - (risk_free_rate + port_beta * (bench_ann_ret - risk_free_rate))
            )
        except Exception:
            return 0.0

    @staticmethod
    def information_ratio(
        returns: pd.Series,
        benchmark_returns: pd.Series,
        trading_days: int = 252,
    ) -> float:
        """Compute the Information Ratio.

        ``IR = mean(active_return) / std(active_return) * sqrt(trading_days)``

        Parameters
        ----------
        returns : pd.Series
            Portfolio daily returns.
        benchmark_returns : pd.Series
            Benchmark daily returns.
        trading_days : int, optional
            Number of trading days per year, by default 252.

        Returns
        -------
        float
            Information ratio.
        """
        try:
            aligned = pd.concat(
                [returns, benchmark_returns], axis=1, join="inner"
            ).dropna()
            if aligned.empty or len(aligned) < 2:
                return 0.0
            active_return = aligned.iloc[:, 0] - aligned.iloc[:, 1]
            tracking_std = active_return.std()
            if tracking_std == 0.0:
                return 0.0
            return float(
                active_return.mean() / tracking_std * np.sqrt(trading_days)
            )
        except Exception:
            return 0.0

    @staticmethod
    def treynor_ratio(
        returns: pd.Series,
        benchmark_returns: pd.Series,
        risk_free_rate: float = 0.05,
        trading_days: int = 252,
    ) -> float:
        """Compute the Treynor ratio.

        ``(annualised_return - rf) / beta``

        Parameters
        ----------
        returns : pd.Series
            Portfolio daily returns.
        benchmark_returns : pd.Series
            Benchmark daily returns.
        risk_free_rate : float, optional
            Annualised risk-free rate, by default 0.05.
        trading_days : int, optional
            Number of trading days per year, by default 252.

        Returns
        -------
        float
            Treynor ratio.
        """
        try:
            ann_ret = RiskMetrics.annualized_return(returns, trading_days)
            port_beta = RiskMetrics.beta(returns, benchmark_returns)
            if port_beta == 0.0:
                return 0.0
            return float((ann_ret - risk_free_rate) / port_beta)
        except Exception:
            return 0.0

    # ------------------------------------------------------------------
    # Additional ratios
    # ------------------------------------------------------------------

    @staticmethod
    def omega_ratio(
        returns: pd.Series,
        threshold: float = 0.0,
        trading_days: int = 252,
    ) -> float:
        """Compute the Omega ratio.

        ``Omega = sum(excess gains) / sum(excess losses)``
        where excess = returns - (threshold / trading_days).

        Parameters
        ----------
        returns : pd.Series
            Daily simple returns.
        threshold : float, optional
            Annualised threshold return, by default 0.0.
        trading_days : int, optional
            Number of trading days per year, by default 252.

        Returns
        -------
        float
            Omega ratio.
        """
        try:
            if returns.empty:
                return 0.0
            daily_threshold = threshold / trading_days
            excess = returns - daily_threshold
            gains = excess[excess > 0].sum()
            losses = abs(excess[excess <= 0].sum())
            if losses == 0.0:
                return 0.0
            return float(gains / losses)
        except Exception:
            return 0.0

    @staticmethod
    def tail_ratio(
        returns: pd.Series,
        confidence: float = 0.95,
    ) -> float:
        """Compute the Tail ratio.

        ``tail_ratio = abs(95th percentile) / abs(5th percentile)``

        A ratio > 1 indicates the right tail is fatter (more large gains
        than large losses).

        Parameters
        ----------
        returns : pd.Series
            Daily simple returns.
        confidence : float, optional
            Confidence level used to define the percentile, by default
            0.95.

        Returns
        -------
        float
            Tail ratio.
        """
        try:
            if returns.empty:
                return 0.0
            upper = np.percentile(returns, confidence * 100)
            lower = np.percentile(returns, (1 - confidence) * 100)
            if lower == 0.0:
                return 0.0
            return float(abs(upper) / abs(lower))
        except Exception:
            return 0.0

    # ------------------------------------------------------------------
    # Rolling metrics
    # ------------------------------------------------------------------

    @staticmethod
    def rolling_sharpe(
        returns: pd.Series,
        window: int = 63,
        risk_free_rate: float = 0.05,
        trading_days: int = 252,
    ) -> pd.Series:
        """Compute a rolling Sharpe ratio.

        Parameters
        ----------
        returns : pd.Series
            Daily simple returns.
        window : int, optional
            Rolling window size in trading days, by default 63
            (≈ 1 quarter).
        risk_free_rate : float, optional
            Annualised risk-free rate, by default 0.05.
        trading_days : int, optional
            Number of trading days per year, by default 252.

        Returns
        -------
        pd.Series
            Rolling Sharpe ratio series.
        """
        try:
            if returns.empty:
                return pd.Series(dtype=float)
            rolling_mean = returns.rolling(window=window).mean() * trading_days
            rolling_std = returns.rolling(window=window).std() * np.sqrt(trading_days)
            rolling_std = rolling_std.replace(0.0, np.nan)
            result = (rolling_mean - risk_free_rate) / rolling_std
            return result
        except Exception:
            return pd.Series(dtype=float)

    @staticmethod
    def rolling_volatility(
        returns: pd.Series,
        window: int = 63,
        trading_days: int = 252,
    ) -> pd.Series:
        """Compute rolling annualised volatility.

        Parameters
        ----------
        returns : pd.Series
            Daily simple returns.
        window : int, optional
            Rolling window size in trading days, by default 63
            (≈ 1 quarter).
        trading_days : int, optional
            Number of trading days per year, by default 252.

        Returns
        -------
        pd.Series
            Rolling annualised volatility series.
        """
        try:
            if returns.empty:
                return pd.Series(dtype=float)
            return returns.rolling(window=window).std() * np.sqrt(trading_days)
        except Exception:
            return pd.Series(dtype=float)

    # ------------------------------------------------------------------
    # Comprehensive summary
    # ------------------------------------------------------------------

    @staticmethod
    def get_all_metrics(
        returns: pd.Series,
        benchmark_returns: pd.Series = None,
        risk_free_rate: float = 0.05,
        trading_days: int = 252,
    ) -> dict:
        """Compute all available risk and performance metrics.

        Parameters
        ----------
        returns : pd.Series
            Portfolio daily returns.
        benchmark_returns : pd.Series, optional
            Benchmark daily returns. When provided, benchmark-relative
            metrics (beta, alpha, information ratio, Treynor ratio) are
            included.
        risk_free_rate : float, optional
            Annualised risk-free rate, by default 0.05.
        trading_days : int, optional
            Number of trading days per year, by default 252.

        Returns
        -------
        dict
            Dictionary of metric name → value.
        """
        metrics: dict = {}

        try:
            # -- Standalone metrics --
            metrics["annualized_return"] = RiskMetrics.annualized_return(
                returns, trading_days
            )
            metrics["annualized_volatility"] = RiskMetrics.annualized_volatility(
                returns, trading_days
            )
            metrics["sharpe_ratio"] = RiskMetrics.sharpe_ratio(
                returns, risk_free_rate, trading_days
            )
            metrics["sortino_ratio"] = RiskMetrics.sortino_ratio(
                returns, risk_free_rate, trading_days
            )
            metrics["calmar_ratio"] = RiskMetrics.calmar_ratio(
                returns, trading_days
            )
            metrics["max_drawdown"] = RiskMetrics.max_drawdown(returns)
            metrics["value_at_risk_95"] = RiskMetrics.value_at_risk(
                returns, confidence=0.95, method="historical"
            )
            metrics["conditional_var_95"] = RiskMetrics.conditional_var(
                returns, confidence=0.95
            )
            metrics["value_at_risk_99"] = RiskMetrics.value_at_risk(
                returns, confidence=0.99, method="historical"
            )
            metrics["conditional_var_99"] = RiskMetrics.conditional_var(
                returns, confidence=0.99
            )
            metrics["omega_ratio"] = RiskMetrics.omega_ratio(
                returns, threshold=0.0, trading_days=trading_days
            )
            metrics["tail_ratio"] = RiskMetrics.tail_ratio(
                returns, confidence=0.95
            )

            # -- Benchmark-relative metrics --
            if benchmark_returns is not None:
                metrics["beta"] = RiskMetrics.beta(returns, benchmark_returns)
                metrics["alpha"] = RiskMetrics.alpha(
                    returns, benchmark_returns, risk_free_rate, trading_days
                )
                metrics["information_ratio"] = RiskMetrics.information_ratio(
                    returns, benchmark_returns, trading_days
                )
                metrics["treynor_ratio"] = RiskMetrics.treynor_ratio(
                    returns, benchmark_returns, risk_free_rate, trading_days
                )
        except Exception:
            pass

        return metrics
