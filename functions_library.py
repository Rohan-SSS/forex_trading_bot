# IMPORTS 

import MetaTrader5 as mt5
import pandas as pd

from datetime import datetime as dt
from datetime import timedelta
import time


# FUNCTIONS
    
def send_order(symbol, order_type):
    """This function creates and sends buy or sell trade

    Args:
        symbol (str): currency_pair
        order_type (int): Buy:0, Sell:1

    Raises:
        MT5 OrderSendResult object error if order fails

    Returns:
        OrderSendResult object (): Information of the order executed

        OrderSendResult(retcode=10009, deal=50548640516, order=50548520509, volume=0.02, 
        price=139.514, bid=139.514, ask=139.518, comment='Request executed', request_id=3448703960, 
        retcode_external=0, request=TradeRequest(action=1, magic=0, order=0, symbol='USDJPY', volume=0.02, 
        price=139.514, stoplimit=0.0, sl=139.714, tp=139.214, deviation=10, type=1, type_filling=1, 
        type_time=0, expiration=0, comment='', position=0, position_by=0))

    """    

    # Lot size, change if needed
    lot = 0.02
    deviation = 10

    # MT5 filling mode for order request
    filling_type = mt5.symbol_info(symbol).filling_mode

    # Point for the symbol, 100 --> 10 pips
    point = mt5.symbol_info(symbol).point

    # For a buy order
    if order_type == 0:
        # Buy is done at ask price 
        price = mt5.symbol_info_tick(symbol).ask
        # Order type --> Buy
        type_mt5 =  mt5.ORDER_TYPE_BUY
        tp = price + 300 * point
        sl = price - 200 * point
    
    # For a Sell order
    elif order_type == 1:
        # Sell is done at bid price
        price = mt5.symbol_info_tick(symbol).bid
        # Order type --> Sell
        type_mt5 =  mt5.ORDER_TYPE_SELL
        tp = price - 300 * point
        sl = price + 200 * point
    
    # MT5 request for creating order
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

    # Sending the created order for execution also returns the result object
    return mt5.order_send(request)


def close_order(symbol, ticket, lot, order_type):
    """Closes an existing order, mainly for closing conflicting trades and/or bookinf partial profit or BE

    Args:
        symbol (str): currency_pair
        ticket (int): ticket number
        lot (float): volume of trade
        order_type (int): Buy:0, Sell:1

    Raises:
        MT5 OrderSendResult object error if order fails

    Returns:
        OrderSendResult object (): Information of the order executed
    """    
    deviation = 10

    filling_type = mt5.symbol_info(symbol).filling_mode

    # If order needs to be sold, meaning closing buy order
    if order_type == 1:
        price = mt5.symbol_info_tick(symbol).bid
        type_mt5 = mt5.ORDER_TYPE_SELL
    
    # If order needs to be bought, meaning closing sell order
    elif order_type == 0:
        price = mt5.symbol_info_tick(symbol).ask
        type_mt5 = mt5.ORDER_TYPE_BUY

    # Create close request
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "position":ticket,
        "volume": lot,
        "type": type_mt5,
        "price": price,
        "deviation": deviation,
        "type_filling": filling_type,
        "type_time": mt5.ORDER_TIME_GTC
    }

    # Send request
    return mt5.order_send(request)


def take_buy(symbol_element, current_symbol_info): 
    """Main function for carrying out buy orders, and closing sells

    Args:
        symbol_element (str): currency pair
        current_symbol_info (dict): current symbol information dictionary
    """    

    # check if there is an existing trade for the current symbol which is a SELL 
    if current_symbol_info != None and current_symbol_info['position'] == 1:

        # Sleep is required as mt5 sometimes doesnt execute actions
        time.sleep(3)

        # Close the existing SELL trade, 1 here denote that a SELL trade needs closing
        close_trade = close_order(symbol_element, current_symbol_info['ticket'], current_symbol_info['volume'], 1)

        # If failed then try again, atm only once 
        if close_trade.order == 0:
            print(f"\nTrade couldn't be closed for {close_trade.request.symbol}, trying again...")

            time.sleep(3)
            close_trade = close_order(symbol_element, current_symbol_info['ticket'], current_symbol_info['volume'], 1)

        # If failed again then dont close, fuck it
        if close_trade.order == 0:
            print(f"\nTrade couldn't be closed for {close_trade.request.symbol}, moving on...")
        else:
            # Confirmation for closing the SELL trade
            print(f"\nTrade closed: {close_trade.request.symbol} {close_trade.order} at {close_trade.price}")

        time.sleep(3)

        # Now execute a BUY trade as predicted by the model, BUY == 0
        new_buy_trade = send_order(symbol_element, 0)
        
        # Try again if failed
        if new_buy_trade.order == 0:
            time.sleep(3)
            print(f"\nBUY trade not executed: {new_buy_trade.request.symbol} trying again...")
            new_buy_trade = send_order(symbol_element, 0)

        if new_buy_trade.order == 0:
            print(f"\nTrade for {new_buy_trade.request.symbol} failed, moving on...")
        else:
            # Confirmation
            print(f"\nTrade executed: BUY {new_buy_trade.request.symbol} at {new_buy_trade.price}")

    # If the pred = 1 and there is already a BUY trade active for the symbol then dont do anything
    elif current_symbol_info != None and current_symbol_info['position'] == 0:
        pass

    # If no trade exists for the current symbol then create a new BUY order and execute
    else:
        time.sleep(3)

        # New trade executed, BUY == 0
        new_buy_trade = send_order(symbol_element, 0)

        if new_buy_trade.order == 0:
            time.sleep(3)
            print(f"\nBUY trade not executed: {new_buy_trade.request.symbol} trying again...")
            new_buy_trade = send_order(symbol_element, 0)

        if new_buy_trade.order == 0:
            print(f"\nTrade for {new_buy_trade.request.symbol} failed, moving on...")
        else:
            print(f"\nTrade executed: BUY {new_buy_trade.request.symbol} at {new_buy_trade.price}")
            

def take_sell(symbol_element, current_symbol_info):
    """Main function for carrying out sell orders, and closing buys

    Args:
        symbol_element (str): currency pair
        current_symbol_info (dict): current symbol information dictionary
    """    

    # check if there is an existing trade for the current symbol which is a BUY 
    if current_symbol_info != None and current_symbol_info['position'] == 0:

        time.sleep(3)

        # Close the existing BUY trade, 0 here denote that a BUY trade needs closing
        close_trade = close_order(symbol_element, current_symbol_info['ticket'], current_symbol_info['volume'], 0)
        
        # Try again if failed
        if close_trade.order == 0:
            print(f"\nTrade couldn't be closed for {close_trade.request.symbol}, trying again...")
            time.sleep(3)
            close_trade = close_order(symbol_element, current_symbol_info['ticket'], current_symbol_info['volume'], 0)

        # ef it
        if close_trade.order == 0:
            print(f"\nTrade couldn't be closed for {close_trade.request.symbol}, moving on...")
        else:   
            print(f"\nTrade closed: {close_trade.request.symbol} {close_trade.order} at {close_trade.price}")

        time.sleep(3)

        # Execute a sell trade
        new_sell_trade = send_order(symbol_element, 1)

        if new_sell_trade.order == 0:
            print(f"\nSELL trade not executed: {new_sell_trade.request.symbol} Trying again...")
            new_sell_trade = send_order(symbol_element, 1)

        if new_sell_trade.order == 0:
            print(f"\nSELL trade for {new_sell_trade.request.symbol} Failed, moving on...")
        else:
            print(f"\nTrade executed: SELL {new_sell_trade.request.symbol} at {new_sell_trade.price}")

    # If the pred = -1 and there is already a SELL trade active for the symbol then dont do anything
    elif current_symbol_info != None and current_symbol_info['position'] == 1:
        pass

    # If no trade exists for the current symbol then create a new SELL order and execute
    else:
        time.sleep(3)

        # New trade executed, SELL == 1
        new_sell_trade = send_order(symbol_element, 1)
        
        if new_sell_trade.order == 0:
            print(f"\nSELL trade not executed: {new_sell_trade.request.symbol} Trying again...")
            new_sell_trade = send_order(symbol_element, 1)

        if new_sell_trade.order == 0:
            print(f"\nSELL trade for {new_sell_trade.request.symbol} Failed, moving on...")
        else:
            print(f"\nTrade executed: SELL {new_sell_trade.request.symbol} at {new_sell_trade.price}")


def change_sltp(current_symbol_info, sl, tp):

    symbol = current_symbol_info["symbol"]

    # Set filling mode
    filling_type = mt5.symbol_info(symbol).filling_mode

    # Change the sl
    request = {
    "action": mt5.TRADE_ACTION_SLTP,
    "symbol": symbol,
    "position": current_symbol_info["ticket"],
    "volume": current_symbol_info["volume"],
    "type": mt5.ORDER_TYPE_SELL,
    "price": current_symbol_info["price"],
    "sl": sl,
    "tp": tp,
    "type_filling": filling_type,
    "type_time": mt5.ORDER_TIME_GTC,
    }

    return mt5.order_send(request)


def show_positions():
    """ Return the current positions. Position=0 --> Buy Position=1 --> Sell"""    
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


def get_positions():
    """ Return the current positions. Position=0 --> Buy Position=1 --> Sell"""    

    # Get the current open trades
    list_current = mt5.positions_get()

    # Create an empty dictionary to store the trade details
    summary = {}

    # Loop to add each trade details to the dictionary
    for element in list_current:
        trade_data = {
            "position": element.type, 
            "symbol": element.symbol,
            "ticket": element.ticket,
            "volume": element.volume,
            "profit": element.profit,
            "price": element.price_open,
            "price_current": element.price_current,
            "tp": element.tp,
            "sl": element.sl
        }
        summary[element.symbol] = trade_data
    
    return summary


def get_sleep_time():
    current_time = dt.utcnow()
    minutes_to_add = (30 - current_time.minute % 30) % 30
    next_candle_in = current_time + timedelta(minutes=minutes_to_add)
    if next_candle_in < current_time:
        next_candle_in += timedelta(minutes=30)
    seconds_left = (next_candle_in - current_time).total_seconds()
    return seconds_left


def get_account_info():
    current_account_info = mt5.account_info()
    print("------------------------------------------------------------------")
    print(f"Login: {mt5.account_info().login} \tserver: {mt5.account_info().server}")
    print(f"Date: {dt.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Balance: {current_account_info.balance} USD, \t Equity: {current_account_info.equity} USD, \t Profit: {current_account_info.profit} USD")
    print(f"Leverage: {current_account_info.leverage} ")
    print(f"Run time: {dt.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("------------------------------------------------------------------")
