"""
Portfolio Optimizer Pro — Application Settings & Configuration.
"""

from typing import Dict, List

# ── Application Metadata ─────────────────────────────────────────────────────
APP_NAME: str = "Portfolio Optimizer Pro"
APP_VERSION: str = "1.0.0"

__all__ = [
    "APP_NAME", "APP_VERSION", "CATEGORIZED_TICKERS", "DEFAULT_TICKERS",
    "SUPPORTED_CURRENCIES", "SUPPORTED_LANGUAGES", "RISK_FREE_RATE",
    "TRADING_DAYS", "DEFAULT_PERIOD", "DEFAULT_BENCHMARK",
    "COLOR_PALETTE", "GRADIENT_COLORS", "SECTOR_COLORS", "OPTIMIZATION_METHODS"
]

# ── Global Stock Universe (Categorized by Country) ───────────────────────────
CATEGORIZED_TICKERS: Dict[str, Dict[str, str]] = {
    "United States": {
        "AAPL": "Apple Inc.",
        "MSFT": "Microsoft",
        "NVDA": "NVIDIA",
        "GOOGL": "Alphabet",
        "META": "Meta Platforms",
        "JPM": "JPMorgan Chase",
        "V": "Visa",
        "MA": "Mastercard",
        "PYPL": "PayPal",
        "LMT": "Lockheed Martin",
        "JNJ": "Johnson & Johnson",
        "UNH": "UnitedHealth",
        "TSLA": "Tesla",
        "AMZN": "Amazon",
        "WMT": "Walmart",
        "XOM": "ExxonMobil"
    },
    "India": {
        "RELIANCE.NS": "Reliance Industries",
        "TCS.NS": "Tata Consultancy",
        "INFY": "Infosys",
        "HDFCBANK.NS": "HDFC Bank",
        "IBN": "ICICI Bank",
        "HAL.NS": "Hindustan Aeronautics",
        "BEL.NS": "Bharat Electronics",
        "SUNPHARMA.NS": "Sun Pharma",
        "MARUTI.NS": "Maruti Suzuki",
        "TATAMOTORS.NS": "Tata Motors",
        "ITC.NS": "ITC Limited"
    },
    "China": {
        "TCEHY": "Tencent",
        "BABA": "Alibaba",
        "PDD": "PDD Holdings",
        "JD": "JD.com",
        "BIDU": "Baidu"
    },
    "Europe": {
        "ASML.AS": "ASML Holding",
        "SAP": "SAP SE",
        "LVMUY": "LVMH Moët Hennessy",
        "NVO": "Novo Nordisk",
        "AZN": "AstraZeneca",
        "THALES.PA": "Thales Group",
        "AIR.PA": "Airbus SE",
        "VOW3.DE": "Volkswagen",
        "SHEL": "Shell plc"
    },
    "Japan": {
        "7203.T": "Toyota Motor",
        "6758.T": "Sony Group",
        "8306.T": "Mitsubishi UFJ",
        "9984.T": "SoftBank Group",
        "6861.T": "Keyence"
    },
    "South Korea": {
        "005930.KS": "Samsung Electronics",
        "000660.KS": "SK Hynix",
        "005380.KS": "Hyundai Motor",
        "035420.KS": "NAVER"
    }
}

# Flatten list of default tickers for fallback use cases
DEFAULT_TICKERS: List[str] = []
for _cat, _stocks in CATEGORIZED_TICKERS.items():
    DEFAULT_TICKERS.extend(_stocks.keys())

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
