# Copyright 2024, MetaQuotes Ltd.
# https://www.mql5.com

import datetime
import MetaTrader5 as mt5
import pandas as pd
import time
from config import ACCOUNT, PASSWORD, SERVER

# Initialize and connect to MT5
print("Initializing MT5...")
time.sleep(1)

if not mt5.initialize():
    print("initialize() failed, error code =", mt5.last_error())
    quit()
else:
    print("Initializing...")

time.sleep(1)

account = ACCOUNT
password = PASSWORD
server = SERVER

print("Logging into account...")
time.sleep(1)

authorized = mt5.login(account, password, server)
if authorized:
    print("Connected to Deriv account")
else:
    print("Failed to connect to account. Error code:", mt5.last_error())
    quit()

time.sleep(1)

def get_data(symbol, timeframe, num_candles):
    print(f"Retrieving data for {symbol} with timeframe {timeframe} and {num_candles} candles...")
    time.sleep(1)
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, num_candles)
    if rates is None:
        print(f"Failed to get rates for {symbol}")
        return None
    else:
        print(f"Successfully retrieved rates for {symbol}")
    df = pd.DataFrame(rates)
    df["time"] = pd.to_datetime(df["time"], unit="s")
    return df


def detect_market_structure(df):
    print("Detecting market structure...")
    time.sleep(1)
    df["high_shift1"] = df["high"].shift(1)
    df["low_shift1"] = df["low"].shift(1)
    df["high_shift2"] = df["high"].shift(2)
    df["low_shift2"] = df["low"].shift(2)

    df["HH"] = (df["high"] > df["high_shift1"]) & (
        df["high_shift1"] > df["high_shift2"]
    )
    df["LL"] = (df["low"] < df["low_shift1"]) & (df["low_shift1"] < df["low_shift2"])

    df["LH"] = (df["high"] < df["high_shift1"]) & (
        df["high_shift1"] < df["high_shift2"]
    )
    df["HL"] = (df["low"] > df["low_shift1"]) & (df["low_shift1"] > df["low_shift2"])

    bullish_change = df["LL"].shift(1) & df["HH"]
    bearish_change = df["HH"].shift(1) & df["LL"]

    df["bullish_change"] = bullish_change
    df["bearish_change"] = bearish_change

    print("Market structure detected:")
    print(df[["time", "high", "low", "bullish_change", "bearish_change"]].tail())  # Print the relevant columns

    return df


def check_for_cms(symbol, timeframe, num_candles):
    print(f"Checking for Change in Market Structure for {symbol}...")
    time.sleep(1)
    df = get_data(symbol, timeframe, num_candles)
    if df is None or df.empty:
        return False, "none", None

    df = detect_market_structure(df)

    cms_detected = False
    direction = "none"

    if df["bullish_change"].iloc[-1]:
        cms_detected = True
        direction = "bullish"
    elif df["bearish_change"].iloc[-1]:
        cms_detected = True
        direction = "bearish"
    print(f"CMS detected: {cms_detected}, direction: {direction}")
    return cms_detected, direction, df


def place_order(symbol, order_type, volume, price=None):
    if price is None:
        price = (
            mt5.symbol_info_tick(symbol).ask
            if order_type == mt5.ORDER_TYPE_BUY
            else mt5.symbol_info_tick(symbol).bid
        )
   
    print(f"\n[{datetime.datetime.now()}] Placing order: symbol={symbol}, type={order_type}, volume={volume}, price={price}")
    time.sleep(1)
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": order_type,
        "price": price,
        "deviation": 10,
        "magic": 234000,
        "comment": "python script open",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    result = mt5.order_send(request)
    return result


# List of symbols to analyze
symbols = [
    "Volatility 10 Index",
    "Volatility 25 Index",
    "Volatility 75 Index",
    "Volatility 100 Index",
    "Crash 1000 Index",
    "Crash 500 Index",
    "Crash 300 Index",
    "Boom 1000 Index",
    "Boom 500 Index",
    "Boom 300 Index",
]
timeframe = mt5.TIMEFRAME_M15
num_candles = 100
volume = 0.2

try:
    while True:
        for symbol in symbols:
            cms_detected, direction, df = check_for_cms(symbol, timeframe, num_candles)
            if cms_detected:
                print(f"Change in Market Structure detected for {symbol}: {direction}")
                # Trade logic
                if direction == "bullish":
                    place_order(symbol, mt5.ORDER_TYPE_BUY, volume)
                elif direction == "bearish":
                    place_order(symbol, mt5.ORDER_TYPE_SELL, volume)

        print(f"Sleeping for 15 minutes...")
        time.sleep(60 * 15)  # Sleep for 15 minutes before checking again

except KeyboardInterrupt:
    print("Script interrupted by user")
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    mt5.shutdown()
    print("MT5 shutdown")
