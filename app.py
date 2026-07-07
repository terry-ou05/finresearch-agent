import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.tools.market_data_tool import get_company_info, get_financial_data, get_historical_prices
from src.tools.metrics_tool import calculate_metrics
from src.tools.report_tool import generate_financial_report
from src.utils.config import get_settings


st.set_page_config(
    page_title="FinResearch Agent",
    page_icon=":chart_with_upwards_trend:",
    layout="wide",
)


def render_price_chart(price_data: pd.DataFrame, ticker: str) -> None:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=price_data.index,
            y=price_data["Close"],
            mode="lines",
            name="Close",
            line=dict(width=2),
        )
    )
    fig.update_layout(
        title=f"{ticker.upper()} Price History",
        xaxis_title="Date",
        yaxis_title="Close Price",
        height=420,
        margin=dict(l=20, r=20, t=60, b=20),
    )
    st.plotly_chart(fig, use_container_width=True)


def render_company_profile(company_info: dict) -> None:
    col1, col2, col3 = st.columns(3)
    col1.metric("Company", company_info.get("longName") or company_info.get("shortName") or "N/A")
    col2.metric("Sector", company_info.get("sector") or "N/A")
    col3.metric("Industry", company_info.get("industry") or "N/A")

    with st.expander("Business Summary", expanded=True):
        st.write(company_info.get("longBusinessSummary") or "N/A")


def render_metrics_table(metrics: dict) -> None:
    rows = [{"Metric": key, "Value": value} for key, value in metrics.items()]
    st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)


def mask_api_key(api_key: str | None) -> str:
    if not api_key:
        return "N/A"
    return f"{api_key[:6]}****"


def render_provider_debug() -> None:
    settings = get_settings()
    provider_rows = [
        {"Item": "LLM Provider", "Value": provider_label(settings.llm_base_url)},
        {"Item": "Model", "Value": settings.llm_model},
    ]
    st.dataframe(pd.DataFrame(provider_rows), hide_index=True, use_container_width=True)

    if settings.debug_provider:
        debug_rows = [
            {"Item": "API key loaded", "Value": "Yes" if settings.api_key else "No"},
            {"Item": "API key prefix", "Value": mask_api_key(settings.api_key)},
            {"Item": "base_url", "Value": settings.llm_base_url or "N/A"},
        ]
        st.caption("Provider debug")
        st.dataframe(pd.DataFrame(debug_rows), hide_index=True, use_container_width=True)


def provider_label(base_url: str | None) -> str:
    if base_url and "deepseek" in base_url.lower():
        return "DeepSeek / OpenAI-compatible"
    return "OpenAI-compatible"


st.title("FinResearch Agent")
st.caption("LLM-powered financial research assistant for educational analysis.")

ticker = st.text_input("Enter a stock ticker", value="AAPL", placeholder="AAPL, MSFT, NVDA")
period = st.selectbox("Historical price period", ["1y", "2y", "5y"], index=0)

analyze = st.button("Analyze", type="primary")

if analyze:
    ticker = ticker.strip().upper()
    if not ticker:
        st.warning("Please enter a valid ticker.")
        st.stop()

    try:
        with st.spinner(f"Fetching market data for {ticker}..."):
            price_data = get_historical_prices(ticker, period=period)
            company_info = get_company_info(ticker)
            financial_data = get_financial_data(ticker)
            metrics = calculate_metrics(price_data, company_info, financial_data)

        st.subheader("Company Profile")
        render_company_profile(company_info)

        st.subheader("Stock Price")
        render_price_chart(price_data, ticker)

        st.subheader("Financial Metrics")
        render_metrics_table(metrics)

        report_payload = {
            "ticker": ticker,
            "company_info": company_info,
            "metrics": metrics,
            "financial_data": financial_data,
        }

        st.subheader("LLM Research Report")
        render_provider_debug()
        with st.spinner("Generating structured research report..."):
            report = generate_financial_report(report_payload)
        st.markdown(report)

    except Exception as exc:
        st.error(f"Analysis failed: {exc}")

st.divider()
st.caption(
    "Disclaimer: This project is for educational and research purposes only and "
    "does not constitute investment advice."
)
