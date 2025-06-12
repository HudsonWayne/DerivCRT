from src.data_simulator import DataSimulator

def print_candle(candle):
    print(f"[{candle['timestamp']}] O:{candle['open']} H:{candle['high']} L:{candle['low']} C:{candle['close']}")

if __name__ == "__main__":
    sim = DataSimulator(filepath="data/volatility75.csv", interval=1.0, callback=print_candle)
    sim.start()

    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Stopping...")
        sim.stop()
