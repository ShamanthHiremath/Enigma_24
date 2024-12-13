import requests
from flask import Blueprint, jsonify
from datetime import datetime, timedelta
import logging

# Create a Blueprint for market routes
market_bp = Blueprint('market_bp', __name__)

class NSEDataFetcher:
    BASE_URL = 'https://www.nseindia.com'
    
    @staticmethod
    def get_headers():
        """Generate headers to mimic browser request"""
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache'
        }

    @classmethod
    def fetch_index_data(cls, index_symbol):
        """
        Fetch index data for Nifty or Sensex
        
        Args:
            index_symbol (str): Index symbol (e.g., 'NIFTY 50', 'SENSEX')
        
        Returns:
            dict: Current price and historical data
        """
        try:
            # Create a session to maintain cookies
            session = requests.Session()
            session.headers.update(cls.get_headers())

            # First, get home page to set cookies
            session.get(cls.BASE_URL, timeout=10)

            # Fetch current index data
            quote_url = f'{cls.BASE_URL}/api/equity-stockIndices'
            response = session.get(quote_url, params={'index': index_symbol}, timeout=10)
            
            if response.status_code != 200:
                logging.error(f"Failed to fetch {index_symbol} data")
                return None

            data = response.json()
            
            if not data or 'data' not in data or not data['data']:
                logging.error(f"No data found for {index_symbol}")
                return None

            # Get the first (latest) data point
            latest_data = data['data'][0]

            # Fetch historical data 
            historical_url = f'{cls.BASE_URL}/api/historical/cm/equity'
            historical_response = session.get(historical_url, params={
                'symbol': index_symbol,
                'series': 'EQ',
                'from': (datetime.now() - timedelta(days=365)).strftime('%d-%m-%Y'),
                'to': datetime.now().strftime('%d-%m-%Y')
            }, timeout=10)

            historical_data = []
            if historical_response.status_code == 200:
                historical_json = historical_response.json()
                historical_data = [
                    {
                        'Date': entry['CH_DATE'],
                        'Close': float(entry['CH_CLOSING_PRICE'])
                    } 
                    for entry in historical_json.get('data', [])
                ][-12:]  # Last 12 months

            return {
                'current': {
                    'price': float(latest_data.get('last', 0)),
                    'change': float(latest_data.get('change', 0)),
                    'changePercent': float(latest_data.get('percentChange', 0))
                },
                'historical': historical_data
            }

        except Exception as e:
            logging.error(f"Error fetching {index_symbol} data: {str(e)}")
            return None

    @classmethod
    def fetch_top_stocks(cls):
        """
        Fetch top performing stocks
        
        Returns:
            list: Top stocks with symbol, price, and change
        """
        try:
            # Create a session to maintain cookies
            session = requests.Session()
            session.headers.update(cls.get_headers())

            # First, get home page to set cookies
            session.get(cls.BASE_URL, timeout=10)

            # Fetch top stocks
            top_stocks_url = f'{cls.BASE_URL}/api/equity-stockIndices'
            response = session.get(top_stocks_url, params={'index': 'NIFTY 50'}, timeout=10)
            
            if response.status_code != 200:
                logging.error("Failed to fetch top stocks")
                return []

            data = response.json()
            
            if not data or 'data' not in data:
                logging.error("No stock data found")
                return []

            # Select top 5 stocks by market cap or performance
            top_stocks = [
                {
                    'symbol': stock['symbol'],
                    'price': float(stock['lastPrice']),
                    'change': float(stock['percentChange'])
                } 
                for stock in data['data'][:5]
            ]

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
        nifty_data = NSEDataFetcher.fetch_index_data('NIFTY 50')
        sensex_data = NSEDataFetcher.fetch_index_data('SENSEX')
        top_stocks = NSEDataFetcher.fetch_top_stocks()

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