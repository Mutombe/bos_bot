# Copyright 2024, MetaQuotes Ltd.
# https://www.mql5.com

from datetime import datetime
import pandas as pd
import MetaTrader5 as mt5
import numpy as np
import matplotlib.pyplot as plt

if not mt5.initialize():
   print("mt5 initialization failed. ERROR CODE = " mt5.last_error())
   quit()
   
 account = ""
 password = ""
 server = "Deriv-Server"
 
 authorised = mt5.login(account, password, server)
 if authorised:
   print("Connected to Deriv Account")
 else:
   print("Failed to connect to account. Error code:", mt5.last_error())
   quit()
   
 def get_data(symbol, timeframe, num_candles):
   rates = mt5.copy_rates_from_pos(symbol, timeframe, 0. num_candles)
   df = pd.DataFrame(rates)
   df['time'] = pd.to_datetime(['time'], unit='s')
   return df
   
 def detect_market_structure(df):
    df['high_shift1'] = df['high'].shift(1)
    df['low_shift1'] = df['low'].shift(1)
    df['high_shift2'] = df['high'].shift(2)
    df['low_shift2'] = df['low'].shift(2)
    
    df['HH'] = (df['high'] > df['high_shift1']) & (df['high_shift1'] > df['high_shift2'])
    df['HL'] = (df['low'] > df['low_shift1']) & (df['low_shift1'] > df['low_shift2'])
    
    bullish_change = (df['LL'].shift(1) & df['HH'])
    bearish_change = (df['HH'].shift(1) & df['LL'])
    
    return df
    
 def check_for_sms(symbol, timeframe, num_candles):
   df = get_data(symbol, timeframe, num_candles)
   df = detect_market_structure(df)
   
   cms_detected = False
   direction = "none"
   
   if df['bullish_change'].iloc[-1]:
      cms_detected = True
      direction = "The market has changed direction to BUY"
   elif df['bearish_change'].iloc[-1]:
      cms_detected = True 
      direction = 'The market has changed direction to SELL'
      
   return cms_detected, direction, df
   
 symbols = ['v25(1s)','v',]  
 timeframe = mt5.TIMEFRAME_H4
 num_candles = 100
 
 while True:
   cms_detected, direction, df = check_for_cms([x for x in symbols], timeframe, num_candles)
   if cms_detected:
      print(f"Change in Market Structure detected: {direction}")
      
 
 

mt5.shutdown()

