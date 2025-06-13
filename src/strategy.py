def calculate_sl_tp(signal_type, candle, sl_ratio=0.5, tp_ratio=1.5):
    """
    Calculates stop loss and take profit levels based on CRT breakout.

    :param signal_type: 'BREAKOUT_UP' or 'BREAKOUT_DOWN'
    :param candle: Latest candle
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
