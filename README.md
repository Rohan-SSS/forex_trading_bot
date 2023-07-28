# High Frequency Trading Bot

## Project Description

The HFT bot processes real-time market data from Meta Trader 5 desktop application to make predictions using multiple ML model for different symbols as a single model fails to work with every symbol.
> Note: Only a reference model is provided here which is working for all symbols, So dont trade with real $.
Using the predictions, the bot execute trades and constantly monitors the active trades. If there are active trades which contradicts the prediction, those are closed and new trades according to predictions are taken.
Also it has a trailing SL, which books partials and tries to ensure profits and minimize losses.

## Installation

Clone the project
```bash
git clone https://github.com/Rohan-SSS/high_frequency_trading_bot
cd high_frequency_trading_bot
```

Create virtual environment and install dependencies
```bash
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

Note: It only works in a windows machine as Meta trader 5 is not available for Linux.

## Usage

Run the streamlit app to see the predictions

Open 2 terminals and run the following in one terminal

```bash
python take_trades.py
```

and in another run the following after a min or so
```bash
python monitor_trades.py
```