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
    query = request.args.get('name', '')
    
    if not query:
        return jsonify({"error": "Please provide a valid stock name or symbol"}), 400
    
    try:
        search_results = search_stocks(query)
        
        if isinstance(search_results, dict) and 'error' in search_results:
            return jsonify(search_results), 404
        
        return jsonify(search_results)
    
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

def get_intraday_stock_data(symbol):
    """
    Retrieve intraday stock data for the last 2 weeks using Alpha Vantage API
    """
    base_url = 'https://www.alphavantage.co/query'
    
    try:
        # 1. Get Intraday Time Series (5-minute intervals)
        intraday_params = {
            'function': 'TIME_SERIES_INTRADAY',
            'symbol': symbol,
            'interval': '5min',
            'outputsize': 'full',
            'apikey': ALPHA_VANTAGE_API_KEY
        }
        intraday_response = requests.get(base_url, params=intraday_params).json()
        
        # Process Intraday Data
        if 'Time Series (5min)' in intraday_response:
            intraday_data = intraday_response['Time Series (5min)']
            return [
                {
                    'timestamp': timestamp,
                    'open': data.get('1. open', ''),
                    'high': data.get('2. high', ''),
                    'low': data.get('3. low', ''),
                    'close': data.get('4. close', ''),
                    'volume': data.get('5. volume', '')
                }
                for timestamp, data in intraday_data.items()
            ]
        else:
            return {"error": "Could not retrieve intraday data"}
    
    except Exception as e:
        print(f"Intraday data error: {e}")
        return {"error": f"Could not retrieve intraday data: {str(e)}"}

@stock_bp.route('/details/intraday/<symbol>', methods=['GET'])
def stock_intraday_data(symbol):
    try:
        intraday_data = get_intraday_stock_data(symbol)
        
        if isinstance(intraday_data, dict) and 'error' in intraday_data:
            return jsonify(intraday_data), 404
        
        return jsonify(intraday_data)
    
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500

def get_weekly_stock_data(symbol):
    """
    Retrieve weekly stock data (past 5 years) using Alpha Vantage API
    """
    base_url = 'https://www.alphavantage.co/query'
    
    try:
        # 2. Get Weekly Time Series
        weekly_params = {
            'function': 'TIME_SERIES_WEEKLY',
            'symbol': symbol,
            'apikey': ALPHA_VANTAGE_API_KEY
        }
        weekly_response = requests.get(base_url, params=weekly_params).json()
        
        # Process Weekly Data
        if 'Weekly Time Series' in weekly_response:
            weekly_data = weekly_response['Weekly Time Series']
            return [
                {
                    'date': date,
                    'open': data.get('1. open', ''),
                    'high': data.get('2. high', ''),
                    'low': data.get('3. low', ''),
                    'close': data.get('4. close', ''),
                    'volume': data.get('5. volume', '')
                }
                for date, data in weekly_data.items()
            ]
        else:
            return {"error": "Could not retrieve weekly data"}
    
    except Exception as e:
        print(f"Weekly data error: {e}")
        return {"error": f"Could not retrieve weekly data: {str(e)}"}

@stock_bp.route('/details/weekly/<symbol>', methods=['GET'])
def stock_weekly_data(symbol):
    try:
        weekly_data = get_weekly_stock_data(symbol)
        
        if isinstance(weekly_data, dict) and 'error' in weekly_data:
            return jsonify(weekly_data), 404
        
        return jsonify(weekly_data)
    
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500

# Monthly data endpoint (commented out for now)
def get_monthly_stock_data(symbol):
    """
    Retrieve monthly stock data (past 20+ years) using Alpha Vantage API
    """
    base_url = 'https://www.alphavantage.co/query'
    
    try:
        # 3. Get Monthly Time Series
        monthly_params = {
            'function': 'TIME_SERIES_MONTHLY',
            'symbol': symbol,
            'apikey': ALPHA_VANTAGE_API_KEY
        }
        monthly_response = requests.get(base_url, params=monthly_params).json()
        
        # Process Monthly Data
        if 'Monthly Time Series' in monthly_response:
            monthly_data = monthly_response['Monthly Time Series']
            return [
                {
                    'date': date,
                    'open': data.get('1. open', ''),
                    'high': data.get('2. high', ''),
                    'low': data.get('3. low', ''),
                    'close': data.get('4. close', ''),
                    'volume': data.get('5. volume', '')
                }
                for date, data in monthly_data.items()
            ]
        else:
            return {"error": "Could not retrieve monthly data"}
    
    except Exception as e:
        print(f"Monthly data error: {e}")
        return {"error": f"Could not retrieve monthly data: {str(e)}"}

# Monthly route (currently commented out)
# @stock_bp.route('/details/monthly/<symbol>', methods=['GET'])
# def stock_monthly_data(symbol):
#     try:
#         monthly_data = get_monthly_stock_data(symbol)
#         
#         if isinstance(monthly_data, dict) and 'error' in monthly_data:
#             return jsonify(monthly_data), 404
#         
#         return jsonify(monthly_data)
#     
#     except Exception as e:
#         print(f"Unexpected error: {e}")
#         return jsonify({"error": "An unexpected error occurred"}), 500
def get_daily_stock_data(symbol):
    """
    Retrieve daily stock data (past 3 months) using Alpha Vantage API
    """
    base_url = 'https://www.alphavantage.co/query'
    
    try:
        # 3. Get Daily Time Series
        daily_params = {
            'function': 'TIME_SERIES_DAILY',
            'symbol': symbol,
            'outputsize': 'compact',  # This will retrieve data for the past 3 months
            'apikey': ALPHA_VANTAGE_API_KEY
        }
        daily_response = requests.get(base_url, params=daily_params).json()
        
        # Process Daily Data
        if 'Time Series (Daily)' in daily_response:
            daily_data = daily_response['Time Series (Daily)']
            return [
                {
                    'date': date,
                    'open': data.get('1. open', ''),
                    'high': data.get('2. high', ''),
                    'low': data.get('3. low', ''),
                    'close': data.get('4. close', ''),
                    'volume': data.get('5. volume', '')
                }
                for date, data in daily_data.items()
            ]
        else:
            return {"error": "Could not retrieve daily data"}
    
    except Exception as e:
        print(f"Daily data error: {e}")
        return {"error": f"Could not retrieve daily data: {str(e)}"}

@stock_bp.route('/details/daily/<symbol>', methods=['GET'])
def stock_daily_data(symbol):
    try:
        daily_data = get_daily_stock_data(symbol)
        
        if isinstance(daily_data, dict) and 'error' in daily_data:
            return jsonify(daily_data), 404
        
        return jsonify(daily_data)
    
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500