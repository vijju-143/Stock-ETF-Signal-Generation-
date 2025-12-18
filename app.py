import streamlit as st
import yfinance as yf
from ta.momentum import RSIIndicator
import matplotlib.pyplot as plt
import pandas as pd

# ----------------------------
# Page configuration
# ----------------------------
st.set_page_config(
    page_title="Stock & ETF Signal Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------
# Sidebar
# ----------------------------
st.sidebar.header("Stock / ETF Signal Generator")
symbol = st.sidebar.text_input("Enter Stock / ETF Symbol", "AAPL")
period = st.sidebar.selectbox("Select Period", ["3mo", "6mo", "1y", "2y"], index=1)

# ----------------------------
# Main Page
# ----------------------------
st.title("📈 Stock & ETF Signal Dashboard")

if st.sidebar.button("Generate Signal"):

    # Fetch data
    data = yf.download(symbol, period=period)

    if data.empty:
        st.error("No data found. Check the symbol.")
    else:
        # Flatten multi-level columns if any
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        # Moving averages
        data['SMA20'] = data['Close'].rolling(20).mean()
        data['SMA50'] = data['Close'].rolling(50).mean()

        # Drop NaNs
        data.dropna(inplace=True)

        # RSI
        rsi = RSIIndicator(data['Close'])
        data['RSI'] = rsi.rsi()

        # Determine trading signal
        signal = "HOLD"
        if data['SMA20'].iloc[-1] > data['SMA50'].iloc[-1] and data['RSI'].iloc[-1] < 70:
            signal = "BUY"
        elif data['SMA20'].iloc[-1] < data['SMA50'].iloc[-1] and data['RSI'].iloc[-1] > 30:
            signal = "SELL"

        # Display signal
        st.markdown(f"### 🔹 Latest Signal: **{signal}**")

        # ----------------------------
        # Line chart using matplotlib
        # ----------------------------
        plt.figure(figsize=(12,6))
        plt.plot(data['Close'], label='Close', color='blue')
        plt.plot(data['SMA20'], label='SMA20', color='orange')
        plt.plot(data['SMA50'], label='SMA50', color='green')
        plt.title(f"{symbol} Price & Moving Averages")
        plt.xlabel("Date")
        plt.ylabel("Price")
        plt.legend()
        plt.grid(True)

        st.pyplot(plt)

        # ----------------------------
        # RSI chart
        # ----------------------------
        plt.figure(figsize=(12,3))
        plt.plot(data['RSI'], label='RSI', color='purple')
        plt.axhline(70, color='red', linestyle='--', label='Overbought (70)')
        plt.axhline(30, color='green', linestyle='--', label='Oversold (30)')
        plt.title(f"{symbol} RSI Indicator")
        plt.xlabel("Date")
        plt.ylabel("RSI")
        plt.legend()
        plt.grid(True)

        st.pyplot(plt)

        # ----------------------------
        # Show data table
        # ----------------------------
        st.markdown("### Recent Data")
        st.dataframe(data.tail(10))
