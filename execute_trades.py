import MetaTrader5 as mt5
import pandas as pd

from datetime import datetime as dt
import time

    
def send_order(symbol, order_type):
    lot = 0.02
    deviation = 10

    filling_type = mt5.symbol_info(symbol).filling_mode
    point = mt5.symbol_info(symbol).point

    if order_type == "buy":
        price = mt5.symbol_info_tick(symbol).ask
        type_mt5 =  mt5.ORDER_TYPE_BUY
        tp = price + 300 * point
        sl = price - 200 * point
    elif order_type == "sell":
        price = mt5.symbol_info_tick(symbol).bid
        type_mt5 =  mt5.ORDER_TYPE_SELL
        tp = price - 300 * point
        sl = price + 200 * point
    else:
        raise ValueError("Invalid order type")       
    
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": type_mt5,
        "price": price,
        "deviation": deviation,
        "tp": tp,
        "sl": sl,
        "type_filling": filling_type,
        "type_time": mt5.ORDER_TIME_GTC
    }

    return mt5.order_send(request)


def close_order(symbol, order, lot, order_type):
    
    deviation = 10

    filling_type = mt5.symbol_info(symbol).filling_mode

    if order_type == "buy":
        price = mt5.symbol_info_tick(symbol).bid
        type_mt5 = mt5.ORDER_TYPE_SELL
    elif order_type == "sell":
        price = mt5.symbol_info_tick(symbol).ask
        type_mt5 = mt5.ORDER_TYPE_BUY
    else:
        raise ValueError("Invalid order type")   

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "position":order,
        "volume": lot,
        "type": type_mt5,
        "price": price,
        "deviation": deviation,
        "type_filling": filling_type,
        "type_time": mt5.ORDER_TIME_GTC
    }

    mt5.order_send(request)

def change_sltp(row, sl, tp):

    symbol = row["symbol"]

    # Set filling mode
    filling_type = mt5.symbol_info(symbol).filling_mode

    # Change the sl
    request = {
    "action": mt5.TRADE_ACTION_SLTP,
    "symbol": symbol,
    "position": row["ticket"],
    "volume": row["volume"],
    "type": mt5.ORDER_TYPE_SELL,
    "price": row["price"],
    "sl": sl,
    "tp": tp,
    "type_filling": filling_type,
    "type_time": mt5.ORDER_TIME_GTC,
    }

    return mt5.order_send(request)


def modify_sltp(max_price, min_price):

    summary = show_positions()
    for i in range(summary.shape[0]):
        row = summary.iloc[i]

        symbol = row["symbol"]
        if row["position"] == 1:
            if symbol not in min_price.keys():
                min_price[symbol] = row["price"]

            current_price = row["price_current"]
            opening_price = row["price"]
            point = mt5.symbol_info(symbol).point

            min_price[symbol] = min(current_price, min_price[symbol])

            if current_price <= row["tp"] + (60 * point) and current_price <= min_price[symbol]:
                time.sleep(3)
                sl = row["sl"] - (60 * point)
                tp = row["tp"] - (60 * point)
                change_info = change_sltp(row, sl, tp)
            
            elif current_price <= opening_price - (240 * point) and current_price <= min_price[symbol]:
                time.sleep(3)
                sl = row["sl"] - 60 * point
                tp = row["tp"] - 60 * point
                change_info = change_sltp(row, sl, tp)

            elif current_price <= opening_price - (180 * point) and current_price <= min_price[symbol]:
                time.sleep(3)
                close_order(symbol, row["ticket"], 0.1, "sell") 

                time.sleep(3)
                sl = row["sl"] - 90 * point
                tp = row["tp"]
                change_info = change_sltp(row, sl, tp)          

            elif current_price <= opening_price - (150 * point) and current_price <= min_price[symbol]:
                time.sleep(3)      
                sl = opening_price
                tp = row["tp"]
                change_info = change_sltp(row, sl, tp)

            elif current_price <= opening_price - (90 * point) and current_price <= min_price[symbol]:
                time.sleep
                sl = row["sl"] - (100 * point)
                tp = row["tp"]
                change_info = change_sltp(row, sl, tp)
            else:
                change_info = ()


        if row["position"] == 0:
            if symbol not in max_price.keys():
                max_price[symbol] = row["price"]

            current_price = row["price_current"]
            opening_price = row["price"]
            point = mt5.symbol_info(symbol).point

            max_price[symbol] = max(current_price, max_price[symbol])

            if current_price >= row["tp"] - (60 * point) and current_price >= max_price[symbol]:
                time.sleep(3)
                sl = row["sl"] + (60 * point)
                tp = row["tp"] + (60 * point)
                change_info = change_sltp(row, sl, tp)
            
            elif current_price >= opening_price + (240 * point) and current_price >= max_price[symbol]:
                time.sleep(3)
                sl = row["sl"] + 60 * point
                tp = row["tp"] + 60 * point
                change_info = change_sltp(row, sl, tp)

            elif current_price >= opening_price + (180 * point) and current_price >= max_price[symbol]:
                time.sleep(3)
                change_info = close_order(symbol, row["ticket"], 0.1, "buy") 

                time.sleep(3)
                sl = row["sl"] + 90 * point
                tp = row["tp"]
                change_info = change_sltp(row, sl, tp)          

            elif current_price >= opening_price + (150 * point) and current_price >= max_price[symbol]:
                time.sleep(3)      
                sl = opening_price
                tp = row["tp"]
                change_info = change_sltp(row, sl, tp)

            elif current_price >= opening_price + (90 * point) and current_price >= max_price[symbol]:
                time.sleep
                sl = row["sl"] + (100 * point)
                tp = row["tp"]
                change_info = change_sltp(row, sl, tp)
            else:
                change_info = ()

        if change_info == ():
            return f"No change for {symbol}"
        else:
            return change_info


def show_positions():
    """ Return the current positions. Position=0 --> Buy """    
    # Define the name of the columns that we will create
    columns = ["ticket", "position", "symbol", "volume", "magic", "profit", "price", "price_current", "tp", "sl","trade_size"]

    # Go take the current open trades
    list_current = mt5.positions_get()

    # Create a empty dataframe
    summary = pd.DataFrame()

    # Loop to add each row in dataframe
    for element in list_current:
        
        element_pandas = pd.DataFrame([element.ticket, element.type, element.symbol, element.volume, element.magic,
                                       element.profit, element.price_open, element.price_current, element.tp,
                                       element.sl, mt5.symbol_info(element.symbol).trade_contract_size],
                                      index=columns).transpose()
        summary = pd.concat((summary, element_pandas), axis=0)
    
    try:
        summary["profit %"] = summary.profit / (summary.price * summary.trade_size * summary.volume)
        summary = summary.reset_index(drop=True)
    except:
        pass
    return summary


def get_account_info():
    current_account_info = mt5.account_info()
    print("------------------------------------------------------------------")
    print(f"Login: {mt5.account_info().login} \tserver: {mt5.account_info().server}")
    print(f"Date: {dt.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Balance: {current_account_info.balance} USD, \t Equity: {current_account_info.equity} USD, \t Profit: {current_account_info.profit} USD")
    print(f"Leverage: {current_account_info.leverage} ")
    print(f"Run time: {dt.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("------------------------------------------------------------------")
