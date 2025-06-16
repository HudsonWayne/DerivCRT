def calculate_sl_tp(signal_type, candle, sl_ratio=0.5, tp_ratio=1.5):
    candle_range = candle['high'] - candle['low']
    entry = candle['close']
    
    if signal_type == 'BREAKOUT_UP':
        sl = entry - (candle_range * sl_ratio)
        tp = entry + (candle_range * tp_ratio)
    else:
        sl = entry + (candle_range * sl_ratio)
        tp = entry - (candle_range * tp_ratio)

    return {'entry': entry, 'stop_loss': sl, 'take_profit': tp}

def handle_candle(candle):
    if candle['close'] > candle['open']:
        signal_type = 'BREAKOUT_UP'
    elif candle['close'] < candle['open']:
        signal_type = 'BREAKOUT_DOWN'
    else:
        return

    levels = calculate_sl_tp(signal_type, candle)
    print(f"🚨 {signal_type} @ {candle['timestamp']} | Entry: {levels['entry']:.2f} | SL: {levels['stop_loss']:.2f} | TP: {levels['take_profit']:.2f}")
