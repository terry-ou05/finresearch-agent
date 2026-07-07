# FinResearch Agent

FinResearch Agent is a Streamlit-based MVP for LLM-assisted equity research. A user enters a stock ticker such as `AAPL`, `MSFT`, or `NVDA`; the app fetches market and company data, calculates basic financial metrics, visualizes price history, and generates a structured research report with an OpenAI-compatible LLM.

This first version is intentionally scoped as a portfolio-ready MVP. It does not include complex RAG, autonomous trading, portfolio execution, or real investment advice.

## Features

- Fetch historical stock prices with `yfinance`
- Fetch company profile, market metadata, and basic financial statements
- Calculate basic metrics including one-year return, annualized volatility, market cap, PE, PB, profit margin, ROE, revenue growth, and dividend yield
- Visualize stock price history with Plotly
- Generate a structured LLM report with required research sections
- Support OpenAI or DeepSeek through an OpenAI-compatible API configuration
- Provide a fallback report when no API key is configured

## Tech Stack

- Python
- Streamlit
- pandas
- yfinance
- plotly
- OpenAI Python SDK
- python-dotenv

## Project Structure

```text
finresearch-agent/
├── app.py
├── requirements.txt
├── README.md
├── .env.example
└── src/
    ├── tools/
    │   ├── market_data_tool.py
    │   ├── metrics_tool.py
    │   └── report_tool.py
    ├── prompts/
    │   └── financial_report_prompt.py
    └── utils/
        └── config.py
```

## Setup

1. Create and activate a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file:

```bash
copy .env.example .env
```

4. Configure an LLM provider.

For OpenAI:

```env
OPENAI_API_KEY=your_openai_api_key_here
LLM_MODEL=gpt-4o-mini
LLM_BASE_URL=
DEBUG_PROVIDER=false
```

For DeepSeek:

```env
OPENAI_API_KEY=your_deepseek_api_key_here
LLM_MODEL=deepseek-chat
LLM_BASE_URL=https://api.deepseek.com
DEBUG_PROVIDER=false
```

By default, the Streamlit page does not display any API key prefix. For local troubleshooting only, set `DEBUG_PROVIDER=true` in `.env` to show provider debug details with a masked key prefix.

## Run

```bash
streamlit run app.py
```

Then open the local Streamlit URL shown in the terminal.

## Report Sections

The generated report includes:

- Company Overview
- Stock Performance
- Valuation
- Profitability
- Key Risks
- Research Summary
- Disclaimer

The prompt explicitly avoids direct investment recommendations such as buy, sell, or strong recommendation language.

## Future Improvements

- Add RAG over SEC filings, earnings transcripts, annual reports, and investor presentations
- Add a vector database such as Chroma, FAISS, or pgvector
- Add an Agent workflow with dedicated tools for market data, filings search, news search, and report generation
- Add citation-backed report sections with source links
- Add multi-company comparison and peer benchmarking
- Add historical financial statement charts
- Add caching with `st.cache_data` to reduce repeated API calls
- Add unit tests and CI checks
- Add Docker deployment

## Disclaimer

This project is for educational and research purposes only and does not constitute investment advice.
