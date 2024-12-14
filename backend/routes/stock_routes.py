from flask import Blueprint, jsonify, request
import logging
import requests
import yfinance as yf
from datetime import datetime, timedelta
from .sentiment_analysis import fetch_and_analyze_stock_sentiment
from .risk_analysis import fetch_risk_results, risk_analysis_model

stock_bp = Blueprint('stock', __name__)
risk_bp = Blueprint('risk', __name__)

@risk_bp.route('/analyze/<symbol>', methods=['GET'])
def analyze_stock_risk(symbol):
    try:
        if not symbol:
            return jsonify({"error": "Symbol is required"}), 400
        
        # Attempt to get risk analysis results
        results = risk_analysis_model(symbol)
        
        # Check for error in results
        if 'error' in results:
            return jsonify({
                "risk_analysis": {
                    "error": results['error'],
                    "risk_level": 'N/A',
                    "volatility": 'N/A',
                    "daily_return": 'N/A',
                    "current_price": 'N/A',
                    "trend": 'N/A',
                    "latest_close": None
                }
            }), 400
        
        # Return successful risk analysis
        return jsonify({
            "risk_analysis": {
                "risk_level": results.get('risk_level', 'N/A'),
                "volatility": results.get('volatility', 'N/A'),
                "daily_return": results.get('daily_return', 'N/A'),
                "current_price": results.get('current_price', 'N/A'),
                "trend": results.get('trend', 'N/A'),
                "latest_close": results.get('latest_close', None)
            }
        })
        
    except Exception as e:
        logging.error(f"Comprehensive error analyzing risk for {symbol}: {str(e)}")
        return jsonify({
            "risk_analysis": {
                "error": "Failed to analyze stock risk",
                "risk_level": 'N/A',
                "volatility": 'N/A',
                "daily_return": 'N/A',
                "current_price": 'N/A',
                "trend": 'N/A',
                "latest_close": None
            }
        }), 500

# Financial Modeling Prep API Configuration
FMP_API_KEY = 'GbXRY0QJF2ZAzqNqFo9G9tmInkDmNMz9'
BASE_URL = 'https://financialmodelingprep.com/api'

def search_stocks(query):
    try:
        search_url = f"{BASE_URL}/v3/search-ticker"
        params = {
            'query': query,
            'limit': 10,
            'apikey': FMP_API_KEY
        }
        
        response = requests.get(search_url, params=params)
        response.raise_for_status()
        data = response.json()
        
        return data if data else []
    
    except Exception as e:
        logging.error(f"Error in stock search: {e}")
        raise

@stock_bp.route('/search', methods=['GET'])
def search_stocks_route():
    query = request.args.get('name', '').strip()
    
    if not query:
        return jsonify({"error": "Please provide a valid stock name or symbol"}), 400
    
    try:
        search_results = search_stocks(query)
        return jsonify(search_results)
    
    except requests.RequestException as e:
        logging.error(f"Network error: {e}")
        return jsonify({"error": "Network error occurred"}), 500
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500

def get_stock_details(symbol):
    try:
        # Initialize default response structure with safe defaults
        stock_details = {
            'current_quote': {
                'price': 0.0,
                'change': 0.0,
                'change_percent': 0.0,
            },
            'profile': {
                'name': 'Unknown',
                'symbol': symbol,
                'industry': 'Unknown',
                'sector': 'Unknown',
                'country': 'Unknown',
                'website': '#',
            },
            'historical_prices': [],
            'news': [],
            'sentiment': None,
            'risk_analysis': None
        }

        # Fetch stock information using yfinance
        stock = yf.Ticker(symbol)

        # Company Profile from yfinance
        if stock.info:
            stock_details['profile'].update({
                'name': stock.info.get('longName', 'Unknown'),
                'industry': stock.info.get('industry', 'Unknown'),
                'sector': stock.info.get('sector', 'Unknown'),
                'country': stock.info.get('country', 'Unknown'),
                'website': stock.info.get('website', '#'),
            })

        # Current Quote from yfinance
        current_price = stock.history(period='1d')
        if not current_price.empty:
            close_price = current_price['Close'].iloc[-1]
            previous_close = current_price['Close'].iloc[0]
            change = close_price - previous_close
            change_percent = (change / previous_close) * 100

            stock_details['current_quote'] = {
                'price': float(close_price),
                'change': float(change),
                'change_percent': float(change_percent)
            }

        # Historical Prices (Last 365 days) from yfinance
        historical_data = stock.history(period='1y')
        if not historical_data.empty:
            stock_details['historical_prices'] = [
                {
                    'date': idx.strftime('%Y-%m-%d'),
                    'close': float(row['Close'])
                }
                for idx, row in historical_data.iterrows()
            ]

        # News from Financial Modeling Prep (unchanged from original)
        news_url = f"{BASE_URL}/v3/stock_news"
        news_response = requests.get(news_url, params={
            'tickers': symbol,
            'limit': 5,
            'apikey': FMP_API_KEY
        })
        news_data = news_response.json()

        if news_data and isinstance(news_data, list):
            stock_details['news'] = [
                {
                    'title': article.get('title', ''),
                    'publisher': article.get('site', ''),
                    'link': article.get('url', ''),
                    'published_at': article.get('publishedDate', '')
                }
                for article in news_data[:5]
            ]

        # Fetch sentiment analysis 
        try:
            sentiment_data = fetch_and_analyze_stock_sentiment(symbol)
            
            # Combine existing news with sentiment news if needed
            existing_news = stock_details.get('news', [])
            sentiment_news = sentiment_data.get('news', [])
            
            # Merge news, prioritizing sentiment news but keeping existing if sentiment news is empty
            stock_details['news'] = sentiment_news if sentiment_news else existing_news
            
            stock_details['sentiment'] = {
                'overall_prediction': sentiment_data.get('overall_prediction', None)
            }
        except Exception as e:
            logging.error(f"Error fetching sentiment: {e}")
            stock_details['sentiment'] = None

        # Fetch Risk Analysis
        try:
            # Use requests to make an internal API call
            risk_response = requests.get(f"{request.host_url}risk/analyze/{symbol}")
            if risk_response.ok:
                stock_details['risk_analysis'] = risk_response.json().get('risk_analysis')
            else:
                stock_details['risk_analysis'] = {
                    'risk_level': 'N/A',
                    'volatility': 'N/A',
                    'daily_return': 'N/A',
                    'current_price': 'N/A',
                    'latest_close': None,
                    'trend': 'N/A'
                }
        except Exception as e:
            logging.error(f"Error fetching risk analysis: {e}")
            stock_details['risk_analysis'] = {
                'risk_level': 'N/A',
                'volatility': 'N/A',
                'daily_return': 'N/A',
                'current_price': 'N/A',
                'latest_close': None,
                'trend': 'N/A'
            }

        return stock_details

    except Exception as e:
        logging.error(f"Comprehensive error fetching stock details: {e}")
        return None
    
@stock_bp.route('/details/<symbol>', methods=['GET'])
def stock_details_route(symbol):
    if not symbol:
        return jsonify({"error": "Symbol is required"}), 400

    try:
        details = get_stock_details(symbol)
        if details is None:
            return jsonify({"error": "Could not retrieve stock details"}), 404
        return jsonify(details)

    except Exception as e:
        logging.error(f"Error in stock details route: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500