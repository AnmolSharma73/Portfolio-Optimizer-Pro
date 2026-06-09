"""
Efficient Frontier — Portfolio Optimizer Pro.

Visualises the mean-variance efficient frontier, the Capital Market
Line, and highlights the maximum-Sharpe and minimum-volatility
portfolios.  Users can interactively adjust tickers, lookback
period, and frontier resolution.
"""

from __future__ import annotations

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

from data.fetcher import StockDataFetcher
from data.processor import DataProcessor
from optimization.markowitz import MarkowitzOptimizer
from optimization.efficient_frontier import EfficientFrontierCalculator
from config.settings import (
    APP_NAME,
    DEFAULT_TICKERS,
    RISK_FREE_RATE,
    DEFAULT_PERIOD,
    COLOR_PALETTE,
    GRADIENT_COLORS,
    TRADING_DAYS,
)
from utils.helpers import format_percentage, format_currency, create_metric_card
from visualization.styles import apply_dynamic_theme
from utils.translations import _
from utils.ui import setup_page, render_settings

# ── Page configuration ────────────────────────────────────────────────────────
setup_page(page_title=f"Efficient Frontier - {APP_NAME}", page_icon="scatter-plot", layout="wide")

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* Card container styling */
    .frontier-card {
        background: var(--theme-card);
        border: 1px solid var(--theme-border);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 16px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .frontier-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 40px rgba(108, 99, 255, 0.15);
        border-color: #6C63FF;
    }
    .portfolio-badge {
        display: inline-block;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 0.04em;
    }
    .badge-sharpe {
        background: rgba(255, 215, 0, 0.15);
        color: #FFD700;
        border: 1px solid rgba(255, 215, 0, 0.3);
    }
    .badge-minvol {
        background: rgba(0, 227, 150, 0.15);
        color: #00E396;
        border: 1px solid rgba(0, 227, 150, 0.3);
    }
    .info-box {
        background: var(--theme-card);
        border-left: 4px solid #6C63FF;
        border-radius: 0 12px 12px 0;
        padding: 20px 24px;
        margin: 16px 0;
        color: var(--theme-muted);
        line-height: 1.7;
    }
    .header-gradient {
        background: linear-gradient(135deg, #6C63FF 0%, #00D2FF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 800;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ═══════════════════════════════════════════════════════════════════════════════
# Helper — chart layout base
# ═══════════════════════════════════════════════════════════════════════════════

from visualization.styles import get_chart_layout


# ═══════════════════════════════════════════════════════════════════════════════
# Helper — donut chart for portfolio weights
# ═══════════════════════════════════════════════════════════════════════════════

def _weights_donut(weights: dict, title: str = "Portfolio Allocation") -> go.Figure:
    """Create a premium donut chart for portfolio weights."""
    # Filter out negligible weights
    filtered = {k: v for k, v in weights.items() if v > 0.001}
    labels = list(filtered.keys())
    values = list(filtered.values())

    colors = GRADIENT_COLORS[: len(labels)]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.55,
                marker=dict(colors=colors, line=dict(color="rgba(0,0,0,0.1)", width=1)),
                textinfo="label+percent",
                textfont=dict(size=12),
                hovertemplate="<b>%{label}</b><br>Weight: %{percent}<extra></extra>",
            )
        ]
    )
    fig.update_layout(
        **get_chart_layout(title, height=380, showlegend=False),
        annotations=[
            dict(
                text="<b>Weights</b>",
                x=0.5, y=0.5,
                font=dict(size=14),
                showarrow=False,
            )
        ],
    )
    return apply_dynamic_theme(fig)


# ═══════════════════════════════════════════════════════════════════════════════
# Sidebar
# ═══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("## Frontier Settings")
    st.markdown("---")

    selected_tickers = st.multiselect(
        "Select Tickers",
        options=DEFAULT_TICKERS,
        default=DEFAULT_TICKERS[:5],
        help="Choose at least 2 assets to construct the frontier.",
        key="ef_tickers",
    )

    period = st.selectbox(
        "Historical Period",
        options=["1y", "2y", "3y", "5y", "10y"],
        index=3,
        help="Lookback window for return estimation.",
        key="ef_period",
    )

    num_points = st.slider(
        "Frontier Points",
        min_value=20,
        max_value=200,
        value=50,
        step=10,
        help="More points yield a smoother curve but take longer.",
        key="ef_num_points",
    )

    st.markdown("---")
    generate_btn = st.button(
        "Generate Frontier",
        type="primary",
        use_container_width=True,
        key="ef_generate",
    )


# ═══════════════════════════════════════════════════════════════════════════════
# Page header
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown(f"# {_('efficient_frontier')}")
st.markdown("*Visualize the risk-return frontier and find the optimal portfolio allocation*")
st.markdown("---")
st.markdown(
    """
    <div class="info-box">
    <strong>Modern Portfolio Theory (MPT)</strong> — introduced by Harry Markowitz
    in 1952 — demonstrates that an investor can construct a set of portfolios
    offering the <em>maximum expected return for a given level of risk</em>.
    The <strong>Efficient Frontier</strong> is the upper boundary of this set,
    representing the optimal risk–return trade-off. The <strong>Capital Market
    Line (CML)</strong> extends from the risk-free rate through the tangency
    (maximum-Sharpe) portfolio and defines the best possible trade-off when
    a risk-free asset is included.
    </div>
    """,
    unsafe_allow_html=True,
)

# ═══════════════════════════════════════════════════════════════════════════════
# Main computation & visualisation
# ═══════════════════════════════════════════════════════════════════════════════

if generate_btn:
    # ── Validation ────────────────────────────────────────────────────────
    if len(selected_tickers) < 2:
        st.error("Please select at least **2 tickers** to plot the frontier.")
        st.stop()

    with st.spinner("Fetching market data & computing the efficient frontier …"):
        # 1. Fetch prices ──────────────────────────────────────────────────
        fetcher = StockDataFetcher()
        prices = fetcher.get_multiple_stocks(selected_tickers, period=period)

        if prices.empty or prices.shape[1] < 2:
            st.error("Could not fetch sufficient price data. Try different tickers.")
            st.stop()

        # 2. Calculate returns & covariance ────────────────────────────────
        returns = DataProcessor.calculate_returns(prices)
        if returns.empty or len(returns) < 2:
            st.error("Not enough valid historical return data to compute the efficient frontier.")
            st.stop()
            
        cov_matrix = DataProcessor.calculate_covariance_matrix(
            returns, method="ledoit_wolf"
        )
        expected_returns = DataProcessor.calculate_annualized_returns(returns)
        
        if expected_returns.empty or cov_matrix.empty:
            st.error("Failed to compute expected returns or covariance matrix.")
            st.stop()

        # 3. Compute efficient frontier ────────────────────────────────────
        ef_calc = EfficientFrontierCalculator(
            expected_returns,
            cov_matrix,
            risk_free_rate=RISK_FREE_RATE,
            num_portfolios=num_points,
        )
        frontier_data = ef_calc.compute_frontier()

        if not frontier_data["returns"]:
            st.error("Could not compute the efficient frontier — try adjusting inputs.")
            st.stop()

        # 4. Key portfolios ────────────────────────────────────────────────
        optimizer = MarkowitzOptimizer(expected_returns, cov_matrix, RISK_FREE_RATE)
        max_sharpe = optimizer.optimize_max_sharpe()
        min_vol = optimizer.optimize_min_volatility()

        # 5. Individual stock scatter points ───────────────────────────────
        individual_stocks: dict = {}
        for ticker in selected_tickers:
            if ticker in expected_returns.index and ticker in cov_matrix.index:
                individual_stocks[ticker] = {
                    "return": float(expected_returns[ticker]),
                    "volatility": float(np.sqrt(cov_matrix.loc[ticker, ticker])),
                }

    # ══════════════════════════════════════════════════════════════════════
    # Interactive Efficient Frontier chart
    # ══════════════════════════════════════════════════════════════════════

    st.markdown("### Efficient Frontier & Capital Market Line")

    fig = go.Figure()

    # -- Frontier curve (colour-coded by Sharpe ratio) -----
    fig.add_trace(
        go.Scatter(
            x=frontier_data["volatilities"],
            y=frontier_data["returns"],
            mode="lines+markers",
            name="Efficient Frontier",
            marker=dict(
                size=5,
                color=frontier_data["sharpe_ratios"],
                colorscale=[[0, "#FF4560"], [0.5, "#FEB019"], [1, "#00E396"]],
                colorbar=dict(
                    title=dict(text="Sharpe"),
                    len=0.5,
                    x=1.02,
                ),
                showscale=True,
            ),
            line=dict(color="rgba(108,99,255,0.5)", width=2),
            hovertemplate=(
                "<b>Frontier Portfolio</b><br>"
                "Return: %{y:.2%}<br>"
                "Volatility: %{x:.2%}<br>"
                "<extra></extra>"
            ),
        )
    )

    # -- Max Sharpe point -----
    fig.add_trace(
        go.Scatter(
            x=[max_sharpe["volatility"]],
            y=[max_sharpe["expected_return"]],
            mode="markers+text",
            name=f"Max Sharpe ({max_sharpe['sharpe_ratio']:.2f})",
            marker=dict(
                size=18,
                color="#FFD700",
                symbol="star",
                line=dict(width=2, color="#0E1117"),
            ),
            text=["Max Sharpe"],
            textposition="top right",
            textfont=dict(color="#FFD700", size=12, family="Inter"),
            hovertemplate=(
                "<b>Maximum Sharpe Ratio</b><br>"
                f"Return: {max_sharpe['expected_return']:.2%}<br>"
                f"Volatility: {max_sharpe['volatility']:.2%}<br>"
                f"Sharpe: {max_sharpe['sharpe_ratio']:.2f}<br>"
                "<extra></extra>"
            ),
        )
    )

    # -- Min Volatility point -----
    fig.add_trace(
        go.Scatter(
            x=[min_vol["volatility"]],
            y=[min_vol["expected_return"]],
            mode="markers+text",
            name=f"Min Volatility ({min_vol['volatility']:.2%})",
            marker=dict(
                size=16,
                color="#00E396",
                symbol="diamond",
                line=dict(width=2, color="#0E1117"),
            ),
            text=["Min Vol"],
            textposition="bottom right",
            textfont=dict(color="#00E396", size=12, family="Inter"),
            hovertemplate=(
                "<b>Minimum Volatility</b><br>"
                f"Return: {min_vol['expected_return']:.2%}<br>"
                f"Volatility: {min_vol['volatility']:.2%}<br>"
                f"Sharpe: {min_vol['sharpe_ratio']:.2f}<br>"
                "<extra></extra>"
            ),
        )
    )

    # -- Individual stocks scatter -----
    for i, (ticker, metrics) in enumerate(individual_stocks.items()):
        color = GRADIENT_COLORS[i % len(GRADIENT_COLORS)]
        fig.add_trace(
            go.Scatter(
                x=[metrics["volatility"]],
                y=[metrics["return"]],
                mode="markers+text",
                name=ticker,
                marker=dict(
                    size=11,
                    color=color,
                    line=dict(width=1.5, color="#0E1117"),
                    opacity=0.85,
                ),
                text=[ticker],
                textposition="top center",
                textfont=dict(color=color, size=11),
                hovertemplate=(
                    f"<b>{ticker}</b><br>"
                    f"Return: {metrics['return']:.2%}<br>"
                    f"Volatility: {metrics['volatility']:.2%}<br>"
                    "<extra></extra>"
                ),
            )
        )

    # -- Capital Market Line (CML) -----
    ms_vol = max_sharpe["volatility"]
    ms_ret = max_sharpe["expected_return"]
    cml_slope = (ms_ret - RISK_FREE_RATE) / ms_vol if ms_vol > 0 else 0
    cml_x_end = max(frontier_data["volatilities"]) * 1.15
    cml_y_end = RISK_FREE_RATE + cml_slope * cml_x_end

    fig.add_trace(
        go.Scatter(
            x=[0, cml_x_end],
            y=[RISK_FREE_RATE, cml_y_end],
            mode="lines",
            name="Capital Market Line",
            line=dict(color="rgba(255,215,0,0.45)", width=2, dash="dash"),
            hovertemplate=(
                "<b>CML</b><br>"
                "Rf: %{y:.2%}<br>"
                "<extra></extra>"
            ),
        )
    )

    # -- Risk-free rate annotation -----
    fig.add_annotation(
        x=0,
        y=RISK_FREE_RATE,
        text=f"Rf = {RISK_FREE_RATE:.1%}",
        showarrow=True,
        arrowhead=2,
        arrowcolor="#FFD700",
        font=dict(color="#FFD700", size=11),
        ax=-50,
        ay=20,
    )

    # -- Layout -----
    fig.update_layout(
        **get_chart_layout("", height=620),
        hovermode="closest",
    )
    fig.update_xaxes(title_text="Annualized Volatility (σ)", tickformat=".0%",
                     gridcolor="rgba(255,255,255,0.06)", zerolinecolor="rgba(255,255,255,0.1)")
    fig.update_yaxes(title_text="Annualized Expected Return (μ)", tickformat=".0%",
                     gridcolor="rgba(255,255,255,0.06)", zerolinecolor="rgba(255,255,255,0.1)")

    st.plotly_chart(apply_dynamic_theme(fig), use_container_width=True, key="efficient_frontier_chart")

    # ══════════════════════════════════════════════════════════════════════
    # Tabbed portfolio details
    # ══════════════════════════════════════════════════════════════════════

    tab_sharpe, tab_minvol, tab_compare = st.tabs(
        ["Max Sharpe", "Min Volatility", "Comparison"]
    )

    # ── Tab 1: Max Sharpe ─────────────────────────────────────────────────
    with tab_sharpe:
        st.markdown(
            '<span class="portfolio-badge badge-sharpe">MAXIMUM SHARPE RATIO</span>',
            unsafe_allow_html=True,
        )
        st.markdown("")

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Expected Return", format_percentage(max_sharpe["expected_return"]))
        with c2:
            st.metric("Volatility", format_percentage(max_sharpe["volatility"]))
        with c3:
            st.metric("Sharpe Ratio", f"{max_sharpe['sharpe_ratio']:.3f}")
        with c4:
            top_holding = max(max_sharpe["weights"], key=max_sharpe["weights"].get)
            st.metric("Top Holding", f"{top_holding} ({max_sharpe['weights'][top_holding]:.1%})")

        st.plotly_chart(
            _weights_donut(max_sharpe["weights"], "Max Sharpe — Allocation"),
            use_container_width=True,
            key="donut_max_sharpe",
        )

    # ── Tab 2: Min Volatility ─────────────────────────────────────────────
    with tab_minvol:
        st.markdown(
            '<span class="portfolio-badge badge-minvol">MINIMUM VOLATILITY</span>',
            unsafe_allow_html=True,
        )
        st.markdown("")

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Expected Return", format_percentage(min_vol["expected_return"]))
        with c2:
            st.metric("Volatility", format_percentage(min_vol["volatility"]))
        with c3:
            st.metric("Sharpe Ratio", f"{min_vol['sharpe_ratio']:.3f}")
        with c4:
            top_holding_mv = max(min_vol["weights"], key=min_vol["weights"].get)
            st.metric("Top Holding", f"{top_holding_mv} ({min_vol['weights'][top_holding_mv]:.1%})")

        st.plotly_chart(
            _weights_donut(min_vol["weights"], "Min Volatility — Allocation"),
            use_container_width=True,
            key="donut_min_vol",
        )

    # ── Tab 3: Side-by-side comparison ────────────────────────────────────
    with tab_compare:
        st.markdown("#### Portfolio Weights — Side-by-Side")

        comparison_rows = []
        all_tickers_sorted = sorted(
            set(list(max_sharpe["weights"].keys()) + list(min_vol["weights"].keys()))
        )
        for ticker in all_tickers_sorted:
            ms_w = max_sharpe["weights"].get(ticker, 0.0)
            mv_w = min_vol["weights"].get(ticker, 0.0)
            diff = ms_w - mv_w
            comparison_rows.append(
                {
                    "Ticker": ticker,
                    "Max Sharpe": f"{ms_w:.2%}",
                    "Min Volatility": f"{mv_w:.2%}",
                    "Difference": f"{diff:+.2%}",
                }
            )

        comparison_df = pd.DataFrame(comparison_rows)
        st.dataframe(
            comparison_df,
            use_container_width=True,
            hide_index=True,
            key="comparison_table",
        )

        # Summary metrics comparison
        st.markdown("#### Performance Summary")
        summary_df = pd.DataFrame(
            {
                "Metric": ["Expected Return", "Volatility", "Sharpe Ratio"],
                "Max Sharpe": [
                    format_percentage(max_sharpe["expected_return"]),
                    format_percentage(max_sharpe["volatility"]),
                    f"{max_sharpe['sharpe_ratio']:.3f}",
                ],
                "Min Volatility": [
                    format_percentage(min_vol["expected_return"]),
                    format_percentage(min_vol["volatility"]),
                    f"{min_vol['sharpe_ratio']:.3f}",
                ],
            }
        )
        st.dataframe(
            summary_df,
            use_container_width=True,
            hide_index=True,
            key="summary_table",
        )

    # ══════════════════════════════════════════════════════════════════════
    # Educational expander
    # ══════════════════════════════════════════════════════════════════════

    with st.expander("Understanding the Efficient Frontier", expanded=False):
        st.markdown(
            """
            #### What is the Efficient Frontier?

            The **Efficient Frontier** is the set of portfolios that offer the
            *highest expected return for each level of risk* (standard deviation).
            Any portfolio **below** the frontier is sub-optimal because a higher
            return could be achieved without taking on additional risk.

            #### Key Concepts

            | Concept | Description |
            |---------|-------------|
            | **Max Sharpe Portfolio** | The portfolio with the best risk-adjusted return — it sits at the tangency point where the Capital Market Line touches the frontier. |
            | **Min Volatility Portfolio** | The leftmost point on the frontier — it carries the least total risk among all fully-invested portfolios. |
            | **Capital Market Line** | A straight line from the risk-free rate through the tangency portfolio, representing the optimal mix of the risk-free asset and the market portfolio. |
            | **Diversification** | Combining imperfectly correlated assets shifts the portfolio leftward on the risk axis, reducing overall volatility. |

            #### Assumptions & Limitations

            - Returns are assumed to follow a **multivariate normal distribution**.
            - The covariance matrix is estimated from historical data and may not
              reflect future correlations.
            - Transaction costs, taxes, and liquidity constraints are **not**
              incorporated.
            - The Ledoit-Wolf shrinkage estimator is used to improve covariance
              matrix stability, but extreme market regimes can still distort
              estimates.
            """
        )

else:
    # ── Placeholder when no frontier has been generated yet ────────────────
    st.markdown("---")
    col_a, col_b, col_c = st.columns([1, 2, 1])
    with col_b:
        st.markdown(
            """
            <div style="text-align: center; padding: 80px 20px;">
                <div style="font-size: 4rem; margin-bottom: 16px;"></div>
                <h3 style="color: var(--theme-fg); margin-bottom: 8px;">
                    Ready to Explore the Frontier
                </h3>
                <p style="color: var(--theme-muted); max-width: 440px; margin: 0 auto;">
                    Select your assets and historical period in the sidebar,
                    then click <strong>Generate Frontier</strong> to visualise
                    the optimal risk–return trade-off.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

render_settings()

