import streamlit as st
import yfinance as yf
import pandas as pd

# Example stock lists for the two regions
us_stocks = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "BRK-B", "V", "JNJ",
    "WMT", "JPM", "XOM", "MA", "PG", "LLY", "UNH", "HD", "CVX", "ABBV",
]
canadian_stocks = [
    "RY.TO", "TD.TO", "BNS.TO", "SHOP.TO", "ENB.TO", "CNR.TO", "BAM.TO", "CNQ.TO", 
    "TRP.TO", "MFC.TO", "BCE.TO", "CM.TO", "SU.TO", "FTS.TO", "FNV.TO",
]

@st.cache_data
def fetch_stock_data(tickers):
    """Fetch stock data for the given tickers."""
    data = []
    for ticker in tickers:
        stock = yf.Ticker(ticker)
        info = stock.info
        history = stock.history(period="1mo")
        
        # Extract metrics
        data.append({
            "Logo": info.get("logo_url"),
            "Ticker": ticker,
            "Company Name": info.get("shortName"),
            "Market Cap": info.get("marketCap"),
            "Price": info.get("regularMarketPrice"),
            "One Day Change (%)": info.get("regularMarketChangePercent"),
            "Volume": info.get("regularMarketVolume"),
            "EPS": info.get("trailingEps"),
            "One Month Performance (%)": ((history['Close'][-1] / history['Close'][0]) - 1) * 100 if len(history) > 0 else None
        })
    
    return pd.DataFrame(data)

# Sidebar: Filters
st.sidebar.title("Filters")

# Region Selection
region = st.sidebar.radio("Select Region", ["US", "Canada"])

# Select the appropriate stock list based on region
stock_list = us_stocks if region == "US" else canadian_stocks

# Number of top stocks to display
n = st.sidebar.slider("Number of Top Stocks by Market Cap", min_value=1, max_value=100, value=10)

# Fetch stock data
df = fetch_stock_data(stock_list)

# Filter: Sort by Market Cap and select top n stocks
df = df.sort_values(by="Market Cap", ascending=False).head(n)

# Add logo images as clickable links
df["Logo"] = df["Logo"].apply(lambda url: f'<img src="{url}" width="30">' if url else "No Logo")

# Main App
st.title("Top Stocks by Market Capitalization")
st.write(f"Showing top {n} stocks in the {region} region:")

# Display DataFrame
st.write(df.to_html(escape=False, index=False), unsafe_allow_html=True)
