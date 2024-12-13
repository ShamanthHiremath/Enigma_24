from flask import Blueprint, jsonify, request
import requests
import os

stock_bp = Blueprint('stock', __name__)

# Alpha Vantage Configuration
ALPHA_VANTAGE_API_KEY = 'NRNB1PVWVWZOAYRU'  # Replace with your actual API key

def search_stocks(query):
    """
    Search stocks using Alpha Vantage API
    """
    base_url = 'https://www.alphavantage.co/query'
    
    # Search for symbol
    search_params = {
        'function': 'SYMBOL_SEARCH',
        'keywords': query,
        'apikey': ALPHA_VANTAGE_API_KEY
    }
    
    try:
        response = requests.get(base_url, params=search_params)
        data = response.json()
        
        # Check if 'bestMatches' exists in the response
        if 'bestMatches' in data:
            results = []
            for match in data['bestMatches']:
                results.append({
                    'symbol': match['1. symbol'],
                    'name': match['2. name'],
                    'type': match['3. type'],
                    'region': match['4. region']
                })
            return results
        else:
            return {"error": "No stocks found matching the query"}
    
    except Exception as e:
        print(f"Error in stock search: {e}")
        return {"error": "An unexpected error occurred"}

def get_stock_quote(symbol):
    """
    Get stock quote details
    """
    base_url = 'https://www.alphavantage.co/query'
    
    quote_params = {
        'function': 'GLOBAL_QUOTE',
        'symbol': symbol,
        'apikey': ALPHA_VANTAGE_API_KEY
    }
    
    try:
        response = requests.get(base_url, params=quote_params)
        data = response.json()
        
        # Check if quote data exists
        if 'Global Quote' in data and data['Global Quote']:
            quote = data['Global Quote']
            return {
                'symbol': quote['01. symbol'],
                'price': quote['05. price'],
                'change': quote['09. change'],
                'change_percent': quote['10. change percent']
            }
        else:
            return {"error": "Could not retrieve stock quote"}
    
    except Exception as e:
        print(f"Error in stock quote retrieval: {e}")
        return {"error": "An unexpected error occurred"}

@stock_bp.route('/search', methods=['GET'])
def search_stocks_route():
    query = request.args.get('name', '').strip()
    
    if not query:
        return jsonify({"error": "Please provide a valid stock name or symbol"}), 400
    
    try:
        search_results = search_stocks(query)
        
        if isinstance(search_results, dict) and 'error' in search_results:
            return jsonify(search_results), 404
        
        return jsonify(search_results)
    
    except requests.RequestException as e:
        print(f"Network error: {e}")
        return jsonify({"error": "Network error occurred"}), 500
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500

@stock_bp.route('/quote/<symbol>', methods=['GET'])
def stock_quote_route(symbol):
    try:
        quote_results = get_stock_quote(symbol)
        
        if isinstance(quote_results, dict) and 'error' in quote_results:
            return jsonify(quote_results), 404
        
        return jsonify(quote_results)
    
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500

def get_comprehensive_stock_details(symbol):
    """
    Retrieve comprehensive stock details using multiple Alpha Vantage endpoints
    """
    base_url = 'https://www.alphavantage.co/query'
    
    # Prepare multiple API calls
    try:
        # 1. Get Current Quote
        quote_params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': symbol,
            'apikey': ALPHA_VANTAGE_API_KEY
        }
        quote_response = requests.get(base_url, params=quote_params).json()
        
        # 2. Get Monthly Time Series (for historical price trends)
        monthly_params = {
            'function': 'TIME_SERIES_MONTHLY_ADJUSTED',
            'symbol': symbol,
            'apikey': ALPHA_VANTAGE_API_KEY
        }
        monthly_response = requests.get(base_url, params=monthly_params).json()
        
        # 3. Get News Sentiment
        news_params = {
            'function': 'NEWS_SENTIMENT',
            'tickers': symbol,
            'limit': 5,
            'apikey': ALPHA_VANTAGE_API_KEY
        }
        news_response = requests.get(base_url, params=news_params).json()
        
        # 4. Get Insider Transactions
        insider_params = {
            'function': 'INSIDER_TRANSACTIONS',
            'symbol': symbol,
            'apikey': ALPHA_VANTAGE_API_KEY
        }
        insider_response = requests.get(base_url, params=insider_params).json()
        
        # Compile comprehensive stock details
        stock_details = {
            # Current Quote Information
            'current_quote': {},
            'historical_prices': {},
            'news': [],
            'insider_transactions': []
        }
        
        # Process Current Quote
        if 'Global Quote' in quote_response and quote_response['Global Quote']:
            quote = quote_response['Global Quote']
            stock_details['current_quote'] = {
                'symbol': quote.get('01. symbol', ''),
                'price': quote.get('05. price', ''),
                'change': quote.get('09. change', ''),
                'change_percent': quote.get('10. change percent', ''),
                'latest_trading_day': quote.get('07. latest trading day', ''),
                'previous_close': quote.get('08. previous close', '')
            }
        
        # Process Historical Prices
        if 'Monthly Adjusted Time Series' in monthly_response:
            monthly_data = monthly_response['Monthly Adjusted Time Series']
            historical_prices = []
            for date, prices in list(monthly_data.items())[:12]:  # Last 12 months
                historical_prices.append({
                    'date': date,
                    'open': prices.get('1. open', ''),
                    'high': prices.get('2. high', ''),
                    'low': prices.get('3. low', ''),
                    'close': prices.get('4. close', ''),
                    'volume': prices.get('6. volume', '')
                })
            stock_details['historical_prices'] = historical_prices
        
        # Process News Sentiment
        if 'feed' in news_response:
            stock_details['news'] = [
                {
                    'title': article.get('title', ''),
                    'url': article.get('url', ''),
                    'published_at': article.get('time_published', ''),
                    'summary': article.get('summary', '')
                } for article in news_response['feed'][:5]
            ]
        
        # Process Insider Transactions
        if 'insider_transactions' in insider_response:
            stock_details['insider_transactions'] = insider_response['insider_transactions'][:5]
        
        return stock_details
    
    except Exception as e:
        print(f"Comprehensive stock details error: {e}")
        return {"error": f"Could not retrieve comprehensive details: {str(e)}"}

@stock_bp.route('/details/<symbol>', methods=['GET'])
def stock_details_route(symbol):
    try:
        details = get_comprehensive_stock_details(symbol)
        
        if isinstance(details, dict) and 'error' in details:
            return jsonify(details), 404
        
        return jsonify(details)
    
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500