# Detect Trend

def detect_trend(data):

    # Simple moving average to determine trend
    
    data["SMA"] = data["close"].rolling(window=20).mean()
    if data["close"].iloc[-1] > data["SMA"].iloc[-1]:
        return "uptrend"
    elif data["close"].iloc[-1] < data["SMA"].iloc[-1]:
        return "downtrend"
    else:
        return "sideways"
