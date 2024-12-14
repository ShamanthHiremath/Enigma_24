import pandas as pd
import numpy as np
import yfinance as yf
import pandas_ta as ta
import joblib
import os
import logging
import pathlib
import traceback
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.model_selection import GridSearchCV, cross_val_score

# Get the current file's directory (routes)
CURRENT_DIR = pathlib.Path(__file__).parent
# Go up one level to backend and then to AI_models
MODELS_DIR = CURRENT_DIR.parent / 'AI_models'

def get_model_paths(ticker):
    """Helper function to generate correct model paths"""
    # Create models directory if it doesn't exist
    os.makedirs(MODELS_DIR, exist_ok=True)
    model_path = MODELS_DIR / f'{ticker}_risk_model.pkl'
    scaler_path = MODELS_DIR / f'{ticker}_scaler.pkl'
    return str(model_path), str(scaler_path)

def get_stock_data(ticker, period='1y', interval='1d'):
    """
    Fetch historical stock data for a given ticker using Yahoo Finance API.
    Dynamically adjusts the period for newly listed stocks if data is unavailable.
    """
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period, interval=interval)

        # If data is not available for the specified period, try shorter periods
        if hist.empty:
            for fallback_period in ['6mo', '3mo', '1mo']:
                hist = stock.history(period=fallback_period, interval=interval)
                if not hist.empty:
                    print(f"Data found for {ticker} with period '{fallback_period}'.")
                    break

        if hist.empty:
            raise ValueError(f"No data found for ticker: {ticker}")

        return hist

    except Exception as e:
        logging.error(f"Error fetching data for ticker {ticker}: {e}")
        raise ValueError(f"Failed to fetch data for {ticker}: {e}")

def preprocess_data(df):
    """
    Preprocess the stock data by handling missing values and resetting the index.
    """
    try:
        if df.empty or len(df) < 10:  # Ensure enough data points exist
            raise ValueError("Insufficient data available for meaningful analysis.")

        df.dropna(inplace=True)  # Remove missing values
        df.reset_index(inplace=True)  # Reset index
        return df
    except Exception as e:
        raise ValueError(f"Error during preprocessing: {e}")

def add_features(df):
    """
    Add technical indicators as features for the model. Handles missing data appropriately.
    """
    try:
        # Basic features
        df['Daily Return'] = df['Close'].pct_change()
        df['Volatility'] = df['Daily Return'].rolling(window=21).std() * np.sqrt(252)
        df['MA50'] = df['Close'].rolling(window=50).mean()
        df['MA200'] = df['Close'].rolling(window=200).mean()

        # Additional technical indicators using pandas_ta
        df['RSI'] = df.ta.rsi(length=14)
        macd = df.ta.macd(fast=12, slow=26, signal=9)
        df['MACD'] = macd['MACD_12_26_9']

        # Bollinger Bands
        bb_bands = df.ta.bbands(close=df['Close'], length=20)
        df['BB_upper'] = bb_bands['BBU_20_2.0']
        df['BB_middle'] = bb_bands['BBM_20_2.0']
        df['BB_lower'] = bb_bands['BBL_20_2.0']

        # Handle missing values after feature addition
        df.dropna(inplace=True)

        return df
    except Exception as e:
        raise ValueError(f"Error adding features: {e}")

def label_risk(df):
    """
    Label the risk level based on volatility quantiles.
    """
    try:
        df = df.dropna(subset=['Volatility'])  # Ensure no missing values in Volatility
        quantiles = df['Volatility'].quantile([0.33, 0.66])
        conditions = [
            (df['Volatility'] > quantiles[0.66]),
            (df['Volatility'] <= quantiles[0.66]) & (df['Volatility'] > quantiles[0.33]),
            (df['Volatility'] <= quantiles[0.33])
        ]
        choices = ['High', 'Medium', 'Low']
        df['Risk Level'] = np.select(conditions, choices)
        return df
    except Exception as e:
        raise ValueError(f"Error during labeling: {e}")

def train_and_save_model(ticker, model_path, scaler_path):
    """
    Train a machine learning model for a specific ticker and save the model along with its scaler.
    """
    try:
        # Fetch, preprocess, and add features to the stock data
        data = get_stock_data(ticker)
        data = preprocess_data(data)
        data = add_features(data)
        data = label_risk(data)

        # Select features and target
        features = ['Daily Return', 'Volatility', 'MA50', 'MA200']
        X = data[features].values
        y = data['Risk Level'].values.ravel()

        # Split the dataset
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)

        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        # Define parameters for grid search
        parameters = [{'n_estimators': [100, 700],
                      'max_features': ['sqrt', 'log2'],
                      'criterion': ['gini', 'entropy']}]

        # Perform Grid Search with cross-validation
        grid_search = GridSearchCV(RandomForestClassifier(random_state=42),
                                 parameters,
                                 cv=5,
                                 scoring='accuracy',
                                 n_jobs=-1)
        grid_search.fit(X_train_scaled, y_train)

        # Get the best model
        best_model = grid_search.best_estimator_

        # Save the best model and scaler
        joblib.dump(best_model, model_path)
        joblib.dump(scaler, scaler_path)

        return best_model, scaler

    except Exception as e:
        raise ValueError(f"Error training and saving model for {ticker}: {e}")

def load_model_and_scaler(model_path, scaler_path):
    """
    Load a trained model and its corresponding scaler from disk.
    """
    try:
        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
        return model, scaler
    except Exception as e:
        raise ValueError(f"Failed to load model or scaler: {e}")

def risk_analysis_model(new_stock_ticker):
    data = get_stock_data(new_stock_ticker)

    # Check if the data is too short for analysis
    if len(data) < 10:
        logging.warning(f"Skipping {new_stock_ticker} due to insufficient data.")
        results = {'error': "Insufficient data for analysis."}
        return results

    # Proceed with analysis if enough data
    data = preprocess_data(data)
    data = add_features(data)
    data = label_risk(data)

    # Paths for the model and scaler
    model_path, scaler_path = get_model_paths(new_stock_ticker)

    # Load or train the model
    if not os.path.exists(model_path) or not os.path.exists(scaler_path):
        model, scaler = train_and_save_model(new_stock_ticker, model_path, scaler_path)
    else:
        model, scaler = load_model_and_scaler(model_path, scaler_path)

    # Get features for prediction
    features = ['Daily Return', 'Volatility', 'MA50', 'MA200']
    latest_data = data[features].iloc[-1]

    # Scale the latest data
    latest_data_scaled = scaler.transform(latest_data.values.reshape(1, -1))

    # Make prediction
    risk_level = model.predict(latest_data_scaled)[0]

    # Prepare results
    results = {
        'risk_level': risk_level,
        'current_price': f"{data['Close'].iloc[-1]:.2f}",
        'volatility': f"{data['Volatility'].iloc[-1] * 100:.2f}%",
        'daily_return': f"{data['Daily Return'].iloc[-1] * 100:.2f}%",
        'latest_close': data['Close'].iloc[-1],
        'trend': "Bullish" if data['MA50'].iloc[-1] > data['MA200'].iloc[-1] else "Bearish"
    }

    return results

def fetch_risk_results(new_stock_ticker, portfolio):
    print(new_stock_ticker)
    model_path, scaler_path = get_model_paths(new_stock_ticker)

    try:
        # Always try to train/retrain the model regardless of portfolio status
        model, scaler = train_and_save_model(new_stock_ticker, model_path, scaler_path)
        print(f"Model trained for {new_stock_ticker}...")
        
        results = risk_analysis_model(new_stock_ticker)
        
        # Add to portfolio if not already present
        if new_stock_ticker not in portfolio:
            portfolio.append(new_stock_ticker)
        
        return results
    except Exception as e:
        logging.error(f"Error in fetch_risk_results: {str(e)}")
        return {'error': str(e)}

if __name__ == "__main__":
    # Portfolio of stocks
    portfolio = ['TCS.NS', 'ITC.NS', 'ZOMATO.NS', 'TATASTEEL.NS', 'INFY.NS', 
                'RELIANCE.NS', 'HDFCBANK.NS', 'ICICIBANK.NS', 'SBIN.NS']

    new_stock_ticker = 'TCS.NS'
    results = fetch_risk_results(new_stock_ticker, portfolio)
    print(results)