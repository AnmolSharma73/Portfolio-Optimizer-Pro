import streamlit as st
from config.settings import *
from utils.helpers import *

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title=APP_NAME, page_icon="📊", layout="wide", initial_sidebar_state="expanded")
init_session_state()

# ─── Premium Dark Theme CSS ──────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Base ─────────────────────────────────────────────────────────────── */
html, body, [data-testid="stAppViewContainer"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    color: #f1f5f9;
}
.main .block-container {
    padding: 2rem 1.5rem 2rem; max-width: 1200px;
}

/* ── Sidebar ──────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #111928, #0e1117, #111928) !important;
    border-right: 1px solid rgba(255,255,255,0.06) !important;
}
[data-testid="stSidebar"] .stMarkdown h2,
[data-testid="stSidebar"] .stMarkdown h3 {
    color: #f1f5f9 !important; font-family: 'Inter', sans-serif !important;
}
[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.06) !important; }

/* ── Metric Cards ─────────────────────────────────────────────────────── */
[data-testid="stMetric"] {
    background: rgba(17,25,40,0.75) !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 12px !important; padding: 1rem !important;
    border-left: 3px solid #667eea !important;
    transition: all 0.3s ease;
}
[data-testid="stMetric"]:hover {
    border-left-color: #a78bfa !important;
    box-shadow: 0 0 15px rgba(102,126,234,0.12);
    transform: translateY(-2px);
}
[data-testid="stMetric"] label {
    color: #94a3b8 !important; font-weight: 500 !important;
    font-size: 0.8rem !important; text-transform: uppercase; letter-spacing: 0.5px;
}
[data-testid="stMetric"] [data-testid="stMetricValue"] {
    font-size: 1.4rem !important; font-weight: 700 !important; color: #f1f5f9 !important;
}

/* ── Buttons ──────────────────────────────────────────────────────────── */
.stButton > button {
    background: linear-gradient(135deg, #667eea, #764ba2) !important;
    color: white !important; border: none !important;
    border-radius: 8px !important; font-weight: 600 !important;
    font-family: 'Inter', sans-serif !important;
    padding: 0.5rem 1.2rem !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 12px rgba(102,126,234,0.25);
}
.stButton > button:hover {
    box-shadow: 0 6px 20px rgba(102,126,234,0.4) !important;
    transform: translateY(-2px) !important;
}

/* ── Tabs ─────────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    gap: 0; background: rgba(17,25,40,0.75) !important;
    border-radius: 10px !important; padding: 3px !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
}
.stTabs [data-baseweb="tab"] {
    color: #94a3b8 !important; font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important; border-radius: 8px !important;
    padding: 0.4rem 0.8rem !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #667eea, #764ba2) !important;
    color: white !important;
}
.stTabs [data-baseweb="tab-highlight"],
.stTabs [data-baseweb="tab-border"] { display: none !important; }

/* ── Inputs ───────────────────────────────────────────────────────────── */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stSelectbox"] > div > div,
[data-testid="stMultiSelect"] > div > div {
    background-color: #1a1f2e !important;
    border-color: rgba(255,255,255,0.06) !important;
    color: #f1f5f9 !important; border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
}
[data-testid="stMultiSelect"] span[data-baseweb="tag"] {
    background: linear-gradient(135deg, #667eea, #764ba2) !important;
    border-radius: 6px !important; color: white !important;
}

/* ── Expanders ────────────────────────────────────────────────────────── */
[data-testid="stExpander"] {
    background: rgba(17,25,40,0.75) !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 12px !important;
}
[data-testid="stExpander"] summary { font-weight: 600 !important; color: #f1f5f9 !important; }

/* ── Plotly ────────────────────────────────────────────────────────────── */
[data-testid="stPlotlyChart"] {
    border-radius: 12px; overflow: hidden;
    border: 1px solid rgba(255,255,255,0.06);
}

/* ── Slider ───────────────────────────────────────────────────────────── */
[data-testid="stSlider"] [role="slider"] { background-color: #667eea !important; }

/* ── Scrollbar ────────────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0e1117; }
::-webkit-scrollbar-thumb { background: #1a1f2e; border-radius: 3px; }

hr { border-color: rgba(255,255,255,0.06) !important; }

/* ── Animations ───────────────────────────────────────────────────────── */
@keyframes gradientShift { 0%{background-position:0% 50%} 50%{background-position:100% 50%} 100%{background-position:0% 50%} }
@keyframes fadeIn { from{opacity:0;transform:translateY(15px)} to{opacity:1;transform:translateY(0)} }
.anim { animation: fadeIn 0.5s ease forwards; }

/* ═══════════════ HEADER ═══════════════ */
.hero-title {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 30%, #f093fb 60%, #667eea 100%);
    background-size: 200% 200%;
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
    animation: gradientShift 6s ease infinite;
    font-size: 2.6rem; font-weight: 800; line-height: 1.2; margin-bottom: 0.2rem;
}
.hero-sub { color: #94a3b8; font-size: 1.05rem; font-weight: 400; }

/* ═══════════════ WELCOME BANNER ═══════════════ */
.welcome {
    background: linear-gradient(135deg, rgba(102,126,234,0.1), rgba(118,75,162,0.06));
    border: 1px solid rgba(102,126,234,0.15);
    border-radius: 16px; padding: 1.8rem; margin: 1.5rem 0;
}
.welcome h3 { color: #f1f5f9 !important; font-weight: 700; margin-bottom: 0.4rem; font-size: 1.2rem; }
.welcome p { color: #94a3b8; line-height: 1.7; margin: 0; font-size: 0.92rem; }

/* ═══════════════ FEATURE CARDS ═══════════════ */
.tools-grid {
    display: grid; gap: 16px;
    grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
}
.tool-card {
    background: rgba(17,25,40,0.75);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px; padding: 1.3rem;
    position: relative; overflow: hidden;
    transition: all 0.3s ease;
}
.tool-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, #667eea, #f093fb);
    opacity: 0; transition: opacity 0.3s ease;
}
.tool-card:hover {
    border-color: rgba(255,255,255,0.12);
    box-shadow: 0 8px 25px rgba(0,0,0,0.3);
    transform: translateY(-4px);
}
.tool-card:hover::before { opacity: 1; }
.tool-card .t-icon { font-size: 2rem; margin-bottom: 0.5rem; display: block; }
.tool-card .t-title { font-size: 1rem; font-weight: 700; color: #f1f5f9; margin-bottom: 0.25rem; }
.tool-card .t-desc { font-size: 0.82rem; color: #94a3b8; line-height: 1.5; }

/* ═══════════════ SIDEBAR BRAND ═══════════════ */
.brand {
    text-align: center; padding: 0.8rem 0; margin-bottom: 0.5rem;
    border-bottom: 1px solid rgba(255,255,255,0.06);
}
.brand .b-icon { font-size: 2rem; display: block; margin-bottom: 0.2rem; }
.brand .b-name {
    font-size: 1.15rem; font-weight: 800;
    background: linear-gradient(135deg, #667eea, #f093fb);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}
.brand .b-ver { font-size: 0.68rem; color: #64748b; letter-spacing: 1px; margin-top: 0.1rem; }

/* ═══════════════ NAV ═══════════════ */
.nav-link {
    display: flex; align-items: center; gap: 0.5rem;
    padding: 0.5rem 0.7rem; border-radius: 8px; margin: 2px 0;
    color: #94a3b8; font-size: 0.88rem; font-weight: 500;
    transition: all 0.2s ease;
}
.nav-link:hover { background: rgba(102,126,234,0.08); color: #f1f5f9; }
.nav-link .n-icon { width: 1.3rem; text-align: center; }

/* ═══════════════ STAT CARDS ═══════════════ */
.stat-card {
    background: rgba(17,25,40,0.75); border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px; padding: 1.1rem; text-align: center;
    transition: all 0.3s ease;
}
.stat-card:hover { border-color: #667eea; box-shadow: 0 0 15px rgba(102,126,234,0.1); }
.stat-card .s-val {
    font-size: 1.6rem; font-weight: 800;
    background: linear-gradient(135deg, #667eea, #f093fb);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}
.stat-card .s-lbl { font-size: 0.72rem; color: #64748b; text-transform: uppercase; letter-spacing: 1px; margin-top: 0.2rem; font-weight: 600; }

/* ═══════════════ FOOTER ═══════════════ */
.footer {
    text-align: center; padding: 1.5rem 0 0.5rem; color: #64748b;
    font-size: 0.72rem; border-top: 1px solid rgba(255,255,255,0.06); margin-top: 2rem;
}
</style>
""", unsafe_allow_html=True)

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="brand">
        <span class="b-icon">📊</span>
        <div class="b-name">Portfolio Optimizer</div>
        <div class="b-ver">v1.0 — PRO</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🧭 Pages")

    nav = [
        ("📈", "Stock Analysis",     "Research & compare stocks"),
        ("🎯", "Portfolio Builder",   "Optimize your portfolio"),
        ("📊", "Efficient Frontier",  "Risk-return tradeoff"),
        ("🎲", "Monte Carlo",         "Simulate scenarios"),
        ("⚖️", "Risk Analysis",       "VaR, drawdown & metrics"),
    ]
    for icon, name, desc in nav:
        st.markdown(f"""
        <div class="nav-link">
            <span class="n-icon">{icon}</span>
            <div><strong>{name}</strong><br>
            <span style="font-size:0.72rem;color:#64748b">{desc}</span></div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    from datetime import datetime
    now = datetime.now()
    is_open = (now.weekday() < 5) and (9 <= now.hour < 16)
    dot, label = ("🟢", "Market Open") if is_open else ("🔴", "Market Closed")
    st.caption(f"{dot} {label}")
    st.caption("Built with Streamlit · Data via Yahoo Finance")

# ─── Main Content ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="anim">
    <div class="hero-title">📊 Portfolio Optimizer</div>
    <div class="hero-sub">Optimize, Analyze & Manage Your Stock Portfolio</div>
</div>
""", unsafe_allow_html=True)

st.markdown("")

# Welcome Banner
st.markdown("""
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

    st.markdown("### ⚡ Your Portfolio")
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f"""<div class="stat-card"><div class="s-val">{format_percentage(results.get('expected_return', 0))}</div><div class="s-lbl">Expected Return</div></div>""", unsafe_allow_html=True)
    c2.markdown(f"""<div class="stat-card"><div class="s-val">{format_percentage(results.get('volatility', 0))}</div><div class="s-lbl">Volatility</div></div>""", unsafe_allow_html=True)
    c3.markdown(f"""<div class="stat-card"><div class="s-val">{results.get('sharpe_ratio', 0):.2f}</div><div class="s-lbl">Sharpe Ratio</div></div>""", unsafe_allow_html=True)
    c4.markdown(f"""<div class="stat-card"><div class="s-val">{format_currency(inv)}</div><div class="s-lbl">Portfolio Value</div></div>""", unsafe_allow_html=True)
    st.markdown("")

# Feature Cards
st.markdown("### 🧩 Tools")

features = [
    ("📈", "Stock Analysis", "Research individual stocks with candlestick charts, technical indicators, and key financial statistics."),
    ("🎯", "Portfolio Builder", "Select stocks and optimize using Max Sharpe, Min Volatility, or Equal Weight strategies."),
    ("📊", "Efficient Frontier", "Visualize the risk-return frontier and find the optimal portfolio allocation."),
    ("🎲", "Monte Carlo Simulation", "Simulate thousands of random portfolios to explore the distribution of outcomes."),
    ("⚖️", "Risk Analysis", "Measure portfolio risk with Sharpe, Sortino, VaR, CVaR, drawdown, and 10+ metrics."),
]

cards = '<div class="tools-grid">'
for i, (icon, title, desc) in enumerate(features):
    cards += f"""
    <div class="tool-card anim" style="animation-delay:{i*0.08}s">
        <span class="t-icon">{icon}</span>
        <div class="t-title">{title}</div>
        <div class="t-desc">{desc}</div>
    </div>"""
cards += '</div>'
st.markdown(cards, unsafe_allow_html=True)

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
st.markdown("""
<div class="footer">
    Portfolio Optimizer Pro v1.0 &nbsp;•&nbsp; Powered by Modern Portfolio Theory &nbsp;•&nbsp; Data via Yahoo Finance
</div>
""", unsafe_allow_html=True)
