import streamlit as st
import pandas as pd
import yfinance as yf
import os
from datetime import datetime, timedelta

DATA_FOLDER = "Data"

st.write(1)
# Helper function to check if the market is open
def is_market_open():
    now = datetime.now()
    market_open_time = now.replace(hour=9, minute=30, second=0, microsecond=0)
    market_close_time = now.replace(hour=16, minute=0, second=0, microsecond=0)
    return market_open_time <= now <= market_close_time

# Function to fetch company metadata, including logo, market cap, sector, and analyst rating
def get_stock_metadata_with_logo(ticker, ticker_data):
    try:
        st.write(ticker, "ticker_data", ticker_data.head(2))
        # ticker_data = updated_data[updated_data['Ticker'] == ticker]
        if ticker_data.empty:
            st.write(23)
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

        stock = yf.Ticker("AAPL")
        info = stock.info
        st.write(53)
        st.write(type(info))
        st.write((info))
        company_name = 'test' # info.get("shortName", ticker)
        st.write(type(info))
        st.write(56)
        market_cap = info['marketCap'] # .get("marketCap", "market cap")
        st.write(57)
        sector = info.get("sector", "Sector")
        logo_url = info.get("logo_url", None)
        st.write(60)
        eps = info.get("trailingEps", " eps ")
        st.write(62)
        analyst_rating = info.get("recommendationKey", "N/A")
        st.write(62)

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
    st.write(region_folder)
    if not os.path.exists(region_folder):
        os.makedirs(region_folder)
    
    existing_csv_files = [f for f in os.listdir(region_folder) if f.endswith('.csv')]
    existing_tickers = [file.replace(".csv", "") for file in existing_csv_files]

    all_updated_data = []
    st.write(existing_csv_files)
    tickers = [csv_file.replace(".csv", "") for csv_file in existing_csv_files]
    
    # Update existing stocks
    for csv_file in existing_csv_files:
        file_path = os.path.join(region_folder, csv_file)
        ticker = csv_file.replace(".csv", "")

        existing_data = pd.read_csv(file_path)
        existing_data['Date'] = pd.to_datetime(existing_data['Date']).dt.date        

        last_date = pd.to_datetime(existing_data['Date']).max().date()
        
        stock_data = yf.download(ticker, start=last_date, progress=False, interval='1d')
        # st.write(stock_data.shape)
        if stock_data.empty:
            log.append(f"No new data for {ticker} in {region}.")
            continue
       
        stock_data.reset_index(inplace=True)
        stock_data = stock_data[['Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']]        
        stock_data['Date'] = pd.to_datetime(stock_data['Date']).dt.date        
        # stock_data['Ticker'] = ticker
        
        # st.write("stock data:")
        # st.dataframe(stock_data.head(2))

        # st.write("existing_data:")
        # st.dataframe(existing_data.head(2))
        # st.write(set(stock_data.columns) - set(existing_data.columns))

        updated_data = pd.concat([existing_data, stock_data], ignore_index=True).drop_duplicates(subset='Date').sort_values('Date')
        st.write("updated_data:")
        st.dataframe(updated_data.head(1))
        st.dataframe(updated_data.tail(1))
        if market_open:
            save_data = updated_data[updated_data['Date'] <= yesterday]
        else:
            save_data = updated_data

        # save_data.to_csv(file_path, index=False)
        all_updated_data.append(updated_data)

        stock_metadata = get_stock_metadata_with_logo(ticker, updated_data)
        st.write(stock_metadata)
        summary_data[ticker] = stock_metadata

    combined_data = pd.concat(all_updated_data, ignore_index=True)
    st.write("combined_data.shape",combined_data.head(2))
    # tickers = combined_data['Ticker'].unique()
    # st.write("tickers", tickers)
    
    # for ticker in tickers:
    #     stock_metadata = get_stock_metadata_with_logo(ticker, combined_data)
    #     st.write(stock_metadata)
    #     summary_data[ticker] = stock_metadata

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
