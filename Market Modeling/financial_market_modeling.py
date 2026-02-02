import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# --- 1. CONFIGURATION ---
# Our current holdings + Watchlist
tickers = {
    "Portfolio_Bull": ["GOOG"],         # We hold this
    "Portfolio_Bear": ["XLF", "XLE", "SGOV"], # We hold these
    "Watchlist": ["NVDA", "SOL-USD", "DAL", "JPM", "LMT"] # DAL=Delta (Earnings Tue), LMT=Defense (Geopolitics)
}

# Flatten list for fetching
all_symbols = [item for sublist in tickers.values() for item in sublist]
all_symbols.append("SPY") # Benchmark

# --- 2. GET DATA ---
print("📡 Fetching data from Yahoo Finance...")
data = yf.download(all_symbols, period="5d", interval="1d", progress=False)['Close']

# [NEW LINE] Fill weekend gaps so stocks have a valid "previous" price
data = data.ffill()

# --- 3. ANALYSIS LOGIC ---
def analyze_market(data):
    latest_prices = data.iloc[-1]
    prev_prices = data.iloc[-2]
    
    # Calculate % Change
    pct_change = ((latest_prices - prev_prices) / prev_prices) * 100
    
    # Calculate "Relative Strength" vs SPY (Benchmark)
    spy_perf = pct_change['SPY']
    rel_strength = pct_change - spy_perf
    
    # Create Summary DataFrame
    summary = pd.DataFrame({
        'Price ($)': latest_prices.round(2),
        'Day %': pct_change.round(2),
        'Rel Strength': rel_strength.round(2)
    })
    
    return summary.sort_values(by='Rel Strength', ascending=False)

# --- 4. EXECUTION ---
try:
    report = analyze_market(data)
    print("\n📊 MONDAY PRE-MARKET SCANNER")
    print("-" * 40)
    print(report)
    print("-" * 40)
    print(f"📉 SPY Benchmark Move: {report.loc['SPY', 'Day %']}%")
    
except Exception as e:
    print(f"Error: {e}")