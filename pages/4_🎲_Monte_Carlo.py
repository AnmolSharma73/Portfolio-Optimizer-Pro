"""
🎲 Monte Carlo Simulation Page
Run Monte Carlo simulations to explore portfolio possibilities and simulate future price paths.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.fetcher import StockDataFetcher
from data.processor import DataProcessor
from optimization.monte_carlo import MonteCarloSimulator
from visualization.charts import plot_monte_carlo_results, plot_portfolio_allocation, plot_future_simulation
from visualization.styles import get_chart_layout, apply_dynamic_theme, COLORS
from config.settings import DEFAULT_TICKERS, TRADING_DAYS, RISK_FREE_RATE, COLOR_PALETTE
from utils.helpers import format_percentage, format_currency
from utils.translations import _
from utils.ui import setup_page

# ── Page Config ──────────────────────────────────────────────────────────────
setup_page(page_title="Monte Carlo Simulation", page_icon="🎲", layout="wide")
init_session_state()

st.markdown("""
<style>
    .mc-result-card {
        background: linear-gradient(135deg, rgba(108,99,255,0.18), rgba(0,210,255,0.08));
        border: 1px solid rgba(108,99,255,0.25);
        border-radius: 14px;
        padding: 1.2rem;
        text-align: center;
        margin-bottom: 1rem;
    }
    .mc-label {
        font-size: 0.8rem;
        color: #8892A0;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .mc-value {
        font-size: 1.6rem;
        font-weight: 700;
        color: #6C63FF;
        margin-top: 0.3rem;
    }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ──────────────────────────────────────────────────────────────────
st.sidebar.markdown(f"## {_('monte_carlo')}")
st.sidebar.markdown("---")

# Use portfolio from session state or let user pick
if st.session_state.get('portfolio_tickers'):
    default_tickers = st.session_state['portfolio_tickers']
else:
    default_tickers = DEFAULT_TICKERS[:5]

selected_tickers = st.sidebar.multiselect(
    "📊 Select Stocks", options=DEFAULT_TICKERS + ['BRK-B', 'UNH', 'HD', 'PG', 'NFLX', 'AMD', 'ADBE'],
    default=default_tickers[:5]
)

period = st.sidebar.selectbox("📅 Historical Period", ["1y", "2y", "3y", "5y"], index=3)

st.sidebar.markdown("---")
st.sidebar.markdown("### ⚙️ Simulation Settings")

num_simulations = st.sidebar.slider(
    "🔢 Number of Simulations",
    min_value=1000, max_value=50000, value=10000, step=1000,
    help="More simulations = more accurate results but slower"
)

st.sidebar.markdown("---")
run_simulation = st.sidebar.button("🚀 RUN SIMULATION", use_container_width=True, type="primary")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔮 Future Simulation")
future_days = st.sidebar.slider("Days to Simulate", 30, 504, 252, 21)
num_paths = st.sidebar.slider("Number of Paths", 100, 2000, 500, 100)
run_future = st.sidebar.button("🔮 SIMULATE FUTURE", use_container_width=True)

# ── Main Content ─────────────────────────────────────────────────────────────
fx = st.session_state.get("fx_rate", 1.0)
curr = st.session_state.get("currency", "USD")
curr_sym = curr

st.markdown(f"# {_('monte_carlo')}")
st.markdown("*Explore thousands of random portfolio allocations to find optimal strategies*")
st.markdown("---")

if len(selected_tickers) < 2:
    st.warning("⚠️ Select at least **2 stocks** to run a simulation.")
    st.stop()

# Fetch data
fetcher = StockDataFetcher()
with st.spinner("Fetching market data..."):
    prices = fetcher.get_multiple_stocks(selected_tickers, period=period)

if prices.empty:
    st.error("❌ Failed to fetch data.")
    st.stop()

prices = DataProcessor.handle_missing_data(prices)
returns = DataProcessor.calculate_returns(prices)
expected_returns = DataProcessor.calculate_annualized_returns(returns)
cov_matrix = DataProcessor.calculate_covariance_matrix(returns, method='ledoit_wolf')

# ── Run Monte Carlo ──────────────────────────────────────────────────────────
if run_simulation:
    with st.spinner(f"🎲 Running {num_simulations:,} simulations..."):
        progress = st.progress(0, text="Initializing simulation...")

        simulator = MonteCarloSimulator(
            expected_returns, cov_matrix,
            risk_free_rate=RISK_FREE_RATE,
            num_simulations=num_simulations
        )

        progress.progress(30, text="Generating random portfolios...")
        mc_results = simulator.run_simulation()
        progress.progress(70, text="Finding optimal portfolios...")
        optimal = simulator.get_optimal_portfolios(mc_results)
        progress.progress(100, text="Complete!")
        progress.empty()

        st.session_state['mc_results'] = mc_results
        st.session_state['mc_optimal'] = optimal
        st.session_state['mc_simulator'] = simulator

        st.success(f"✅ {num_simulations:,} portfolio simulations completed!")

# ── Display Results ──────────────────────────────────────────────────────────
if st.session_state.get('mc_results'):
    mc_results = st.session_state['mc_results']
    optimal = st.session_state['mc_optimal']

    # Key findings
    st.markdown("## 🏆 Key Findings")
    col1, col2, col3, col4 = st.columns(4)

    max_s = optimal.get('max_sharpe', {})
    min_v = optimal.get('min_volatility', {})

    col1.markdown(f"""
    <div class="mc-result-card">
        <div class="mc-label">Best Sharpe Ratio</div>
        <div class="mc-value">{max_s.get('sharpe', 0):.3f}</div>
    </div>""", unsafe_allow_html=True)

    col2.markdown(f"""
    <div class="mc-result-card">
        <div class="mc-label">Best Return (Max Sharpe)</div>
        <div class="mc-value">{max_s.get('return', 0):.2%}</div>
    </div>""", unsafe_allow_html=True)

    col3.markdown(f"""
    <div class="mc-result-card">
        <div class="mc-label">Min Volatility</div>
        <div class="mc-value">{min_v.get('volatility', 0):.2%}</div>
    </div>""", unsafe_allow_html=True)

    col4.markdown(f"""
    <div class="mc-result-card">
        <div class="mc-label">Simulations</div>
        <div class="mc-value">{len(mc_results.get('returns', [])):,}</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # Monte Carlo Scatter Plot
    st.markdown("### 📊 Simulation Results")
    fig_mc = plot_monte_carlo_results(mc_results, optimal)
    st.plotly_chart(apply_dynamic_theme(fig_mc), use_container_width=True)

    # Optimal portfolios side by side
    st.markdown("### 🏅 Optimal Portfolios Comparison")
    opt_col1, opt_col2 = st.columns(2)

    with opt_col1:
        st.markdown("#### ⭐ Maximum Sharpe Ratio")
        if max_s.get('weights'):
            fig_ms = plot_portfolio_allocation(
                max_s['weights'],
                title=f"Max Sharpe ({max_s.get('sharpe', 0):.3f})"
            )
            st.plotly_chart(apply_dynamic_theme(fig_ms), use_container_width=True)

            ms_data = [{
                'Metric': m,
                'Value': v
            } for m, v in [
                ('Expected Return', f"{max_s.get('return', 0):.2%}"),
                ('Volatility', f"{max_s.get('volatility', 0):.2%}"),
                ('Sharpe Ratio', f"{max_s.get('sharpe', 0):.3f}")
            ]]
            st.dataframe(pd.DataFrame(ms_data).set_index('Metric'), use_container_width=True)

    with opt_col2:
        st.markdown("#### 🛡️ Minimum Volatility")
        if min_v.get('weights'):
            fig_mv = plot_portfolio_allocation(
                min_v['weights'],
                title=f"Min Vol ({min_v.get('volatility', 0):.2%})"
            )
            st.plotly_chart(apply_dynamic_theme(fig_mv), use_container_width=True)

            mv_data = [{
                'Metric': m,
                'Value': v
            } for m, v in [
                ('Expected Return', f"{min_v.get('return', 0):.2%}"),
                ('Volatility', f"{min_v.get('volatility', 0):.2%}"),
                ('Sharpe Ratio', f"{min_v.get('sharpe', 0):.3f}")
            ]]
            st.dataframe(pd.DataFrame(mv_data).set_index('Metric'), use_container_width=True)

    # Distribution charts
    st.markdown("### 📈 Distribution Analysis")
    dist_col1, dist_col2 = st.columns(2)

    with dist_col1:
        fig_ret_dist = go.Figure()
        fig_ret_dist.add_trace(go.Histogram(
            x=mc_results['returns'], nbinsx=80,
            marker_color=COLOR_PALETTE['primary'], opacity=0.7,
            name='Returns'
        ))
        fig_ret_dist.update_layout(**get_chart_layout(title="Return Distribution", height=400))
        fig_ret_dist.update_xaxes(title_text="Expected Return", tickformat=".1%")
        fig_ret_dist.update_yaxes(title_text="Frequency")
        st.plotly_chart(apply_dynamic_theme(fig_ret_dist), use_container_width=True)

    with dist_col2:
        fig_sr_dist = go.Figure()
        fig_sr_dist.add_trace(go.Histogram(
            x=mc_results['sharpe_ratios'], nbinsx=80,
            marker_color=COLOR_PALETTE['secondary'], opacity=0.7,
            name='Sharpe Ratios'
        ))
        fig_sr_dist.update_layout(**get_chart_layout(title="Sharpe Ratio Distribution", height=400))
        fig_sr_dist.update_xaxes(title_text="Sharpe Ratio")
        fig_sr_dist.update_yaxes(title_text="Frequency")
        st.plotly_chart(apply_dynamic_theme(fig_sr_dist), use_container_width=True)

# ── Future Simulation ────────────────────────────────────────────────────────
if run_future and st.session_state.get('mc_simulator'):
    simulator = st.session_state['mc_simulator']
    optimal = st.session_state.get('mc_optimal', {})
    max_s = optimal.get('max_sharpe', {})

    if max_s.get('weights'):
        with st.spinner(f"🔮 Simulating {num_paths} future price paths over {future_days} days..."):
            # Get current prices and weights
            current_prices_list = [prices[t].iloc[-1] for t in selected_tickers]
            weights_arr = np.array([max_s['weights'].get(t, 0) for t in selected_tickers])

            simulation_paths = simulator.simulate_future_prices(
                current_prices=np.array(current_prices_list),
                weights=weights_arr,
                days=future_days,
                num_paths=num_paths
            )

            st.markdown("---")
            st.markdown("## 🔮 Future Price Simulation")
            st.markdown(f"*{num_paths} simulated paths over {future_days} trading days using Max Sharpe weights*")

            if simulation_paths is not None and len(simulation_paths) > 0:
                fig_future = plot_future_simulation(simulation_paths, title="Simulated Portfolio Value")
                st.plotly_chart(apply_dynamic_theme(fig_future), use_container_width=True)

                # Summary statistics
                final_values = simulation_paths[:, -1]
                initial_value = simulation_paths[0, 0] if simulation_paths.shape[1] > 0 else 100

                fs1, fs2, fs3, fs4 = st.columns(4)
                fs1.metric("Median Final Value",
                          format_currency(np.median(final_values) * fx, curr_sym),
                          f"{(np.median(final_values)/initial_value - 1):.1%}")
                fs2.metric("5th Percentile (Worst)",
                          format_currency(np.percentile(final_values, 5) * fx, curr_sym),
                          f"{(np.percentile(final_values, 5)/initial_value - 1):.1%}",
                          delta_color="inverse")
                fs3.metric("95th Percentile (Best)",
                          format_currency(np.percentile(final_values, 95) * fx, curr_sym),
                          f"{(np.percentile(final_values, 95)/initial_value - 1):.1%}")
                fs4.metric("Prob. of Profit",
                          f"{(final_values > initial_value).mean():.1%}")
    else:
        st.warning("Run Monte Carlo simulation first to get optimal weights for future simulation.")
