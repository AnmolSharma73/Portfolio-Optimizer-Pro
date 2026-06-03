"""
Portfolio Optimizer Pro — Application Settings & Configuration.
"""

from typing import Dict, List

# ── Application Metadata ─────────────────────────────────────────────────────
APP_NAME: str = "Portfolio Optimizer Pro"
APP_VERSION: str = "1.0.0"

# ── Default Portfolio Configuration ───────────────────────────────────────────
DEFAULT_TICKERS: List[str] = [
    # US
    "AAPL", "MSFT", "NVDA",
    # India
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS",
    # China
    "TCEHY", "BABA",
    # Europe
    "ASML.AS", "LVMUY", "SAP",
    # Japan
    "7203.T", "6758.T", # Toyota, Sony
    # South Korea
    "005930.KS", # Samsung
]

# ── Supported Currencies ──────────────────────────────────────────────────────
SUPPORTED_CURRENCIES: Dict[str, str] = {
    "USD ($)": "USD",
    "INR (₹)": "INR",
    "EUR (€)": "EUR",
    "JPY (¥)": "JPY",
    "KRW (₩)": "KRW",
    "CNY (¥)": "CNY",
}

# ── Supported Languages ───────────────────────────────────────────────────────
SUPPORTED_LANGUAGES: Dict[str, str] = {
    "English": "en",
    "Hindi": "hi",
    "Spanish": "es",
    "French": "fr",
    "Chinese": "zh",
}

# ── Financial Parameters ──────────────────────────────────────────────────────
RISK_FREE_RATE: float = 0.05
TRADING_DAYS: int = 252
DEFAULT_PERIOD: str = "5y"
DEFAULT_BENCHMARK: str = "^GSPC"

# ── Color Palette ─────────────────────────────────────────────────────────────
COLOR_PALETTE: Dict[str, str] = {
    "primary":    "#6C63FF",
    "secondary":  "#00D2FF",
    "accent":     "#FFD700",
    "success":    "#00E396",
    "danger":     "#FF4560",
    "warning":    "#FEB019",
    "info":       "#008FFB",
    "background": "#0E1117",
    "card":       "#1A1F2E",
    "card_hover": "#252B3B",
    "text":       "#E0E0E0",
    "text_muted": "#8892A0",
}

# ── Gradient Colors (charts) ─────────────────────────────────────────────────
GRADIENT_COLORS: List[str] = [
    "#6C63FF", "#7B6FFF", "#5A8DFF", "#3CA5FF", "#00BCD4",
    "#00D2FF", "#26C6DA", "#00E396", "#FEB019", "#FFD700",
]

# ── Sector Color Mapping ─────────────────────────────────────────────────────
SECTOR_COLORS: Dict[str, str] = {
    "Technology":             "#6C63FF",
    "Healthcare":             "#00E396",
    "Financial Services":     "#008FFB",
    "Financials":             "#008FFB",
    "Consumer Cyclical":      "#FEB019",
    "Consumer Defensive":     "#26C6DA",
    "Communication Services": "#FF6EC7",
    "Energy":                 "#FF4560",
    "Industrials":            "#775DD0",
    "Utilities":              "#3F51B5",
    "Real Estate":            "#33B2DF",
    "Basic Materials":        "#A5978B",
}

# ── Optimization Methods (simplified — 3 strategies) ─────────────────────────
OPTIMIZATION_METHODS: Dict[str, str] = {
    "Maximum Sharpe Ratio": "max_sharpe",
    "Minimum Volatility":   "min_vol",
    "Equal Weight":         "equal_weight",
}
