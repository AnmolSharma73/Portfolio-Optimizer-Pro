import streamlit as st
import importlib
import config.settings
importlib.reload(config.settings)
from config.settings import *
from utils.helpers import *
from utils.translations import _

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title=APP_NAME, page_icon="📊", layout="wide", initial_sidebar_state="expanded")
init_session_state()

theme = st.session_state.get("theme", "dark")
t_bg = "#0E1117" if theme == "dark" else "#F8FAFC"
t_fg = "#f1f5f9" if theme == "dark" else "#0f172a"
t_card = "#1A1F2E" if theme == "dark" else "#FFFFFF"
t_card_hover = "#252B3B" if theme == "dark" else "#F1F5F9"
t_sidebar = "linear-gradient(180deg, #111928, #0e1117, #111928)" if theme == "dark" else "linear-gradient(180deg, #F8FAFC, #FFFFFF, #F8FAFC)"
t_border = "rgba(255,255,255,0.06)" if theme == "dark" else "rgba(0,0,0,0.08)"
t_muted = "#94a3b8" if theme == "dark" else "#64748b"
t_input = "#1a1f2e" if theme == "dark" else "#FFFFFF"

# ─── Dynamic CSS Theme ────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [data-testid="stAppViewContainer"] {{
    font-family: 'Inter', sans-serif !important;
    background-color: {t_bg} !important;
    color: {t_fg} !important;
}}

.main .block-container {{ padding: 2rem 1.5rem 2rem; max-width: 1200px; }}

[data-testid="stSidebar"] {{
    background: {t_sidebar} !important;
    border-right: 1px solid {t_border} !important;
}}
[data-testid="stSidebar"] .stMarkdown h2,
[data-testid="stSidebar"] .stMarkdown h3,
[data-testid="stSidebar"] p {{
    color: {t_fg} !important; font-family: 'Inter', sans-serif !important;
}}
hr {{ border-color: {t_border} !important; }}

[data-testid="stMetric"] {{
    background: {t_card} !important;
    border: 1px solid {t_border} !important;
    border-radius: 12px !important; padding: 1rem !important;
    border-left: 3px solid #667eea !important;
    transition: all 0.3s ease;
}}
[data-testid="stMetric"]:hover {{
    border-left-color: #a78bfa !important;
    box-shadow: 0 0 15px rgba(102,126,234,0.12);
    transform: translateY(-2px);
}}
[data-testid="stMetric"] label {{ color: {t_muted} !important; font-weight: 500 !important; font-size: 0.8rem !important; text-transform: uppercase; }}
[data-testid="stMetric"] [data-testid="stMetricValue"] {{ font-size: 1.4rem !important; font-weight: 700 !important; color: {t_fg} !important; }}

.stButton > button {{
    background: linear-gradient(135deg, #667eea, #764ba2) !important;
    color: white !important; border: none !important;
    border-radius: 8px !important; font-weight: 600 !important;
    padding: 0.5rem 1.2rem !important; transition: all 0.3s ease !important;
    box-shadow: 0 4px 12px rgba(102,126,234,0.25);
}}
.stButton > button:hover {{ box-shadow: 0 6px 20px rgba(102,126,234,0.4) !important; transform: translateY(-2px) !important; }}

.stTabs [data-baseweb="tab-list"] {{ background: {t_card} !important; border: 1px solid {t_border} !important; border-radius: 10px !important; padding: 3px !important; }}
.stTabs [data-baseweb="tab"] {{ color: {t_muted} !important; font-weight: 500 !important; border-radius: 8px !important; }}
.stTabs [aria-selected="true"] {{ background: linear-gradient(135deg, #667eea, #764ba2) !important; color: white !important; }}

[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stSelectbox"] > div > div,
[data-testid="stMultiSelect"] > div > div {{
    background-color: {t_input} !important; border-color: {t_border} !important;
    color: {t_fg} !important; border-radius: 8px !important;
}}

[data-testid="stExpander"] {{ background: {t_card} !important; border: 1px solid {t_border} !important; border-radius: 12px !important; }}
[data-testid="stExpander"] summary {{ font-weight: 600 !important; color: {t_fg} !important; }}

[data-testid="stPlotlyChart"] {{ border-radius: 12px; overflow: hidden; border: 1px solid {t_border}; background: {t_card} !important; }}
[data-testid="stSlider"] [role="slider"] {{ background-color: #667eea !important; }}

.hero-title {{
    background: linear-gradient(135deg, #667eea 0%, #764ba2 30%, #f093fb 60%, #667eea 100%);
    background-size: 200% 200%;
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
    font-size: 2.6rem; font-weight: 800; line-height: 1.2; margin-bottom: 0.2rem;
}}
.hero-sub {{ color: {t_muted}; font-size: 1.05rem; font-weight: 400; }}

.welcome {{
    background: linear-gradient(135deg, rgba(102,126,234,0.1), rgba(118,75,162,0.06));
    border: 1px solid rgba(102,126,234,0.15);
    border-radius: 16px; padding: 1.8rem; margin: 1.5rem 0;
}}
.welcome h3 {{ color: {t_fg} !important; font-weight: 700; margin-bottom: 0.4rem; font-size: 1.2rem; }}
.welcome p {{ color: {t_muted}; line-height: 1.7; margin: 0; font-size: 0.92rem; }}

.brand {{ text-align: center; padding: 0.8rem 0; margin-bottom: 0.5rem; border-bottom: 1px solid {t_border}; }}
.brand .b-icon {{ font-size: 2rem; display: block; margin-bottom: 0.2rem; }}
.brand .b-name {{
    font-size: 1.15rem; font-weight: 800;
    background: linear-gradient(135deg, #667eea, #f093fb);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}}
.brand .b-ver {{ font-size: 0.68rem; color: {t_muted}; letter-spacing: 1px; margin-top: 0.1rem; }}

.stat-card {{
    background: {t_card}; border: 1px solid {t_border};
    border-radius: 14px; padding: 1.1rem; text-align: center;
}}
.stat-card .s-val {{
    font-size: 1.6rem; font-weight: 800;
    background: linear-gradient(135deg, #667eea, #f093fb);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}}
.stat-card .s-lbl {{ font-size: 0.72rem; color: {t_muted}; text-transform: uppercase; margin-top: 0.2rem; font-weight: 600; }}

.footer {{ text-align: center; padding: 1.5rem 0 0.5rem; color: {t_muted}; font-size: 0.72rem; border-top: 1px solid {t_border}; margin-top: 2rem; }}
</style>
""", unsafe_allow_html=True)

# ─── Sidebar Settings ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="brand">
        <span class="b-icon">📊</span>
        <div class="b-name">Portfolio Optimizer</div>
        <div class="b-ver">v2.0 — PRO</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"### {_('settings')}")
    
    # Theme
    theme_options = ["dark", "light"]
    current_theme = st.session_state.get("theme", "dark")
    new_theme = st.selectbox(_("theme"), theme_options, index=theme_options.index(current_theme), format_func=lambda x: _(f"{x}_mode"))
    if new_theme != current_theme:
        st.session_state["theme"] = new_theme
        st.rerun()

    # Language
    lang_names = list(SUPPORTED_LANGUAGES.keys())
    current_lang_code = st.session_state.get("language", "en")
    current_lang = [k for k, v in SUPPORTED_LANGUAGES.items() if v == current_lang_code][0]
    new_lang = st.selectbox(_("language"), lang_names, index=lang_names.index(current_lang))
    if SUPPORTED_LANGUAGES[new_lang] != current_lang_code:
        st.session_state["language"] = SUPPORTED_LANGUAGES[new_lang]
        st.rerun()

    # Currency
    curr_names = list(SUPPORTED_CURRENCIES.keys())
    current_curr_code = st.session_state.get("currency", "USD")
    current_curr = [k for k, v in SUPPORTED_CURRENCIES.items() if v == current_curr_code][0]
    new_curr = st.selectbox(_("currency"), curr_names, index=curr_names.index(current_curr))
    if SUPPORTED_CURRENCIES[new_curr] != current_curr_code:
        st.session_state["currency"] = SUPPORTED_CURRENCIES[new_curr]
        
        # Trigger FX fetch
        from data.fetcher import StockDataFetcher
        fx = StockDataFetcher().get_exchange_rate("USD", SUPPORTED_CURRENCIES[new_curr])
        st.session_state["fx_rate"] = fx
        st.rerun()

    st.markdown("---")
    st.markdown(f"### {_('home')}")

    nav = [
        ("📈", _("stock_analysis"),     "pages/1_📈_Stock_Analysis.py"),
        ("🎯", _("portfolio_builder"),   "pages/2_🎯_Portfolio_Builder.py"),
        ("📊", _("efficient_frontier"),  "pages/3_📊_Efficient_Frontier.py"),
        ("🎲", _("monte_carlo"),         "pages/4_🎲_Monte_Carlo.py"),
        ("⚖️", _("risk_analysis"),       "pages/5_⚖️_Risk_Analysis.py"),
    ]
    for icon, name, path in nav:
        st.page_link(path, label=f"{icon} {name}", use_container_width=True)

    st.markdown("---")
    from datetime import datetime
    now = datetime.now()
    is_open = (now.weekday() < 5) and (9 <= now.hour < 16)
    dot, label = ("🟢", "Market Open") if is_open else ("🔴", "Market Closed")
    st.caption(f"{dot} {label}")
    st.caption("Built with Streamlit · Real-Time FX & Market Data via Yahoo Finance")

# ─── Main Content ─────────────────────────────────────────────────────────────
st.markdown(f"""
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
    ("📈", _("stock_analysis"), "Research individual stocks with candlestick charts, technical indicators, and key financial statistics.", "pages/1_📈_Stock_Analysis.py"),
    ("🎯", _("portfolio_builder"), "Select stocks and optimize using Max Sharpe, Min Volatility, or Equal Weight strategies.", "pages/2_🎯_Portfolio_Builder.py"),
    ("📊", _("efficient_frontier"), "Visualize the risk-return frontier and find the optimal portfolio allocation.", "pages/3_📊_Efficient_Frontier.py"),
    ("🎲", _("monte_carlo"), "Simulate thousands of random portfolios to explore the distribution of outcomes.", "pages/4_🎲_Monte_Carlo.py"),
    ("⚖️", _("risk_analysis"), "Measure portfolio risk with Sharpe, Sortino, VaR, CVaR, drawdown, and 10+ metrics.", "pages/5_⚖️_Risk_Analysis.py"),
]

col1, col2 = st.columns(2)
for i, (icon, title, desc, path) in enumerate(features):
    c = col1 if i % 2 == 0 else col2
    with c:
        st.markdown(f"""
        <div style="background: {t_card}; border: 1px solid {t_border}; border-radius: 14px; padding: 1.3rem; margin-bottom: 0.5rem; height: 140px;">
            <div style="font-size: 1.5rem; margin-bottom: 0.3rem;">{icon}</div>
            <div style="font-size: 1.1rem; font-weight: 700; color: {t_fg};">{title}</div>
            <div style="font-size: 0.85rem; color: {t_muted}; line-height: 1.4;">{desc}</div>
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
