"""
Portfolio Optimizer Pro — Stock Data Fetcher.
Provides cached data retrieval from Yahoo Finance via yfinance.
"""

from __future__ import annotations
from typing import Dict, List, Optional
import pandas as pd
import streamlit as st
import yfinance as yf


# ═══════════════════════════════════════════════════════════════════════════════
# Module-level cached functions
# ═══════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=3600, show_spinner=False)
def _fetch_stock_data(ticker: str, period: str = "5y", interval: str = "1d") -> pd.DataFrame:
    """Download OHLCV data for a single ticker."""
    try:
        data = yf.download(ticker, period=period, interval=interval, progress=False, auto_adjust=True)
        if data.empty:
            return pd.DataFrame()
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        return data
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=3600, show_spinner=False)
def _fetch_multiple_stocks(tickers: tuple, period: str = "5y", interval: str = "1d") -> pd.DataFrame:
    """Download adjusted close prices for multiple tickers."""
    try:
        tickers_list = list(tickers)
        data = yf.download(tickers_list, period=period, interval=interval,
                           progress=False, auto_adjust=True, group_by="ticker")
        if data.empty:
            return pd.DataFrame()

        if isinstance(data.columns, pd.MultiIndex):
            close_prices = pd.DataFrame()
            for tkr in tickers_list:
                try:
                    if tkr in data.columns.get_level_values(0):
                        close_prices[tkr] = data[(tkr, "Close")]
                except KeyError:
                    continue
            return close_prices if not close_prices.empty else pd.DataFrame()
        else:
            if len(tickers_list) == 1:
                return data[["Close"]].rename(columns={"Close": tickers_list[0]})
            return data
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=3600, show_spinner=False)
def _fetch_stock_info(ticker: str) -> dict:
    """Return the yfinance .info dict for a ticker."""
    try:
        return yf.Ticker(ticker).info or {}
    except Exception:
        return {}


@st.cache_data(ttl=3600, show_spinner=False)
def _fetch_current_price(ticker: str) -> Optional[float]:
    """Return the latest closing price for a ticker."""
    try:
        hist = yf.Ticker(ticker).history(period="5d")
        if hist.empty:
            return None
        return float(hist["Close"].iloc[-1])
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# Public class
# ═══════════════════════════════════════════════════════════════════════════════

class StockDataFetcher:
    """High-level interface for fetching and caching stock market data."""

    def get_stock_data(self, ticker: str, period: str = "5y", interval: str = "1d") -> pd.DataFrame:
        """Download OHLCV data for a single ticker."""
        return _fetch_stock_data(ticker, period, interval)

    def get_multiple_stocks(self, tickers: List[str], period: str = "5y", interval: str = "1d") -> pd.DataFrame:
        """Download adjusted close prices for a list of tickers."""
        return _fetch_multiple_stocks(tuple(sorted(tickers)), period, interval)

    def get_stock_info(self, ticker: str) -> dict:
        """Return company info dict from Yahoo Finance."""
        return _fetch_stock_info(ticker)

    def get_current_price(self, ticker: str) -> Optional[float]:
        """Return the most recent closing price."""
        return _fetch_current_price(ticker)

    def get_market_caps(self, tickers: List[str]) -> Dict[str, Optional[float]]:
        """Return market capitalisation for each ticker."""
        caps: Dict[str, Optional[float]] = {}
        for tkr in tickers:
            info = self.get_stock_info(tkr)
            caps[tkr] = info.get("marketCap")
        return caps
