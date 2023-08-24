from model.make_predicitons import *
from strategy.apr_one import *
from functions_library import *

from datetime import datetime, timedelta
import time

import MetaTrader5 as mt5

if __name__ == "__main__":
    # Starting mt5 if not running in background already
    mt5.initialize()

    # Print out account info
    get_account_info()
    print("-"*100)
    
    # Chosen symbols for trading
        # Default : ["EURUSD", "GBPJPY", "USDJPY", "XAUUSD"]
        # When checking trades every 15 mins ["EURUSD", "GBPJPY", "USDJPY", "USDCAD", "XAUUSD", "USDCHF"]
    symbol_list = ["EURUSDm", "GBPJPYm", "USDJPYm", "USDCADm", "XAUUSDm", "USDCHFm"]

    # To change the lot sizing check functions library send_order()
    # lot = 0.02 at 1:100 leverage

    # To infinity and beyond xD
    while True:

        # active_trade_info stores the currently active trades in a dict of dict
        # {'XAUUSD': {'position': 1,'symbol': 'XAUUSD','ticket': 50548212517,'volume': 0.02,'magic': 0,'profit': 4.16,'price': 1980.83,'price_current': 1978.75,'tp': 1977.83,'sl': 1982.83,'trade_size': 100.0}
        active_trade_info = get_positions()

        # For every symbol from list it checks for existing trades, execute new trades and close conflicting trades 
        for symbol_element in symbol_list:
            
            # Initialize empty dict, which stores current symbol's active trade info 
            # {'position': 1,'symbol': 'XAUUSD','ticket': 50548212517,'volume': 0.02,'magic': 0,'profit': 4.16,'price': 1980.83,'price_current': 1978.75,'tp': 1977.83,'sl': 1982.83,'trade_size': 100.0}
            current_symbol_info = None
            
            # Check if active trade exists, if so store info
            try:
                current_symbol_info = active_trade_info[symbol_element]
            except:
                current_symbol_info = None

            # Get the prediction for current symbol -1 or 0 or 1 using ML model
            # prediction = get_prediction(symbol_element)
            
            # Get the prediction for current symbol -1 or 0 or 1 using strat
            prediction = get_prediction_str(symbol_element)
            
            """
            Note: Trade position for a SELL in mt5 is 1 and for BUY is 0
            """

            # For a buy trade
            if prediction == 1:
                print(f"Prediction for {symbol_element}: BUY")  
                
                # Buy
                take_buy(symbol_element, current_symbol_info)
                
            # For a sell trade
            if prediction == -1:
                print(f"Prediction for {symbol_element}: SELL")  
                
                # Sell
                take_sell(symbol_element, current_symbol_info)
                
            # If prediction is 0 then stfd
            if prediction == 0:
                print(f"No Trade for {symbol_element}\n")

        # Print out the active positions 
        print("\n", show_positions(), "\n", "-"*100, "\n")

        # Get sleep time till the current 30m candle closing
        sleep_time = get_sleep_time()
        print(f"sleeping for {sleep_time}")
        time.sleep(sleep_time)

# END

# Features to add here :
# --------------------------------------------------------------------------------------------
# Remove market opening hours to prevent high volatilty
# Change the time of sleep to a favourable delay
#




