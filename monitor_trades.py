from functions_library import *

import time 
import MetaTrader5 as mt5

if __name__ == "__main__":
    mt5.initialize()

    symbol_list = ["EURUSD", "GBPJPY", "USDJPY", "USDCAD", "XAUUSD", "USDCHF"]

    # Maintains the min and max prices for a symbol to compare, Still not being deleted if the trade is closed
    min_price = {}
    max_price = {}

    # trade_stage keeps track of the trailing sl stages defined below ion code
    trade_stage = {}

    while True:

        active_trade_info = get_positions()
        # {'XAUUSD': {'position': 1,'symbol': 'XAUUSD','ticket': 50548212517,'volume': 0.02,'magic': 0,'profit': 4.16,'price': 1980.83,'price_current': 1978.75,'tp': 1977.83,'sl': 1982.83,'trade_size': 100.0}

        for symbol_element in symbol_list:

            # Empty dict for the symbols
            current_symbol_info = None

            # Check if active trade exists, if so store info
            try:
                current_symbol_info = active_trade_info[symbol_element]
            except:
                current_symbol_info = None

            # It is to check the trade_stage if it exists or not, if yes then pass if not init a 0, or if not active then del if it was previously
            if symbol_element not in trade_stage.keys() and symbol_element in active_trade_info:
                trade_stage[symbol_element] = 0
            elif symbol_element in trade_stage.keys() and symbol_element not in active_trade_info:
                del trade_stage[symbol_element]

            # Monitors Sell positions
            if current_symbol_info != None and current_symbol_info['position'] == 1:

                # Adds a newly created trade symbol to min_price
                if symbol_element not in min_price.keys():
                    min_price[symbol_element] = current_symbol_info['price']

                # Current price and Opening prices for reference for changing tp and sl
                current_price = current_symbol_info['price_current']
                opening_price = current_symbol_info['price']

                point = mt5.symbol_info(symbol_element).point

                # if current_price < current_symbol_info["tp"] + (60 * point) and current_price < min_price[symbol_element]:
                #     time.sleep(3)
                #     sl = current_symbol_info["sl"] - (60 * point)
                #     tp = current_symbol_info["tp"] - (60 * point)
                #     change_info = change_sltp(current_symbol_info, sl, tp)
                
                # If trade reached 80% put sl at 70% and tp + 20% 
                if current_price < opening_price - (240 * point) and current_price < min_price[symbol_element] and trade_stage[symbol_element] == 3:

                    time.sleep(3)
                    sl = opening_price - (210 * point)
                    tp = current_symbol_info["tp"] - 60 * point

                    # Changes the SL and TP
                    change_info = change_sltp(current_symbol_info, sl, tp)
                    
                # If trade reached 70% put sl at 60% 
                elif current_price < opening_price - (210 * point) and current_price < min_price[symbol_element] and trade_stage[symbol_element] == 2:

                    # time.sleep(3)
                    # close_order(symbol_element, current_symbol_info["ticket"], 0.1, 1) 

                    time.sleep(3)
                    sl = opening_price - (180 * point)
                    tp = current_symbol_info["tp"]

                    change_info = change_sltp(current_symbol_info, sl, tp)    

                    # Proceed to stage 3
                    trade_stage[symbol_element] = 3

                # If trade reached 50% put sl at 30%
                elif current_price < opening_price - (150 * point) and current_price < min_price[symbol_element] and trade_stage[symbol_element] == 1:

                    time.sleep(3)      
                    sl = opening_price - (90 * point)
                    tp = current_symbol_info["tp"]

                    change_info = change_sltp(current_symbol_info, sl, tp)
                    trade_stage[symbol_element] = 2

                # Basic Rat trading, Book partials at 30% and put sl at opening price
                elif current_price < opening_price - (90 * point) and current_price < min_price[symbol_element]and trade_stage[symbol_element] == 0:

                    time.sleep(3)
                    close_trade = close_order(symbol_element, current_symbol_info["ticket"], 0.01, 1) 

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

                # Lastly modify the min_price for next irteration, as doing it initially breaks the modifying of sltp
                min_price[symbol_element] = min(current_price, min_price[symbol_element])
            
            # Monitors Sell positions
            if current_symbol_info != None and current_symbol_info['position'] == 0:

                if symbol_element not in max_price.keys():
                    max_price[symbol_element] = current_symbol_info['price']
                
                # Current price and opening price
                current_price = current_symbol_info['price_current']
                opening_price = current_symbol_info['price']

                # 100 point --> 10 pips
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
                    close_trade = close_order(symbol_element, current_symbol_info['ticket'], 0.01, 0)

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

                max_price[symbol_element] = max(current_price, max_price[symbol_element])

            if change_info == ():
                continue
            else:
                print(change_info)