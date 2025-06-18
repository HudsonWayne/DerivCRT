from deriv_ws import DerivLiveStreamer
from live_plot import LiveCandlePlot
from pattern_detector import CRTStrategy
import pandas as pd

symbol = "R_75"
candles = []
signals = []

def on_new_candle(candle):
    global signals
    candles.append(candle)
    if len(candles) > 100:
        candles.pop(0)
    strategy = CRTStrategy(candles)
    signals = strategy.run()

def get_candles():
    return candles

def get_signals():
    return signals

if __name__ == "__main__":
    print("🟢 Starting CRT + Breakout Detector with Thank You Chart")
    DerivLiveStreamer(app_id="1089", symbol=symbol, granularity=14400, callback=on_new_candle).start()
    plot = LiveCandlePlot(get_candles, get_signals)
    plot.show()
