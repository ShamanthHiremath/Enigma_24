import pandas as pd
import numpy as np
import yfinance as yf
import pandas_ta as ta
import joblib
import os
import logging
import traceback
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier

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
            print(f"Data for {ticker} not available for period '{period}'. Trying shorter periods.")
            for fallback_period in ['6mo', '3mo', '1mo']:
                hist = stock.history(period=fallback_period, interval=interval)
                if not hist.empty:
                    print(f"Data found for {ticker} with period '{fallback_period}'.")
                    break

        if hist.empty:
            raise ValueError(f"No data found for ticker: {ticker}")

        print(hist.head())
        return hist

    except Exception as e:
        logging.error(f"Error fetching data for ticker {ticker}: {e}")
        raise ValueError(f"Failed to fetch data for {ticker}: {e}")


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
        print("\nPREPROCESSED DATA")
        print(df.head())
        print()
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

        print("\nADDED TECHNICAL INDICATORS AS FEATURES")
        print(df.head())
        print()

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

from sklearn.metrics import confusion_matrix, classification_report
from sklearn.model_selection import GridSearchCV, cross_val_score

def train_and_save_model(ticker, model_path, scaler_path):
    """
    Train a machine learning model for a specific ticker, optimize hyperparameters using GridSearchCV,
    and save the model along with its scaler.
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

        # Retrieve the best model and parameters
        best_model = grid_search.best_estimator_
        best_params = grid_search.best_params_
        print(f"Best Accuracy (Grid Search): {grid_search.best_score_ * 100:.2f}%")
        print(f"Best Parameters: {best_params}")

        # Fit the model with the best parameters
        best_model.fit(X_train_scaled, y_train)

        # Evaluate the model on the test set
        y_pred = best_model.predict(X_test_scaled)
        print("\nConfusion Matrix:")
        print(confusion_matrix(y_test, y_pred))

        print("\nClassification Report:")
        print(classification_report(y_test, y_pred))

        # Perform cross-validation on the training set
        cv_score = cross_val_score(best_model, X_train_scaled, y_train, cv=5, scoring='accuracy').mean()
        print(f"Cross-Validation Score: {cv_score:.4f}")

        # Save the best model and scaler
        joblib.dump(best_model, model_path)
        joblib.dump(scaler, scaler_path)
        print(f"\nModel and scaler saved for {ticker} at:\nModel: {model_path}\nScaler: {scaler_path}")

        return best_model, scaler

    except Exception as e:
        raise ValueError(f"Error training and saving model for {ticker}: {e}")

def load_model_and_scaler(model_path, scaler_path):
    """
    Load a trained model and its corresponding scaler from disk.

    Args:
        model_path (str): Path to the saved model file.
        scaler_path (str): Path to the saved scaler file.

    Returns:
        tuple: Loaded model and scaler.
    """
    try:
        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
        return model, scaler
    except Exception as e:
        raise ValueError(f"Failed to load model or scaler: {e}")


def analyze_stock(ticker):
    try:
        model_path = f'Ai_models/{ticker}_risk_model.pkl'
        scaler_path = f'Ai_models/{ticker}_scaler.pkl'

        # Train and save model for the ticker if it doesn't exist
        if not os.path.exists(model_path) or not os.path.exists(scaler_path):
            os.makedirs(os.path.dirname(model_path), exist_ok=True)
            model, scaler = train_and_save_model(ticker, model_path, scaler_path)
        else:
            model, scaler = load_model_and_scaler(model_path, scaler_path)

        # Fetch and process the stock data
        data = get_stock_data(ticker)
        if len(data) < 10:
            raise ValueError(f"Not enough data available for meaningful analysis of {ticker}.")

        data = preprocess_data(data)
        data = add_features(data)
        data = label_risk(data)

        # Get features for prediction
        features = ['Daily Return', 'Volatility', 'MA50', 'MA200']
        latest_data = data[features].iloc[-1]

        # Scale the latest data
        latest_data_scaled = scaler.transform(latest_data.values.reshape(1, -1))

        # Make prediction
        risk_level = model.predict(latest_data_scaled)[0]

        # Format dates and prices for the chart (last 30 days)
        if not isinstance(data.index, pd.DatetimeIndex):
            data.index = pd.to_datetime(data.index)
        dates = [d.strftime('%Y-%m-%d') for d in data.index[-30:]]
        prices = data['Close'].tail(30).tolist()

        # Return the analysis results
        return {
            'risk_level': risk_level,
            'current_price': f"{data['Close'].iloc[-1]:.2f}",
            'volatility': f"{data['Volatility'].iloc[-1]*100:.2f}",
            'daily_return': f"{data['Daily Return'].iloc[-1]*100:.2f}",
            'dates': dates,
            'prices': prices
        }
    except Exception as e:
        logging.error(traceback.format_exc())
        return {'error': str(e)}


def get_latest_stock_data(ticker):
    """
    Fetch the latest available stock data for a given ticker.

    Args:
        ticker (str): Stock ticker symbol

    Returns:
        pd.DataFrame: Dataframe containing the latest stock data or the most recent record.
    """
    try:
        # Fetch data for the last 5 days to ensure the latest available data is included
        stock = yf.Ticker(ticker)
        hist = stock.history(period='5d', interval='1d')

        # Check if data is available
        if hist.empty:
            raise ValueError(f"No data available for {ticker}.")

        # Ensure the data is for today or the last available trading day
        latest_data = hist.iloc[-1].to_frame().T
        latest_data.reset_index(inplace=True)
        latest_data.rename(columns={'index': 'Date'}, inplace=True)

        return latest_data

    except Exception as e:
        logging.error(f"Error fetching latest data for ticker {ticker}: {e}")
        raise ValueError(f"Failed to fetch the latest data for {ticker}: {e}")
def comprehensive_stock_analysis(tickers):
    """
    Perform comprehensive analysis for multiple stock tickers.

    Args:
        tickers (list): List of stock ticker symbols

    Returns:
        dict: Comprehensive analysis results for each ticker
    """
    results = {}

    for ticker in tickers:
        try:
            data = get_stock_data(ticker)
            if len(data) < 10:
                logging.warning(f"Skipping {ticker} due to insufficient data.")
                results[ticker] = {'error': "Insufficient data for analysis."}
                continue

            # Proceed with analysis
            data = preprocess_data(data)
            data = add_features(data)
            data = label_risk(data)

            # Paths for the model and scaler
            model_path = f'Ai_models/{ticker}_risk_model.pkl'
            scaler_path = f'Ai_models/{ticker}_scaler.pkl'

            # Load or train the model
            if not os.path.exists(model_path) or not os.path.exists(scaler_path):
                model, scaler = train_and_save_model(ticker, model_path, scaler_path)
            # else:
                model, scaler = load_model_and_scaler(model_path, scaler_path)

            # Get features for prediction
            features = ['Daily Return', 'Volatility', 'MA50', 'MA200']
            latest_data = data[features].iloc[-1]

            # Scale the latest data
            latest_data_scaled = scaler.transform(latest_data.values.reshape(1, -1))

            # Make prediction
            risk_level = model.predict(latest_data_scaled)[0]

            # Prepare results
            results[ticker] = {
                'risk_level': risk_level,
                'current_price': f"{data['Close'].iloc[-1]:.2f}",
                'volatility': f"{data['Volatility'].iloc[-1] * 100:.2f}%",
                'daily_return': f"{data['Daily Return'].iloc[-1] * 100:.2f}%",
                'latest_close': data['Close'].iloc[-1],
                'trend': "Bullish" if data['MA50'].iloc[-1] > data['MA200'].iloc[-1] else "Bearish"
            }

        except Exception as e:
            results[ticker] = {
                'error': f"Analysis failed: {str(e)}"
            }

    return results
def risk_analysis_model(new_stock_ticker):
    data = get_stock_data(new_stock_ticker)

    # Check if the data is too short for analysis
    if len(data) < 10:
        logging.warning(f"Skipping {new_stock_ticker} due to insufficient data.")
        results = {'error': "Insufficient data for analysis."}
        return results  # Early return if insufficient data

    # Proceed with analysis if enough data
    data = preprocess_data(data)
    data = add_features(data)
    data = label_risk(data)

    # Paths for the model and scaler
    model_path = f'Ai_models/{new_stock_ticker}_risk_model.pkl'
    scaler_path = f'Ai_models/{new_stock_ticker}_scaler.pkl'

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

    if new_stock_ticker not in portfolio:
        portfolio.append(new_stock_ticker)
        model_path = f'Ai_models/{new_stock_ticker}_risk_model.pkl'
        scaler_path = f'Ai_models/{new_stock_ticker}_scaler.pkl'

        model, scaler = train_and_save_model(new_stock_ticker, model_path, scaler_path)
        print(f"Model trained for {new_stock_ticker}...")

        load_model_and_scaler(model_path, scaler_path)
        print(f"Loaded trained model for {new_stock_ticker}...")

        results = risk_analysis_model(new_stock_ticker)
        return results
    else:
        model_path = f'Ai_models/{new_stock_ticker}_risk_model.pkl'
        scaler_path = f'Ai_models/{new_stock_ticker}_scaler.pkl'
        print(f"{new_stock_ticker} is already in the portfolio.")

        model, scaler = load_model_and_scaler(model_path, scaler_path)

        results = risk_analysis_model(new_stock_ticker)
        return results
portfolio = ['TCS.NS', 'ITC.NS', 'TCS.NS', 'ZOMATO.NS', 'TATASTEEL.NS', 'INFY.NS', 'RELIANCE.NS', 'HDFCBANK.NS', 'ICICIBANK.NS', 'SBIN.NS']

new_stock_tickerr = 'CIPLA.NS'

results = fetch_risk_results(new_stock_tickerr, portfolio)

print(results)