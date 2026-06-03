"""
Portfolio Optimizer Pro — Utility Helpers.
Formatting, validation, and session-state helpers.
"""

from __future__ import annotations
import datetime as dt
from typing import List, Optional, Tuple
import streamlit as st

__all__ = [
    "format_currency",
    "format_percentage",
    "format_large_number",
    "create_metric_card",
    "init_session_state",
]


def format_currency(value: float, symbol: str = "$") -> str:
    """Format a numeric value as currency."""
    try:
        return f"{symbol}{value:,.2f}"
    except (TypeError, ValueError):
        return f"{symbol}0.00"


def format_percentage(value: float, decimals: int = 2) -> str:
    """Format a decimal value as a percentage string."""
    try:
        return f"{value * 100:,.{decimals}f}%"
    except (TypeError, ValueError):
        return "0.00%"


def format_large_number(value: float) -> str:
    """Convert a large number to a human-readable K / M / B / T string."""
    try:
        value = float(value)
    except (TypeError, ValueError):
        return "N/A"
    abs_value = abs(value)
    sign = "-" if value < 0 else ""
    if abs_value >= 1e12:
        return f"{sign}{abs_value / 1e12:.2f}T"
    elif abs_value >= 1e9:
        return f"{sign}{abs_value / 1e9:.2f}B"
    elif abs_value >= 1e6:
        return f"{sign}{abs_value / 1e6:.2f}M"
    elif abs_value >= 1e3:
        return f"{sign}{abs_value / 1e3:.2f}K"
    else:
        return f"{sign}{abs_value:,.2f}"


def create_metric_card(label: str, value: str, delta: Optional[str] = None, delta_color: str = "normal") -> None:
    """Render a styled st.metric."""
    st.metric(label=label, value=value, delta=delta, delta_color=delta_color)


def init_session_state() -> None:
    """Initialise all required session_state variables."""
    defaults = {
        "portfolio_tickers": [],
        "portfolio_weights": {},
        "investment_amount": 100_000.0,
        "optimized": False,
        "optimization_method": "max_sharpe",
        "optimization_result": None,
        "price_data": None,
        "returns_data": None,
        "selected_period": "5y",
        "risk_free_rate": 0.05,
        "theme": "dark",
        "language": "en",
        "currency": "USD",
        "fx_rate": 1.0,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
