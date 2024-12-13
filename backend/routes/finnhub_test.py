import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Function to fetch stock data for Nifty 50 and Sensex
def fetch_data(symbol, start_date, end_date):
    data = yf.download(symbol, start=start_date, end=end_date)
    return data

# Function to plot the stock data
def plot_stock_data(data, title, color='green'):
    plt.figure(figsize=(12, 6))
    plt.plot(data.index, data['Close'], color=color)
    plt.title(title)
    plt.xlabel('Date')
    plt.ylabel('Closing Price')
    plt.grid(True)
    plt.show()

# Function to fetch top performing stocks (from a predefined list)
def fetch_top_stocks():
    symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA', 'JPM', 'V']
    top_stocks = {}
    
    for symbol in symbols:
        stock_data = yf.Ticker(symbol)
        hist_data = stock_data.history(period='1d', start="2023-01-01", end="2023-12-31")
        top_stocks[symbol] = hist_data['Close'].iloc[-1]  # Latest closing price

    # Sort stocks by the latest closing price
    sorted_top_stocks = sorted(top_stocks.items(), key=lambda x: x[1], reverse=True)
    return sorted_top_stocks

# Main function to get data and plot
def main():
    # Fetch Nifty 50 and Sensex data
    nifty_data = fetch_data('^NSEI', '2023-01-01', '2023-12-31')
    sensex_data = fetch_data('^BSESN', '2023-01-01', '2023-12-31')

    # Plot Nifty 50 and Sensex data
    plot_stock_data(nifty_data, 'Nifty 50 Closing Price')
    plot_stock_data(sensex_data, 'Sensex Closing Price', color='blue')

    # Fetch and display top performing stocks
    top_stocks = fetch_top_stocks()
    print("Top Performing Stocks:")
    for stock, price in top_stocks:
        print(f"{stock}: ₹{price}")

if __name__ == "__main__":
    main()
