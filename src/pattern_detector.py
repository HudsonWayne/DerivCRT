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
