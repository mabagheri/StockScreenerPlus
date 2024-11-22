import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd

# List of top 100 US stocks
top_100_stocks = [
    "AAPL", "MSFT"]

@st.cache_data
def fetch_stock_data(tickers):
    """ Fetch stock data for the given tickers."""
    data = []
    for ticker in tickers:
        stock = yf.Ticker(ticker)
        info = stock.info
        history = stock.history(period="1mo")
        
        # Extract desired metrics
        data.append({
            " ": ticker,
            "MarCap (B)": np.round((info.get("marketCap") / 1e9), 2) if info.get("marketCap") else None,
            # "Price": info.get("regularMarketPrice"),
            "Price": stock.history(period='1d')['Close'][0],
            # "Chg (%)": info.get("regularMarketChangePercent"),
            "Volume": info.get("regularMarketVolume"),
            "EPS": info.get("trailingEps"),
            # "1M Perf (%)": ((history['Close'][-1] / history['Close'][0]) - 1) * 100 if len(history) > 0 else None
        })

    st.write(stock.history(period='1d'))
    return pd.DataFrame(data)

# Fetch data (cached)
df = fetch_stock_data(top_100_stocks)
# df = pd.DataFrame({'num_legs': [2, 4, 8, 0],
#                     'num_wings': [2, 0, 0, 0],
#                     'num_specimen_seen': [10, 2, 1, 8]},
#                    index=['falcon', 'dog', 'spider', 'fish'])

# Streamlit app
st.title("Top 100 US Stocks by Market Capitalization")
st.write("Sortable table with metrics:")
st.dataframe(df, use_container_width=True)
