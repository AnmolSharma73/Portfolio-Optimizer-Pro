"""
📈 Stock Analysis Page
Analyze individual stocks with price charts, key statistics,
technical indicators, and multi-stock comparison.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.fetcher import StockDataFetcher
from data.processor import DataProcessor
from risk.metrics import RiskMetrics
from visualization.charts import plot_stock_price, plot_correlation_heatmap, plot_risk_return_scatter
from visualization.styles import get_chart_layout, apply_dynamic_theme, COLORS
from config.settings import CATEGORIZED_TICKERS, DEFAULT_PERIOD, TRADING_DAYS, RISK_FREE_RATE, COLOR_PALETTE
from utils.helpers import format_currency, format_percentage, format_large_number
from utils.translations import _
from utils.ui import setup_page

# ── Page Config ──────────────────────────────────────────────────────────────
setup_page(page_title="Stock Analysis", page_icon="📈", layout="wide")

# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .stock-header {
        background: linear-gradient(135deg, rgba(108,99,255,0.15), rgba(0,210,255,0.10));
        border: 1px solid rgba(108,99,255,0.2);
        border-radius: 16px;
        padding: 1.5rem 2rem;
        margin-bottom: 1.5rem;
        backdrop-filter: blur(10px);
    }
    .stock-name {
        font-size: 1.8rem;
        font-weight: 700;
        color: #E0E0E0;
        margin-bottom: 0.2rem;
    }
    .stock-sector {
        font-size: 0.95rem;
        color: #8892A0;
    }
    .price-big {
        font-size: 2.5rem;
        font-weight: 800;
        color: #6C63FF;
    }
    .stat-card {
        background: rgba(26,31,46,0.8);
        border: 1px solid rgba(108,99,255,0.15);
        border-radius: 12px;
        padding: 1rem 1.2rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    .stat-card:hover {
        border-color: rgba(108,99,255,0.4);
        transform: translateY(-2px);
    }
    .stat-label {
        font-size: 0.8rem;
        color: #8892A0;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .stat-value {
        font-size: 1.3rem;
        font-weight: 700;
        color: #E0E0E0;
        margin-top: 0.3rem;
    }
</style>
""", unsafe_allow_html=True)

# ── Sidebar Controls ─────────────────────────────────────────────────────────
st.sidebar.markdown(f"## {_('stock_analysis')}")
st.sidebar.markdown("---")

category_options = list(CATEGORIZED_TICKERS.keys())
selected_category = st.sidebar.selectbox("📂 Select Sector", category_options, index=0)

category_stocks = CATEGORIZED_TICKERS[selected_category]
ticker = st.sidebar.selectbox(
    f"🔍 {_('select_ticker')}",
    options=list(category_stocks.keys()),
    format_func=lambda x: f"{x} - {category_stocks[x]}"
).upper().strip()

period_options = {"1 Month": "1mo", "3 Months": "3mo", "6 Months": "6mo",
                  "1 Year": "1y", "2 Years": "2y", "5 Years": "5y", "Max": "max"}
selected_period = st.sidebar.selectbox("📅 Time Period", list(period_options.keys()), index=4)
period = period_options[selected_period]

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Compare Stocks")

all_flattened_tickers = {k: v for d in CATEGORIZED_TICKERS.values() for k, v in d.items()}
compare_tickers = st.sidebar.multiselect(
    "Add tickers to compare",
    options=[t for t in all_flattened_tickers.keys() if t != ticker],
    format_func=lambda x: f"{x} - {all_flattened_tickers[x]}",
    default=[]
)

st.sidebar.markdown("---")
show_sma = st.sidebar.checkbox("📏 Show SMA (20, 50)", value=False)
show_ema = st.sidebar.checkbox("📐 Show EMA (12, 26)", value=False)
show_bollinger = st.sidebar.checkbox("📉 Bollinger Bands", value=False)

# ── Main Content ─────────────────────────────────────────────────────────────
fetcher = StockDataFetcher()
fx = st.session_state.get("fx_rate", 1.0)
curr = st.session_state.get("currency", "USD")
curr_sym = curr

st.markdown(f"# {_('stock_analysis')}")
st.markdown("*Deep-dive into individual stock performance, technicals & comparisons*")
st.markdown("---")

if not ticker:
    st.warning("Please enter a ticker symbol in the sidebar.")
    st.stop()

# Fetch data
with st.spinner(f"Fetching data for {ticker}..."):
    stock_data = fetcher.get_stock_data(ticker, period=period)
    stock_info = fetcher.get_stock_info(ticker)

if stock_data.empty:
    st.error(f"❌ Could not fetch data for **{ticker}**. Please check the ticker symbol.")
    st.stop()

# ── Stock Header ─────────────────────────────────────────────────────────────
company_name = stock_info.get('longName', stock_info.get('shortName', ticker))
sector = stock_info.get('sector', 'N/A')
industry = stock_info.get('industry', 'N/A')
current_price = stock_info.get('currentPrice') or stock_info.get('regularMarketPrice') or stock_data['Close'].iloc[-1]
prev_close = stock_info.get('previousClose') or stock_info.get('regularMarketPreviousClose') or (stock_data['Close'].iloc[-2] if len(stock_data) > 1 else current_price)

price_change = (current_price or 0) - (prev_close or 0)
price_change_pct = (price_change / prev_close * 100) if prev_close else 0
change_color = COLOR_PALETTE['success'] if price_change >= 0 else COLOR_PALETTE['danger']
change_arrow = "▲" if price_change >= 0 else "▼"

st.markdown(f"""
<div class="stock-header">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
        <div>
            <div class="stock-name">{company_name} ({ticker})</div>
            <div class="stock-sector">{sector} • {industry}</div>
        </div>
        <div style="text-align: right;">
            <div class="price-big">{format_currency(current_price * fx, curr_sym)}</div>
            <div style="font-size: 1.1rem; color: {change_color}; font-weight: 600;">
                {change_arrow} {format_currency(abs(price_change) * fx, curr_sym)} ({price_change_pct:+.2f}%)
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Key Statistics ───────────────────────────────────────────────────────────
col1, col2, col3, col4, col5, col6 = st.columns(6)

stats = {
    _("market_cap"): curr_sym + format_large_number((stock_info.get('marketCap') or 0) * fx),
    "52W High": format_currency(((stock_info.get('fiftyTwoWeekHigh') or 0) * fx), curr_sym),
    "52W Low": format_currency(((stock_info.get('fiftyTwoWeekLow') or 0) * fx), curr_sym),
    "Avg Volume": format_large_number(stock_info.get('averageVolume') or 0),
    "P/E Ratio": f"{stock_info.get('trailingPE', 'N/A'):.2f}" if isinstance(stock_info.get('trailingPE'), (int, float)) else "N/A",
    "Div Yield": format_percentage(stock_info.get('dividendYield') or 0) if stock_info.get('dividendYield') else "N/A"
}

for col, (label, value) in zip([col1, col2, col3, col4, col5, col6], stats.items()):
    col.markdown(f"""
    <div class="stat-card">
        <div class="stat-label">{label}</div>
        <div class="stat-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Tabs ─────────────────────────────────────────────────────────────────────
tab_price, tab_returns, tab_compare = st.tabs(["📊 Price Chart", "📈 Returns Analysis", "🔄 Comparison"])

# ── Tab 1: Price Chart ───────────────────────────────────────────────────────
with tab_price:
    # Build price chart with optional indicators
    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True,
        vertical_spacing=0.03, row_heights=[0.75, 0.25],
        subplot_titles=("", "Volume")
    )

    # Candlestick
    fig.add_trace(go.Candlestick(
        x=stock_data.index,
        open=stock_data['Open'], high=stock_data['High'],
        low=stock_data['Low'], close=stock_data['Close'],
        name=ticker,
        increasing_line_color=COLOR_PALETTE['success'],
        decreasing_line_color=COLOR_PALETTE['danger']
    ), row=1, col=1)

    # SMA
    if show_sma:
        for window, color in [(20, '#FFD700'), (50, '#00D2FF')]:
            sma = stock_data['Close'].rolling(window=window).mean()
            fig.add_trace(go.Scatter(
                x=stock_data.index, y=sma,
                name=f'SMA {window}', line=dict(color=color, width=1.5)
            ), row=1, col=1)

    # EMA
    if show_ema:
        for window, color in [(12, '#FF6B6B'), (26, '#4ECDC4')]:
            ema = stock_data['Close'].ewm(span=window, adjust=False).mean()
            fig.add_trace(go.Scatter(
                x=stock_data.index, y=ema,
                name=f'EMA {window}', line=dict(color=color, width=1.5, dash='dash')
            ), row=1, col=1)

    # Bollinger Bands
    if show_bollinger:
        sma20 = stock_data['Close'].rolling(window=20).mean()
        std20 = stock_data['Close'].rolling(window=20).std()
        upper = sma20 + 2 * std20
        lower = sma20 - 2 * std20
        fig.add_trace(go.Scatter(
            x=stock_data.index, y=upper, name='BB Upper',
            line=dict(color='rgba(108,99,255,0.3)', width=1)
        ), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=stock_data.index, y=lower, name='BB Lower',
            line=dict(color='rgba(108,99,255,0.3)', width=1),
            fill='tonexty', fillcolor='rgba(108,99,255,0.05)'
        ), row=1, col=1)

    # Volume bars
    colors = [COLOR_PALETTE['success'] if c >= o else COLOR_PALETTE['danger']
              for c, o in zip(stock_data['Close'], stock_data['Open'])]
    fig.add_trace(go.Bar(
        x=stock_data.index, y=stock_data['Volume'],
        name='Volume', marker_color=colors, opacity=0.5
    ), row=2, col=1)

    layout = get_chart_layout(title=f"{ticker} Price Chart", height=650)
    layout['xaxis_rangeslider_visible'] = False
    fig.update_layout(**layout)
    fig.update_yaxes(title_text=f"Price ({curr})", row=1, col=1)
    fig.update_yaxes(title_text="Volume", row=2, col=1)

    st.plotly_chart(apply_dynamic_theme(fig), use_container_width=True)

# ── Tab 2: Returns Analysis ─────────────────────────────────────────────────
with tab_returns:
    returns = DataProcessor.calculate_returns(stock_data[['Close']])

    r1, r2, r3, r4 = st.columns(4)
    ann_return = RiskMetrics.annualized_return(returns['Close'])
    ann_vol = RiskMetrics.annualized_volatility(returns['Close'])
    sharpe = RiskMetrics.sharpe_ratio(returns['Close'])
    max_dd = RiskMetrics.max_drawdown(returns['Close'])

    r1.metric("Annualized Return", format_percentage(ann_return),
              delta=f"{'Good' if ann_return > 0 else 'Negative'}")
    r2.metric("Annualized Volatility", format_percentage(ann_vol))
    r3.metric("Sharpe Ratio", f"{sharpe:.3f}",
              delta=f"{'Good' if sharpe > 1 else 'Below 1'}")
    r4.metric("Max Drawdown", format_percentage(max_dd),
              delta="Risk", delta_color="inverse")

    st.markdown("---")

    col_ret1, col_ret2 = st.columns(2)

    with col_ret1:
        # Returns distribution
        fig_dist = go.Figure()
        fig_dist.add_trace(go.Histogram(
            x=returns['Close'].values,
            nbinsx=80,
            marker_color=COLOR_PALETTE['primary'],
            opacity=0.7,
            name='Daily Returns'
        ))

        # VaR line
        var_95 = RiskMetrics.value_at_risk(returns['Close'], confidence=0.95)
        fig_dist.add_vline(
            x=var_95, line_dash="dash", line_color=COLOR_PALETTE['danger'],
            annotation_text=f"VaR 95%: {var_95:.4f}"
        )

        fig_dist.update_layout(**get_chart_layout(title="Returns Distribution", height=400))
        fig_dist.update_xaxes(title_text="Daily Return")
        fig_dist.update_yaxes(title_text="Frequency")
        st.plotly_chart(apply_dynamic_theme(fig_dist), use_container_width=True)

    with col_ret2:
        # Cumulative returns
        cum_returns = (1 + returns['Close']).cumprod()
        fig_cum = go.Figure()
        fig_cum.add_trace(go.Scatter(
            x=cum_returns.index, y=cum_returns.values,
            fill='tozeroy',
            fillcolor='rgba(108,99,255,0.1)',
            line=dict(color=COLOR_PALETTE['primary'], width=2),
            name='Cumulative Return'
        ))
        fig_cum.update_layout(**get_chart_layout(title="Cumulative Returns", height=400))
        st.plotly_chart(apply_dynamic_theme(fig_cum), use_container_width=True)

    # Drawdown chart
    dd_series = RiskMetrics.drawdown_series(returns['Close'])
    fig_dd = go.Figure()
    fig_dd.add_trace(go.Scatter(
        x=dd_series.index, y=dd_series.values,
        fill='tozeroy',
        fillcolor='rgba(255,69,96,0.15)',
        line=dict(color=COLOR_PALETTE['danger'], width=1.5),
        name='Drawdown'
    ))
    fig_dd.update_layout(**get_chart_layout(title="Drawdown Analysis", height=350))
    fig_dd.update_yaxes(title_text="Drawdown", tickformat='.1%')
    st.plotly_chart(apply_dynamic_theme(fig_dd), use_container_width=True)

# ── Tab 3: Comparison ────────────────────────────────────────────────────────
with tab_compare:
    if not compare_tickers:
        st.info("👈 Add tickers in the sidebar to compare stocks.")
    else:
        all_tickers = [ticker] + compare_tickers
        with st.spinner("Fetching comparison data..."):
            multi_data = fetcher.get_multiple_stocks(all_tickers, period=period)

        if multi_data.empty:
            st.error("Could not fetch data for the selected tickers.")
        else:
            multi_data = DataProcessor.handle_missing_data(multi_data)
            multi_returns = DataProcessor.calculate_returns(multi_data)

            # Normalized price comparison
            normalized = multi_data / multi_data.iloc[0] * 100
            fig_comp = go.Figure()
            gradient_colors = ['#6C63FF', '#00D2FF', '#FFD700', '#00E396', '#FF4560',
                               '#FEB019', '#775DD0', '#2B908F', '#F9A3A4', '#90EE7E']
            for i, t in enumerate(normalized.columns):
                fig_comp.add_trace(go.Scatter(
                    x=normalized.index, y=normalized[t],
                    name=t, line=dict(color=gradient_colors[i % len(gradient_colors)], width=2)
                ))
            fig_comp.update_layout(**get_chart_layout(title="Normalized Price Comparison (Base=100)", height=500))
            st.plotly_chart(apply_dynamic_theme(fig_comp), use_container_width=True)

            c1, c2 = st.columns(2)

            with c1:
                # Risk-Return scatter
                ann_rets = DataProcessor.calculate_annualized_returns(multi_returns)
                ann_vols = multi_returns.std() * np.sqrt(TRADING_DAYS)
                fig_rr = plot_risk_return_scatter(
                    list(ann_rets.index), ann_rets.values, ann_vols.values
                )
                st.plotly_chart(apply_dynamic_theme(fig_rr), use_container_width=True)

            with c2:
                # Correlation heatmap
                corr = multi_returns.corr()
                fig_corr = plot_correlation_heatmap(corr)
                st.plotly_chart(apply_dynamic_theme(fig_corr), use_container_width=True)

            # Comparison table
            st.markdown("### 📋 Comparison Table")
            comp_data = []
            for t in all_tickers:
                if t in multi_returns.columns:
                    r = multi_returns[t]
                    comp_data.append({
                        'Ticker': t,
                        'Ann. Return': f"{RiskMetrics.annualized_return(r):.2%}",
                        'Ann. Volatility': f"{RiskMetrics.annualized_volatility(r):.2%}",
                        'Sharpe Ratio': f"{RiskMetrics.sharpe_ratio(r):.3f}",
                        'Max Drawdown': f"{RiskMetrics.max_drawdown(r):.2%}",
                        'Sortino Ratio': f"{RiskMetrics.sortino_ratio(r):.3f}"
                    })
            st.dataframe(pd.DataFrame(comp_data).set_index('Ticker'),
                         use_container_width=True)
