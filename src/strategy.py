def calculate_sl_tp(signal_type, candle, sl_ratio=0.5, tp_ratio=1.5):
    """
    Calculates stop loss and take profit levels based on CRT breakout.

    :param signal_type: 'BREAKOUT_UP' or 'BREAKOUT_DOWN'
    :param candle: Latest candle dict with keys 'high', 'low', 'close'
    :param sl_ratio: Multiplier for stop loss
    :param tp_ratio: Multiplier for take profit
    :return: Dictionary with SL and TP levels
    """
    candle_range = candle['high'] - candle['low']
    
    if signal_type == 'BREAKOUT_UP':
        entry = candle['close']
        sl = entry - (candle_range * sl_ratio)
        tp = entry + (candle_range * tp_ratio)
    else:  # BREAKOUT_DOWN
        entry = candle['close']
        sl = entry + (candle_range * sl_ratio)
        tp = entry - (candle_range * tp_ratio)

    return {'entry': entry, 'stop_loss': sl, 'take_profit': tp}


def handle_candle(candle):
    """
    Example handler function to be called for each incoming candle.
    This function should analyze the candle, detect signals, and
    possibly print or store signals.

    :param candle: Dictionary with keys: timestamp, open, high, low, close
    """
    # This is where you put your CRT detection logic.
    # For demonstration, let's say any candle with close > open is a breakout up,
    # and close < open is breakout down.
    if candle['close'] > candle['open']:
        signal_type = 'BREAKOUT_UP'
    elif candle['close'] < candle['open']:
        signal_type = 'BREAKOUT_DOWN'
    else:
        # No signal
        return

    levels = calculate_sl_tp(signal_type, candle)
    print(f"Signal: {signal_type} at {candle['timestamp']}")
    print(f"Entry: {levels['entry']}, SL: {levels['stop_loss']}, TP: {levels['take_profit']}")
