from make_predicitons import *
from functions_library import *

import time 
import MetaTrader5 as mt5

if __name__ == "__main__":
    mt5.initialize()

    symbol_list = ["EURUSD", "GBPJPY", "USDJPY", "USDCAD", "XAUUSD", "USDCHF"]

    min_price = {}
    max_price = {}

    trade_stage = {}

    while True:

        active_trade_info = get_positions()
        # Example 
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

        for symbol_element in symbol_list:
            current_symbol_info = None
            # Check if active trade exists, if so store info
            try:
                current_symbol_info = active_trade_info[symbol_element]

            except:
                current_symbol_info = None
                
            if symbol_element not in trade_stage.keys() and symbol_element in active_trade_info:
                trade_stage[symbol_element] = 0
            elif symbol_element in trade_stage.keys() and symbol_element not in active_trade_info:
                del trade_stage[symbol_element]

            if current_symbol_info != None and current_symbol_info['position'] == 1:
                if symbol_element not in min_price.keys():
                    min_price[symbol_element] = current_symbol_info['price']

                current_price = current_symbol_info['price_current']
                opening_price = current_symbol_info['price']

                point = mt5.symbol_info(symbol_element).point

                # if current_price < current_symbol_info["tp"] + (60 * point) and current_price < min_price[symbol_element]:
                #     time.sleep(3)
                #     sl = current_symbol_info["sl"] - (60 * point)
                #     tp = current_symbol_info["tp"] - (60 * point)
                #     change_info = change_sltp(current_symbol_info, sl, tp)
                
                if current_price < opening_price - (240 * point) and current_price < min_price[symbol_element]:
                    time.sleep(3)
                    sl = opening_price - (210 * point)
                    tp = current_symbol_info["tp"] - 60 * point

                    change_info = change_sltp(current_symbol_info, sl, tp)

                elif current_price < opening_price - (210 * point) and current_price < min_price[symbol_element] and trade_stage[symbol_element] == 2:
                    # time.sleep(3)
                    # close_order(symbol_element, current_symbol_info["ticket"], 0.1, 1) 

                    time.sleep(3)
                    sl = opening_price - (180 * point)
                    tp = current_symbol_info["tp"]

                    change_info = change_sltp(current_symbol_info, sl, tp)          
                    trade_stage[symbol_element] = 3

                elif current_price < opening_price - (150 * point) and current_price < min_price[symbol_element] and trade_stage[symbol_element] == 1:
                    time.sleep(3)      
                    sl = opening_price - (90 * point)
                    tp = current_symbol_info["tp"]

                    change_info = change_sltp(current_symbol_info, sl, tp)
                    trade_stage[symbol_element] = 2

                elif current_price < opening_price - (90 * point) and current_price < min_price[symbol_element]and trade_stage[symbol_element] == 0:
                    time.sleep(3)
                    close_trade = close_order(symbol_element, current_symbol_info["ticket"], 0.01, 0) 

                    # If failed then try again, atm only once 
                    if close_trade.order == 0:
                        print(f"\nTrade couldn't be closed for {close_trade.request.symbol}, trying again...")

                        time.sleep(3)
                        close_trade = close_order(symbol_element, current_symbol_info['ticket'], 0.01, 0)

                    # If failed again then dont close, fuck it
                    if close_trade.order == 0:
                        print(f"\nTrade couldn't be closed for {close_trade.request.symbol}, moving on...")
                        print(close_trade)
                    else:
                        # Confirmation for closing the SELL trade
                        print(f"\nTrade closed: {close_trade.request.symbol} {close_trade.order} at {close_trade.price}")

                    time.sleep(3)
                    sl = opening_price
                    tp = current_symbol_info["tp"]

                    change_info = change_sltp(current_symbol_info, sl, tp)
                    trade_stage[symbol_element] = 1
                else:
                    change_info = ()

                min_price[symbol_element] = min(current_price, min_price[symbol_element])
            
            if current_symbol_info != None and current_symbol_info['position'] == 0:
                if symbol_element not in max_price.keys():
                    max_price[symbol_element] = current_symbol_info['price']
                
                current_price = current_symbol_info['price_current']
                opening_price = current_symbol_info['price']

                point = mt5.symbol_info(symbol_element).point

                # if current_price < current_symbol_info["tp"] + (60 * point) and current_price < min_price[symbol_element]:
                #     time.sleep(3)
                #     sl = current_symbol_info["sl"] - (60 * point)
                #     tp = current_symbol_info["tp"] - (60 * point)
                #     change_info = change_sltp(current_symbol_info, sl, tp)
                
                if current_price > opening_price + (270 * point) and current_price > max_price[symbol_element] and trade_stage[symbol_element] == 3:
                    time.sleep(3)
                    sl = opening_price - (240 * point)
                    tp = current_symbol_info["tp"] - 60 * point

                    change_info = change_sltp(current_symbol_info, sl, tp)

                elif current_price > opening_price + (210 * point) and current_price > max_price[symbol_element] and trade_stage[symbol_element] == 2:
                    # time.sleep(3)
                    # close_order(symbol_element, current_symbol_info["ticket"], 0.1, 1) 

                    time.sleep(3)
                    sl = opening_price - (180 * point)
                    tp = current_symbol_info["tp"]

                    change_info = change_sltp(current_symbol_info, sl, tp)          
                    trade_stage[symbol_element] = 3

                elif current_price > opening_price + (150 * point) and current_price > max_price[symbol_element] and trade_stage[symbol_element] == 1:
                    time.sleep(3)      
                    sl = opening_price - (90 * point)
                    tp = current_symbol_info["tp"]

                    change_info = change_sltp(current_symbol_info, sl, tp)
                    trade_stage[symbol_element] = 2

                elif current_price > opening_price + (90 * point) and current_price > max_price[symbol_element]  and trade_stage[symbol_element] == 0:
                    time.sleep(3)
                    close_trade = close_order(symbol_element, current_symbol_info['ticket'], 0.01, 1)

                    # If failed then try again, atm only once 
                    if close_trade.order == 0:
                        print(f"\nTrade couldn't be closed for {close_trade.request.symbol}, trying again...")

                        time.sleep(3)
                        close_trade = close_order(symbol_element, current_symbol_info['ticket'], 0.01, 1)

                    # If failed again then dont close, fuck it
                    if close_trade.order == 0:
                        print(f"\nTrade couldn't be closed for {close_trade.request.symbol}, moving on...")
                        print(close_trade)
                    else:
                        # Confirmation for closing the SELL trade
                        print(f"\nTrade closed: {close_trade.request.symbol} {close_trade.order} at {close_trade.price}")

                    time.sleep(3)
                    sl = opening_price
                    tp = current_symbol_info["tp"]

                    change_info = change_sltp(current_symbol_info, sl, tp)
                    trade_stage[symbol_element] = 1
                else:
                    change_info = ()

                max_price[symbol_element] = max(current_price, max_price[symbol_element])

            if change_info == ():
                continue
            else:
                print(change_info)