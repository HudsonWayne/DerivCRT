def calculate_levels(candle, direction):
    entry_price = candle["close"]
    buffer = (candle["high"] - candle["low"]) * 0.1

    if direction == "buy":
        stop_loss = entry_price - buffer
        take_profit = entry_price + 2 * buffer
    elif direction == "sell":
        stop_loss = entry_price + buffer
        take_profit = entry_price - 2 * buffer
    else:
        return None

    return {
        "entry": entry_price,
        "sl": stop_loss,
        "tp": take_profit
    }
