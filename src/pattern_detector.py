def detect_crt_pattern(candles):
    signals = []
    if len(candles) < 3:
        return signals
    last = candles[-1]
    prev1 = candles[-2]
    prev2 = candles[-3]

    if last["close"] > prev1["close"] and last["close"] > prev2["close"]:
        signals.append({"index": len(candles) - 1, "signal": "buy"})
    elif last["close"] < prev1["close"] and last["close"] < prev2["close"]:
        signals.append({"index": len(candles) - 1, "signal": "sell"})

    return signals

def predict_direction(candles):
    if len(candles) < 3:
        return None
    last = candles[-1]
    prev1 = candles[-2]
    prev2 = candles[-3]

    if last["close"] > prev1["close"] > prev2["close"]:
        return "buy"
    elif last["close"] < prev1["close"] < prev2["close"]:
        return "sell"
    return None
