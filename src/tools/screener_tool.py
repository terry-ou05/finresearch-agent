from __future__ import annotations

import pandas as pd

from src.tools.market_data_tool import get_company_info, get_financial_data, get_historical_prices
from src.tools.metrics_tool import calculate_metrics
from src.tools.scoring_tool import calculate_research_score


WATCHLIST_COLUMNS = [
    "Rank",
    "Ticker",
    "Overall Score",
    "Rating",
    "Momentum",
    "Valuation",
    "Quality",
    "Risk",
    "Liquidity",
    "Risk Flags",
]


def run_market_screener(tickers: list[str]) -> pd.DataFrame:
    cleaned_tickers = _clean_tickers(tickers)
    if not cleaned_tickers:
        return pd.DataFrame(columns=WATCHLIST_COLUMNS)

    rows = []
    for ticker in cleaned_tickers:
        try:
            price_data = get_historical_prices(ticker, period="1y")
            company_info = get_company_info(ticker)
            try:
                financial_data = get_financial_data(ticker)
            except Exception:
                financial_data = {}
            metrics = calculate_metrics(price_data, company_info, financial_data)
            score = calculate_research_score(ticker, metrics, price_data)
            rows.append(_score_to_row(score))
        except Exception as exc:
            rows.append(_error_row(ticker, exc))

    result = pd.DataFrame(rows, columns=WATCHLIST_COLUMNS)
    if result.empty:
        return result

    result = result.sort_values(["Overall Score", "Ticker"], ascending=[False, True], ignore_index=True)
    result["Rank"] = range(1, len(result) + 1)
    return result


def parse_ticker_list(ticker_text: str) -> list[str]:
    return _clean_tickers(ticker_text.split(","))


def _clean_tickers(tickers: list[str]) -> list[str]:
    cleaned = []
    seen = set()
    for raw_ticker in tickers:
        ticker = raw_ticker.strip().upper()
        if ticker and ticker not in seen:
            cleaned.append(ticker)
            seen.add(ticker)
    return cleaned


def _score_to_row(score: dict) -> dict:
    return {
        "Rank": None,
        "Ticker": score["ticker"],
        "Overall Score": score["overall_score"],
        "Rating": score["rating"],
        "Momentum": score["momentum_score"],
        "Valuation": score["valuation_score"],
        "Quality": score["quality_score"],
        "Risk": score["risk_score"],
        "Liquidity": score["liquidity_score"],
        "Risk Flags": "; ".join(score["risk_flags"]),
    }


def _error_row(ticker: str, exc: Exception) -> dict:
    return {
        "Rank": None,
        "Ticker": ticker,
        "Overall Score": 0,
        "Rating": "Data Error",
        "Momentum": "N/A",
        "Valuation": "N/A",
        "Quality": "N/A",
        "Risk": "N/A",
        "Liquidity": "N/A",
        "Risk Flags": f"Data fetch failed: {exc}",
    }
