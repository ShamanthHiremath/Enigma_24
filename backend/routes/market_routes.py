import yfinance as yf
import requests
from flask import Blueprint, jsonify
from datetime import datetime, timedelta
import logging
import pandas as pd

# Create a Blueprint for market routes
market_bp = Blueprint('market_bp', __name__)

class MarketDataFetcher:
    @staticmethod
    def fetch_index_data(index_symbol):
        """
        Fetch index data using YFinance
        
        Args:
            index_symbol (str): Index symbol (e.g., '^NSEI' for Nifty 50, '^BSESN' for Sensex)
        
        Returns:
            dict: Current price and historical data
        """
        try:
            # Fetch ticker data
            ticker = yf.Ticker(index_symbol)
            
            # Get current data
            current_info = ticker.info
            current_price = current_info.get('regularMarketPrice', 0)
            previous_close = current_info.get('previousClose', 0)
            change = current_price - previous_close
            change_percent = (change / previous_close) * 100 if previous_close else 0

            # Get historical data for last 12 months
            historical_data = ticker.history(period='1y')
            
            # Transform historical data
            historical_prices = [
                {
                    'Date': idx.strftime('%Y-%m-%d'),
                    'Close': float(row['Close'])
                }
                for idx, row in historical_data.iterrows()
            ][-12:]  # Last 12 months

            return {
                'current': {
                    'price': float(current_price),
                    'change': float(change),
                    'changePercent': float(change_percent)
                },
                'historical': historical_prices
            }

        except Exception as e:
            logging.error(f"Error fetching {index_symbol} data: {str(e)}")
            return None

    @staticmethod
    def fetch_top_stocks():
        """
        Fetch top performing stocks using YFinance
        
        Returns:
            list: Top stocks with symbol, price, and change
        """
        try:
            # Nifty 50 top stocks symbols
            top_stocks_symbols = [
                'INFY.NS', 'TCS.NS', 'RELIANCE.NS', 
                'HDFCBANK.NS', 'ICICIBANK.NS'
            ]

            top_stocks = []
            for symbol in top_stocks_symbols:
                try:
                    ticker = yf.Ticker(symbol)
                    info = ticker.info
                    
                    top_stocks.append({
                        'symbol': symbol.replace('.NS', ''),
                        'price': float(info.get('regularMarketPrice', 0)),
                        'change': float(info.get('regularMarketChangePercent', 0))
                    })
                except Exception as e:
                    logging.error(f"Error fetching stock {symbol}: {str(e)}")

            return top_stocks

        except Exception as e:
            logging.error(f"Error fetching top stocks: {str(e)}")
            return []

def get_market_indices():
    """
    Comprehensive market data retrieval
    
    Returns:
        dict: Market data including Nifty 50, Sensex, and top stocks
    """
    try:
        nifty_data = MarketDataFetcher.fetch_index_data('^NSEI')
        sensex_data = MarketDataFetcher.fetch_index_data('^BSESN')
        top_stocks = MarketDataFetcher.fetch_top_stocks()

        return {
            'nifty50': nifty_data or {'historical': [], 'current': {}},
            'sensex': sensex_data or {'historical': [], 'current': {}},
            'topStocks': top_stocks
        }

    except Exception as e:
        logging.error(f"Unexpected error in market overview: {str(e)}")
        return {
            'nifty50': {'historical': [], 'current': {}},
            'sensex': {'historical': [], 'current': {}},
            'topStocks': []
        }

@market_bp.route('/market-overview', methods=['GET'])
def market_overview():
    """
    API endpoint for market overview
    
    Returns:
        JSON response with market data
    """
    try:
        market_data = get_market_indices()
        return jsonify(market_data)
    
    except Exception as e:
        logging.error(f"Unexpected error in market overview route: {str(e)}")
        return jsonify({"error": "Unable to fetch market data"}), 500