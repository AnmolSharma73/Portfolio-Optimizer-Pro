"""
⚖️ Risk Analysis Page
Comprehensive risk metrics dashboard with VaR, drawdown analysis,
rolling metrics, and benchmark comparison.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.fetcher import StockDataFetcher
from data.processor import DataProcessor
from risk.metrics import RiskMetrics
from visualization.charts import (plot_drawdown, plot_correlation_heatmap,
                                   plot_rolling_metrics, plot_cumulative_returns)
from visualization.styles import get_chart_layout, apply_dynamic_theme, COLORS
from config.settings import (DEFAULT_TICKERS, RISK_FREE_RATE, TRADING_DAYS,
                              COLOR_PALETTE, DEFAULT_BENCHMARK, DEFAULT_PERIOD)
from utils.helpers import format_currency, format_percentage, init_session_state
from utils.translations import _
from utils.ui import setup_page

# ── Page Config ──────────────────────────────────────────────────────────────
setup_page(page_title="Risk Analysis", page_icon="shield", layout="wide")
init_session_state()

st.markdown("""
<style>
    .risk-card {
        background: var(--theme-card);
        border: 1px solid rgba(108,99,255,0.2);
        border-radius: 14px;
        padding: 1.2rem;
        text-align: center;
        transition: all 0.3s ease;
        min-height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .risk-card:hover {
        border-color: rgba(108,99,255,0.5);
        box-shadow: 0 4px 20px rgba(108,99,255,0.15);
        transform: translateY(-3px);
    }
    .risk-label {
        font-size: 0.75rem;
        color: var(--theme-muted);
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }
    .risk-value {
        font-size: 1.5rem;
        font-weight: 700;
        margin-top: 0.3rem;
    }
    .risk-good { color: #00E396; }
    .risk-warn { color: #FEB019; }
    .risk-bad { color: #FF4560; }
    .risk-neutral { color: #6C63FF; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ──────────────────────────────────────────────────────────────────
st.sidebar.markdown(f"## {_('risk_analysis')}")
st.sidebar.markdown("---")

# Portfolio selection
use_portfolio = st.sidebar.checkbox("Use Optimized Portfolio",
                                     value=bool(st.session_state.get('optimized')))

if use_portfolio and st.session_state.get('portfolio_tickers'):
    selected_tickers = st.session_state['portfolio_tickers']
    weights = st.session_state.get('portfolio_weights', {})
    st.sidebar.success(f"Using {len(selected_tickers)} stock portfolio")
else:
    selected_tickers = st.sidebar.multiselect(
        "Select Stocks",
        options=DEFAULT_TICKERS + ['BRK-B', 'UNH', 'HD', 'NFLX', 'AMD'],
        default=DEFAULT_TICKERS[:5]
    )
    # Equal weight if no portfolio
    weights = {t: 1.0/len(selected_tickers) for t in selected_tickers} if selected_tickers else {}

period = st.sidebar.selectbox("Period", ["1y", "2y", "3y", "5y"], index=3)

benchmark_options = {"S&P 500": "^GSPC", "NASDAQ": "^IXIC", "Dow Jones": "^DJI", "Russell 2000": "^RUT"}
benchmark_name = st.sidebar.selectbox("Benchmark", list(benchmark_options.keys()))
benchmark_ticker = benchmark_options[benchmark_name]

confidence_level = st.sidebar.slider("VaR Confidence Level", 0.90, 0.99, 0.95, 0.01)

analyze_clicked = st.sidebar.button("ANALYZE RISK", use_container_width=True, type="primary")

# ── Main Content ─────────────────────────────────────────────────────────────
fx = st.session_state.get("fx_rate", 1.0)
curr = st.session_state.get("currency", "USD")
curr_sym = curr

st.markdown(f"# {_('risk_analysis')}")
st.markdown("*Comprehensive risk metrics, VaR analysis, drawdowns & rolling performance*")
st.markdown("---")

if len(selected_tickers) < 1:
    st.warning("Select at least 1 stock.")
    st.stop()

# Fetch data
fetcher = StockDataFetcher()
with st.spinner("Fetching data..."):
    prices = fetcher.get_multiple_stocks(selected_tickers, period=period)
    benchmark_data = fetcher.get_stock_data(benchmark_ticker, period=period)

if prices.empty:
    st.error("Failed to fetch data.")
    st.stop()

prices = DataProcessor.handle_missing_data(prices)
returns = DataProcessor.calculate_returns(prices)

# Calculate portfolio returns
weight_arr = np.array([weights.get(t, 1.0/len(selected_tickers)) for t in returns.columns])
weight_arr = weight_arr / weight_arr.sum()  # Normalize
portfolio_returns = (returns * weight_arr).sum(axis=1)
portfolio_returns.name = 'Portfolio'

# Benchmark returns
benchmark_returns = None
if not benchmark_data.empty:
    bench_ret = DataProcessor.calculate_returns(benchmark_data[['Close']])
    if not bench_ret.empty:
        benchmark_returns = bench_ret['Close']
        # Align
        common_idx = portfolio_returns.index.intersection(benchmark_returns.index)
        portfolio_returns = portfolio_returns.loc[common_idx]
        benchmark_returns = benchmark_returns.loc[common_idx]

# ── Calculate All Metrics ────────────────────────────────────────────────────
all_metrics = RiskMetrics.get_all_metrics(
    portfolio_returns,
    benchmark_returns=benchmark_returns,
    risk_free_rate=RISK_FREE_RATE,
    trading_days=TRADING_DAYS
)

# ── Top Risk Metrics Cards ──────────────────────────────────────────────────
st.markdown("### Key Risk Metrics")

def get_risk_class(metric_name, value):
    """Determine CSS class based on metric value."""
    if metric_name in ['sharpe_ratio', 'sortino_ratio']:
        return 'risk-good' if value > 1 else 'risk-warn' if value > 0 else 'risk-bad'
    elif metric_name == 'max_drawdown':
        return 'risk-good' if abs(value) < 0.1 else 'risk-warn' if abs(value) < 0.25 else 'risk-bad'
    elif metric_name == 'annualized_return':
        return 'risk-good' if value > 0.08 else 'risk-warn' if value > 0 else 'risk-bad'
    return 'risk-neutral'

top_metrics = [
    ("Ann. Return", all_metrics.get('annualized_return', 0), 'annualized_return', '.2%'),
    ("Ann. Volatility", all_metrics.get('annualized_volatility', 0), 'annualized_volatility', '.2%'),
    ("Sharpe Ratio", all_metrics.get('sharpe_ratio', 0), 'sharpe_ratio', '.3f'),
    ("Sortino Ratio", all_metrics.get('sortino_ratio', 0), 'sortino_ratio', '.3f'),
    (f"VaR ({confidence_level:.0%})", all_metrics.get('value_at_risk', 0), 'max_drawdown', '.2%'),
    ("Max Drawdown", all_metrics.get('max_drawdown', 0), 'max_drawdown', '.2%'),
]

cols = st.columns(6)
for col, (label, value, metric_key, fmt) in zip(cols, top_metrics):
    css_class = get_risk_class(metric_key, value)
    formatted = f"{value:{fmt}}" if isinstance(value, (int, float)) else str(value)
    col.markdown(f"""
    <div class="risk-card">
        <div class="risk-label">{label}</div>
        <div class="risk-value {css_class}">{formatted}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Tabs ─────────────────────────────────────────────────────────────────────
tab_overview, tab_drawdown, tab_var, tab_rolling, tab_corr = st.tabs([
    "Overview", "Drawdown", "Value at Risk", "Rolling Metrics", "Correlation"
])

# ── Tab 1: Overview ──────────────────────────────────────────────────────────
with tab_overview:
    ov_col1, ov_col2 = st.columns([1, 1])

    with ov_col1:
        st.markdown("#### All Risk Metrics")
        metrics_display = []
        display_map = {
            'annualized_return': ('Annualized Return', '.2%'),
            'annualized_volatility': ('Annualized Volatility', '.2%'),
            'sharpe_ratio': ('Sharpe Ratio', '.3f'),
            'sortino_ratio': ('Sortino Ratio', '.3f'),
            'calmar_ratio': ('Calmar Ratio', '.3f'),
            'max_drawdown': ('Max Drawdown', '.2%'),
            'value_at_risk': ('Value at Risk (95%)', '.4f'),
            'conditional_var': ('CVaR / Expected Shortfall', '.4f'),
            'omega_ratio': ('Omega Ratio', '.3f'),
            'tail_ratio': ('Tail Ratio', '.3f'),
        }

        # Add benchmark metrics if available
        if benchmark_returns is not None:
            display_map.update({
                'beta': ('Beta', '.3f'),
                'alpha': ('Alpha (Jensen\'s)', '.4f'),
                'information_ratio': ('Information Ratio', '.3f'),
                'treynor_ratio': ('Treynor Ratio', '.4f'),
            })

        for key, (label, fmt) in display_map.items():
            val = all_metrics.get(key, 'N/A')
            if isinstance(val, (int, float)) and not np.isnan(val) and not np.isinf(val):
                metrics_display.append({'Metric': label, 'Value': f"{val:{fmt}}"})
            else:
                metrics_display.append({'Metric': label, 'Value': 'N/A'})

        st.dataframe(pd.DataFrame(metrics_display).set_index('Metric'),
                     use_container_width=True, height=500)

    with ov_col2:
        st.markdown("#### Cumulative Returns")
        returns_dict = {'Portfolio': portfolio_returns}
        if benchmark_returns is not None:
            returns_dict[benchmark_name] = benchmark_returns
        fig_cum = plot_cumulative_returns(returns_dict)
        st.plotly_chart(apply_dynamic_theme(fig_cum), use_container_width=True)

        # Per-stock metrics if multiple
        if len(selected_tickers) > 1:
            st.markdown("#### Per-Stock Metrics")
            stock_metrics = []
            for t in selected_tickers:
                if t in returns.columns:
                    r = returns[t]
                    stock_metrics.append({
                        'Ticker': t,
                        'Return': f"{RiskMetrics.annualized_return(r):.2%}",
                        'Volatility': f"{RiskMetrics.annualized_volatility(r):.2%}",
                        'Sharpe': f"{RiskMetrics.sharpe_ratio(r):.3f}",
                        'Max DD': f"{RiskMetrics.max_drawdown(r):.2%}",
                        'Weight': f"{weights.get(t, 1/len(selected_tickers)):.2%}"
                    })
            st.dataframe(pd.DataFrame(stock_metrics).set_index('Ticker'), use_container_width=True)

# ── Tab 2: Drawdown ─────────────────────────────────────────────────────────
with tab_drawdown:
    fig_dd = plot_drawdown(portfolio_returns, title="Portfolio Drawdown")
    st.plotly_chart(apply_dynamic_theme(fig_dd), use_container_width=True)

    dd_series = RiskMetrics.drawdown_series(portfolio_returns)
    max_dd_val = dd_series.min()
    max_dd_date = dd_series.idxmin()

    dd1, dd2, dd3 = st.columns(3)
    dd1.metric("Maximum Drawdown", f"{max_dd_val:.2%}")
    dd2.metric("Date of Max Drawdown", max_dd_date.strftime('%Y-%m-%d') if hasattr(max_dd_date, 'strftime') else str(max_dd_date))
    dd3.metric("Current Drawdown", f"{dd_series.iloc[-1]:.2%}")

    # Top 5 drawdowns
    st.markdown("#### Significant Drawdown Periods")
    st.info("Drawdown measures peak-to-trough decline. A drawdown of -20% means the portfolio lost 20% from its peak.")

# ── Tab 3: Value at Risk ─────────────────────────────────────────────────────
with tab_var:
    var_col1, var_col2 = st.columns(2)

    with var_col1:
        st.markdown("#### Historical VaR Distribution")
        fig_var = go.Figure()

        fig_var.add_trace(go.Histogram(
            x=portfolio_returns.values,
            nbinsx=80,
            marker_color=COLOR_PALETTE['primary'],
            opacity=0.7,
            name='Daily Returns'
        ))

        # VaR lines
        var_hist = RiskMetrics.value_at_risk(portfolio_returns, confidence=confidence_level, method='historical')
        cvar = RiskMetrics.conditional_var(portfolio_returns, confidence=confidence_level)

        fig_var.add_vline(x=var_hist, line_dash="dash", line_color=COLOR_PALETTE['danger'],
                         annotation_text=f"VaR: {var_hist:.4f}")
        fig_var.add_vline(x=cvar, line_dash="dot", line_color=COLOR_PALETTE['warning'],
                         annotation_text=f"CVaR: {cvar:.4f}")

        fig_var.update_layout(**get_chart_layout(title=f"VaR at {confidence_level:.0%} Confidence", height=450))
        fig_var.update_xaxes(title_text="Daily Return")
        fig_var.update_yaxes(title_text="Frequency")
        st.plotly_chart(apply_dynamic_theme(fig_var), use_container_width=True)

    with var_col2:
        st.markdown("#### VaR Summary")

        var_parametric = RiskMetrics.value_at_risk(portfolio_returns, confidence=confidence_level, method='parametric')
        var_historical = RiskMetrics.value_at_risk(portfolio_returns, confidence=confidence_level, method='historical')

        inv_amt = st.session_state.get('investment_amount', 100000)

        var_data = [
            {'Method': 'Historical VaR', 'Daily VaR': f"{var_historical:.4f}",
             'Dollar Impact': format_currency(abs(var_historical) * inv_amt * fx, curr_sym)},
            {'Method': 'Parametric VaR', 'Daily VaR': f"{var_parametric:.4f}",
             'Dollar Impact': format_currency(abs(var_parametric) * inv_amt * fx, curr_sym)},
            {'Method': 'CVaR (Expected Shortfall)', 'Daily VaR': f"{cvar:.4f}",
             'Dollar Impact': format_currency(abs(cvar) * inv_amt * fx, curr_sym)},
        ]
        st.dataframe(pd.DataFrame(var_data).set_index('Method'), use_container_width=True)

        st.markdown("---")
        st.markdown("#### Interpretation")
        st.markdown(f"""
        - **VaR ({confidence_level:.0%})**: On {(1-confidence_level)*100:.0f}% of days, the portfolio could lose more than 
          **{format_currency(abs(var_historical) * inv_amt * fx, curr_sym)}** on a **{format_currency(inv_amt * fx, curr_sym)}** investment.
        - **CVaR**: When losses exceed VaR, the average loss is **{format_currency(abs(cvar) * inv_amt * fx, curr_sym)}**.
        """)

# ── Tab 4: Rolling Metrics ──────────────────────────────────────────────────
with tab_rolling:
    rolling_window = st.slider("Rolling Window (Trading Days)", 21, 252, 63, 21)

    rolling_sharpe = RiskMetrics.rolling_sharpe(portfolio_returns, window=rolling_window)
    rolling_vol = RiskMetrics.rolling_volatility(portfolio_returns, window=rolling_window)

    r_col1, r_col2 = st.columns(2)

    with r_col1:
        fig_rs = go.Figure()
        fig_rs.add_trace(go.Scatter(
            x=rolling_sharpe.index, y=rolling_sharpe.values,
            fill='tozeroy',
            fillcolor='rgba(108,99,255,0.1)',
            line=dict(color=COLOR_PALETTE['primary'], width=2),
            name='Rolling Sharpe'
        ))
        fig_rs.add_hline(y=0, line_dash="dash", line_color="rgba(255,255,255,0.3)")
        fig_rs.add_hline(y=1, line_dash="dot", line_color=COLOR_PALETTE['success'],
                        annotation_text="Sharpe=1")
        fig_rs.update_layout(**get_chart_layout(
            title=f"Rolling Sharpe Ratio ({rolling_window}d)", height=400))
        st.plotly_chart(apply_dynamic_theme(fig_rs), use_container_width=True)

    with r_col2:
        fig_rv = go.Figure()
        fig_rv.add_trace(go.Scatter(
            x=rolling_vol.index, y=rolling_vol.values,
            fill='tozeroy',
            fillcolor='rgba(255,69,96,0.1)',
            line=dict(color=COLOR_PALETTE['danger'], width=2),
            name='Rolling Volatility'
        ))
        fig_rv.update_layout(**get_chart_layout(
            title=f"Rolling Volatility ({rolling_window}d)", height=400))
        fig_rv.update_yaxes(tickformat='.1%')
        st.plotly_chart(apply_dynamic_theme(fig_rv), use_container_width=True)

# ── Tab 5: Correlation ──────────────────────────────────────────────────────
with tab_corr:
    if len(selected_tickers) > 1:
        fig_corr = plot_correlation_heatmap(returns.corr())
        st.plotly_chart(apply_dynamic_theme(fig_corr), use_container_width=True)
    else:
        st.info("Select multiple stocks to see correlation analysis.")
