class CRTPatternDetector:
    def __init__(self, window_size=3):
        self.window_size = window_size
        self.candles = []

    def add_candle(self, candle):
        """
        Simple CRT detection:
        - Bullish CRT breakout: last candle close > max high of previous candles in window
        - Bearish CRT breakout: last candle close < min low of previous candles in window
        """
        self.candles.append(candle)
        if len(self.candles) < self.window_size:
            return None
        if len(self.candles) > self.window_size:
            self.candles.pop(0)

        last = self.candles[-1]
        prev_high = max(c["high"] for c in self.candles[:-1])
        prev_low = min(c["low"] for c in self.candles[:-1])

        if last["close"] > prev_high:
            return {"type": "Bullish"}
        elif last["close"] < prev_low:
            return {"type": "Bearish"}
        return None
