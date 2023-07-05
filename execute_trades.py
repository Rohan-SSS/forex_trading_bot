import MetaTrader5 as mt5
import pandas as pd

from datetime import datetime as dt
import time

def send_buy_order(symbol):
    lot = 0.02
    deviation = 10

    filling_type = mt5.symbol_info(symbol).filling_mode

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": mt5.ORDER_TYPE_BUY,
        "price": mt5.symbol_info_tick(symbol).ask,
        "deviation": deviation,
        "type_filling": filling_type,
        "type_time": mt5.ORDER_TIME_GTC
    }

    mt5.order_send(request)


def send_sell_order(symbol):
    lot = 0.02
    deviation = 10

    filling_type = mt5.symbol_info(symbol).filling_mode

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": mt5.ORDER_TYPE_SELL,
        "price": mt5.symbol_info_tick(symbol).bid,
        "deviation": deviation,
        "type_filling": filling_type,
        "type_time": mt5.ORDER_TIME_GTC
    }
    
    mt5.order_send(request)

def get_positions():

    positions = mt5.positions_get()

    # Example for mt5.positions_get()
    # ...
    # OrderSendResult(retcode=10004, deal=0, order=0, volume=0.0, price=0.0, bid=1929.22, ask=1929.31, 
    # comment='Requote', request_id=1474138634, retcode_external=0, request=TradeRequest(action=1, 
    # magic=0, order=0, symbol='XAUUSD', volume=0.02, price=1929.33, stoplimit=0.0, sl=0.0, tp=0.0, 
    # deviation=10, type=0, type_filling=3, type_time=0, expiration=0, comment='', position=0, position_by=0))

    if positions is None:
        print("No positions Taken.")
        return
    
    position_info = []

    for position in positions:
        ticket = position.ticket
        symbol = position.symbol
        open_price = position.price_open
        volume = position.volume
        sl = position.sl
        tp = position.tp
        trade_time = dt.utcfromtimestamp(position.time).strftime("%Y-%m-%d %H:%M:%S")

        position_info.append({
            "Symbol": symbol,
            "Ticket": ticket,
            "Time": trade_time,
            "Volume": volume,
            "Open Price": open_price,
            "Stop Loss": sl,
            "Take Profit": tp
        })

    return position_info