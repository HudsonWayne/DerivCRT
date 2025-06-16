# main.py
from src.timeframe_manager import TimeframeManager
from src.pattern_detector import CRTPatternDetector
from src.deriv_ws import DerivLiveStreamer
import time

def handle_candle(candle):
    print(f"[{candle['timestamp']}] O:{candle['open']} H:{candle['high']} L:{candle['low']} C:{candle['close']}")
    signal = detector.add_candle(candle)
    if signal:
        print(f"🚨 {signal['type']} CRT at {signal['candle']['timestamp']}")

if __name__ == "__main__":
    tf_mgr = TimeframeManager()
    detector = CRTPatternDetector(window_size=3)

    while True:
        print("\n📈 Select Timeframe:")
        for tf in tf_mgr.list_timeframes():
            print(f" - {tf}")
        choice = input("Enter timeframe (e.g. 1m): ").strip()
        try:
            tf_mgr.set_timeframe(choice)
        except ValueError as e:
            print(e)
            continue

        print(f"\n▶️ Streaming with timeframe: {tf_mgr}")
        stream = DerivLiveStreamer(symbol="R_75", on_candle_callback=handle_candle, granularity=tf_mgr.get_granularity())
        stream.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🔁 Restarting or exiting.")
            break
