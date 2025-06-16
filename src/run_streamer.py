from deriv_ws import DerivLiveStreamer
from live_plot import start_plotting, add_candle
from strategy import handle_candle
import threading
import time

def on_new_candle(candle):
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Open: {candle['open']}, High: {candle['high']}, Low: {candle['low']}, Close: {candle['close']}")
    handle_candle(candle)
    add_candle(candle)

if __name__ == "__main__":
    # Start streaming in background thread
    def stream():
        streamer = DerivLiveStreamer("R_100", on_new_candle)
        streamer.start()

    threading.Thread(target=stream, daemon=True).start()

    # Run plot in main thread
    start_plotting()
