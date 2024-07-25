# Copyright 2024, MetaQuotes Ltd.
# https://www.mql5.com

import MetaTrader5 as mt5
import pandas as pd
import time

# Initialize and connect to MT5
if not mt5.initialize():
    print("initialize() failed, error code =", mt5.last_error())
    quit()

account = 123456  # replace with your account number
password = "your_password"
server = "Deriv-Server"  # replace with your server

authorized = mt5.login(account, password, server)
if authorized:
    print("Connected to Deriv account")
else:
    print("Failed to connect to account. Error code:", mt5.last_error())
    quit()

def get_data(symbol, timeframe, num_candles):
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, num_candles)
    if rates is None:
        print(f"Failed to get rates for {symbol}")
        return None
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    return df

def detect_market_structure(df):
    df['high_shift1'] = df['high'].shift(1)
    df['low_shift1'] = df['low'].shift(1)
    df['high_shift2'] = df['high'].shift(2)
    df['low_shift2'] = df['low'].shift(2)
    
    df['HH'] = (df['high'] > df['high_shift1']) & (df['high_shift1'] > df['high_shift2'])
    df['LL'] = (df['low'] < df['low_shift1']) & (df['low_shift1'] < df['low_shift2'])
    
    df['LH'] = (df['high'] < df['high_shift1']) & (df['high_shift1'] < df['high_shift2'])
    df['HL'] = (df['low'] > df['low_shift1']) & (df['low_shift1'] > df['low_shift2'])

    bullish_change = (df['LL'].shift(1) & df['HH'])
    bearish_change = (df['HH'].shift(1) & df['LL'])

    df['bullish_change'] = bullish_change
    df['bearish_change'] = bearish_change

    return df

def check_for_cms(symbol, timeframe, num_candles):
    df = get_data(symbol, timeframe, num_candles)
    if df is None or df.empty:
        return False, "none", None
    
    df = detect_market_structure(df)
    
    cms_detected = False
    direction = "none"
    
    if df['bullish_change'].iloc[-1]:
        cms_detected = True
        direction = "bullish"
    elif df['bearish_change'].iloc[-1]:
        cms_detected = True
        direction = "bearish"
    
    return cms_detected, direction, df

def place_order(symbol, order_type, volume, price):
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

symbol = "V75"
timeframe = mt5.TIMEFRAME_H4
num_candles = 100
volume = 0.2

while True:
    cms_detected, direction, df = check_for_cms(symbol, timeframe, num_candles)
    if cms_detected:
        print(f"Change in Market Structure detected: {direction}")
        # Trade logic
        if direction == "bullish":
            place_order(symbol, mt5.ORDER_TYPE_BUY, volume)
        elif direction == "bearish":
             place_order(symbol, mt5.ORDER_TYPE_SELL, volume)
    
    time.sleep(60 * 60 * 4)  # Sleep for 4 hours before checking again

mt5.shutdown()


