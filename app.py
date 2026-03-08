import streamlit as st
import requests
import yfinance as yf

# Page configuration
st.set_page_config(
    page_title="AI Financial Intelligence Agent",
    page_icon="📊",
    layout="wide"
)

# Title
st.title("📊 AI Financial Intelligence Agent Platform")
st.markdown("AI-powered stock analysis, sentiment insights, and market intelligence")

st.divider()

# Sidebar
st.sidebar.header("Stock Analyzer")

popular_stocks = [
    "AAPL",
    "TSLA",
    "MSFT",
    "GOOGL",
    "AMZN",
    "NVDA",
    "META",
    "RELIANCE.NS",
    "TCS.NS",
    "INFY.NS"
]

ticker = st.sidebar.selectbox("Choose Stock", popular_stocks)

analyze = st.sidebar.button("Analyze Stock")

# Layout columns
col1, col2 = st.columns(2)

if analyze:

    url = f"http://127.0.0.1:8000/report?ticker={ticker}"

    try:
        response = requests.get(url, proxies={"http": None, "https": None})

        if response.status_code == 200:
            data = response.json()

            # AI Summary
            st.subheader("🤖 AI Financial Summary")
            st.success(data.get("summary", "No summary available"))

            st.divider()

            # Stock Chart
            st.subheader("📈 Stock Price Chart")
            stock = yf.Ticker(ticker)
            hist = stock.history(period="6mo")

            if not hist.empty:
                st.line_chart(hist["Close"])
            else:
                st.warning("No stock data available")

            st.divider()

            with col1:
                st.subheader("📊 Stock Metrics")
                st.json(data.get("stock_metrics", {}))

            with col2:
                st.subheader("📰 News Sentiment")
                st.json(data.get("sentiment", {}))

        else:
            st.error(f"Backend Error: {response.status_code}")

    except Exception as e:
        st.error(f"Connection Error: {e}")