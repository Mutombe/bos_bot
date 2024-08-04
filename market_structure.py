# Detect market structure
import time

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
    print(df[["time", "high", "low", "bullish_change", "bearish_change"]].tail())

    return df
