from __future__ import annotations

from typing import Any

import pandas as pd
import yfinance as yf


def _get_ticker(ticker: str) -> yf.Ticker:
    symbol = ticker.strip().upper()
    if not symbol:
        raise ValueError("Ticker cannot be empty.")
    return yf.Ticker(symbol)


def get_historical_prices(ticker: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    """Fetch historical OHLCV data for a ticker."""
    try:
        stock = _get_ticker(ticker)
        data = stock.history(period=period, interval=interval, auto_adjust=False)
    except Exception as exc:
        raise RuntimeError(f"Failed to fetch historical prices for {ticker}: {exc}") from exc

    if data.empty:
        raise ValueError(f"No historical price data returned for {ticker}.")

    required_columns = {"Open", "High", "Low", "Close", "Volume"}
    missing_columns = required_columns.difference(data.columns)
    if missing_columns:
        raise ValueError(f"Historical data for {ticker} is missing columns: {sorted(missing_columns)}")

    return data


def get_company_info(ticker: str) -> dict[str, Any]:
    """Fetch company profile and market metadata from Yahoo Finance."""
    try:
        stock = _get_ticker(ticker)
        info = stock.info or {}
    except Exception as exc:
        raise RuntimeError(f"Failed to fetch company info for {ticker}: {exc}") from exc

    if not info:
        raise ValueError(f"No company info returned for {ticker}.")

    return info


def get_financial_data(ticker: str) -> dict[str, Any]:
    """Fetch basic financial statements and balance-sheet data."""
    try:
        stock = _get_ticker(ticker)
        financials = stock.financials
        balance_sheet = stock.balance_sheet
        cashflow = stock.cashflow
    except Exception as exc:
        raise RuntimeError(f"Failed to fetch financial statements for {ticker}: {exc}") from exc

    return {
        "income_statement": _dataframe_to_compact_dict(financials),
        "balance_sheet": _dataframe_to_compact_dict(balance_sheet),
        "cashflow": _dataframe_to_compact_dict(cashflow),
    }


def _dataframe_to_compact_dict(data: pd.DataFrame | None, max_rows: int = 12) -> dict[str, Any]:
    if data is None or data.empty:
        return {}

    compact = data.head(max_rows).copy()
    compact.columns = [str(col.date()) if hasattr(col, "date") else str(col) for col in compact.columns]
    return compact.fillna("N/A").to_dict()
