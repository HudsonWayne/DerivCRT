import time
from deriv_ws import DerivLiveStreamer
from pattern_detector import detect_crt_pattern

candle_history = []
last_signaled_epoch = None  # Last candle epoch we gave a signal for
last_signal = None          # The last signal details (to avoid printing duplicates)

def signals_equal(sig1, sig2):
    """Helper to check if two signals are effectively the same."""
    if sig1 is None or sig2 is None:
        return False
    return (
        sig1['type'] == sig2['type'] and
        abs(sig1['entry'] - sig2['entry']) < 1e-5 and
        abs(sig1['stop_loss'] - sig2['stop_loss']) < 1e-5 and
        abs(sig1['take_profit'] - sig2['take_profit']) < 1e-5
    )

def on_candle(candle):
    global last_signaled_epoch, last_signal

    print(f"[{time.strftime('%Y-%m-%d %H:%M', time.gmtime(candle['epoch']))}] O:{candle['open']} H:{candle['high']} L:{candle['low']} C:{candle['close']}")

    candle_history.append(candle)

    # Limit candle history size
    if len(candle_history) > 50:
        candle_history.pop(0)

    # Detect CRT pattern (returns one signal dict or None)
    signal = detect_crt_pattern(candle_history)

    # Only print a new signal if:
    # - There is a signal,
    # - AND it's a new candle epoch (new 4H candle),
    # - OR the signal has changed from the last printed signal (in case of updates)
    if signal:
        if candle['epoch'] != last_signaled_epoch or not signals_equal(signal, last_signal):
            last_signaled_epoch = candle['epoch']
            last_signal = signal
            print(f"\n=== TRADE SIGNAL for candle @ {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime(candle['epoch']))} ===")
            print(f"Action: {signal['type'].upper()}")
            print(f"{'Buy' if signal['type'].lower() == 'buy' else 'Sell'} at: {signal['entry']:.5f}")
            print(f"Stop Loss: {signal['stop_loss']:.5f}")
            print(f"Take Profit: {signal['take_profit']:.5f}")

            # Optionally, print time until next 4H candle:
            next_candle_time = candle['epoch'] + 14400
            time_left = next_candle_time - int(time.time())
            if time_left > 0:
                mins, secs = divmod(time_left, 60)
                print(f"Time until next 4H candle: {mins} min {secs} sec\n")
    else:
        # No signal - reset last_signal so next valid signal prints
        last_signal = None


if __name__ == "__main__":
    symbol = "R_100"
    granularity = 14400  # 4H candles

    streamer = DerivLiveStreamer(symbol=symbol, callback=on_candle, granularity=granularity)
    streamer.start()

    print("[INFO] Streaming started. Waiting for 4H candles...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("[INFO] Stopping streamer...")
        streamer.stop()
        print("[INFO] Exited cleanly.")
