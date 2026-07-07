from __future__ import annotations

from typing import Any

import pandas as pd


WEIGHTS = {
    "momentum": 0.25,
    "valuation": 0.20,
    "quality": 0.25,
    "risk": 0.20,
    "liquidity": 0.10,
}


def calculate_research_score(ticker: str, metrics: dict[str, Any], price_data: pd.DataFrame) -> dict[str, Any]:
    risk_flags: list[str] = []
    factor_explanations: dict[str, str] = {}

    momentum_score = _score_momentum(metrics, price_data, risk_flags, factor_explanations)
    valuation_score = _score_valuation(metrics, risk_flags, factor_explanations)
    quality_score = _score_quality(metrics, risk_flags, factor_explanations)
    risk_score = _score_risk(metrics, risk_flags, factor_explanations)
    liquidity_score = _score_liquidity(metrics, risk_flags, factor_explanations)

    overall_score = round(
        momentum_score * WEIGHTS["momentum"]
        + valuation_score * WEIGHTS["valuation"]
        + quality_score * WEIGHTS["quality"]
        + risk_score * WEIGHTS["risk"]
        + liquidity_score * WEIGHTS["liquidity"],
        1,
    )

    return {
        "ticker": ticker.strip().upper(),
        "overall_score": overall_score,
        "momentum_score": momentum_score,
        "valuation_score": valuation_score,
        "quality_score": quality_score,
        "risk_score": risk_score,
        "liquidity_score": liquidity_score,
        "rating": _rating_for_score(overall_score),
        "risk_flags": risk_flags or ["No major rule-based risk flags"],
        "factor_explanations": factor_explanations,
    }


def _score_momentum(
    metrics: dict[str, Any],
    price_data: pd.DataFrame,
    risk_flags: list[str],
    factor_explanations: dict[str, str],
) -> int:
    one_year_return = _parse_percent(metrics.get("One-Year Return"))
    six_month_return = _calculate_period_return(price_data, periods=126)
    selected_return = one_year_return if one_year_return is not None else six_month_return

    if selected_return is None:
        risk_flags.append("Missing financial data")
        factor_explanations["momentum"] = "Momentum data is missing, so a neutral score was assigned."
        return 50

    if selected_return < 0:
        risk_flags.append("Negative momentum")

    score = _linear_score(selected_return, low=-0.30, high=0.60)
    factor_explanations["momentum"] = f"Momentum score is based on return of {selected_return:.1%}."
    return score


def _score_valuation(
    metrics: dict[str, Any],
    risk_flags: list[str],
    factor_explanations: dict[str, str],
) -> int:
    trailing_pe = _parse_number(metrics.get("Trailing PE"))
    forward_pe = _parse_number(metrics.get("Forward PE"))
    price_to_book = _parse_number(metrics.get("Price to Book"))

    scores = []
    if trailing_pe is not None and trailing_pe > 0:
        scores.append(_inverse_linear_score(trailing_pe, low=10, high=50))
    if forward_pe is not None and forward_pe > 0:
        scores.append(_inverse_linear_score(forward_pe, low=10, high=45))
    if price_to_book is not None and price_to_book > 0:
        scores.append(_inverse_linear_score(price_to_book, low=1, high=12))

    if not scores:
        risk_flags.append("Missing financial data")
        factor_explanations["valuation"] = "Valuation metrics are missing, so a neutral score was assigned."
        return 50

    score = round(sum(scores) / len(scores))
    if score < 45:
        risk_flags.append("Premium valuation")
    factor_explanations["valuation"] = "Valuation score uses trailing PE, forward PE, and price to book when available."
    return score


def _score_quality(
    metrics: dict[str, Any],
    risk_flags: list[str],
    factor_explanations: dict[str, str],
) -> int:
    profit_margin = _parse_percent(metrics.get("Profit Margin"))
    roe = _parse_percent(metrics.get("ROE"))
    revenue_growth = _parse_percent(metrics.get("Revenue Growth"))

    scores = []
    if profit_margin is not None:
        scores.append(_linear_score(profit_margin, low=0.00, high=0.35))
    if roe is not None:
        scores.append(_linear_score(roe, low=0.00, high=0.40))
    if revenue_growth is not None:
        scores.append(_linear_score(revenue_growth, low=-0.10, high=0.30))

    if not scores:
        risk_flags.append("Missing financial data")
        factor_explanations["quality"] = "Quality metrics are missing, so a neutral score was assigned."
        return 50

    score = round(sum(scores) / len(scores))
    if score < 45:
        risk_flags.append("Weak profitability")
    factor_explanations["quality"] = "Quality score uses profit margin, ROE, and revenue growth when available."
    return score


def _score_risk(
    metrics: dict[str, Any],
    risk_flags: list[str],
    factor_explanations: dict[str, str],
) -> int:
    volatility = _parse_percent(metrics.get("Annualized Volatility"))
    if volatility is None:
        risk_flags.append("Missing financial data")
        factor_explanations["risk"] = "Volatility is missing, so a neutral score was assigned."
        return 50

    if volatility > 0.45:
        risk_flags.append("High volatility")

    score = _inverse_linear_score(volatility, low=0.15, high=0.65)
    factor_explanations["risk"] = f"Risk score is based on annualized volatility of {volatility:.1%}."
    return score


def _score_liquidity(
    metrics: dict[str, Any],
    risk_flags: list[str],
    factor_explanations: dict[str, str],
) -> int:
    market_cap = _parse_market_cap(metrics.get("Market Cap"))
    if market_cap is None:
        risk_flags.append("Missing financial data")
        factor_explanations["liquidity"] = "Market cap is missing, so a neutral score was assigned."
        return 50

    if market_cap >= 200_000_000_000:
        score = 95
    elif market_cap >= 50_000_000_000:
        score = 85
    elif market_cap >= 10_000_000_000:
        score = 70
    elif market_cap >= 2_000_000_000:
        score = 55
    else:
        score = 40

    factor_explanations["liquidity"] = "Liquidity score uses market capitalization as a first-pass proxy."
    return score


def _rating_for_score(score: float) -> str:
    if score >= 80:
        return "Strong Research Candidate"
    if score >= 65:
        return "Watchlist Candidate"
    if score >= 50:
        return "Neutral"
    return "High Risk / Weak Candidate"


def _calculate_period_return(price_data: pd.DataFrame, periods: int) -> float | None:
    if price_data.empty or "Close" not in price_data.columns:
        return None

    close_prices = price_data["Close"].dropna()
    if len(close_prices) < 2:
        return None

    start_index = max(0, len(close_prices) - periods)
    first_price = close_prices.iloc[start_index]
    last_price = close_prices.iloc[-1]
    if first_price == 0:
        return None
    return (last_price / first_price) - 1


def _linear_score(value: float, low: float, high: float) -> int:
    if value <= low:
        return 0
    if value >= high:
        return 100
    return round(((value - low) / (high - low)) * 100)


def _inverse_linear_score(value: float, low: float, high: float) -> int:
    return 100 - _linear_score(value, low, high)


def _parse_percent(value: Any) -> float | None:
    if value is None or value == "N/A":
        return None
    if isinstance(value, str):
        cleaned = value.strip().replace("%", "").replace(",", "")
        if not cleaned:
            return None
        try:
            return float(cleaned) / 100
        except ValueError:
            return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _parse_number(value: Any) -> float | None:
    if value is None or value == "N/A":
        return None
    if isinstance(value, str):
        cleaned = value.strip().replace(",", "")
        if not cleaned:
            return None
        try:
            return float(cleaned)
        except ValueError:
            return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _parse_market_cap(value: Any) -> float | None:
    if value is None or value == "N/A":
        return None
    if not isinstance(value, str):
        return _parse_number(value)

    cleaned = value.strip().replace(",", "")
    if not cleaned:
        return None

    multiplier = 1
    suffix = cleaned[-1].upper()
    if suffix == "T":
        multiplier = 1_000_000_000_000
        cleaned = cleaned[:-1]
    elif suffix == "B":
        multiplier = 1_000_000_000
        cleaned = cleaned[:-1]
    elif suffix == "M":
        multiplier = 1_000_000
        cleaned = cleaned[:-1]

    try:
        return float(cleaned) * multiplier
    except ValueError:
        return None
