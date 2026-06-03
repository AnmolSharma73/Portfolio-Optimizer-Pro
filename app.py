import streamlit as st
import importlib
import config.settings
importlib.reload(config.settings)
from config.settings import *
from utils.helpers import *
from utils.translations import _
from utils.ui import setup_page

# ─── Page Config ──────────────────────────────────────────────────────────────
setup_page(page_title=APP_NAME, page_icon="📊", layout="wide")
init_session_state()

# ─── Main Content ─────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
.anim {{ animation: fadeIn 0.8s ease-in; }}
@keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}

.hero-title {{
    background: linear-gradient(135deg, #667eea 0%, #764ba2 30%, #f093fb 60%, #667eea 100%);
    background-size: 200% 200%;
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
    font-size: 2.6rem; font-weight: 800; line-height: 1.2; margin-bottom: 0.2rem;
}}
.hero-sub {{ color: {COLOR_PALETTE['text_muted']}; font-size: 1.05rem; font-weight: 400; }}

.welcome {{
    background: linear-gradient(135deg, rgba(102,126,234,0.1), rgba(118,75,162,0.06));
    border: 1px solid rgba(102,126,234,0.15);
    border-radius: 16px; padding: 1.8rem; margin: 1.5rem 0;
}}
.welcome h3 {{ font-weight: 700; margin-bottom: 0.4rem; font-size: 1.2rem; }}
.welcome p {{ color: {COLOR_PALETTE['text_muted']}; line-height: 1.7; margin: 0; font-size: 0.92rem; }}

.stat-card {{
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px; padding: 1.1rem; text-align: center;
}}
.stat-card .s-val {{
    font-size: 1.6rem; font-weight: 800;
    background: linear-gradient(135deg, #667eea, #f093fb);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}}
.stat-card .s-lbl {{ font-size: 0.72rem; color: {COLOR_PALETTE['text_muted']}; text-transform: uppercase; margin-top: 0.2rem; font-weight: 600; }}

.footer {{ text-align: center; padding: 1.5rem 0 0.5rem; color: {COLOR_PALETTE['text_muted']}; font-size: 0.72rem; margin-top: 2rem; }}
</style>
<div class="anim">
    <div class="hero-title">{_('app_title')}</div>
    <div class="hero-sub">Optimize, Analyze & Manage Your Stock Portfolio Globally</div>
</div>
""", unsafe_allow_html=True)

st.markdown("")

# Welcome Banner
st.markdown(f"""
<div class="welcome anim">
    <h3>Welcome to Portfolio Optimizer Pro 🚀</h3>
    <p>
        Build optimized portfolios using <strong>Modern Portfolio Theory</strong>.
        Compare stocks, visualize the efficient frontier, run Monte Carlo simulations,
        and analyze portfolio risk — all powered by real market data from Yahoo Finance.
    </p>
</div>
""", unsafe_allow_html=True)

# Quick Stats if portfolio exists
if st.session_state.get("portfolio_weights") and st.session_state.get("optimization_result"):
    results = st.session_state["optimization_result"]
    inv = st.session_state.get("investment_amount", 100000)
    fx = st.session_state.get("fx_rate", 1.0)
    curr_sym = current_curr.split(" ")[1].strip("()")

    st.markdown("### ⚡ Your Portfolio")
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f"""<div class="stat-card"><div class="s-val">{format_percentage(results.get('expected_return', 0))}</div><div class="s-lbl">{_('expected_return')}</div></div>""", unsafe_allow_html=True)
    c2.markdown(f"""<div class="stat-card"><div class="s-val">{format_percentage(results.get('volatility', 0))}</div><div class="s-lbl">{_('volatility')}</div></div>""", unsafe_allow_html=True)
    c3.markdown(f"""<div class="stat-card"><div class="s-val">{results.get('sharpe_ratio', 0):.2f}</div><div class="s-lbl">{_('sharpe_ratio')}</div></div>""", unsafe_allow_html=True)
    c4.markdown(f"""<div class="stat-card"><div class="s-val">{format_currency(inv * fx, curr_sym)}</div><div class="s-lbl">Portfolio Value</div></div>""", unsafe_allow_html=True)
    st.markdown("")

# Feature Cards using Streamlit columns for layout and standard buttons for routing
st.markdown("### 🧩 Tools")

features = [
    (
        '<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#6C63FF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/></svg>',
        _("stock_analysis"), "Research individual stocks with candlestick charts, technical indicators, and key financial statistics.", "pages/1_📈_Stock_Analysis.py"
    ),
    (
        '<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#00D2FF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>',
        _("portfolio_builder"), "Select stocks and optimize using Max Sharpe, Min Volatility, or Equal Weight strategies.", "pages/2_🎯_Portfolio_Builder.py"
    ),
    (
        '<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#FFD700" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"/><path d="M18 17V9"/><path d="M13 17V5"/><path d="M8 17v-3"/></svg>',
        _("efficient_frontier"), "Visualize the risk-return frontier and find the optimal portfolio allocation.", "pages/3_📊_Efficient_Frontier.py"
    ),
    (
        '<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#FF4560" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg>',
        _("monte_carlo"), "Simulate thousands of random portfolios to explore the distribution of outcomes.", "pages/4_🎲_Monte_Carlo.py"
    ),
    (
        '<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#00E396" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m16 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="m2 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="M7 21h10"/><path d="M12 3v18"/><path d="M3 7h2c2 0 5-1 7-2 2 1 5 2 7 2h2"/></svg>',
        _("risk_analysis"), "Measure portfolio risk with Sharpe, Sortino, VaR, CVaR, drawdown, and 10+ metrics.", "pages/5_⚖️_Risk_Analysis.py"
    ),
]

col1, col2 = st.columns(2)
for i, (svg_icon, title, desc, path) in enumerate(features):
    c = col1 if i % 2 == 0 else col2
    with c:
        st.markdown(f"""
        <div style="border: 1px solid rgba(255,255,255,0.06); border-radius: 14px; padding: 1.3rem; margin-bottom: 0.5rem; height: 160px; text-align: left; display: flex; flex-direction: column; justify-content: center;">
            <div style="margin-bottom: 0.5rem;">{svg_icon}</div>
            <div style="font-size: 1.1rem; font-weight: 700; margin-bottom: 0.3rem;">{title}</div>
            <div style="font-size: 0.85rem; color: {COLOR_PALETTE['text_muted']}; line-height: 1.4;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"Go to {title} ↗", key=f"btn_{i}", use_container_width=True):
            st.switch_page(path)

st.markdown("")

# How it works
with st.expander("📖 How to Use This App"):
    st.markdown("""
    **Step 1 — Stock Analysis** → Research and compare stocks using historical price data and technical indicators.

    **Step 2 — Portfolio Builder** → Select stocks, choose an optimization strategy, and find optimal weights.

    **Step 3 — Efficient Frontier** → See where your portfolio sits on the risk-return frontier.

    **Step 4 — Monte Carlo** → Run simulations to understand the range of possible outcomes.

    **Step 5 — Risk Analysis** → Deep-dive into risk metrics like VaR, drawdown, and Sharpe ratio.
    """)

# Footer
st.markdown(f"""
<div class="footer">
    Portfolio Optimizer Pro v2.0 &nbsp;•&nbsp; Powered by Modern Portfolio Theory &nbsp;•&nbsp; Real-time Data via Yahoo Finance
</div>
""", unsafe_allow_html=True)
