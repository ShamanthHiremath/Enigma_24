import os
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential, load_model
from keras.layers import LSTM, Dense
import joblib
from datetime import datetime
from sklearn.model_selection import TimeSeriesSplit

# Define technical indicators
def getSMA(data, window):
    data[f'sma_{window}'] = data['Close'].rolling(window=window).mean()
    return data

def getEMA(data, window):
    data[f'ema_{window}'] = data['Close'].ewm(span=window, adjust=False).mean()
    return data

def getMACD(data, fast=12, slow=26, signal=9):
    data['macd'] = data['Close'].ewm(span=fast, adjust=False).mean() - data['Close'].ewm(span=slow, adjust=False).mean()
    data['macd_signal'] = data['macd'].ewm(span=signal, adjust=False).mean()
    data['macd_value'] = data['macd'] - data['macd_signal']
    return data

def getRSI(data, window=14):
    delta = data['Close'].diff(1)
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=window, min_periods=1).mean()
    avg_loss = loss.rolling(window=window, min_periods=1).mean()
    rs = avg_gain / avg_loss
    data[f'rsi_{window}'] = 100 - (100 / (1 + rs))
    return data

# Train or load LSTM model
def train_or_load_model(ticker, start_date, end_date, model_dir="models/", n_splits=10, epochs=100, batch_size=8):
    model_path = os.path.join(model_dir, f"{ticker}_model.h5")
    scaler_path = os.path.join(model_dir, f"{ticker}_scaler.pkl")
    os.makedirs(model_dir, exist_ok=True)

    if os.path.exists(model_path) and os.path.exists(scaler_path):
        # Load model and scaler
        print("Loading saved model and scaler...")
        model = load_model(model_path)
        scaler = joblib.load(scaler_path)
    else:
        # Fetch data
        df = yf.download(ticker, start=start_date, end=end_date)
        if df.empty:
            raise ValueError(f"No data found for ticker {ticker}. Check the ticker symbol and date range.")

        print("Training model...")
        df = df[['Open', 'High', 'Low', 'Close', 'Volume']].dropna()

        # Add technical indicators
        df = getSMA(df, 20)
        df = getSMA(df, 50)
        df = getEMA(df, 20)
        df = getEMA(df, 50)
        df = getMACD(df)
        df = getRSI(df, 14)
        df.dropna(inplace=True)

        # Prepare features and target
        features = ['Open', 'High', 'Low', 'Volume', 'sma_20', 'sma_50', 'ema_20', 'ema_50', 'macd_value', 'rsi_14']
        target = 'Close'

        scaler = MinMaxScaler()
        scaled_features = scaler.fit_transform(df[features])
        scaled_df = pd.DataFrame(scaled_features, columns=features, index=df.index)

        # Time series split
        timesplit = TimeSeriesSplit(n_splits=n_splits)
        for train_index, test_index in timesplit.split(scaled_df):
            X_train, X_test = scaled_df.iloc[train_index], scaled_df.iloc[test_index]
            y_train, y_test = df[target].iloc[train_index], df[target].iloc[test_index]

        # Reshape for LSTM
        X_train = X_train.values.reshape(X_train.shape[0], 1, X_train.shape[1])
        X_test = X_test.values.reshape(X_test.shape[0], 1, X_test.shape[1])

        # Build LSTM model
        model = Sequential()
        model.add(LSTM(50, input_shape=(1, len(features)), activation='relu'))
        model.add(Dense(1))
        model.compile(optimizer='adam', loss='mean_squared_error')

        # Train the model
        model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size, verbose=1, shuffle=False)

        # Save model and scaler
        model.save(model_path)
        joblib.dump(scaler, scaler_path)
        print(f"Model saved to {model_path}")
        print(f"Scaler saved to {scaler_path}")

        # Predict on test set
        y_pred = model.predict(X_test).flatten()
        y_test = y_test.values

        # Plot actual vs predicted
        plt.figure(figsize=(10, 6))
        plt.plot(y_test, label="Actual Prices", color="blue")
        plt.plot(y_pred, label="Predicted Prices", color="red", linestyle="--")
        plt.title(f"Actual vs Predicted Prices for {ticker}")
        plt.xlabel("Time (Test Data)")
        plt.ylabel("Stock Price")
        plt.legend()
        plt.show()

    return model, scaler

def stock_price_predictor(ticker, start_date, end_date, model_dir="models/"):
    model, scaler = train_or_load_model(ticker, start_date, end_date, model_dir)

    # Load the latest data for prediction
    df = yf.download(ticker, start=start_date, end=end_date)
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']].dropna()
    df = getSMA(df, 20)
    df = getSMA(df, 50)
    df = getEMA(df, 20)
    df = getEMA(df, 50)
    df = getMACD(df)
    df = getRSI(df, 14)
    df.dropna(inplace=True)

    # Prepare the last 60 rows for prediction
    features = ['Open', 'High', 'Low', 'Volume', 'sma_20', 'sma_50', 'ema_20', 'ema_50', 'macd_value', 'rsi_14']
    if len(df) < 60:
        raise ValueError("Not enough data to create 60 time steps for prediction.")

    last_60_rows = df[features].iloc[-60:].values
    last_60_scaled = scaler.transform(last_60_rows)
    last_60_scaled = last_60_scaled.reshape(1, 60, -1)  # Reshape to (1, 60, 10)

    # Predict the next day's price
    next_day_price = model.predict(last_60_scaled).flatten()[0]
    print(f"Predicted next day price for {ticker}: {next_day_price:.2f}")
    return next_day_price


if __name__ == "__main__":
    ticker = "AAPL"
    start_date = "2020-01-01"  # Start date for training and testing
    end_date = datetime.now().strftime("%Y-%m-%d")  # End date for training/testing
    
    print(f"Predicting stock price for {ticker} from {start_date} to {end_date}...")
    
    try:
        # Predict the next day's stock price
        predicted_price = stock_price_predictor(ticker, start_date, end_date, model_dir="models/")
        print(f"The predicted next day price for {ticker} is: ${predicted_price:.2f}")
    except Exception as e:
        print(f"An error occurred: {e}")