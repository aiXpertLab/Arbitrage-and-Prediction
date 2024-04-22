import streamlit as st
import requests
from requests.exceptions import HTTPError, Timeout
import pandas as pd
import numpy as np
from scipy.signal import argrelextrema
import time
    
def introduction():
    st.markdown("""
        ## Methodology
        In our approach to generating trading signals, we employ a variety of techniques that leverage Python’s capabilities in conjunction with the Financial Modeling Prep (FMP) API. Our strategy includes the use of candlestick pattern recognition, peak detection, and the application of statistical tests to identify consolidation phases within the markets.

        ##### Candlestick Pattern Recognition
        We focus on identifying engulfing patterns, which are key indicators of potential market reversals. A bullish engulfing pattern suggests a buying opportunity, whereas a bearish engulfing indicates a potential sell.

        ##### Peak and Trough Analysis
        By detecting local maxima and minima in the price data, we can signal critical turning points in market trends. This method allows traders to anticipate swings and time their entries and exits more effectively.

        ##### Consolidation Detection
        Recognizing consolidation patterns helps traders understand when the market is in a state of equilibrium — where the forces of supply and demand are balanced, often preceding significant price movements.

        ##### Technical Indicators
        We integrate simple moving averages (SMAs) and the Relative Strength Index (RSI) to further refine our signals. These indicators help confirm the trends identified by our primary methods, providing a more robust basis for the trading signals.

        Each component of our methodology is implemented through specific Python functions that process the data, analyze the patterns, and output actionable trading signals. This systematic approach ensures that our trading strategies are data-driven and grounded in statistical analysis, enhancing the probability of successful trades.
""")
    
def signals():
    def fetch_data(symbol, api_key):
        url = f"https://financialmodelingprep.com/api/v3/historical-chart/1min/{symbol}?apikey={api_key}"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data             # raw JSON
        except HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except Timeout as timeout_err:
            print(f"Request timed out: {timeout_err}")
        except Exception as e:
            print(f"Other error occurred: {e}")
        return None
    
    def convert_to_dataframe(data):
        if not data:
            return pd.DataFrame()       #After fetching the data, this function converts the raw JSON response into a structured Pandas DataFrame.
        return (pd.DataFrame(data)
                .assign(date=lambda df: pd.to_datetime(df['date']).dt.tz_localize('UTC'))
                .set_index('date')
                .apply(pd.to_numeric, errors='coerce')
                .resample('5T')
                .agg({'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last'})
                .dropna())
        
    def detect_engulfing(dataframe):
        """Detect bullish and bearish engulfing patterns in a DataFrame."""
        conditions = [
            # Bullish engulfing
            (dataframe['close'].shift(1) < dataframe['open'].shift(1)) &  # previous candle is red
            (dataframe['open'] < dataframe['close']) &  # current candle is green
            (dataframe['open'] < dataframe['close'].shift(1)) &  # current open is lower than previous close
            (dataframe['close'] > dataframe['open'].shift(1)),  # current close is higher than previous open

            # Bearish engulfing
            (dataframe['open'].shift(1) < dataframe['close'].shift(1)) &  # previous candle is green
            (dataframe['close'] < dataframe['open']) &  # current candle is red
            (dataframe['close'] < dataframe['open'].shift(1)) &  # current close is lower than previous open
            (dataframe['open'] > dataframe['close'].shift(1))  # current open is higher than previous close
        ]
        choices = ['bullish engulfing', 'bearish engulfing']
        dataframe['engulfing_pattern'] = np.select(conditions, choices, default=None)
        return dataframe

    def detect_peaks(data, lookahead=5, delta=0):
        # Finding local maxima
        max_idx = argrelextrema(data.values, np.greater, order=lookahead)[0]
        # Finding local minima
        min_idx = argrelextrema(data.values, np.less, order=lookahead)[0]
        
        peaks = pd.DataFrame(data.iloc[max_idx], columns=['peak'])
        troughs = pd.DataFrame(data.iloc[min_idx], columns=['trough'])
        return peaks, troughs
    
    def detect_consolidation(dataframe, window=30):
        """Detect consolidation patterns in a DataFrame based on detected peaks and troughs."""
        highs = dataframe['high'].rolling(window=window, min_periods=1).max()
        lows = dataframe['low'].rolling(window=window, min_periods=1).min()

        peaks, troughs = detect_peaks(dataframe['close'], lookahead=5)

        consolidation = (highs - lows) < (highs.shift(1) - lows.shift(1))
        dataframe['consolidation_pattern'] = np.where(consolidation, 'Possible Consolidation', None)
        return dataframe
    
    def compute_rsi(data, window=14):
        """Compute the Relative Strength Index (RSI) for a given series."""
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.fillna(50)  # Fill NaN values with 50, which is a neutral RSI value

    def generate_signals(dataframe):
        """Generate trading signals based on adjusted SMA, RSI thresholds, and existing patterns."""
        # Calculate SMA and RSI
        dataframe['sma20'] = dataframe['close'].rolling(window=20).mean()
        dataframe['rsi14'] = compute_rsi(dataframe['close'], 14)

        # Adjusted RSI thresholds
        rsi_buy_threshold = 35  # Less extreme oversold condition
        rsi_sell_threshold = 65  # Less extreme overbought condition

        # Generate buy and sell signals using combined and adjusted conditions
        dataframe['buy_signal'] = (
            ((dataframe['engulfing_pattern'] == 'bullish engulfing') |
            (dataframe['consolidation_pattern'] == 'Possible Consolidation')) |
            (dataframe['close'] > dataframe['sma20'] * 1.01) &  # Price is at least 1% above SMA
            (dataframe['rsi14'] < rsi_buy_threshold)
        )
        
        dataframe['sell_signal'] = (
            ((dataframe['engulfing_pattern'] == 'bearish engulfing') |
            (dataframe['consolidation_pattern'] == 'Possible Consolidation')) |
            (dataframe['close'] < dataframe['sma20'] * 0.99) &  # Price is at least 1% below SMA
            (dataframe['rsi14'] > rsi_sell_threshold)
        )
        return dataframe
    
    def buy_sell_price(dataframe):
        """Print out buy and sell signals from the dataframe."""
        for index, row in dataframe.iterrows():
            if row['buy_signal']:
                print(f"Buy Signal: Buy at {row['close']} on {index}")
            elif row['sell_signal']:
                print(f"Sell Signal: Sell at {row['close']} on {index}")

    def final_signals(api_key, symbol):
        while True:
            try:
                # Fetch and prepare data
                raw_data = fetch_data(symbol, api_key)
                dataframe = convert_to_dataframe(raw_data)
                if not dataframe.empty:
                    # Process data through your trading functions
                    dataframe = detect_engulfing(dataframe)
                    dataframe = detect_consolidation(dataframe)
                    dataframe = generate_signals(dataframe)
                    buy_sell_price(dataframe)
                else:
                    print("No new data to process.")
                time.sleep(60)  # Sleep for 1 minutes (60 seconds)
            except Exception as e:
                print(f"An error occurred: {e}")
                time.sleep(60)  # Wait 1 minutes before retrying
                
    