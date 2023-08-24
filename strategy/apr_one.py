import pandas as pd
from ta.volatility import *
from ta.momentum import *

import MetaTrader5 as mt5
from datetime import datetime


# Getting data for making predictions
def get_ticker_data(ticker):
    """
    This fucntion uses Meta Trader 5 application to fetch the real time data needed to make predictions
    """

    mt5.initialize()
    # Compute now date
    from_date = datetime.now()

    # Extract n Ticks before now
    rates = mt5.copy_rates_from(f"{ticker}", mt5.TIMEFRAME_M30, from_date, 1000)

    # Transform Tuple into a DataFrame
    df_rates = pd.DataFrame(rates)

    # Convert number format of the date into date format
    df_rates["time"] = pd.to_datetime(df_rates["time"], unit="s")
    df_rates = df_rates.drop(['spread', 'real_volume'], axis=1)
    df_rates.rename(columns={"tick_volume":"volume"}, inplace=True)
    return df_rates



# Stochastic RSI
def stochrsi_kd(df):
    """Adds STochastic RSI k and d and signal""" 
    # Calculate Stochastic RSI
    stochrsi = StochRSIIndicator(close=df['close'], window=14, smooth1=3, smooth2=3)
    
    df['stochrsi'] = stochrsi.stochrsi()
    df['stochrsi_k'] = stochrsi.stochrsi_k()
    df['stochrsi_d'] = stochrsi.stochrsi_d()

    return df


def stochrsi_signal(df):
    stochrsi = StochasticOscillator(high=df['high'], low=df['low'], close=df['close'], window=14, smooth_window=3)
    df['stoch'] = stochrsi.stoch()
    df['stoch_signal'] = stochrsi.stoch_signal()
    return df

def stochrsi_main(df, ob=0.8, os=0.2):
    stochrsi = StochRSIIndicator(close=df['close'], window=14, smooth1=3, smooth2=3)
    stochrsi_k = stochrsi.stochrsi_k()
    stochrsi_d = stochrsi.stochrsi_d()
    
    is_ob = (stochrsi_k > ob) & (stochrsi_d > ob) & (stochrsi_k < stochrsi_d)
    is_os = (stochrsi_k < os) & (stochrsi_d < os) & (stochrsi_k > stochrsi_d)
    
    signal = pd.Series(np.zeros(len(df)), index=df.index)
    signal[is_ob] = -1
    signal[is_os] = 1
    
    df['stochrsi_signal'] = signal.astype(int)
    
    return df    

def get_prediction_str(ticker):
    df = get_ticker_data(ticker)
    stochrsi_main(df)
    pred = df['stochrsi_signal'].tolist()
    return pred[-1]

# if __name__ == '__main__':
#     ticker = "EURUSDm"
#     df = get_ticker_data(ticker)
#     print(stochrsi_main(df))
    