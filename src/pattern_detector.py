import datetime

class CRTStrategy:
    def __init__(self, candles):
        self.candles = candles

    def run(self):
        signals = []
        if len(self.candles) < 5:
            return [{"description": "No valid setup", "type": "none"}]

        c1, c2, c3 = self.candles[-3:]
        direction = None

        # 🔍 Detect long CRT (Accumulation → Manipulation → Expansion)
        if c2['low'] < c1['low'] and c2['low'] < c3['low'] and c3['close'] > c1['open']:
            direction = 'buy'
        elif c2['high'] > c1['high'] and c2['high'] > c3['high'] and c3['close'] < c1['open']:
            direction = 'sell'

        # ✅ Breakout Pattern: Big candle after tight range
        if not direction:
            body_sizes = [abs(c['close'] - c['open']) for c in self.candles[-5:]]
            avg = sum(body_sizes[:-1]) / 4
            if body_sizes[-1] > 1.8 * avg:
                direction = 'buy' if self.candles[-1]['close'] > self.candles[-1]['open'] else 'sell'

        if direction:
            level = self.calculate_levels(self.candles[-1], direction)
            signals.append({
                "entry_index": len(self.candles) - 1,
                "entry_price": level['entry'],
                "tp_price": level['tp'],
                "sl_price": level['sl'],
                "type": direction,
                "description": "CRT Long Trade" if direction else "Breakout",
            })
        else:
            signals.append({"description": "No valid setup", "type": "none"})
        return signals

    def calculate_levels(self, candle, direction):
        entry = candle["close"]
        buffer = (candle["high"] - candle["low"]) * 0.2
        if direction == "buy":
            sl = entry - buffer
            tp = entry + buffer * 2
        else:
            sl = entry + buffer
            tp = entry - buffer * 2
        return {"entry": entry, "sl": sl, "tp": tp}

def find_next_4h_candle_open(current_time):
    """
    Given current_time (datetime), find the next 4H candle open time.
    4H candles start at 0:00, 4:00, 8:00, 12:00, 16:00, 20:00 UTC.
    We'll consider local time, you can adjust timezone accordingly.
    """
    hour = current_time.hour
    next_hour = ((hour // 4) + 1) * 4
    if next_hour >= 24:
        # next day
        next_open = current_time.replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(days=1)
    else:
        next_open = current_time.replace(hour=next_hour, minute=0, second=0, microsecond=0)
    return next_open

def main():
    # Example candle data (you replace with your live candle data)
    candles = [
        {"open": 100, "close": 102, "high": 103, "low": 99, "time": "2025-06-18T04:00:00"},
        {"open": 102, "close": 101, "high": 104, "low": 100, "time": "2025-06-18T08:00:00"},
        {"open": 101, "close": 103, "high": 105, "low": 100, "time": "2025-06-18T12:00:00"},
        {"open": 103, "close": 105, "high": 106, "low": 102, "time": "2025-06-18T16:00:00"},
        {"open": 105, "close": 107, "high": 108, "low": 104, "time": "2025-06-18T20:00:00"},
    ]

    now = datetime.datetime.now()
    next_candle_open = find_next_4h_candle_open(now)

    print(f"Current time: {now}")
    print(f"Next 4H candle open: {next_candle_open}")

    strategy = CRTStrategy(candles)

    # Run on last candle (simulate signal for upcoming candle)
    signals = strategy.run()

    # Print signals
    for sig in signals:
        if sig["type"] != "none":
            print(f"\n🚦 Signal for candle opening at {next_candle_open}:")
            print(f"Type: {sig['type'].upper()}")
            print(f"Entry Price: {sig['entry_price']}")
            print(f"Stop Loss: {sig['sl_price']}")
            print(f"Take Profit: {sig['tp_price']}")
            print(f"Description: {sig['description']}")
        else:
            print("\nNo valid trade setup detected.")

if __name__ == "__main__":
    main()
