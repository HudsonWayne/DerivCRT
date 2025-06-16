class CRTPatternDetector:
    def __init__(self, window_size=3):
        self.window_size = window_size
        self.candles = []

    def add_candle(self, candle):
        self.candles.append(candle)
        if len(self.candles) < self.window_size:
            return None
        if len(self.candles) > self.window_size:
            self.candles.pop(0)

        last = self.candles[-1]
        prev_high = max(c["high"] for c in self.candles[:-1])
        prev_low = min(c["low"] for c in self.candles[:-1])

        if last["close"] > prev_high:
            return {"type": "Bullish", "candle": last}
        elif last["close"] < prev_low:
            return {"type": "Bearish", "candle": last}
        return None
