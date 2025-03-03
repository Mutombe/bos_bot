import MetaTrader5 as mt5
import time
import logging
from cms import check_for_cms
from sma_trend import detect_trend
from dynamic_size import calculate_position_size
from support_and_resistance import identify_support_resistance
from historical_data import get_data
import config
from trailing import trail_stop_loss
from initializing import initialize_mt5

logging.basicConfig(
    filename="trading_bot.log", level=logging.INFO, format="%(asctime)s %(message)s"
)

open_positions = {}

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
        print("Bearish break detected")
        return True
    print("No conclusive market signal"'\n')
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
        "type_filling": mt5.ORDER_FILLING_FOK,
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
        data = get_data(symbol, timeframe, config.NUMBER_OF_CANDLES)
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

        cms_detected, direction, df = check_for_cms(
            symbol, timeframe, config.NUMBER_OF_CANDLES
        )

        if market_structure_break and cms_detected:
            print(f"Confirmation for change in Market Structure detected for {symbol}: {direction}")
            account_info = mt5.account_info()
            account_balance = account_info.balance
            risk_per_trade = 0.01  # Risk 1% of account per trade
            stop_loss_pips = 50  # Stop loss in pips
            pip_value = 10  # Pip value in the account currency
            trail_amount = 50

            volume = calculate_position_size(
                account_balance, risk_per_trade, stop_loss_pips, pip_value
            )

            if trend == "uptrend" and direction == "Bullish":
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
                        data = get_data(symbol, timeframe, config.NUMBER_OF_CANDLES)
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
            elif trend == "downtrend" and direction == "Bearish":
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
                        data = get_data(symbol, timeframe, config.NUMBER_OF_CANDLES)
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
    for timeframe in config.TIMEFRAMES:
        strategy(
            config.SYMBOLS, timeframe, config.ACCOUNT, config.PASSWORD, config.SERVER
        )
