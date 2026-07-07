from __future__ import annotations

from typing import Any

import pandas as pd


TRADING_DAYS_PER_YEAR = 252


def calculate_metrics(
    price_data: pd.DataFrame,
    company_info: dict[str, Any],
    financial_data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if price_data.empty or "Close" not in price_data.columns:
        raise ValueError("Price data must include a non-empty Close column.")

    close_prices = price_data["Close"].dropna()
    if close_prices.empty:
        raise ValueError("Close price series is empty.")

    one_year_return = _calculate_one_year_return(close_prices)
    volatility = _calculate_annualized_volatility(close_prices)

    return {
        "Ticker": company_info.get("symbol", "N/A"),
        "Company Name": company_info.get("longName") or company_info.get("shortName") or "N/A",
        "Currency": company_info.get("currency", "N/A"),
        "Market Cap": _format_large_number(company_info.get("marketCap")),
        "Trailing PE": _format_number(company_info.get("trailingPE")),
        "Forward PE": _format_number(company_info.get("forwardPE")),
        "Price to Book": _format_number(company_info.get("priceToBook")),
        "Profit Margin": _format_percent(company_info.get("profitMargins")),
        "ROE": _format_percent(company_info.get("returnOnEquity")),
        "Revenue Growth": _format_percent(company_info.get("revenueGrowth")),
        "Dividend Yield": _format_percent(company_info.get("dividendYield")),
        "One-Year Return": _format_percent(one_year_return),
        "Annualized Volatility": _format_percent(volatility),
    }


def _calculate_one_year_return(close_prices: pd.Series) -> float | None:
    if len(close_prices) < 2:
        return None
    first_price = close_prices.iloc[0]
    last_price = close_prices.iloc[-1]
    if first_price == 0:
        return None
    return (last_price / first_price) - 1


def _calculate_annualized_volatility(close_prices: pd.Series) -> float | None:
    returns = close_prices.pct_change().dropna()
    if returns.empty:
        return None
    return returns.std() * (TRADING_DAYS_PER_YEAR**0.5)


def _format_number(value: Any) -> str:
    if value is None or pd.isna(value):
        return "N/A"
    try:
        return f"{float(value):,.2f}"
    except (TypeError, ValueError):
        return "N/A"


def _format_percent(value: Any) -> str:
    if value is None or pd.isna(value):
        return "N/A"
    try:
        return f"{float(value) * 100:.2f}%"
    except (TypeError, ValueError):
        return "N/A"


def _format_large_number(value: Any) -> str:
    if value is None or pd.isna(value):
        return "N/A"
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "N/A"

    units = [("T", 1_000_000_000_000), ("B", 1_000_000_000), ("M", 1_000_000)]
    for suffix, threshold in units:
        if abs(number) >= threshold:
            return f"{number / threshold:,.2f}{suffix}"
    return f"{number:,.0f}"
