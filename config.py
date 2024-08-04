import MetaTrader5 as mt5

ACCOUNT = 31529305
PASSWORD = "Simbarashe@1700"
SERVER = "Deriv-Demo"

SYMBOLS = [
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

TIMEFRAMES = [
        mt5.TIMEFRAME_M30,
        mt5.TIMEFRAME_H1,
        mt5.TIMEFRAME_H4,
        mt5.TIMEFRAME_D1,
]

NUMBER_OF_CANDLES = 1000