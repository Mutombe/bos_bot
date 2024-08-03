import MetaTrader5 as mt5
import pandas as pd
import time
import logging
from sma_trend import detect_trend
from dynamic_size import calculate_position_size
from support_and_resistance import identify_support_resistance
from config import ACCOUNT, PASSWORD, SERVER
from trailing import trail_stop_loss

logging.basicConfig(
    filename="trading_bot.log", level=logging.INFO, format="%(asctime)s %(message)s"
)

open_positions = {}


# Initialize connection to MetaTrader 5
def initialize_mt5(account, password, server):
    mt5.initialize()
    if mt5.initialize():
        print("Initializing...")
    else:
        print("Failed to initialize MetaTrader 5")
    time.sleep(1)
    authorized = mt5.login(account, password, server)
    if not authorized:
        print(
            f"Failed to connect to account #{account}, error code: {mt5.last_error()}"
        )
        logging.error(
            f"Failed to connect to account #{account}, error code: {mt5.last_error()}"
        )
    else:
        logging.info(f"Connected to account #{account}")


# Fetch historical data
def get_historical_data(symbol, timeframe, num_candles):
    print(
        f"Retrieving data for {symbol} with timeframe {timeframe} and {num_candles} candles..."
    )
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


# Check for market structure break
def check_market_structure_break(
    trend, support_levels, resistance_levels, current_price
):
    # Checking for market structure break using resistance and support
    print("# Checking for market structure break using resistance and support...")
    time.sleep(1)
    if trend == "uptrend" and current_price > resistance_levels[-1]:
        print("Bullish break detected")
        return True
    elif trend == "downtrend" and current_price < support_levels[-1]:
        print("Bearing break detected")
        return True
    print("No conclusive market signal")
    return False


# Place order
def place_order(symbol, order_type, volume, price, sl, tp):
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": order_type,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": 20,
        "magic": 234000,
        "comment": "Trend Following Strategy",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:

        logging.error(f"Order send `failed` : {result}")
        print(f"Order placement `failed` : {result}")
    else:
        logging.info(f"Order placement result: {result}")
        print(f"Order placement result {result}")
        time.sleep(1)
    print(f"Order placement successful...")
    return result


# Strategy implementation
def strategy(symbols, timeframe, account, password, server):

    initialize_mt5(account, password, server)

    for symbol in symbols:
        data = get_historical_data(symbol, timeframe, 1000)
        trend = detect_trend(data)
        support_levels, resistance_levels = identify_support_resistance(data)

        current_price = (
            mt5.symbol_info_tick(symbol).ask
            if trend == "uptrend"
            else mt5.symbol_info_tick(symbol).bid
        )
        market_structure_break = check_market_structure_break(
            trend, support_levels, resistance_levels, current_price
        )

        if market_structure_break:
            account_info = mt5.account_info()
            account_balance = account_info.balance
            risk_per_trade = 0.01  # Risk 1% of account per trade
            stop_loss_pips = 50  # Stop loss in pips
            pip_value = 10  # Pip value in the account currency
            trail_amount = 50

            volume = calculate_position_size(
                account_balance, risk_per_trade, stop_loss_pips, pip_value
            )

            if trend == "uptrend":
                tp = resistance_levels[-1] + (
                    resistance_levels[-1] - support_levels[-1]
                )  # TP calculation
                sl = support_levels[-1] - (
                    resistance_levels[-1] - support_levels[-1]
                )  # SL calculation
                initial_entry = place_order(
                    symbol, mt5.ORDER_TYPE_BUY, volume, current_price, sl, tp
                )
                if initial_entry.retcode == mt5.TRADE_RETCODE_DONE:
                    open_positions[symbol] = initial_entry.order
                    logging.info(
                        f"Initial buy order placed for {symbol} with a Lot Size of `{volume}`, SL of {sl} & TP of {tp}"
                    )
                    print(
                        f"Initial buy order placed for {symbol} with a Lot Size of `{volume}`, SL of {sl} & TP of {tp}"
                    )
                    while True:
                        data = get_historical_data(symbol, timeframe, 1000)
                        trend = detect_trend(data)
                        if trend != "uptrend":
                            break
                        support_levels, resistance_levels = identify_support_resistance(
                            data
                        )
                        current_price = mt5.symbol_info_tick(symbol).bid
                        if current_price > initial_entry.price:
                            print(
                                f"Market in profit for {symbol}, considering scaling in."
                            )
                            pullback_entry = place_order(
                                symbol,
                                mt5.ORDER_TYPE_BUY,
                                volume,
                                current_price,
                                sl,
                                tp,
                            )
                            if pullback_entry.retcode == mt5.TRADE_RETCODE_DONE:
                                logging.info(
                                    f"Scaling in buy order placed for {symbol}"
                                )
                    print(f"Adjusting trailing stop loss for {symbol}.")
                    trail_stop_loss(pullback_entry, trail_amount)
            elif trend == "downtrend":
                tp = support_levels[-1] - (
                    resistance_levels[-1] - support_levels[-1]
                )  # TP calculation
                sl = resistance_levels[-1] + (
                    resistance_levels[-1] - support_levels[-1]
                )  # SL calculation
                initial_entry = place_order(
                    symbol, mt5.ORDER_TYPE_SELL, volume, current_price, sl, tp
                )
                if initial_entry.retcode == mt5.TRADE_RETCODE_DONE:
                    open_positions[symbol] = initial_entry.order
                    logging.info(
                        f"Initial sell order placed for {symbol} with a Lot Size of `{volume}`, SL of {sl} & TP of {tp}"
                    )
                    print(
                        f"Initial sell order placed for {symbol} with a Lot Size of `{volume}`, SL of {sl} & TP of {tp}"
                    )
                    while True:
                        data = get_historical_data(symbol, timeframe, 1000)
                        trend = detect_trend(data)
                        if trend != "downtrend":
                            break
                        support_levels, resistance_levels = identify_support_resistance(
                            data
                        )
                        current_price = mt5.symbol_info_tick(symbol).ask
                        if current_price < initial_entry.price:
                            print(
                                f"Market in profit for {symbol}, considering scaling in."
                            )
                            pullback_entry = place_order(
                                symbol,
                                mt5.ORDER_TYPE_SELL,
                                volume,
                                current_price,
                                sl,
                                tp,
                            )
                            if pullback_entry.retcode == mt5.TRADE_RETCODE_DONE:
                                logging.info(
                                    f"Scaling in sell order placed for {symbol}"
                                )
        time.sleep(60)


if __name__ == "__main__":
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
    timeframes = [
        mt5.TIMEFRAME_M30,
        mt5.TIMEFRAME_H1,
        mt5.TIMEFRAME_H4,
        mt5.TIMEFRAME_D1,
    ]
    for timeframe in timeframes:
        strategy(symbols, timeframe, ACCOUNT, PASSWORD, SERVER)
