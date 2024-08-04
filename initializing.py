import time
import MetaTrader5 as mt5
import logging

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