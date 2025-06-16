# run_streamer.py
from deriv_ws import DerivLiveStreamer
from live_plot import LiveCandlePlot, start_plotting
from pattern_detector import detect_crt_pattern
import pandas as pd

candle_history = []
crt_labels = []

def on_new_candle(candle):
    print(f"[{candle['epoch']}] O:{candle['open']} H:{candle['high']} L:{candle['low']} C:{candle['close']}")
    candle_history.append(candle)

    if len(candle_history) > 100:
        candle_history.pop(0)

    patterns, labels = detect_crt_pattern(candle_history)
    crt_labels.clear()
    crt_labels.extend(labels)

streamer = DerivLiveStreamer(stream_symbol="R_100", callback=on_new_candle)
streamer.start()

plotter = LiveCandlePlot(
    get_data_callback=lambda: pd.DataFrame(candle_history),
    get_labels_callback=lambda: crt_labels
)

start_plotting()
