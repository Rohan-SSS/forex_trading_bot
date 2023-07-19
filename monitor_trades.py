from make_predicitons import *
from execute_trades import *

import time 
import MetaTrader5 as mt5

if __name__ == "__main__":
    mt5.initialize()

    max_price = {}
    min_price = {}

    symbols = ["EURUSD", "GBPJPY", "USDJPY", "USDCAD", "XAUUSD", "USDCHF"]

    while True:
        summary = show_positions()
        # Example summary
        # ticket           50543855506
        # position                   0
        # symbol                USDCHF
        # volume                  0.02
        # magic                      0
        # profit                  2.79
        # price                0.85748
        # price_current        0.85868
        # tp                   0.86048
        # sl                   0.85548
        # trade_size          100000.0
        # profit %            0.001627

        for i in range(summary.shape[0]):
            current_trade = summary.iloc[i]

            symbol = current_trade["symbol"]

            if current_trade["position"] == 1:
                if symbol not in min_price.keys():
                    min_price[symbol] = current_trade["price"]
                
                current_price = current_trade["price_current"]
                opening_price = current_trade["price"]
                point = mt5.symbol_info(symbol).point

                min_price[symbol] = min(current_price, min_price[symbol])
                if current_price <= current_trade["tp"] + (60 * point) and current_price <= min_price[symbol]:
                    time.sleep(3)
                    sl = current_trade["sl"] - (60 * point)
                    tp = current_trade["tp"] - (60 * point)
                    change_info = change_sltp(current_trade, sl, tp)
                
                elif current_price <= opening_price - (240 * point) and current_price <= min_price[symbol]:
                    time.sleep(3)
                    sl = current_trade["sl"] - 60 * point
                    tp = current_trade["tp"] - 60 * point
                    change_info = change_sltp(current_trade, sl, tp)

                elif current_price <= opening_price - (180 * point) and current_price <= min_price[symbol]:
                    time.sleep(3)
                    close_order(symbol, current_trade["ticket"], 0.1, "sell") 

                    time.sleep(3)
                    sl = current_trade["sl"] - 90 * point
                    tp = current_trade["tp"]
                    change_info = change_sltp(current_trade, sl, tp)          

                elif current_price <= opening_price - (150 * point) and current_price <= min_price[symbol]:
                    time.sleep(3)      
                    sl = opening_price
                    tp = current_trade["tp"]
                    change_info = change_sltp(current_trade, sl, tp)

                elif current_price <= opening_price - (90 * point) and current_price <= min_price[symbol]:
                    time.sleep(3)
                    sl = current_trade["sl"] - (100 * point)
                    tp = current_trade["tp"]
                    change_info = change_sltp(current_trade, sl, tp)
                else:
                    change_info = ()


            if current_trade["position"] == 0:
                if symbol not in max_price.keys():
                    max_price[symbol] = current_trade["price"]

                current_price = current_trade["price_current"]
                opening_price = current_trade["price"]
                point = mt5.symbol_info(symbol).point

                max_price[symbol] = max(current_price, max_price[symbol])

                if current_price >= current_trade["tp"] - (60 * point) and current_price >= max_price[symbol]:
                    time.sleep(3)
                    sl = current_trade["sl"] + (60 * point)
                    tp = current_trade["tp"] + (60 * point)
                    change_info = change_sltp(current_trade, sl, tp)
                
                elif current_price >= opening_price + (240 * point) and current_price >= max_price[symbol]:
                    time.sleep(3)
                    sl = current_trade["sl"] + 60 * point
                    tp = current_trade["tp"] + 60 * point
                    change_info = change_sltp(current_trade, sl, tp)

                elif current_price >= opening_price + (180 * point) and current_price >= max_price[symbol]:
                    time.sleep(3)
                    change_info = close_order(symbol, current_trade["ticket"], 0.1, "buy") 

                    time.sleep(3)
                    sl = current_trade["sl"] + 90 * point
                    tp = current_trade["tp"]
                    change_info = change_sltp(current_trade, sl, tp)          

                elif current_price >= opening_price + (150 * point) and current_price >= max_price[symbol]:
                    time.sleep(3)      
                    sl = opening_price
                    tp = current_trade["tp"]
                    change_info = change_sltp(current_trade, sl, tp)

                elif current_price >= opening_price + (90 * point) and current_price >= max_price[symbol]:
                    time.sleep(3)
                    sl = current_trade["sl"] + (100 * point)
                    tp = current_trade["tp"]
                    change_info = change_sltp(current_trade, sl, tp)
                else:
                    change_info = ()

            if change_info == ():
                continue
            else:
                print(change_info)