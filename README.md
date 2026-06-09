<div align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue.svg?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B.svg?style=for-the-badge&logo=Streamlit&logoColor=white" alt="Streamlit">
  <img src="https://img.shields.io/badge/Pandas-150458.svg?style=for-the-badge&logo=pandas&logoColor=white" alt="Pandas">
  <img src="https://img.shields.io/badge/Plotly-239120.svg?style=for-the-badge&logo=plotly&logoColor=white" alt="Plotly">
  
  <h1>📊 Portfolio Optimizer Pro</h1>
  <p><b>Advanced Portfolio Construction & Risk Analysis Engine powered by Modern Portfolio Theory (MPT)</b></p>
  
  <a href="https://anmolsharma73-portfolio-optimizer-pro-app-k94z4r.streamlit.app">
    <img src="https://img.shields.io/badge/View_Live_Demo-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Live Demo">
  </a>
</div>

<br>

**Portfolio Optimizer Pro** is a cutting-edge, interactive financial dashboard built with Streamlit. It enables retail investors, analysts, and wealth managers to construct mathematically optimized stock portfolios, visualize efficient frontiers, run probabilistic Monte Carlo simulations, and dive deep into institutional-grade risk metrics.

---

## ✨ Key Features

### 📈 Comprehensive Stock Analysis
Deep-dive into individual stock performance with interactive Plotly candlestick charts. Overlay technical indicators like **SMA, EMA, and Bollinger Bands**, and compare returns with market benchmarks.

### 🎯 Intelligent Portfolio Builder
Build and backtest multi-asset portfolios using advanced optimization algorithms:
- **Maximum Sharpe Ratio** (Highest risk-adjusted return)
- **Minimum Volatility** (Lowest possible risk)
- **Equal Weighting** (Naive diversification)

### 📊 The Efficient Frontier
Visualize your portfolio against the Markowitz Efficient Frontier. Interactively explore the Capital Market Line (CML) and immediately identify whether your asset allocation is mathematically optimal.

### 🎲 Monte Carlo Simulations
Forecast future portfolio values using geometric Brownian motion. Run 10,000+ stochastic price paths to visualize 95% confidence intervals and understand the probability distribution of your future wealth.

### ⚖️ Institutional Risk Analysis
Go beyond basic returns with wall-street grade risk metrics:
- **Risk & Returns:** Annualized Volatility, Alpha, Beta
- **Tail Risk:** Value at Risk (VaR), Conditional VaR (CVaR), Maximum Drawdown
- **Ratios:** Sharpe Ratio, Sortino Ratio, Treynor Ratio, Calmar Ratio

---

## 🛠️ Architecture & Tech Stack

- **Frontend:** [Streamlit](https://streamlit.io/) (Fully responsive, dark/light mode native)
- **Data Engine:** `yfinance` (Real-time stock data), `pandas`, `numpy`
- **Optimization:** `PyPortfolioOpt`, `scipy.optimize`
- **Visualization:** `Plotly Graph Objects` & `Plotly Express`

---

## 🚀 Getting Started

### Prerequisites
Make sure you have **Python 3.10+** and `git` installed on your machine.

### Installation
1. **Clone the repository**
   ```bash
   git clone https://github.com/AnmolSharma73/Portfolio-Optimizer-Pro.git
   cd Portfolio-Optimizer-Pro
   ```

2. **Create a virtual environment (Recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Launch the application**
   ```bash
   streamlit run app.py
   ```
   *The dashboard will automatically open in your browser at `http://localhost:8501`.*

---

## 📁 Project Structure

```text
Portfolio Optimizer/
├── app.py                          # Application entry point
├── config/
│   └── settings.py                 # Core constants & asset categorization
├── data/
│   ├── fetcher.py                  # Robust API polling & fallback logic
│   └── processor.py                # Covariance & returns calculation
├── optimization/
│   ├── markowitz.py                # Core MPT optimizers
│   └── monte_carlo.py              # Geometric Brownian Motion simulations
├── risk/
│   └── metrics.py                  # Institutional risk formulas
├── visualization/
│   ├── charts.py                   # Custom Plotly chart engines
│   └── styles.py                   # Adaptive CSS & Plotly layout templating
└── pages/                          # Streamlit multi-page routing
```

---

## 💡 How to Use

1. **Configure Settings:** Open the left sidebar to set your preferred language, base currency, and theme.
2. **Select Assets:** Navigate to the *Portfolio Builder* and add assets from the categorized dropdown menu.
3. **Set Parameters:** Choose your historical lookback period (e.g., 5y) and risk-free rate.
4. **Optimize:** Click the "Optimize" button to instantly generate optimal weights and view the resulting risk/return profile.
5. **Analyze:** Click through the remaining tabs (Efficient Frontier, Monte Carlo, Risk Analysis) to stress-test your newly generated portfolio.

---

## 🤝 Contributing
Contributions, issues, and feature requests are always welcome! Feel free to check the [issues page](https://github.com/AnmolSharma73/Portfolio-Optimizer-Pro/issues) if you want to contribute.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

<div align="center">
  <p>Built with ❤️ by Anmol Sharma</p>
</div>
