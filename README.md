# 📊 Portfolio Optimizer Pro

A Python-based portfolio optimization and analysis dashboard built with **Streamlit**, powered by **Modern Portfolio Theory (MPT)**.

🌐 **Live Demo:** [https://anmolsharma73-portfolio-optimizer-pro-app-k94z4r.streamlit.app](https://anmolsharma73-portfolio-optimizer-pro-app-k94z4r.streamlit.app)

## 🎯 Features

| Page | Description |
|------|-------------|
| 📈 **Stock Analysis** | Research stocks with candlestick charts, technical indicators (SMA, EMA, Bollinger Bands), and key financial statistics |
| 🎯 **Portfolio Builder** | Optimize portfolio weights using Max Sharpe, Min Volatility, or Equal Weight strategies |
| 📊 **Efficient Frontier** | Visualize the risk-return efficient frontier and identify optimal portfolios |
| 🎲 **Monte Carlo Simulation** | Run 10,000+ random portfolio simulations and simulate future price paths |
| ⚖️ **Risk Analysis** | Comprehensive risk metrics — Sharpe, Sortino, VaR, CVaR, Max Drawdown, Beta, Alpha, and more |

## 🛠 Tech Stack

- **Python 3.10+**
- **Streamlit** — Interactive web dashboard
- **yfinance** — Real-time stock data from Yahoo Finance
- **PyPortfolioOpt** — Portfolio optimization (Markowitz)
- **Plotly** — Interactive charts and visualizations
- **NumPy / Pandas / SciPy** — Data processing and calculations

## 📁 Project Structure

```
Portfolio Optimizer/
├── app.py                          # Main landing page
├── requirements.txt                # Dependencies
├── .streamlit/config.toml          # Theme configuration
├── config/
│   └── settings.py                 # App constants and color palette
├── data/
│   ├── fetcher.py                  # Yahoo Finance data fetcher (cached)
│   └── processor.py                # Returns, covariance, data cleaning
├── optimization/
│   ├── markowitz.py                # Mean-Variance Optimization
│   ├── efficient_frontier.py       # Efficient Frontier Calculator
│   ├── monte_carlo.py              # Monte Carlo Simulator
│   ├── risk_parity.py              # Risk Parity Optimizer
│   └── black_litterman.py          # Black-Litterman Model
├── risk/
│   └── metrics.py                  # 15+ risk metrics (Sharpe, VaR, etc.)
├── backtest/
│   └── engine.py                   # Backtesting engine
├── visualization/
│   ├── charts.py                   # Plotly chart functions
│   └── styles.py                   # Dark theme styling
├── utils/
│   └── helpers.py                  # Formatting and session state
└── pages/
    ├── 1_📈_Stock_Analysis.py
    ├── 2_🎯_Portfolio_Builder.py
    ├── 3_📊_Efficient_Frontier.py
    ├── 4_🎲_Monte_Carlo.py
    └── 5_⚖️_Risk_Analysis.py
```

## 🚀 Setup & Run

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

The app will open at **http://localhost:8501**.

## 📖 How to Use

1. **Stock Analysis** — Enter a ticker symbol (e.g., AAPL) to view price history, technicals, and key stats
2. **Portfolio Builder** — Select 2+ stocks → Choose a strategy → Click "Optimize"
3. **Efficient Frontier** — View the risk-return curve with your portfolio highlighted
4. **Monte Carlo** — Run simulations to see the distribution of possible outcomes
5. **Risk Analysis** — Analyze VaR, drawdown, rolling Sharpe, and benchmark comparison

## 📊 Key Concepts

- **Markowitz Mean-Variance Optimization** — Finds the portfolio weights that maximize return for a given risk level
- **Sharpe Ratio** — Risk-adjusted return metric (higher = better)
- **Value at Risk (VaR)** — Maximum expected loss at a given confidence level
- **Efficient Frontier** — The set of optimal portfolios offering the highest return for each risk level
- **Monte Carlo Simulation** — Random sampling to model uncertainty in portfolio outcomes
