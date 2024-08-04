import time
from market_structure import detect_market_structure
from historical_data import get_data

def check_for_cms(symbol, timeframe, num_candles):
    print(f"Checking for Change in Market Structure for `{symbol}`..."'\n')
    time.sleep(1)
    df = get_data(symbol, timeframe, num_candles)
    if df is None or df.empty:
        return False, "none", None

    df = detect_market_structure(df)

    cms_detected = False
    direction = "none"

    if df["bullish_change"].iloc[-1]:
        cms_detected = True
        direction = "Bullish"
    elif df["bearish_change"].iloc[-1]:
        cms_detected = True
        direction = "Bearish"
    print(f"CMS detected: {cms_detected}, direction: {direction}")
    return cms_detected, direction, df
