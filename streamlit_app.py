import streamlit as st
import yfinance as yf
import pandas as pd

# List of top 100 US stocks
top_100_stocks = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "BRK-B", "V", "JNJ",
    "WMT", "JPM", "XOM", "MA", "PG", "LLY", "UNH", "HD", "CVX", "ABBV",
    # Add more tickers here...
]

@st.cache_data
def fetch_stock_data(tickers):
    """Fetch stock data for the given tickers."""
    data = []
    for ticker in tickers:
        stock = yf.Ticker(ticker)
        info = stock.info
        history = stock.history(period="1mo")
        
        # Extract desired metrics
        data.append({
            "Ticker": ticker,
            "Market Cap": info.get("marketCap"),
            "Price": info.get("regularMarketPrice"),
            "One Day Change (%)": info.get("regularMarketChangePercent"),
            "Volume": info.get("regularMarketVolume"),
            "EPS": info.get("trailingEps"),
            "One Month Performance (%)": ((history['Close'][-1] / history['Close'][0]) - 1) * 100 if len(history) > 0 else None
        })
    
    return pd.DataFrame(data)

# Fetch data (cached)
df = fetch_stock_data(top_100_stocks)

# Streamlit app
st.title("Top 100 US Stocks by Market Capitalization")
st.write("Sortable table with metrics:")
st.dataframe(df, use_container_width=True)
