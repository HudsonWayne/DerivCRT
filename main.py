import argparse
import time
from src.data_simulator import DataSimulator
from src.pattern_detector import CRTPatternDetector
from src.deriv_ws import DerivLiveStreamer  # <- IMPORTANT

detector = CRTPatternDetector()

def handle_candle(candle):
    print(f"[{candle['timestamp']}] O:{candle['open']} H:{candle['high']} L:{candle['low']} C:{candle['close']}")
    signal = detector.add_candle(candle)
    if signal:
        print(f"🚨 CRT Pattern Detected: {signal['type']} at {signal['candle']['timestamp']}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["offline", "online"], default="offline")
    parser.add_argument("--symbol", type=str, default="R_75")
    args = parser.parse_args()

    if args.mode == "offline":
        print("[INFO] Running in OFFLINE mode.")
        sim = DataSimulator(filepath="data/volatility75.csv", interval=1.0, callback=handle_candle)
        sim.start()
    elif args.mode == "online":
        print(f"[INFO] Running in ONLINE mode with symbol: {args.symbol}")
        stream = DerivLiveStreamer(symbol=args.symbol, callback=handle_candle)
        stream.start()

    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Stopping...")
        if args.mode == "offline":
            sim.stop()
        elif args.mode == "online":
            stream.stop()
