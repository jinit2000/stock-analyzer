# Stock Analyzer

This is a simple Python application that helps analyze stock performance using both technical indicators and basic fundamental data. It comes with a basic graphical user interface (GUI) built using Tkinter, so anyone can enter a stock symbol and get an instant summary.

---

## What It Does

The tool pulls live stock data from Yahoo Finance and calculates:
- RSI (Relative Strength Index)
- 50-day and 200-day moving averages
- Pivot-based support and resistance levels

It also collects a few key metrics like:
- P/E Ratio
- Earnings per Share (EPS)
- Return on Equity (ROE)

Based on this data, it gives a buy/sell recommendation along with a short explanation of why.

---

## How to Use It

1. **Install the required libraries**:

   ```bash
   pip install yfinance, pandas, numpy, ta, tkinter

2. **Run the script:**:

   ```bash
   python stock_analyzer.py

3. **A small window will open. Just type in a stock ticker like AAPL, TSLA, or MSFT and click Analyze.**:


