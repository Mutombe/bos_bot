import time
import pandas as pd
import MetaTrader5 as mt5

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