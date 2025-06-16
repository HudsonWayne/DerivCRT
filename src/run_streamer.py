from deriv_ws import DerivLiveStreamer
from live_plot import LiveCandlePlot
from pattern_detector import detect_crt_pattern
import pandas as pd
import threading

candle_history = []
crt_labels = []

def on_new_candle(candle):
    candle_history.append(candle)

    # Keep only the latest 100 candles
    if len(candle_history) > 100:
        candle_history.pop(0)

    # Detect CRT patterns
    patterns, labels = detect_crt_pattern(candle_history)
    crt_labels.clear()
    crt_labels.extend(labels)

    # Optional: print detected CRT pattern info
    for pattern in patterns:
        direction = pattern["direction"].upper()
        print(
            f"🚨 CRT {direction} @ {pd.to_datetime(pattern['time'], unit='s')} | "
            f"Entry: {pattern['entry']:.2f} | SL: {pattern['sl']:.2f} | TP: {pattern['tp']:.2f}"
        )

def run_stream():
    symbol = "R_75"
    streamer = DerivLiveStreamer(
        stream_symbol=symbol,
        callback=on_new_candle,
        granularity=14400  # 4-hour candles
    )
    streamer.start()

if __name__ == "__main__":
    # Initialize live plot with callbacks
    plotter = LiveCandlePlot(
        get_data_callback=lambda: pd.DataFrame(candle_history),
        get_labels_callback=lambda: crt_labels
    )

    # Start the WebSocket stream in a background thread
    threading.Thread(target=run_stream, daemon=True).start()

    # Show the plot window (blocking)
    plotter.show()
