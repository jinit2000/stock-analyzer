import tkinter as tk
from tkinter import ttk, messagebox
import yfinance as yf
import pandas as pd
import numpy as np
import ta

# Fetch historical stock data from Yahoo Finance
def fetch_stock_data(ticker):
    stock = yf.Ticker(ticker)
    df = stock.history(period='12mo', interval='1d')
    df.dropna(inplace=True)
    return df

# Calculate technical indicators: RSI, 50-day SMA, and 200-day SMA
def calculate_technical_indicators(df):
    df['RSI'] = ta.momentum.RSIIndicator(df['Close'], window=14).rsi()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    df['SMA_200'] = df['Close'].rolling(window=200).mean()
    return df

# Calculate pivot point-based support and resistance using recent 10 days
def calculate_pivot_support_resistance(df):
    recent_data = df.tail(10)
    high = recent_data['High'].max()
    low = recent_data['Low'].min()
    close = recent_data['Close'].iloc[-1]

    pivot = (high + low + close) / 3
    support = (2 * pivot) - high
    resistance = (2 * pivot) - low

    return round(support, 2), round(resistance, 2)

# Get fundamental data like P/E, EPS, and ROE from Yahoo Finance
def fundamental_summary(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info
    return {
        'P/E Ratio': info.get('trailingPE', 'N/A'),
        'EPS': info.get('trailingEps', 'N/A'),
        'ROE': info.get('returnOnEquity', 'N/A')
    }

# Generate a recommendation by combining technicals and fundamentals
def give_combined_recommendation(df, support, resistance, fundamentals):
    current_price = df['Close'].iloc[-1]
    rsi = df['RSI'].iloc[-1]
    sma_50 = df['SMA_50'].iloc[-1]
    sma_200 = df['SMA_200'].iloc[-1] if 'SMA_200' in df.columns else None

    pe = fundamentals.get('P/E Ratio', 0)
    eps = fundamentals.get('EPS', 0)
    roe = fundamentals.get('ROE', 0)

    score = 0
    reasons = []

    # RSI logic: oversold = buy, overbought = sell
    if rsi < 40:
        score += 2
        reasons.append("RSI < 40 (oversold)")
    elif rsi > 70:
        score -= 2
        reasons.append("RSI > 70 (overbought)")

    # Check proximity to support/resistance using small buffer
    buffer = 0.5
    if current_price <= support * (1 + buffer / 100):
        score += 1
        reasons.append("Price near support")
    elif current_price >= resistance * (1 - buffer / 100):
        score -= 1
        reasons.append("Price near resistance")
    else:
        reasons.append("Price between support and resistance")

    # Bonus points for breaking above resistance
    if current_price > resistance:
        score += 2
        reasons.append("Price broke above resistance (bullish breakout)")

    # Check if price is above 50-day SMA (trend strength)
    if current_price > sma_50:
        score += 1
        reasons.append("Price above 50-day SMA")

    # Short-term trend over the last 10 days
    if len(df) >= 10:
        recent_diff = df['Close'].iloc[-1] - df['Close'].iloc[-10]
        if recent_diff > 0:
            score += 1
            reasons.append("Uptrend in past 10 days")

    # Check golden cross 
    if not pd.isna(sma_200):
        if sma_50 > sma_200:
            score += 2
            reasons.append("SMA 50 > 200 (Uptrend)")
        elif sma_50 < sma_200:
            score -= 2
            reasons.append("SMA 50 < 200 (Downtrend)")
    else:
        reasons.append("⚠️ Not enough data for SMA 200")

    # Evaluate fundamental metrics
    if isinstance(pe, (int, float)):
        if pe < 30:
            score += 1
            reasons.append("P/E < 30")
        elif pe > 50:
            score -= 1
            reasons.append("P/E > 50")

    if isinstance(eps, (int, float)) and eps > 5:
        score += 1
        reasons.append("EPS > 5")

    if isinstance(roe, (int, float)) and roe > 0.2:
        score += 1
        reasons.append("ROE > 20%")

    # Final recommendation based on total score
    if score >= 4:
        rec = "STRONG BUY"
    elif score >= 2:
        rec = "BUY"
    elif score >= 0:
        rec = "HOLD"
    else:
        rec = "SELL"

    # Investment horizon statement
    if isinstance(pe, (int, float)) and pe < 30 and isinstance(roe, (int, float)) and roe > 0.2 and isinstance(eps, (int, float)) and eps > 5:
        horizon = "This stock is suitable for long-term investment based on strong fundamentals."
    elif rsi < 50 and current_price > sma_50:
        horizon = "This stock may be good for short-term trading due to technical momentum."
    elif score >= 4:
        horizon = "This stock is strong for both short-term and long-term holding."
    else:
        horizon = "Investment horizon is unclear; further news or breakout confirmation needed."

    return rec, score, reasons, horizon

# Main function triggered by the GUI button
def analyze_stock():
    ticker = ticker_entry.get().strip().upper()
    if not ticker:
        messagebox.showwarning("Input Error", "Please enter a stock ticker.")
        return

    try:
        # Run all steps of the analysis
        df = fetch_stock_data(ticker)
        df = calculate_technical_indicators(df)
        support, resistance = calculate_pivot_support_resistance(df)
        fundamentals = fundamental_summary(ticker)
        rec, score, reasons, horizon = give_combined_recommendation(df, support, resistance, fundamentals)

        # Extract latest values for display
        current_price = df['Close'].iloc[-1]
        rsi = df['RSI'].iloc[-1]
        sma_50 = df['SMA_50'].iloc[-1]
        sma_200 = df['SMA_200'].iloc[-1] if not pd.isna(df['SMA_200'].iloc[-1]) else "N/A"

        # Format the output summary
        output = f"""--- Analysis for {ticker} ---
Current Price: ${current_price:.2f}
Support Level: ${support}
Resistance Level: ${resistance}
RSI: {rsi:.2f}
50-Day SMA: ${sma_50:.2f}
200-Day SMA: {sma_200:.2f}

--- Fundamental Summary ---
P/E Ratio: {fundamentals['P/E Ratio']}
EPS: {fundamentals['EPS']}
ROE: {fundamentals['ROE']}

✅ Final Recommendation: {rec}
📊 Score: {score}
📌 Reasons:"""

        # Add all reason lines
        for r in reasons:
            output += f"\n - {r}"

        # Final horizon and disclaimer
        output += f"\n\n🧭 {horizon}"
        output += f"\n\n⚠️ Always invest based on your own research and risk tolerance."

        # Display output in the text widget
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, output)

    except Exception as e:
        messagebox.showerror("Error", f"Something went wrong:\n{e}")

# GUI setup starts here
root = tk.Tk()
root.title("Stock Buy/Sell Analyzer")
root.geometry("700x600")
root.resizable(False, False)

frame = ttk.Frame(root, padding=20)
frame.pack(fill='both', expand=True)

title = ttk.Label(frame, text="Stock Analyzer", font=("Helvetica", 18, "bold"))
title.pack(pady=10)

ticker_label = ttk.Label(frame, text="Enter Stock Ticker:")
ticker_label.pack()

ticker_entry = ttk.Entry(frame, width=20)
ticker_entry.pack(pady=5)

analyze_button = ttk.Button(frame, text="Analyze", command=analyze_stock)
analyze_button.pack(pady=10)

result_text = tk.Text(frame, height=25, wrap='word', font=('Courier', 10))
result_text.pack(fill='both', expand=True)

# Run the GUI
root.mainloop()
