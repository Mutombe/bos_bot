import MetaTrader5 as mt5

def adjust_stop_loss(order, new_stop_loss):
    """
    Adjust the stop loss of an existing order.
    """
    request = {
        "action": mt5.TRADE_ACTION_SLTP,
        "position": order["ticket"],
        "sl": new_stop_loss,
    }
    result = mt5.order_send(request)
    return result


def trail_stop_loss(order, trail_amount):
    """
    Implement a trailing stop loss.
    """
    current_price = mt5.symbol_info_tick(order["symbol"]).ask
    new_stop_loss = (
        current_price - trail_amount
        if order["type"] == mt5.ORDER_TYPE_BUY
        else current_price + trail_amount
    )
    return adjust_stop_loss(order, new_stop_loss)
