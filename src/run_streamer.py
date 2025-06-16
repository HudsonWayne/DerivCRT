from deriv_ws import DerivLiveStreamer
from live_plot import start_plotting, add_candle
from strategy import handle_candle
import threading
import time

def on_new_candle(candle):
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] O:{candle['open']} H:{candle['high']} L:{candle['low']} C:{candle['close']}")
    handle_candle(candle)
    add_candle(candle)

if __name__ == "__main__":
    def stream():
        streamer = DerivLiveStreamer("R_75", on_new_candle, granularity=14400)
        streamer.start()

    threading.Thread(target=stream, daemon=True).start()
    start_plotting()
