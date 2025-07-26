import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta

# Streamlit app title
st.title("Stock RS Analysis Dashboard")

# Sidebar for user inputs
st.sidebar.header("Input Parameters")
ticker = st.sidebar.text_input("Enter Stock Ticker", value="UBER")
start_date = st.sidebar.date_input("Start Date", value=datetime(2024, 7, 1))
end_date = st.sidebar.date_input("End Date", value=datetime(2025, 7, 25))
lookback = st.sidebar.slider("Lookback Period for Percent Rank", min_value=50, max_value=200, value=100)

# Function to calculate RS metrics
def calculate_rs_and_rank(df, lookback=100):
    try:
        df['ThreeMthRS'] = 0.4 * (df['Close'] / df['Close'].shift(63))
        df['SixMthRS'] = 0.2 * (df['Close'] / df['Close'].shift(126))
        df['NineMthRS'] = 0.2 * (df['Close'] / df['Close'].shift(189))
        df['TwelveMthRS'] = 0.2 * (df['Close'] / df['Close'].shift(250))
        
        df['RSraw'] = df[['ThreeMthRS', 'SixMthRS', 'NineMthRS', 'TwelveMthRS']].sum(axis=1)
        
        df['PercentRank'] = df['Close'].rolling(window=lookback).apply(
            lambda x: pd.Series(x).rank(pct=True).iloc[-1] * 100, raw=True
        )
        
        df['Color_HSB'] = df['PercentRank'].apply(lambda x: (x * 64 / 100, 255, 255))
        
        return df
    except Exception as e:
        st.error(f"Error in RS calculation: {e}")
        return None

# Fetch data and process when the user clicks a button
if st.button("Run Analysis"):
    try:
        # Fetch data from Yahoo Finance
        # Adjust start date to ensure enough data for 250-day lookback
        adjusted_start_date = start_date - timedelta(days=365)  # Add buffer for lookback
        df = yf.download(ticker, start=adjusted_start_date, end=end_date, progress=False)
        if df.empty:
            st.error("No data found for the ticker or date range. Please try again.")
        else:
            df = df[['Close', 'Volume']].copy()
            df.reset_index(inplace=True)
            df.set_index('Date', inplace=True)

            # Filter data to user-specified date range
            df = df.loc[start_date:end_date]

            # Calculate RS metrics
            result = calculate_rs_and_rank(df, lookback=lookback)
            if result is not None:
                output = result[['Close', 'Volume', 'RSraw', 'PercentRank']].dropna()

                # Display results
                st.subheader(f"Analysis for {ticker}")
                st.write("Last 5 rows of the data:")
                st.dataframe(output.tail(), use_container_width=True)

                # Plot closing prices
                st.subheader("Closing Price Trend")
                st.line_chart(output['Close'])

                # Provide Excel download option
                st.subheader("Download Results")
                # Use BytesIO for in-memory Excel file to avoid file system issues
                from io import BytesIO
                excel_buffer = pd.ExcelWriter(BytesIO(), engine='openpyxl')
                output.to_excel(excel_buffer, sheet_name=f'{ticker} Data', index=True)
                excel_data = excel_buffer.getvalue()
                st.download_button(
                    label="Download Excel File",
                    data=excel_data,
                    file_name=f"{ticker}_RS_Analysis.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
    except Exception as e:
        st.error(f"An error occurred: {e}")

# Note about trading days
st.sidebar.write(f"Note: There are approximately 270 trading days between {start_date} and {end_date}.")
