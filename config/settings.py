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

# ── Global Stock Universe (Categorized) ───────────────────────────────────────
CATEGORIZED_TICKERS: Dict[str, Dict[str, str]] = {
    "Technology & IT": {
        "AAPL": "Apple Inc.",
        "MSFT": "Microsoft",
        "NVDA": "NVIDIA",
        "TCS.NS": "Tata Consultancy",
        "INFY": "Infosys",
        "TCEHY": "Tencent",
        "BABA": "Alibaba",
        "ASML.AS": "ASML Holding",
        "SAP": "SAP SE",
        "005930.KS": "Samsung Electronics",
        "6758.T": "Sony Group",
        "GOOGL": "Alphabet",
        "META": "Meta Platforms"
    },
    "Fintech & Finance": {
        "JPM": "JPMorgan Chase",
        "V": "Visa",
        "MA": "Mastercard",
        "PYPL": "PayPal",
        "SQ": "Block (Square)",
        "HDFCBANK.NS": "HDFC Bank",
        "IBN": "ICICI Bank",
        "HSBC": "HSBC Holdings",
        "AXP": "American Express",
        "GS": "Goldman Sachs"
    },
    "Defence & Aerospace": {
        "LMT": "Lockheed Martin",
        "RTX": "RTX Corp",
        "NOC": "Northrop Grumman",
        "GD": "General Dynamics",
        "BA": "Boeing",
        "THALES.PA": "Thales Group",
        "BA.L": "BAE Systems",
        "AIR.PA": "Airbus SE",
        "HAL.NS": "Hindustan Aeronautics",
        "BEL.NS": "Bharat Electronics"
    },
    "Healthcare & Biotech": {
        "JNJ": "Johnson & Johnson",
        "UNH": "UnitedHealth",
        "LLY": "Eli Lilly",
        "NVO": "Novo Nordisk",
        "PFE": "Pfizer",
        "AZN": "AstraZeneca",
        "SUNPHARMA.NS": "Sun Pharma",
        "MRK": "Merck & Co"
    },
    "Automotive & Transport": {
        "TSLA": "Tesla",
        "7203.T": "Toyota Motor",
        "TM": "Toyota (US ADR)",
        "F": "Ford Motor",
        "GM": "General Motors",
        "RACE": "Ferrari",
        "MARUTI.NS": "Maruti Suzuki",
        "TATAMOTORS.NS": "Tata Motors",
        "VOW3.DE": "Volkswagen"
    },
    "Energy & Materials": {
        "XOM": "ExxonMobil",
        "CVX": "Chevron",
        "SHEL": "Shell plc",
        "RELIANCE.NS": "Reliance Industries",
        "BHP": "BHP Group",
        "RIO": "Rio Tinto",
        "TTE": "TotalEnergies",
        "BP": "BP plc"
    },
    "Consumer & Retail": {
        "AMZN": "Amazon",
        "WMT": "Walmart",
        "LVMUY": "LVMH Moët Hennessy",
        "PG": "Procter & Gamble",
        "KO": "Coca-Cola",
        "PEP": "PepsiCo",
        "NKE": "Nike",
        "ITC.NS": "ITC Limited",
        "HUN": "Unilever"
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
