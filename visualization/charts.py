"""
visualization/charts.py — Premium Plotly chart library for Portfolio Optimizer.

Every public function returns a fully styled ``plotly.graph_objects.Figure``
using the ``portfolio_dark`` template defined in ``visualization.styles``.

Charts
------
* ``plot_efficient_frontier``      – Efficient frontier scatter with Sharpe colouring.
* ``plot_portfolio_allocation``    – Donut / pie allocation chart.
* ``plot_correlation_heatmap``     – Annotated correlation heatmap.
* ``plot_cumulative_returns``      – Multi-line cumulative return curves.
* ``plot_drawdown``                – Drawdown area chart.
* ``plot_monte_carlo_results``     – Monte-Carlo simulation scatter.
* ``plot_risk_return_scatter``     – Individual-stock risk / return bubbles.
* ``plot_stock_price``             – Candlestick + volume chart.
* ``plot_sector_allocation``       – Treemap of sector weights.
* ``plot_rolling_metrics``         – Rolling metrics multi-line chart.
* ``plot_monthly_returns_heatmap`` – Year × Month heatmap of returns.
* ``plot_future_simulation``       – Spaghetti plot with confidence bands.
"""

from __future__ import annotations

from typing import Dict, List, Optional

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from .styles import COLORS, GRADIENT_COLORS, format_hover_template, get_chart_layout

__all__ = [
    "plot_efficient_frontier",
    "plot_portfolio_allocation",
    "plot_correlation_heatmap",
    "plot_cumulative_returns",
    "plot_drawdown",
    "plot_monte_carlo_results",
    "plot_risk_return_scatter",
    "plot_stock_price",
    "plot_sector_allocation",
    "plot_rolling_metrics",
    "plot_monthly_returns_heatmap",
    "plot_future_simulation",
]

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. Efficient Frontier
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def plot_efficient_frontier(
    frontier_data: dict,
    key_portfolios: Optional[Dict[str, dict]] = None,
    individual_stocks: Optional[Dict[str, dict]] = None,
) -> go.Figure:
    """Plot the efficient frontier coloured by Sharpe ratio.

    Parameters
    ----------
    frontier_data : dict
        Must contain ``'returns'``, ``'volatilities'``, ``'sharpe_ratios'``
        (each a list / array of equal length).
    key_portfolios : dict | None
        ``{name: {'return': float, 'volatility': float, 'sharpe': float}}``.
        Plotted as ★ star markers.
    individual_stocks : dict | None
        ``{ticker: {'return': float, 'volatility': float}}``.
        Plotted as ◆ diamond markers.

    Returns
    -------
    go.Figure
    """
    fig = go.Figure()

    # -- frontier scatter --
    vols = np.asarray(frontier_data["volatilities"])
    rets = np.asarray(frontier_data["returns"])
    sharpes = np.asarray(frontier_data["sharpe_ratios"])

    fig.add_trace(
        go.Scatter(
            x=vols,
            y=rets,
            mode="markers",
            marker=dict(
                size=6,
                color=sharpes,
                colorscale="Viridis",
                colorbar=dict(
                    title=dict(text="Sharpe", font=dict(size=12)),
                    thickness=15,
                    len=0.6,
                    tickfont=dict(size=10),
                ),
                line=dict(width=0.3, color="rgba(255,255,255,0.3)"),
            ),
            hovertemplate=(
                "<b>Volatility</b>: %{x:.2%}<br>"
                "<b>Return</b>: %{y:.2%}<br>"
                "<b>Sharpe</b>: %{marker.color:.3f}"
                "<extra>Frontier</extra>"
            ),
            name="Frontier",
            showlegend=False,
        )
    )

    # -- key portfolios (stars) --
    if key_portfolios:
        for name, data in key_portfolios.items():
            fig.add_trace(
                go.Scatter(
                    x=[data["volatility"]],
                    y=[data["return"]],
                    mode="markers+text",
                    marker=dict(
                        symbol="star",
                        size=18,
                        color=COLORS["accent"],
                        line=dict(width=1.5, color=COLORS["text"]),
                    ),
                    text=[name],
                    textposition="top center",
                    textfont=dict(size=11, color=COLORS["text"]),
                    hovertemplate=(
                        f"<b>{name}</b><br>"
                        f"Volatility: {data['volatility']:.2%}<br>"
                        f"Return: {data['return']:.2%}<br>"
                        f"Sharpe: {data.get('sharpe', 0):.3f}"
                        "<extra></extra>"
                    ),
                    name=name,
                )
            )

    # -- individual stocks (diamonds) --
    if individual_stocks:
        tickers = list(individual_stocks.keys())
        sx = [individual_stocks[t]["volatility"] for t in tickers]
        sy = [individual_stocks[t]["return"] for t in tickers]
        fig.add_trace(
            go.Scatter(
                x=sx,
                y=sy,
                mode="markers+text",
                marker=dict(
                    symbol="diamond",
                    size=12,
                    color=COLORS["info"],
                    line=dict(width=1, color=COLORS["text"]),
                ),
                text=tickers,
                textposition="top center",
                textfont=dict(size=10, color=COLORS["text_muted"]),
                hovertemplate=(
                    "<b>%{text}</b><br>"
                    "Volatility: %{x:.2%}<br>"
                    "Return: %{y:.2%}"
                    "<extra></extra>"
                ),
                name="Stocks",
            )
        )

    fig.update_layout(
        **get_chart_layout("Efficient Frontier", height=550),
        xaxis_title="Annualized Volatility",
        yaxis_title="Annualized Return",
        xaxis_tickformat=".1%",
        yaxis_tickformat=".1%",
    )
    return fig


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2. Portfolio Allocation — Donut Chart
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def plot_portfolio_allocation(
    weights: dict,
    title: str = "Portfolio Allocation",
) -> go.Figure:
    """Render a premium donut chart of portfolio weights.

    Parameters
    ----------
    weights : dict
        ``{ticker: weight}`` — weights should sum to ~1.0.
    title : str
        Chart title.

    Returns
    -------
    go.Figure
    """
    labels = list(weights.keys())
    values = list(weights.values())

    # Pull the largest slice slightly
    pull = [0.05 if v == max(values) else 0 for v in values]

    colors = (GRADIENT_COLORS * ((len(labels) // len(GRADIENT_COLORS)) + 1))[
        : len(labels)
    ]

    fig = go.Figure(
        go.Pie(
            labels=labels,
            values=values,
            hole=0.4,
            pull=pull,
            marker=dict(colors=colors, line=dict(color=COLORS["background"], width=2)),
            textinfo="percent+label",
            textposition="outside",
            textfont=dict(size=12),
            hovertemplate=(
                "<b>%{label}</b><br>"
                "Weight: %{percent}<br>"
                "Value: %{value:.4f}"
                "<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        **get_chart_layout(title, height=500, showlegend=False),
        annotations=[
            dict(
                text="<b>Allocation</b>",
                x=0.5,
                y=0.5,
                font_size=14,
                font_color=COLORS["text_muted"],
                showarrow=False,
            )
        ],
    )
    return fig


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3. Correlation Heatmap
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def plot_correlation_heatmap(corr_matrix: pd.DataFrame) -> go.Figure:
    """Annotated heatmap of a correlation matrix.

    Parameters
    ----------
    corr_matrix : pd.DataFrame
        Square DataFrame of pairwise correlations.

    Returns
    -------
    go.Figure
    """
    labels = list(corr_matrix.columns)
    z = corr_matrix.values

    # Build annotation text
    text_vals = [[f"{val:.2f}" for val in row] for row in z]

    fig = go.Figure(
        go.Heatmap(
            z=z,
            x=labels,
            y=labels,
            zmin=-1,
            zmax=1,
            colorscale="RdBu_r",
            text=text_vals,
            texttemplate="%{text}",
            textfont=dict(size=11),
            colorbar=dict(
                title=dict(text="Correlation", font=dict(size=12)),
                thickness=15,
                len=0.6,
                tickfont=dict(size=10),
            ),
            hovertemplate=(
                "<b>%{x}</b> vs <b>%{y}</b><br>"
                "Correlation: %{z:.3f}"
                "<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        **get_chart_layout("Correlation Matrix", height=550, showlegend=False),
        xaxis=dict(side="bottom", tickangle=-45),
        yaxis=dict(autorange="reversed"),
    )
    return fig


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 4. Cumulative Returns
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def plot_cumulative_returns(
    returns_dict: dict,
    title: str = "Cumulative Returns",
) -> go.Figure:
    """Multi-line cumulative return chart.

    Parameters
    ----------
    returns_dict : dict
        ``{series_name: pd.Series}`` of daily simple returns.
    title : str
        Chart title.

    Returns
    -------
    go.Figure
    """
    _line_colors = [
        COLORS["primary"],
        COLORS["secondary"],
        COLORS["accent"],
        COLORS["success"],
        COLORS["danger"],
        COLORS["warning"],
        COLORS["info"],
    ]

    fig = go.Figure()

    for idx, (name, rets) in enumerate(returns_dict.items()):
        cum = (1 + rets).cumprod()
        color = _line_colors[idx % len(_line_colors)]
        fig.add_trace(
            go.Scatter(
                x=cum.index,
                y=cum.values,
                mode="lines",
                name=name,
                line=dict(color=color, width=2.5),
                hovertemplate=(
                    f"<b>{name}</b><br>"
                    "Date: %{x|%Y-%m-%d}<br>"
                    "Cumulative: %{y:.4f}"
                    "<extra></extra>"
                ),
            )
        )

    # Add a baseline at 1.0
    fig.add_hline(
        y=1.0,
        line_dash="dot",
        line_color=COLORS["text_muted"],
        line_width=1,
        annotation_text="Start",
        annotation_font_color=COLORS["text_muted"],
        annotation_font_size=10,
    )

    fig.update_layout(
        **get_chart_layout(title, height=500),
        xaxis_title="Date",
        yaxis_title="Cumulative Return",
        yaxis_tickformat=".2f",
        hovermode="x unified",
    )
    return fig


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 5. Drawdown
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def plot_drawdown(
    returns: pd.Series,
    title: str = "Drawdown",
) -> go.Figure:
    """Area chart of the drawdown series.

    Parameters
    ----------
    returns : pd.Series
        Daily simple returns.
    title : str
        Chart title.

    Returns
    -------
    go.Figure
    """
    wealth = (1 + returns).cumprod()
    peak = wealth.cummax()
    dd = (wealth - peak) / peak

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=dd.index,
            y=dd.values,
            mode="lines",
            fill="tozeroy",
            fillcolor="rgba(255,69,96,0.25)",
            line=dict(color=COLORS["danger"], width=1.5),
            hovertemplate=(
                "<b>Date</b>: %{x|%Y-%m-%d}<br>"
                "<b>Drawdown</b>: %{y:.2%}"
                "<extra></extra>"
            ),
            name="Drawdown",
        )
    )

    # Max drawdown annotation
    max_dd = dd.min()
    max_dd_date = dd.idxmin()
    fig.add_hline(
        y=max_dd,
        line_dash="dash",
        line_color=COLORS["warning"],
        line_width=1,
        annotation_text=f"Max DD: {max_dd:.2%}",
        annotation_font_color=COLORS["warning"],
        annotation_font_size=11,
    )
    fig.add_trace(
        go.Scatter(
            x=[max_dd_date],
            y=[max_dd],
            mode="markers",
            marker=dict(size=10, color=COLORS["warning"], symbol="circle"),
            showlegend=False,
            hovertemplate=(
                f"<b>Max Drawdown</b><br>"
                f"Date: {max_dd_date}<br>"
                f"Drawdown: {max_dd:.2%}"
                "<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        **get_chart_layout(title, height=400, showlegend=False),
        xaxis_title="Date",
        yaxis_title="Drawdown",
        yaxis_tickformat=".1%",
    )
    return fig


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 6. Monte-Carlo Results
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def plot_monte_carlo_results(
    mc_results: dict,
    key_portfolios: Optional[Dict[str, dict]] = None,
) -> go.Figure:
    """Scatter of Monte-Carlo simulation portfolios coloured by Sharpe.

    Parameters
    ----------
    mc_results : dict
        ``{'returns': list, 'volatilities': list, 'sharpe_ratios': list}``.
    key_portfolios : dict | None
        ``{name: {'return': float, 'volatility': float, 'sharpe': float}}``.

    Returns
    -------
    go.Figure
    """
    fig = go.Figure()

    vols = np.asarray(mc_results["volatilities"])
    rets = np.asarray(mc_results["returns"])
    sharpes = np.asarray(mc_results["sharpe_ratios"])

    fig.add_trace(
        go.Scatter(
            x=vols,
            y=rets,
            mode="markers",
            marker=dict(
                size=4,
                color=sharpes,
                colorscale="Viridis",
                colorbar=dict(
                    title=dict(text="Sharpe", font=dict(size=12)),
                    thickness=15,
                    len=0.6,
                ),
                opacity=0.7,
            ),
            hovertemplate=(
                "Volatility: %{x:.2%}<br>"
                "Return: %{y:.2%}<br>"
                "Sharpe: %{marker.color:.3f}"
                "<extra>Simulation</extra>"
            ),
            name="Simulations",
            showlegend=False,
        )
    )

    if key_portfolios:
        for name, data in key_portfolios.items():
            fig.add_trace(
                go.Scatter(
                    x=[data["volatility"]],
                    y=[data["return"]],
                    mode="markers+text",
                    marker=dict(
                        symbol="star",
                        size=18,
                        color=COLORS["accent"],
                        line=dict(width=1.5, color=COLORS["text"]),
                    ),
                    text=[name],
                    textposition="top center",
                    textfont=dict(size=11, color=COLORS["text"]),
                    hovertemplate=(
                        f"<b>{name}</b><br>"
                        f"Vol: {data['volatility']:.2%}<br>"
                        f"Ret: {data['return']:.2%}<br>"
                        f"Sharpe: {data.get('sharpe', 0):.3f}"
                        "<extra></extra>"
                    ),
                    name=name,
                )
            )

    fig.update_layout(
        **get_chart_layout("Monte Carlo Simulation", height=550),
        xaxis_title="Annualized Volatility",
        yaxis_title="Annualized Return",
        xaxis_tickformat=".1%",
        yaxis_tickformat=".1%",
    )
    return fig


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 7. Risk / Return Scatter
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def plot_risk_return_scatter(
    tickers: list,
    returns: list,
    volatilities: list,
) -> go.Figure:
    """Bubble chart of individual-stock risk vs return.

    Bubble size is proportional to the absolute Sharpe ratio.

    Parameters
    ----------
    tickers : list[str]
    returns : list[float]
        Annualized returns per ticker.
    volatilities : list[float]
        Annualized volatilities per ticker.

    Returns
    -------
    go.Figure
    """
    rets_arr = np.asarray(returns)
    vols_arr = np.asarray(volatilities)
    sharpes = np.where(vols_arr > 0, (rets_arr - 0.05) / vols_arr, 0)
    sizes = np.clip(np.abs(sharpes) * 25, 8, 60)

    colors = (GRADIENT_COLORS * ((len(tickers) // len(GRADIENT_COLORS)) + 1))[
        : len(tickers)
    ]

    fig = go.Figure(
        go.Scatter(
            x=vols_arr,
            y=rets_arr,
            mode="markers+text",
            marker=dict(
                size=sizes,
                color=colors,
                line=dict(width=1, color="rgba(255,255,255,0.4)"),
                opacity=0.85,
            ),
            text=tickers,
            textposition="top center",
            textfont=dict(size=11, color=COLORS["text"]),
            hovertemplate=(
                "<b>%{text}</b><br>"
                "Volatility: %{x:.2%}<br>"
                "Return: %{y:.2%}"
                "<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        **get_chart_layout("Risk vs Return", height=500, showlegend=False),
        xaxis_title="Annualized Volatility",
        yaxis_title="Annualized Return",
        xaxis_tickformat=".1%",
        yaxis_tickformat=".1%",
    )
    return fig


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 8. Stock Price (Candlestick / Line + Volume)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def plot_stock_price(
    df: pd.DataFrame,
    ticker: str,
    indicators: Optional[Dict[str, pd.Series]] = None,
) -> go.Figure:
    """Candlestick (or line) chart with an optional volume subplot.

    Parameters
    ----------
    df : pd.DataFrame
        Must have at least a ``Close`` column. If ``Open``, ``High``,
        ``Low`` are also present a candlestick chart is drawn.
    ticker : str
        Stock ticker symbol (used in the title).
    indicators : dict | None
        ``{indicator_name: pd.Series}`` to overlay (e.g. SMA, EMA).

    Returns
    -------
    go.Figure
    """
    has_ohlc = all(col in df.columns for col in ["Open", "High", "Low", "Close"])
    has_volume = "Volume" in df.columns

    rows = 2 if has_volume else 1
    row_heights = [0.75, 0.25] if has_volume else [1]

    fig = make_subplots(
        rows=rows,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.04,
        row_heights=row_heights,
    )

    # -- price trace --
    if has_ohlc:
        fig.add_trace(
            go.Candlestick(
                x=df.index,
                open=df["Open"],
                high=df["High"],
                low=df["Low"],
                close=df["Close"],
                increasing_line_color=COLORS["success"],
                decreasing_line_color=COLORS["danger"],
                name=ticker,
            ),
            row=1,
            col=1,
        )
    else:
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["Close"],
                mode="lines",
                line=dict(color=COLORS["primary"], width=2),
                name=ticker,
                hovertemplate=(
                    "<b>Date</b>: %{x|%Y-%m-%d}<br>"
                    "<b>Close</b>: $%{y:,.2f}"
                    "<extra></extra>"
                ),
            ),
            row=1,
            col=1,
        )

    # -- indicators --
    if indicators:
        ind_colors = [
            COLORS["accent"],
            COLORS["secondary"],
            COLORS["warning"],
            COLORS["info"],
        ]
        for idx, (ind_name, ind_series) in enumerate(indicators.items()):
            fig.add_trace(
                go.Scatter(
                    x=ind_series.index,
                    y=ind_series.values,
                    mode="lines",
                    line=dict(
                        color=ind_colors[idx % len(ind_colors)],
                        width=1.5,
                        dash="dot",
                    ),
                    name=ind_name,
                    hovertemplate=(
                        f"<b>{ind_name}</b><br>"
                        "Date: %{x|%Y-%m-%d}<br>"
                        "Value: $%{y:,.2f}"
                        "<extra></extra>"
                    ),
                ),
                row=1,
                col=1,
            )

    # -- volume --
    if has_volume:
        vol_colors = [
            COLORS["success"] if c >= o else COLORS["danger"]
            for c, o in zip(df["Close"], df.get("Open", df["Close"]))
        ]
        fig.add_trace(
            go.Bar(
                x=df.index,
                y=df["Volume"],
                marker_color=vol_colors,
                opacity=0.5,
                name="Volume",
                showlegend=False,
                hovertemplate=(
                    "Date: %{x|%Y-%m-%d}<br>"
                    "Volume: %{y:,.0f}"
                    "<extra></extra>"
                ),
            ),
            row=2,
            col=1,
        )
        fig.update_yaxes(title_text="Volume", row=2, col=1)

    fig.update_layout(
        **get_chart_layout(f"{ticker} — Price History", height=600),
        xaxis_rangeslider_visible=False,
        yaxis_title="Price (USD)",
    )
    return fig


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 9. Sector Allocation — Treemap
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def plot_sector_allocation(sector_weights: dict) -> go.Figure:
    """Treemap of portfolio sector weights.

    Parameters
    ----------
    sector_weights : dict
        ``{sector_name: weight}``.

    Returns
    -------
    go.Figure
    """
    sectors = list(sector_weights.keys())
    values = list(sector_weights.values())

    colors = (GRADIENT_COLORS * ((len(sectors) // len(GRADIENT_COLORS)) + 1))[
        : len(sectors)
    ]

    fig = go.Figure(
        go.Treemap(
            labels=sectors,
            parents=[""] * len(sectors),
            values=values,
            marker=dict(
                colors=colors,
                line=dict(width=2, color=COLORS["background"]),
            ),
            textinfo="label+percent entry",
            textfont=dict(size=14),
            hovertemplate=(
                "<b>%{label}</b><br>"
                "Weight: %{value:.2%}<br>"
                "Share: %{percentEntry}"
                "<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        **get_chart_layout("Sector Allocation", height=500, showlegend=False),
    )
    return fig


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 10. Rolling Metrics
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def plot_rolling_metrics(
    metrics_dict: dict,
    title: str = "Rolling Metrics",
) -> go.Figure:
    """Multi-line chart of rolling portfolio metrics.

    Parameters
    ----------
    metrics_dict : dict
        ``{metric_name: pd.Series}`` — each series indexed by date.
    title : str
        Chart title.

    Returns
    -------
    go.Figure
    """
    fig = go.Figure()

    for idx, (name, series) in enumerate(metrics_dict.items()):
        color = GRADIENT_COLORS[idx % len(GRADIENT_COLORS)]
        fig.add_trace(
            go.Scatter(
                x=series.index,
                y=series.values,
                mode="lines",
                name=name,
                line=dict(color=color, width=2),
                hovertemplate=(
                    f"<b>{name}</b><br>"
                    "Date: %{x|%Y-%m-%d}<br>"
                    "Value: %{y:.4f}"
                    "<extra></extra>"
                ),
            )
        )

    fig.update_layout(
        **get_chart_layout(title, height=450),
        xaxis_title="Date",
        yaxis_title="Metric Value",
        hovermode="x unified",
    )
    return fig


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 11. Monthly Returns Heatmap
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

_MONTH_NAMES = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
]


def plot_monthly_returns_heatmap(monthly_returns: pd.DataFrame) -> go.Figure:
    """Year × Month heatmap of portfolio returns.

    Parameters
    ----------
    monthly_returns : pd.DataFrame
        Rows = years, columns = months (1–12). Values are decimal returns.

    Returns
    -------
    go.Figure
    """
    z = monthly_returns.values * 100  # percent
    years = [str(y) for y in monthly_returns.index]
    months = [
        _MONTH_NAMES[int(c) - 1] if isinstance(c, (int, float)) and 1 <= int(c) <= 12 else str(c)
        for c in monthly_returns.columns
    ]

    text_vals = [[f"{v:.1f}%" for v in row] for row in z]

    fig = go.Figure(
        go.Heatmap(
            z=z,
            x=months,
            y=years,
            colorscale="RdYlGn",
            zmid=0,
            text=text_vals,
            texttemplate="%{text}",
            textfont=dict(size=11),
            colorbar=dict(
                title=dict(text="Return %", font=dict(size=12)),
                thickness=15,
                ticksuffix="%",
            ),
            hovertemplate=(
                "<b>%{y} — %{x}</b><br>"
                "Return: %{text}"
                "<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        **get_chart_layout("Monthly Returns", height=max(350, len(years) * 45 + 120), showlegend=False),
        xaxis=dict(side="top"),
        yaxis=dict(autorange="reversed"),
    )
    return fig


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 12. Future Price Simulation (Spaghetti + Confidence Bands)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def plot_future_simulation(
    simulation_paths: pd.DataFrame,
    title: str = "Future Price Simulation",
) -> go.Figure:
    """Spaghetti plot with median and 90 % confidence bands.

    Parameters
    ----------
    simulation_paths : pd.DataFrame
        Each column is one simulated price path; the index is the
        time axis (dates or integers).
    title : str
        Chart title.

    Returns
    -------
    go.Figure
    """
    fig = go.Figure()

    import pandas as pd
    if not hasattr(simulation_paths, "columns") and hasattr(simulation_paths, "shape"):
        # The simulator returns an array of shape (num_paths, days).
        # We need a DataFrame where each column is a path.
        simulation_paths = pd.DataFrame(simulation_paths).T

    # Individual paths (low opacity)
    max_paths_to_draw = min(simulation_paths.shape[1], 200)
    sample_cols = simulation_paths.columns[:max_paths_to_draw]

    for col in sample_cols:
        fig.add_trace(
            go.Scatter(
                x=simulation_paths.index,
                y=simulation_paths[col],
                mode="lines",
                line=dict(color=COLORS["primary"], width=0.5),
                opacity=0.08,
                showlegend=False,
                hoverinfo="skip",
            )
        )

    # Statistics
    median = simulation_paths.median(axis=1)
    p5 = simulation_paths.quantile(0.05, axis=1)
    p95 = simulation_paths.quantile(0.95, axis=1)

    # 90% confidence band (fill between p5 and p95)
    fig.add_trace(
        go.Scatter(
            x=list(simulation_paths.index) + list(simulation_paths.index[::-1]),
            y=list(p95) + list(p5[::-1]),
            fill="toself",
            fillcolor="rgba(108,99,255,0.15)",
            line=dict(color="rgba(0,0,0,0)"),
            name="90% Confidence",
            hoverinfo="skip",
        )
    )

    # Median line
    fig.add_trace(
        go.Scatter(
            x=simulation_paths.index,
            y=median,
            mode="lines",
            line=dict(color=COLORS["secondary"], width=2.5),
            name="Median",
            hovertemplate=(
                "Day: %{x}<br>"
                "Median: $%{y:,.2f}"
                "<extra></extra>"
            ),
        )
    )

    # 5th and 95th percentile lines
    fig.add_trace(
        go.Scatter(
            x=simulation_paths.index,
            y=p5,
            mode="lines",
            line=dict(color=COLORS["danger"], width=1.5, dash="dash"),
            name="5th Percentile",
            hovertemplate="5th %ile: $%{y:,.2f}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=simulation_paths.index,
            y=p95,
            mode="lines",
            line=dict(color=COLORS["success"], width=1.5, dash="dash"),
            name="95th Percentile",
            hovertemplate="95th %ile: $%{y:,.2f}<extra></extra>",
        )
    )

    fig.update_layout(
        **get_chart_layout(title, height=550),
        xaxis_title="Time",
        yaxis_title="Portfolio Value ($)",
        yaxis_tickformat="$,.0f",
        hovermode="x unified",
    )
    return fig
