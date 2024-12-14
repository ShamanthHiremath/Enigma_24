import os
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import TimeSeriesSplit
from keras.models import Sequential, load_model
from keras.layers import LSTM, Dense, Dropout
import joblib
from datetime import datetime, timedelta
import logging

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
    
def train_or_load_model(symbol, start_date, end_date):
    try:
        model_dir = "models/"
        os.makedirs(model_dir, exist_ok=True)
        
        model_path = os.path.join(model_dir, f"{symbol}_model.h5")
        scaler_path = os.path.join(model_dir, f"{symbol}_scaler.pkl")
        
        # Check if model needs retraining (older than 7 days)
        retrain = True
        if os.path.exists(model_path) and os.path.exists(scaler_path):
            model_time = datetime.fromtimestamp(os.path.getmtime(model_path))
            if (datetime.now() - model_time).days < 7:
                retrain = False
        
        if not retrain:
            model = load_model(model_path)
            scaler = joblib.load(scaler_path)
            return model, scaler
        
        # Fetch and prepare data
        df = yf.download(symbol, start=start_date, end=end_date)
        if df.empty:
            raise ValueError(f"No data found for {symbol}")
        
        df = prepare_data(df)
        df.dropna(inplace=True)
        
        features = ['Open', 'High', 'Low', 'Volume', 'sma_20', 'sma_50', 
                   'ema_20', 'ema_50', 'macd_value', 'rsi_14']
        
        # Scale features
        scaler = MinMaxScaler()
        scaled_data = scaler.fit_transform(df[features])
        
        # Prepare sequences
        sequence_length = 60
        X, y = [], []
        for i in range(sequence_length, len(scaled_data)):
            X.append(scaled_data[i-sequence_length:i])
            y.append(df['Close'].iloc[i])
        
        X = np.array(X)
        y = np.array(y)
        
        # Split data
        split = int(0.8 * len(X))
        X_train, X_test = X[:split], X[split:]
        y_train, y_test = y[:split], y[split:]
        
        # Build model
        model = Sequential([
            LSTM(50, return_sequences=True, input_shape=(sequence_length, len(features))),
            Dropout(0.2),
            LSTM(50, return_sequences=False),
            Dropout(0.2),
            Dense(25),
            Dense(1)
        ])
        
        model.compile(optimizer='adam', loss='mse')
        model.fit(X_train, y_train, epochs=50, batch_size=32, validation_split=0.1, verbose=0)
        
        # Save model and scaler
        model.save(model_path)
        joblib.dump(scaler, scaler_path)
        
        return model, scaler
        
    except Exception as e:
        logging.error(f"Error in model training: {str(e)}")
        raise

# In stock_price_predictor.py

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