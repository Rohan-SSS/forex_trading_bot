from make_predicitons import *
from execute_trades import *

from datetime import datetime, timedelta
import time

def get_prediction(symbol):
    predictions = make_predictions(symbol)
    return predictions[-1]

taken_trades = {}


if __name__ == '__main__':
    mt5.initialize()
    symbols = ["EURUSD", "GBPJPY", "USDJPY", "USDCAD", "XAUUSD", "USDCHF"]
    max_price = {}
    min_price = {}
    while True:
        for symbol in symbols:
            
            # if symbol in taken_trades:
            #     modify_sltp(max_price, min_price)
            #     print("--------------------------")
            #     print("max_price ", max_price, "min_price ", min_price)

            # else:
            #     print(f"----------{symbol}----------")
            prediction = get_prediction(symbol)

            if prediction == 1:
                # Check if there is an existing sell order for the symbol
                if symbol in taken_trades and taken_trades[symbol]["order_type"] == "sell":
                    # Close the sell order
                    close_order(symbol, taken_trades[symbol]["order_id"], 0.2, "sell")
                    del taken_trades[symbol]

                time.sleep(3)

                # Place a new buy order
                current_trade = send_order(symbol, "buy")
                taken_trades[symbol] = {"order_type": "buy", "order_id": current_trade.order}
                print(f"Trade Buy: {symbol} {current_trade.order}")
            
            elif prediction == -1:
                if symbol in taken_trades and taken_trades[symbol]["order_type"] == "buy":
                    # Close the buy order
                    close_order(symbol, taken_trades[symbol]["order_id"], 0.2, "buy")
                    del taken_trades[symbol]

                time.sleep(3)

                # Place a new sell order
                current_trade = send_order(symbol, "sell")
                taken_trades[symbol] = {"order_type": "sell", "order_id": current_trade.order}
                print(f"Trade Sell: {symbol} {current_trade.order}")

            else:
                print(f"Prediction for {symbol} = {prediction}")

        current_time = datetime.utcnow()
        next_candle_time = current_time + timedelta(minutes=30)  # Get the start time of the next 30-minute candle
        
        # Calculate the time difference between the current time and the start time of the next candle
        sleep_time = (next_candle_time - current_time).total_seconds()
        
        print("\n", show_positions(), "\n")
        print("--------------------")
        print("taken_trades: ", taken_trades)
        time.sleep(sleep_time)