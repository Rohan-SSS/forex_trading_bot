from make_predicitons import *
from execute_trades import *

from datetime import datetime, timedelta
import time

import MetaTrader5 as mt5

if __name__ == "__main__":
    mt5.initialize()
    
    symbols = ["EURUSD", "GBPJPY", "USDJPY", "USDCAD", "XAUUSD", "USDCHF"]

    lot = 0.02

    # Stores active trades information
    taken_trades = {}

    while True:
        for symbol in symbols:
            prediction = get_prediction(symbol)

            if prediction == 1:
                print(f"Prediction for {symbol}: BUY")
                if symbol in taken_trades and taken_trades[symbol]["order_type"] == "sell":
                    close_trade = close_order(symbol, taken_trades[symbol]["order_id"], lot, "sell")
                    print(f"\nTrade closed: {close_trade.request.symbol} {close_trade.order} at {close_trade.price}")

                    del taken_trades[symbol]

                    time.sleep(3)

                    new_buy_trade = send_order(symbol, "buy")
                    taken_trades[symbol] = {"order_type": "buy", "order_id": new_buy_trade.order}

                    print(f"\nTrade executed: BUY {new_buy_trade.request.symbol} at {new_buy_trade.price}")

                elif symbol in taken_trades and taken_trades[symbol]["order_type"] == "buy":
                    pass
                    
                else:
                    new_buy_trade = send_order(symbol, "buy")
                    taken_trades[symbol] = {"order_type": "buy", "order_id": new_buy_trade.order}

                    print(f"\nTrade executed: BUY {new_buy_trade.request.symbol} at {new_buy_trade.price}")

            if prediction == -1:
                print(f"Prediction for {symbol}: SELL")
                if symbol in taken_trades and taken_trades[symbol]["order_type"] == "buy":
                    close_trade = close_order(symbol, taken_trades[symbol]["order_id"], lot, "buy")
                    print(f"\nTrade closed: {close_trade.request.symbol} {close_trade.order} at {close_trade.price}")
                    
                    del taken_trades[symbol]
                    
                    time.sleep(3)

                    new_sell_trade = send_order(symbol, "sell")
                    taken_trades[symbol] = {"order_type": "sell", "order_id": new_sell_trade.order}

                    print(f"\nTrade executed: SELL {new_sell_trade.request.symbol} at {new_sell_trade.price}")

                elif symbol in taken_trades and taken_trades[symbol]["order_type"] == "sell":
                    pass

                else:
                    new_sell_trade = send_order(symbol, "sell")
                    taken_trades[symbol] = {"order_type": "sell", "order_id": new_sell_trade.order}

                    print(f"\nTrade executed: SELL {new_sell_trade.request.symbol} at {new_sell_trade.price}")

            if prediction == 0:
                print(f"\nNo Trade for {symbol}")

        print("\n", show_positions(), "\n", "-"*100, "\n", taken_trades, "\n", "-"*100, "\n")

        current_time = datetime.utcnow()
        minutes_to_add = (30 - current_time.minute % 30) % 30
        next_candle_in = current_time + timedelta(minutes=minutes_to_add)
        if next_candle_in < current_time:
            next_candle_in += timedelta(minutes=30)
        seconds_left = (next_candle_in - current_time).total_seconds()
        print(f"sleeping for {seconds_left}")
        time.sleep(seconds_left)




