from flask import Blueprint, jsonify, request
import requests
from datetime import datetime, timedelta

stock_bp = Blueprint('stock', __name__)

# Financial Modeling Prep API Configuration
FMP_API_KEY = 'cRDdT2E7PbKeYPsVST8kmnUBJwof2sTa'
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
        print(f"Error in stock search: {e}")
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
        print(f"Network error: {e}")
        return jsonify({"error": "Network error occurred"}), 500
    except Exception as e:
        print(f"Unexpected error: {e}")
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
            'news': []
        }

        # Fetch profile data
        profile_url = f"{BASE_URL}/v3/profile/{symbol}"
        profile_response = requests.get(profile_url, params={'apikey': FMP_API_KEY})
        profile_data = profile_response.json()

        if profile_data and isinstance(profile_data, list) and len(profile_data) > 0:
            profile = profile_data[0]
            stock_details['profile'].update({
                'name': profile.get('companyName', 'Unknown'),
                'industry': profile.get('industry', 'Unknown'),
                'sector': profile.get('sector', 'Unknown'),
                'country': profile.get('country', 'Unknown'),
                'website': profile.get('website', '#'),
            })

        # Fetch quote data
        quote_url = f"{BASE_URL}/v3/quote/{symbol}"
        quote_response = requests.get(quote_url, params={'apikey': FMP_API_KEY})
        quote_data = quote_response.json()

        if quote_data and isinstance(quote_data, list) and len(quote_data) > 0:
            quote = quote_data[0]
            stock_details['current_quote'].update({
                'price': float(quote.get('price', 0.0)),
                'change': float(quote.get('change', 0.0)),
                'change_percent': float(quote.get('changesPercentage', 0.0)),
            })

        # Fetch historical data for the last year (365 days)
        historical_url = f"{BASE_URL}/v3/historical-price-full/{symbol}"
        historical_response = requests.get(historical_url, params={'apikey': FMP_API_KEY, 'timeseries': 365})
        historical_data = historical_response.json()

        if historical_data and 'historical' in historical_data:
            # Reverse the historical data so it shows from most recent to oldest
            stock_details['historical_prices'] = [
                {
                    'date': entry.get('date', ''),
                    'close': float(entry.get('close', 0.0))
                }
                for entry in reversed(historical_data['historical'][:365])  # Reverse the data order
                if entry.get('date') and entry.get('close')
            ]

        # Fetch news data
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

        return stock_details

    except Exception as e:
        print(f"Error fetching stock details: {e}")
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
        print(f"Error in stock details route: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500