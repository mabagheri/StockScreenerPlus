import streamlit as st
import pandas as pd
import yfinance as yf
import os
from datetime import datetime, timedelta

DATA_FOLDER = "data"

# Helper function to check if the market is open
def is_market_open():
    now = datetime.now()
    market_open_time = now.replace(hour=9, minute=30, second=0, microsecond=0)
    market_close_time = now.replace(hour=16, minute=0, second=0, microsecond=0)
    return market_open_time <= now <= market_close_time

# Function to fetch company metadata, including logo, market cap, sector, and analyst rating
def get_stock_metadata_with_logo(ticker, updated_data):
    try:
        ticker_data = updated_data[updated_data['Ticker'] == ticker]
        if ticker_data.empty:
            return {
                "Logo": None,
                "Company": "N/A",
                "Market Cap": "N/A",
                "Sector": "N/A",
                "EPS": "N/A",
                "Current Price": "N/A",
                "Percentage Change (%)": "N/A",
                "1Y Decrease (%)": "N/A",
                "90D Decrease (%)": "N/A",
                "Analyst Rating": "N/A",
            }

        current_price = ticker_data['Close'].iloc[-1]
        highest_1y = ticker_data[ticker_data['Date'] >= (datetime.now().date() - timedelta(days=365))]['High'].max()
        highest_90d = ticker_data[ticker_data['Date'] >= (datetime.now().date() - timedelta(days=90))]['High'].max()
        previous_close = ticker_data['Close'].iloc[-2] if len(ticker_data) > 1 else None
        percentage_change = (
            ((current_price - previous_close) / previous_close) * 100 if previous_close else "N/A"
        )
        decrease_1y = (
            ((highest_1y - current_price) / highest_1y) * 100 if highest_1y else "N/A"
        )
        decrease_90d = (
            ((highest_90d - current_price) / highest_90d) * 100 if highest_90d else "N/A"
        )

        stock = yf.Ticker(ticker)
        info = stock.info
        company_name = info.get("shortName", ticker)
        market_cap = info.get("marketCap", "N/A")
        sector = info.get("sector", "N/A")
        logo_url = info.get("logo_url", None)
        eps = info.get("trailingEps", "N/A")
        analyst_rating = info.get("recommendationKey", "N/A")

        return {
            "Logo": logo_url,
            "Company": company_name,
            "Market Cap": market_cap,
            "Sector": sector,
            "EPS": eps,
            "Current Price": current_price,
            "Percentage Change (%)": percentage_change,
            "1Y Decrease (%)": decrease_1y,
            "90D Decrease (%)": decrease_90d,
            "Analyst Rating": analyst_rating,
        }
    except Exception:
        return {
            "Logo": None,
            "Company": "N/A",
            "Market Cap": "N/A",
            "Sector": "N/A",
            "EPS": "N/A",
            "Current Price": "N/A",
            "Percentage Change (%)": "N/A",
            "1Y Decrease (%)": "N/A",
            "90D Decrease (%)": "N/A",
            "Analyst Rating": "N/A",
        }

# Main function to update stock data and generate metadata table
def update_stock_data_with_metadata(region, new_tickers=None):
    log = []
    summary_data = {}
    market_open = is_market_open()
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)

    region_folder = os.path.join(DATA_FOLDER, region)
    if not os.path.exists(region_folder):
        os.makedirs(region_folder)

    existing_csv_files = [f for f in os.listdir(region_folder) if f.endswith('.csv')]
    existing_tickers = [file.replace(".csv", "") for file in existing_csv_files]

    all_updated_data = []

    # Update existing stocks
    for csv_file in existing_csv_files:
        file_path = os.path.join(region_folder, csv_file)
        ticker = csv_file.replace(".csv", "")

        existing_data = pd.read_csv(file_path)
        last_date = pd.to_datetime(existing_data['Date']).max().date()

        stock_data = yf.download(ticker, start=last_date + timedelta(days=1), progress=False)
        if stock_data.empty:
            log.append(f"No new data for {ticker} in {region}.")
            continue

        stock_data.reset_index(inplace=True)
        stock_data = stock_data[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
        stock_data['Date'] = pd.to_datetime(stock_data['Date']).dt.date
        stock_data['Ticker'] = ticker

        updated_data = pd.concat([existing_data, stock_data]).drop_duplicates(subset='Date').sort_values('Date')

        if market_open:
            save_data = updated_data[updated_data['Date'] <= yesterday]
        else:
            save_data = updated_data

        save_data.to_csv(file_path, index=False)
        all_updated_data.append(updated_data)

    # Add new tickers if provided
    if new_tickers:
        for ticker in new_tickers:
            if ticker in existing_tickers:
                log.append(f"{ticker} already exists in {region}. Skipping...")
                continue

            stock_data = yf.download(ticker, period="5y", progress=False)
            if stock_data.empty:
                log.append(f"Failed to fetch data for {ticker}. Skipping...")
                continue

            stock_data.reset_index(inplace=True)
            stock_data = stock_data[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
            stock_data['Date'] = pd.to_datetime(stock_data['Date']).dt.date
            stock_data['Ticker'] = ticker

            if market_open:
                save_data = stock_data[stock_data['Date'] <= yesterday]
            else:
                save_data = stock_data

            save_data.to_csv(os.path.join(region_folder, f"{ticker}.csv"), index=False)
            all_updated_data.append(stock_data)

    combined_data = pd.concat(all_updated_data, ignore_index=True)

    tickers = combined_data['Ticker'].unique()
    for ticker in tickers:
        stock_metadata = get_stock_metadata_with_logo(ticker, combined_data)
        summary_data[ticker] = stock_metadata

    summary_df = pd.DataFrame.from_dict(summary_data, orient='index')
    return log, summary_df

# Streamlit App
st.sidebar.title("Stock Data Updater")
region = st.sidebar.selectbox(
    "Select Region",
    ["US", "Canada"]
)

new_tickers_input = st.sidebar.text_area(
    "Optionally Enter New Stocks (comma-separated, e.g., AAPL, TSLA, GOOG):"
)

if st.sidebar.button(f"Update {region} Stock Data"):
    new_tickers = [ticker.strip().upper() for ticker in new_tickers_input.split(",") if ticker.strip()] if new_tickers_input else None
    with st.spinner(f"Updating stock data for {region}..."):
        log, summary_df = update_stock_data_with_metadata(region, new_tickers)
    st.success(f"Update complete for {region}!")
    st.text_area("Logs", "\n".join(log))

    if not summary_df.empty:
        st.subheader(f"{region} Stock Summary")
        st.dataframe(summary_df)
