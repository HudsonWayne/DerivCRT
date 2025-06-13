import time
from src.data_simulator import DataSimulator
from src.pattern_detector import CRTPatternDetector
from src.strategy import calculate_sl_tp

detector = CRTPatternDetector()

def handle_candle(candle):
    print(f"[{candle['timestamp']}] O:{candle['open']} H:{candle['high']} L:{candle['low']} C:{candle['close']}")
    signal = detector.add_candle(candle)
    if signal:
        print(f"🚨 CRT Pattern Detected: {signal['type']} at {signal['candle']['timestamp']}")
        strategy = calculate_sl_tp(signal['type'], signal['candle'])
        print(f"➡️ Entry: {strategy['entry']:.2f} | SL: {strategy['stop_loss']} | TP: {strategy['take_profit']}")

if __name__ == "__main__":
    sim = DataSimulator(filepath="data/volatility75.csv", interval=1.0, callback=handle_candle)
    sim.start()

    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Stopping...")
        sim.stop()
