# Risk management: Calculate position size

def calculate_position_size(account_balance, risk_per_trade, stop_loss_pips, pip_value):
    risk_amount = account_balance * risk_per_trade
    position_size = risk_amount / (stop_loss_pips * pip_value)
    return position_size
