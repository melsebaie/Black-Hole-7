import yfinance as yf
import pandas as pd
import ta

def get_macd_status(df):
    close_prices = df['Close'].squeeze()
    macd_line = ta.trend.macd(close_prices)
    signal_line = ta.trend.macd_signal(close_prices)

    cross_up = (macd_line > signal_line) & (macd_line.shift(1) <= signal_line.shift(1))
    cross_down = (macd_line < signal_line) & (macd_line.shift(1) >= signal_line.shift(1))

    latest_macd = macd_line.iloc[-1]
    latest_signal = signal_line.iloc[-1]
    status = "Neutral"

    if cross_up.iloc[-1]:
        status = "P+.Cross Over"
    elif cross_down.iloc[-1]:
        status = "N-.Cross Over"
    elif latest_macd >= latest_signal:
        status = "Up"
    elif latest_signal > latest_macd:
        status = "Down"

    return latest_macd, latest_signal, status

# Load AAPL data for at least 17 years (covers quarterly calculation)
symbol = "AAPL"
raw_data = yf.download(symbol, period="17y", interval="1d")

# Resample dataframes
daily_df = raw_data.copy()
weekly_df = raw_data.resample("W").last()
monthly_df = raw_data.resample("ME").last()
quarterly_df = raw_data.resample("QE").last()

# Extract MACD status per timeframe
macd_d, signal_d, status_d = get_macd_status(daily_df)
macd_w, signal_w, status_w = get_macd_status(weekly_df)
macd_m, signal_m, status_m = get_macd_status(monthly_df)
macd_q, signal_q, status_q = get_macd_status(quarterly_df)

# Calculate MACDTotal and MACDCount
macdtot = (
    (1 if macd_d >= signal_d else 0) +
    (10 if macd_w >= signal_w else 0) +
    (100 if macd_m >= signal_m else 0) +
    (1000 if macd_q >= signal_q else 0)
)

macdcont = sum([
    1 if macd_d >= signal_d else 0,
    1 if macd_w >= signal_w else 0,
    1 if macd_m >= signal_m else 0,
    1 if macd_q >= signal_q else 0
])

# Display Output
print(f"\n📊 MACD Signal Summary for {symbol} (Last Trading Session)")
print(f"📅 Daily     : {status_d}")
print(f"📈 Weekly    : {status_w}")
print(f"📆 Monthly   : {status_m}")
print(f"🗓️ Quarterly : {status_q}")
print(f"\n📊 MACDTotal : {macdtot}")
print(f"📈 MACDCount : {macdcont}")