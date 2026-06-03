"""
🎯 Portfolio Builder Page
Build and optimize your stock portfolio using 3 core strategies.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.fetcher import StockDataFetcher
from data.processor import DataProcessor
from optimization.markowitz import MarkowitzOptimizer
from risk.metrics import RiskMetrics
from visualization.charts import plot_portfolio_allocation, plot_correlation_heatmap, plot_risk_return_scatter
from visualization.styles import get_chart_layout, apply_dynamic_theme, COLORS
from config.settings import DEFAULT_TICKERS, RISK_FREE_RATE, TRADING_DAYS, OPTIMIZATION_METHODS, COLOR_PALETTE
from utils.helpers import format_currency, format_percentage, init_session_state
from utils.translations import _

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="Portfolio Builder", page_icon="🎯", layout="wide")
init_session_state()

# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .result-card {
        background: linear-gradient(135deg, rgba(102,126,234,0.15), rgba(118,75,162,0.08));
        border: 1px solid rgba(102,126,234,0.2);
        border-radius: 14px; padding: 1.3rem; text-align: center;
        transition: all 0.3s ease;
    }
    .result-card:hover { border-color: rgba(102,126,234,0.4); box-shadow: 0 0 15px rgba(102,126,234,0.1); }
    .result-label { font-size: 0.78rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 0.2rem; }
    .result-value {
        font-size: 1.8rem; font-weight: 800;
        background: linear-gradient(135deg, #667eea, #00D2FF);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ──────────────────────────────────────────────────────────────────
st.sidebar.markdown(f"## {_('portfolio_builder')}")
st.sidebar.markdown("---")

selected_tickers = st.sidebar.multiselect(
    "📊 Select Stocks",
    options=DEFAULT_TICKERS + ['BRK-B', 'UNH', 'HD', 'PG', 'MA', 'DIS', 'NFLX', 'ADBE', 'CRM', 'INTC', 'AMD', 'PYPL'],
    default=DEFAULT_TICKERS[:5],
    help="Select 2 or more stocks for your portfolio"
)

investment_amount = st.sidebar.number_input(
    "💰 Investment Amount ($)",
    min_value=1000.0, max_value=10_000_000.0,
    value=float(st.session_state.get('investment_amount', 100000)),
    step=10000.0, format="%.0f"
)

period = st.sidebar.selectbox("📅 Historical Period", ["1y", "2y", "3y", "5y"], index=3)

st.sidebar.markdown("---")
st.sidebar.markdown("### ⚙️ Optimization Settings")

optimization_method = st.sidebar.selectbox("🎯 Strategy", list(OPTIMIZATION_METHODS.keys()))
method_key = OPTIMIZATION_METHODS[optimization_method]

max_weight = st.sidebar.slider("Max Weight per Stock", 0.1, 1.0, 1.0, 0.05)
weight_bounds = (0.0, max_weight)

cov_method = st.sidebar.selectbox("📐 Covariance Method", ["Ledoit-Wolf (Shrinkage)", "Sample"], index=0)
cov_key = 'ledoit_wolf' if 'Ledoit' in cov_method else 'sample'

st.sidebar.markdown("---")
optimize_clicked = st.sidebar.button("🚀 OPTIMIZE PORTFOLIO", use_container_width=True, type="primary")

# ── Main Content ─────────────────────────────────────────────────────────────
fx = st.session_state.get("fx_rate", 1.0)
curr = st.session_state.get("currency", "USD")
curr_sym = curr

st.markdown(f"# {_('portfolio_builder')}")
st.markdown("*Select stocks and optimize your portfolio allocation*")
st.markdown("---")

if len(selected_tickers) < 2:
    st.warning("⚠️ Please select at least **2 stocks** from the sidebar to build a portfolio.")
    st.stop()

# ── Fetch Data ───────────────────────────────────────────────────────────────
fetcher = StockDataFetcher()

with st.spinner("📊 Fetching market data..."):
    prices = fetcher.get_multiple_stocks(selected_tickers, period=period)

if prices.empty:
    st.error("❌ Failed to fetch stock data. Please check your internet connection.")
    st.stop()

prices = DataProcessor.handle_missing_data(prices)
returns = DataProcessor.calculate_returns(prices)

# ── Stock Overview ───────────────────────────────────────────────────────────
st.markdown("### 📋 Selected Stocks")

cols = st.columns(min(len(selected_tickers), 5))
for i, t in enumerate(selected_tickers):
    with cols[i % 5]:
        latest = prices[t].iloc[-1] if t in prices.columns else 0
        daily_ret = returns[t].iloc[-1] if t in returns.columns else 0
        st.metric(t, format_currency(latest * fx, curr_sym), f"{daily_ret:.2%}")

st.markdown("---")

# Charts
col1, col2 = st.columns(2)
with col1:
    fig_corr = plot_correlation_heatmap(returns.corr())
    st.plotly_chart(apply_dynamic_theme(fig_corr), use_container_width=True)
with col2:
    ann_rets = DataProcessor.calculate_annualized_returns(returns)
    ann_vols = returns.std() * np.sqrt(TRADING_DAYS)
    fig_rr = plot_risk_return_scatter(list(ann_rets.index), ann_rets.values, ann_vols.values)
    st.plotly_chart(apply_dynamic_theme(fig_rr), use_container_width=True)

# ── Optimization ─────────────────────────────────────────────────────────────
if optimize_clicked:
    with st.spinner("🧮 Optimizing portfolio..."):
        try:
            expected_returns = DataProcessor.calculate_annualized_returns(returns)
            cov_matrix = DataProcessor.calculate_covariance_matrix(returns, method=cov_key)
            optimizer = MarkowitzOptimizer(expected_returns, cov_matrix, RISK_FREE_RATE)

            if method_key == 'max_sharpe':
                result = optimizer.optimize_max_sharpe(weight_bounds=weight_bounds)
            elif method_key == 'min_vol':
                result = optimizer.optimize_min_volatility(weight_bounds=weight_bounds)
            else:  # equal_weight
                result = optimizer.optimize_equal_weight()

            if result:
                st.session_state['optimized'] = True
                st.session_state['portfolio_tickers'] = selected_tickers
                st.session_state['portfolio_weights'] = result['weights']
                st.session_state['investment_amount'] = investment_amount
                st.session_state['optimization_result'] = result
                st.session_state['prices'] = prices
                st.session_state['returns'] = returns
                st.success("✅ Portfolio optimized successfully!")

        except Exception as e:
            st.error(f"❌ Optimization failed: {str(e)}")

# ── Display Results ──────────────────────────────────────────────────────────
if st.session_state.get('optimized') and st.session_state.get('optimization_result'):
    result = st.session_state['optimization_result']
    weights = result['weights']

    st.markdown("---")
    st.markdown("## 🏆 Optimized Portfolio")

    mc1, mc2, mc3, mc4 = st.columns(4)
    mc1.markdown(f"""<div class="result-card"><div class="result-label">{_('expected_return')}</div><div class="result-value">{{result['expected_return']:.2%}}</div></div>""", unsafe_allow_html=True)
    mc2.markdown(f"""<div class="result-card"><div class="result-label">{_('volatility')}</div><div class="result-value">{{result['volatility']:.2%}}</div></div>""", unsafe_allow_html=True)
    mc3.markdown(f"""<div class="result-card"><div class="result-label">{_('sharpe_ratio')}</div><div class="result-value">{{result['sharpe_ratio']:.3f}}</div></div>""", unsafe_allow_html=True)
    mc4.markdown(f"""<div class="result-card"><div class="result-label">{_('investment_amount')}</div><div class="result-value">{{format_currency(investment_amount * fx, curr_sym)}}</div></div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    alloc_col, table_col = st.columns([1, 1])

    with alloc_col:
        filtered = {k: v for k, v in weights.items() if abs(v) > 0.001}
        fig_alloc = plot_portfolio_allocation(filtered, title="Optimal Allocation")
        st.plotly_chart(apply_dynamic_theme(fig_alloc), use_container_width=True)

    with table_col:
        st.markdown("### 📊 Portfolio Weights")
        rows = []
        for t, w in sorted(weights.items(), key=lambda x: -abs(x[1])):
            if abs(w) > 0.001:
                amt = w * investment_amount
                price = prices[t].iloc[-1] if t in prices.columns and prices[t].iloc[-1] > 0 else 1
                rows.append({
                    'Ticker': t, 'Weight': f"{w:.2%}",
                    'Amount': format_currency(amt * fx, curr_sym),
                    'Shares': f"{amt / price:.1f}",
                    'Price': format_currency(price * fx, curr_sym)
                })
        if rows:
            st.dataframe(pd.DataFrame(rows).set_index('Ticker'), use_container_width=True, height=350)

    st.info("💡 **Tip:** Your optimized portfolio is saved. Navigate to Efficient Frontier, Monte Carlo, or Risk Analysis to analyze it further!")
