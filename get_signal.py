from make_predicitons import *
from execute_trades import *

mt5.initialize()

symbol = "XAUUSD"

positions = get_positions()
print(positions)

predictions = make_predictions(symbol)
print(predictions)

current_prediction = predictions[-1]
print(current_prediction)


def take_trade(symbol):
    if current_prediction == 1:
        send_buy_order(symbol)
    elif current_prediction == -1:
        send_sell_order(symbol)


