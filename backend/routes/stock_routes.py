from flask import Blueprint, jsonify, request
import logging
import numpy as np
import requests
import yfinance as yf
from datetime import datetime, timedelta
from .sentiment_analysis import fetch_and_analyze_stock_sentiment
from .risk_analysis import fetch_risk_results, risk_analysis_model
from .prediction_analysis import stock_price_predictor, train_or_load_model

stock_bp = Blueprint('stock', __name__)
risk_bp = Blueprint('risk', __name__)
portfolio = ['TCS.NS', 'ITC.NS', 'ZOMATO.NS', 'TATASTEEL.NS', 'INFY.NS', 
                'RELIANCE.NS', 'HDFCBANK.NS', 'ICICIBANK.NS', 'SBIN.NS']
@risk_bp.route('/analyze/<symbol>', methods=['GET'])
def analyze_stock_risk(symbol):
    try:
        if not symbol:
            return jsonify({"error": "Symbol is required"}), 400
        
        # Attempt to get risk analysis results
        results = fetch_risk_results(symbol, portfolio)
        
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
def prepare_data(df):
    """Prepare data with technical indicators"""
    df['sma_20'] = df['Close'].rolling(window=20).mean()
    df['sma_50'] = df['Close'].rolling(window=50).mean()
    df['ema_20'] = df['Close'].ewm(span=20, adjust=False).mean()
    df['ema_50'] = df['Close'].ewm(span=50, adjust=False).mean()
    
    # MACD
    df['macd'] = df['Close'].ewm(span=12, adjust=False).mean() - df['Close'].ewm(span=26, adjust=False).mean()
    df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
    df['macd_value'] = df['macd'] - df['macd_signal']
    
    # RSI
    delta = df['Close'].diff(1)
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=14, min_periods=1).mean()
    avg_loss = loss.rolling(window=14, min_periods=1).mean()
    rs = avg_gain / avg_loss
    df['rsi_14'] = 100 - (100 / (1 + rs))
    
    return df

def stock_price_predictor(symbol, start_date, end_date):
    try:
        # Get current price data
        stock = yf.Ticker(symbol)
        current_data = stock.history(period='1d')
        
        if current_data.empty:
            logging.error(f"No current data found for {symbol}")
            return {'error': 'Could not fetch current stock data'}
        
        last_close_price = float(current_data['Close'].iloc[-1])
        
        # Train/load model and make prediction
        try:
            model, scaler = train_or_load_model(symbol, start_date, end_date)
        except Exception as e:
            logging.error(f"Model training error for {symbol}: {str(e)}")
            return {'error': f"Failed to train model: {str(e)}"}
        
        # Prepare latest data for prediction
        try:
            df = yf.download(symbol, start=start_date - timedelta(days=100), end=end_date)
            if df.empty:
                return {'error': 'Insufficient historical data for prediction'}
            
            df = prepare_data(df)
            df.dropna(inplace=True)
            
            if len(df) < 60:  # Check if we have enough data points
                return {'error': 'Insufficient data points for prediction'}
            
            features = ['Open', 'High', 'Low', 'Volume', 'sma_20', 'sma_50', 
                       'ema_20', 'ema_50', 'macd_value', 'rsi_14']
            
            # Verify all features exist
            missing_features = [f for f in features if f not in df.columns]
            if missing_features:
                return {'error': f'Missing features: {missing_features}'}
            
            # Scale and reshape latest data
            latest_data = scaler.transform(df[features].tail(60))
            latest_data = latest_data.reshape(1, 60, len(features))
            
            # Make prediction
            predicted_price = float(model.predict(latest_data)[0][0])
            
            # Calculate metrics
            price_change = predicted_price - last_close_price
            price_change_percent = (price_change / last_close_price) * 100
            
            # Calculate confidence based on recent prediction accuracy
            recent_predictions = model.predict(latest_data[-10:])
            recent_actuals = df['Close'].tail(10).values
            prediction_errors = np.abs((recent_predictions - recent_actuals) / recent_actuals)
            confidence = max(min(100 * (1 - np.mean(prediction_errors)), 95), 50)
            
            return {
                'predicted_price': round(predicted_price, 2),
                'last_close_price': round(last_close_price, 2),
                'price_change': round(price_change, 2),
                'price_change_percent': round(price_change_percent, 2),
                'prediction_confidence': round(confidence, 1),
                'prediction_direction': 'Bullish' if price_change > 0 else 'Bearish'
            }
            
        except Exception as e:
            logging.error(f"Data preparation error for {symbol}: {str(e)}")
            return {'error': f"Failed to prepare prediction data: {str(e)}"}
        
    except Exception as e:
        logging.error(f"Price prediction error for {symbol}: {str(e)}")
        return {'error': f"Failed to predict price: {str(e)}"}
# Financial Modeling Prep API Configuration
#FMP_API_KEY = 'GbXRY0QJF2ZAzqNqFo9G9tmInkDmNMz9'
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
            'risk_analysis': None,
            'price_prediction': None  # New field for price prediction
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
        try:
            # Use the stock_price_predictor function
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)
            prediction_result = stock_price_predictor(symbol, start_date, end_date)
            
            if 'error' not in prediction_result:
                stock_details['price_prediction'] = {
                    'predicted_price': prediction_result.get('predicted_price'),
                    'last_close_price': prediction_result.get('last_close_price'),
                    'price_change': prediction_result.get('price_change'),
                    'prediction_confidence': prediction_result.get('prediction_confidence'),
                    'prediction_direction': prediction_result.get('prediction_direction')
                }
            else:
                logging.error(f"Price prediction error: {prediction_result['error']}")
                stock_details['price_prediction'] = None

        except Exception as e:
            logging.error(f"Error in price prediction: {e}")
            stock_details['price_prediction'] = None

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