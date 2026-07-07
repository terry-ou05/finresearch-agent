from __future__ import annotations

import json
import re
from typing import Any

from openai import APIConnectionError, APIStatusError, AuthenticationError, BadRequestError, NotFoundError, OpenAI

from src.prompts.financial_report_prompt import REPORT_TEMPLATE, SYSTEM_PROMPT
from src.utils.config import get_settings


FORBIDDEN_RECOMMENDATION_PATTERNS = [
    r"\bstrong buy\b",
    r"\bstrong sell\b",
    r"\bbuy recommendation\b",
    r"\bsell recommendation\b",
    r"\brecommend buying\b",
    r"\brecommend selling\b",
]


def generate_financial_report(financial_data: dict[str, Any]) -> str:
    settings = get_settings()
    if not settings.api_key:
        return _missing_api_key_report(financial_data)

    client_kwargs = {"api_key": settings.api_key}
    if settings.llm_base_url:
        client_kwargs["base_url"] = settings.llm_base_url

    client = OpenAI(**client_kwargs)
    user_prompt = REPORT_TEMPLATE.format(
        financial_data=json.dumps(financial_data, indent=2, ensure_ascii=False, default=str)
    )

    try:
        response = client.chat.completions.create(
            model=settings.llm_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
        )
        report = response.choices[0].message.content or ""
    except Exception as exc:
        return _llm_error_report(exc)

    if not report.strip():
        return _llm_error_report(RuntimeError("The LLM returned an empty response."))

    return _sanitize_report(report)


def _sanitize_report(report: str) -> str:
    cleaned = report.strip()
    for pattern in FORBIDDEN_RECOMMENDATION_PATTERNS:
        cleaned = re.sub(pattern, "not a direct investment recommendation", cleaned, flags=re.IGNORECASE)
    return cleaned


def _llm_error_report(exc: Exception) -> str:
    return f"""
### LLM Call Error
API key exists but LLM call failed.

- Error category: {_classify_llm_error(exc)}
- Error type: {type(exc).__name__}
- Details: {_clean_error_message(str(exc))}

Check the provider settings, API key validity, account balance, model name, and base_url.
""".strip()


def _classify_llm_error(exc: Exception) -> str:
    message = str(exc).lower()

    if isinstance(exc, AuthenticationError) or "authentication" in message or "unauthorized" in message:
        return "authentication error"
    if "insufficient" in message and "balance" in message:
        return "insufficient balance"
    if isinstance(exc, NotFoundError) or "model" in message and ("not found" in message or "invalid" in message):
        return "invalid model"
    if isinstance(exc, APIConnectionError) or "connection" in message or "connect" in message:
        return "connection error"
    if "base_url" in message or "unsupported protocol" in message or "invalid url" in message:
        return "base_url issue"
    if isinstance(exc, BadRequestError):
        return "bad request"
    if isinstance(exc, APIStatusError):
        return f"provider API error, status code {exc.status_code}"
    return "unknown LLM error"


def _clean_error_message(message: str) -> str:
    return message.replace("\n", " ").strip() or "No error details returned by provider."


def _missing_api_key_report(financial_data: dict[str, Any]) -> str:
    ticker = financial_data.get("ticker", "N/A")
    metrics = financial_data.get("metrics", {})
    company_info = financial_data.get("company_info", {})

    return f"""
### Company Overview
{company_info.get("longName") or company_info.get("shortName") or ticker} operates in the {company_info.get("sector", "N/A")} sector and the {company_info.get("industry", "N/A")} industry.

### Stock Performance
The one-year return is {metrics.get("One-Year Return", "N/A")}, with annualized volatility of {metrics.get("Annualized Volatility", "N/A")}.

### Valuation
Market cap is {metrics.get("Market Cap", "N/A")}. Trailing PE is {metrics.get("Trailing PE", "N/A")}, forward PE is {metrics.get("Forward PE", "N/A")}, and price-to-book is {metrics.get("Price to Book", "N/A")}.

### Profitability
Profit margin is {metrics.get("Profit Margin", "N/A")}, ROE is {metrics.get("ROE", "N/A")}, and revenue growth is {metrics.get("Revenue Growth", "N/A")}.

### Key Risks
Key risks may include market volatility, changes in growth expectations, competitive pressure, macroeconomic uncertainty, and company-specific execution risks.

### Research Summary
This fallback report summarizes the structured data available in the application. Add an API key in `.env` to generate a richer LLM-written report.

### Disclaimer
This project is for educational and research purposes only and does not constitute investment advice.
""".strip()
