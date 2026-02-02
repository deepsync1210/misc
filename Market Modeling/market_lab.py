import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Market Lab 🔬")

st.title("🔬 The Market Lab: Interactive Trend Analysis")
st.markdown("Use this tool to visually compare assets and spot trends vs. the S&P 500.")

# --- 2. SIDEBAR (CONTROLS) ---
st.sidebar.header("⚙️ Configuration")

# Input: Tickers to Analyze
default_tickers = "NVDA, GOOGL, XLF, DAL, BTC-USD"
tickers_input = st.sidebar.text_input("Enter Tickers (comma separated)", default_tickers)
symbols = [x.strip().upper() for x in tickers_input.split(",")]
symbols.append("SPY") # Always add Benchmark

# Input: Time Range
time_period = st.sidebar.selectbox("Time Period", ["5d", "1mo", "3mo", "6mo", "1y", "ytd", "max"], index=1)

# Input: Chart Type
chart_type = st.sidebar.radio("Chart Style", ["Line Comparison", "Candlestick Deep Dive"])

# --- 3. DATA ENGINE ---
@st.cache_data
def load_data(symbols, period):
    data = yf.download(symbols, period=period, progress=False)['Close']
    return data.ffill() # Fix weekend gaps

if len(symbols) > 0:
    df = load_data(symbols, time_period)
    
    # Calculate % Growth from Day 1 of selected period (Normalized)
    df_normalized = df / df.iloc[0] * 100

    # --- 4. VISUALIZATION ---
    
    # A. RELATIVE PERFORMANCE CHART (Who is winning?)
    if chart_type == "Line Comparison":
        st.subheader(f"📈 Relative Performance ({time_period})")
        st.write("This chart normalizes all assets to start at 100. It shows pure % growth.")
        
        fig = px.line(df_normalized, x=df_normalized.index, y=df_normalized.columns, 
                      labels={"value": "Growth (Base=100)", "variable": "Asset"})
        st.plotly_chart(fig, use_container_width=True)

    # B. CANDLESTICK CHART (Technical Analysis)
    elif chart_type == "Candlestick Deep Dive":
        st.subheader("🕯️ Technical Deep Dive")
        selected_asset = st.sidebar.selectbox("Select Asset for Deep Dive", symbols)
        
        # Fetch OHLC Data for specific asset
        asset_data = yf.download(selected_asset, period=time_period, progress=False)
        
        fig = go.Figure()
        
        # Candlestick Trace
        fig.add_trace(go.Candlestick(x=asset_data.index,
                        open=asset_data['Open'],
                        high=asset_data['High'],
                        low=asset_data['Low'],
                        close=asset_data['Close'],
                        name='Price'))
        
        # Add 50-Day Moving Average (The "Trend Line")
        if len(asset_data) > 50:
            ma50 = asset_data['Close'].rolling(window=50).mean()
            fig.add_trace(go.Scatter(x=asset_data.index, y=ma50, 
                                     line=dict(color='orange', width=1), name='50-Day MA'))
            
        fig.update_layout(title=f"{selected_asset} Price Action", xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

    # --- 5. STATS SUMMARY ---
    st.subheader("📊 Performance Report")
    
    # Calculate total return over the period
    latest_price = df.iloc[-1]
    start_price = df.iloc[0]
    total_return = ((latest_price - start_price) / start_price) * 100
    
    # Create columns for metrics
    cols = st.columns(len(symbols))
    for i, sym in enumerate(symbols):
        val = total_return[sym]
        color = "normal"
        if val > 0: color = "normal" # Streamlit handles green automatically for + deltas
        
        cols[i].metric(label=sym, value=f"${latest_price[sym]:.2f}", delta=f"{val:.2f}%")

else:
    st.info("Please enter at least one ticker in the sidebar.")