import yfinance as yf
from flask import Blueprint, jsonify
import pandas as pd

# Create a Blueprint for market routes
market_bp = Blueprint('market_bp', __name__)

# Function to fetch stock data for Nifty 50 and Sensex
def fetch_data(symbol, start_date, end_date):
    try:
        data = yf.download(symbol, start=start_date, end=end_date)
        if data.empty:
            raise ValueError(f"No data returned for {symbol}")
        return data
    except Exception as e:
        print(f"Error fetching data for {symbol}: {str(e)}")
        raise

# Function to fetch top performing stocks (from a predefined list)
def fetch_top_stocks():
    symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA', 'JPM', 'V']
    top_stocks = {}
    
    for symbol in symbols:
        try:
            stock_data = yf.Ticker(symbol)
            hist_data = stock_data.history(period='1d', start="2023-01-01", end="2023-12-31")
            if hist_data.empty:
                raise ValueError(f"No data returned for {symbol}")
            top_stocks[symbol] = hist_data['Close'].iloc[-1]  # Latest closing price
        except Exception as e:
            print(f"Error fetching data for {symbol}: {str(e)}")
            continue

    # Sort stocks by the latest closing price
    sorted_top_stocks = sorted(top_stocks.items(), key=lambda x: x[1], reverse=True)
    return sorted_top_stocks

# API Route to get Nifty 50 and Sensex data
@market_bp.route('/market-overview', methods=['GET'])
def market_overview():
    try:
        # Fetch Nifty 50 and Sensex data for the last year
        nifty_data = fetch_data('^NSEI', '2023-01-01', '2023-12-31')
        sensex_data = fetch_data('^BSESN', '2023-01-01', '2023-12-31')

        # Get the latest values for Nifty 50 and Sensex
        nifty_current = nifty_data['Close'].iloc[-1]
        sensex_current = sensex_data['Close'].iloc[-1]

        # Fetch top-performing stocks
        top_stocks = fetch_top_stocks()

        # Prepare the response
        response = {
            'nifty50': {
                'historical': nifty_data[['Close']].reset_index().to_dict(orient='records'),
                'current': nifty_current
            },
            'sensex': {
                'historical': sensex_data[['Close']].reset_index().to_dict(orient='records'),
                'current': sensex_current
            },
            'topStocks': [{'symbol': stock[0], 'price': stock[1]} for stock in top_stocks]
        }
        
        return jsonify(response)
    except Exception as e:
        print(f"Error in market overview: {str(e)}")
        return jsonify({"error": str(e)}), 500
