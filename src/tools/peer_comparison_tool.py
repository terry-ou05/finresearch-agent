from __future__ import annotations

from typing import Any

import pandas as pd
import yfinance as yf

from src.tools.metrics_tool import _format_large_number, _format_number, _format_percent


DEFAULT_PEERS = {
    "AAPL": ["MSFT", "GOOGL", "AMZN", "NVDA"],
    "MSFT": ["AAPL", "GOOGL", "AMZN", "ORCL"],
    "NVDA": ["AMD", "INTC", "AVGO", "QCOM"],
    "TSLA": ["F", "GM", "RIVN", "LCID"],
}


PEER_COLUMNS = [
    "Ticker",
    "Company Name",
    "Market Cap",
    "Trailing PE",
    "Forward PE",
    "Price to Book",
    "Profit Margin",
    "ROE",
    "Revenue Growth",
]


def get_default_peers(ticker: str) -> list[str]:
    return DEFAULT_PEERS.get(ticker.strip().upper(), [])


def parse_peer_tickers(peer_tickers: str | None) -> list[str]:
    if not peer_tickers:
        return []

    parsed = []
    seen = set()
    for raw_ticker in peer_tickers.split(","):
        ticker = raw_ticker.strip().upper()
        if ticker and ticker not in seen:
            parsed.append(ticker)
            seen.add(ticker)
    return parsed


def get_peer_tickers(primary_ticker: str, peer_tickers: str | None = None) -> list[str]:
    primary = primary_ticker.strip().upper()
    peers = parse_peer_tickers(peer_tickers) or get_default_peers(primary)
    return [peer for peer in peers if peer != primary]


def get_peer_comparison(primary_ticker: str, peer_tickers: str | None = None) -> pd.DataFrame:
    primary = primary_ticker.strip().upper()
    tickers = [primary, *get_peer_tickers(primary, peer_tickers)]

    rows = [_build_peer_row(ticker) for ticker in tickers if ticker]
    if not rows:
        return pd.DataFrame(columns=PEER_COLUMNS)
    return pd.DataFrame(rows, columns=PEER_COLUMNS)


def _build_peer_row(ticker: str) -> dict[str, Any]:
    try:
        info = yf.Ticker(ticker).info or {}
    except Exception:
        info = {}

    return {
        "Ticker": info.get("symbol") or ticker,
        "Company Name": info.get("longName") or info.get("shortName") or "N/A",
        "Market Cap": _format_large_number(info.get("marketCap")),
        "Trailing PE": _format_number(info.get("trailingPE")),
        "Forward PE": _format_number(info.get("forwardPE")),
        "Price to Book": _format_number(info.get("priceToBook")),
        "Profit Margin": _format_percent(info.get("profitMargins")),
        "ROE": _format_percent(info.get("returnOnEquity")),
        "Revenue Growth": _format_percent(info.get("revenueGrowth")),
    }
