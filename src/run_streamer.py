# run_streamer.py

from deriv_ws import DerivLiveStreamer
from live_plot import LiveCandlePlot
from pattern_detector import detect_crt_pattern, predict_direction
from strategy import calculate_levels
import datetime
import math
import threading
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

CANDLE_SECONDS_1H = 3600
CANDLE_SECONDS_4H = 3600 * 4

symbols = [
    "R_10", "R_25", "R_50", "R_75", "R_100",
    "R_10_1s", "R_25_1s", "R_50_1s", "R_75_1s", "R_100_1s"
]

candles_by_symbol = {}
signals_by_symbol = {}

class CRTTracker:
    def __init__(self, symbol):
        self.symbol = symbol
        self.final_candles = []
        self.forming_candle = None
        self.signal_given_for_4h_epoch = None

    def create_new_candle(self, epoch):
        start = epoch - (epoch % CANDLE_SECONDS_1H)
        print(f"🟢 [{self.symbol}] New 1H candle @ {datetime.datetime.fromtimestamp(start)}")
        return {
            "epoch": start,
            "open": None,
            "high": -math.inf,
            "low": math.inf,
            "close": None,
        }

    def update_forming_candle(self, candle):
        ts = candle["epoch"]
        if not self.forming_candle or ts >= self.forming_candle["epoch"] + CANDLE_SECONDS_1H:
            if self.forming_candle and self.forming_candle["open"] is not None:
                self.final_candles.append(self.forming_candle)
                if len(self.final_candles) > 50:
                    self.final_candles.pop(0)
            self.forming_candle = self.create_new_candle(ts)

        price = candle["close"]
        self.forming_candle["open"] = self.forming_candle["open"] or price
        self.forming_candle["high"] = max(self.forming_candle["high"], candle["high"])
        self.forming_candle["low"] = min(self.forming_candle["low"], candle["low"])
        self.forming_candle["close"] = price

        self.check_for_signal()

    def is_4h_candle_start_local(self, epoch_utc):
        dt_local = datetime.datetime.utcfromtimestamp(epoch_utc) + datetime.timedelta(hours=2)
        return dt_local.hour % 4 == 2 and dt_local.minute == 0 and dt_local.second == 0

    def check_for_signal(self):
        if len(self.final_candles) < 3 or not self.forming_candle:
            return

        forming_epoch = self.forming_candle["epoch"]
        candle_4h_start_epoch = forming_epoch - (forming_epoch % CANDLE_SECONDS_4H)

        if self.is_4h_candle_start_local(candle_4h_start_epoch):
            if self.signal_given_for_4h_epoch != candle_4h_start_epoch:
                direction = predict_direction(self.final_candles)
                signal = detect_crt_pattern(self.final_candles)
                if signal:
                    last = self.final_candles[-1]
                    levels = calculate_levels(last, direction)
                    emoji = "📈" if direction == "buy" else "📉"
                    msg = f"{emoji} {self.symbol} {direction.upper()} SIGNAL | Entry: {levels['entry']:.2f}, TP: {levels['tp']:.2f}, SL: {levels['sl']:.2f}"
                    print(f"[CRT SIGNAL] {msg}")
                else:
                    print(f"❌ {self.symbol}: No signal for this 4H candle.")
                self.signal_given_for_4h_epoch = candle_4h_start_epoch
        else:
            self.signal_given_for_4h_epoch = None


def start_stream(symbol):
    tracker = CRTTracker(symbol)
    candles_by_symbol[symbol] = tracker

    def on_candle(candle):
        print(f"📥 {symbol} 1-min @ {datetime.datetime.fromtimestamp(candle['epoch'])} | Close: {candle['close']}")
        tracker.update_forming_candle(candle)

    DerivLiveStreamer(app_id="80707", symbol=symbol, granularity=60, callback=on_candle).start()


if __name__ == "__main__":
    for sym in symbols:
        threading.Thread(target=start_stream, args=(sym,), daemon=True).start()

    print("\n✅ All volatility index streams running...")

    while True:
        try:
            pass
        except KeyboardInterrupt:
            print("\nStopping...")
            break
