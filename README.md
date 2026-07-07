# FinResearch Agent

FinResearch Agent is a Streamlit-based MVP for LLM-assisted equity research. A user can run a manual ticker-list market screener, review a ranked research watchlist, or analyze a single ticker such as `AAPL`, `MSFT`, or `NVDA`. The app fetches market and company data, calculates financial metrics, compares peers, and generates a structured research report with an OpenAI-compatible LLM.

This project is intentionally scoped as a portfolio-ready MVP. It does not include complex RAG, autonomous trading, portfolio execution, or real investment advice.

## Features

- Fetch historical stock prices with `yfinance`
- Fetch company profile, market metadata, and basic financial statements
- Calculate basic metrics including one-year return, annualized volatility, market cap, PE, PB, profit margin, ROE, revenue growth, and dividend yield
- Run a manual ticker-list market screener
- Generate a multi-factor research score for momentum, valuation, quality, risk, and liquidity
- Output a ranked research watchlist, not a stock recommendation or buy signal
- Compare the primary ticker with peers using market cap, valuation, profitability, ROE, and revenue growth metrics
- Visualize stock price history with Plotly
- Generate a structured LLM report with required research sections
- Support OpenAI or DeepSeek through an OpenAI-compatible API configuration
- Provide a fallback report only when no API key is configured
- Show safe provider information by default without exposing API key prefixes

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
|-- app.py
|-- requirements.txt
|-- README.md
|-- .env.example
`-- src/
    |-- tools/
    |   |-- market_data_tool.py
    |   |-- metrics_tool.py
    |   |-- peer_comparison_tool.py
    |   |-- scoring_tool.py
    |   |-- screener_tool.py
    |   `-- report_tool.py
    |-- prompts/
    |   `-- financial_report_prompt.py
    `-- utils/
        `-- config.py
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

## Market Screener

The V3 screener accepts a manual ticker list such as `AAPL,MSFT,NVDA,TSLA,GOOGL`. It fetches market and company data for each ticker, calculates a code-based multi-factor research score, and displays a ranked research watchlist.

Scoring factors:

- Momentum: one-year or six-month return
- Valuation: trailing PE, forward PE, and price to book
- Quality: profit margin, ROE, and revenue growth
- Risk: annualized volatility
- Liquidity: market cap

The LLM does not choose stocks and does not determine ranking. The ranking is produced by deterministic code-based scoring. LLM output is used only for explanatory research reports in the single-stock analysis section.

The watchlist is for research screening only and is not a buy/sell recommendation.

## Peer Comparison

The app supports peer comparison for valuation and profitability context. Users can enter peer tickers manually, such as `MSFT,GOOGL,NVDA`, or leave the field blank to use the built-in mapping:

- `AAPL`: `MSFT`, `GOOGL`, `AMZN`, `NVDA`
- `MSFT`: `AAPL`, `GOOGL`, `AMZN`, `ORCL`
- `NVDA`: `AMD`, `INTC`, `AVGO`, `QCOM`
- `TSLA`: `F`, `GM`, `RIVN`, `LCID`

The comparison table includes market cap, trailing PE, forward PE, price to book, profit margin, ROE, and revenue growth. Missing data is displayed as `N/A`.

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
- Add an Agent workflow with dedicated tools for market data, screening, scoring, filings search, news search, peer comparison, and report generation
- Add citation-backed report sections with source links
- Add multi-company comparison charts and peer benchmarking
- Add historical financial statement charts
- Add caching with `st.cache_data` to reduce repeated API calls
- Add unit tests and CI checks
- Add Docker deployment

## Disclaimer

This project is for educational and research purposes only and does not constitute investment advice.
