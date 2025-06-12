class CRTPatternDetector:
    def __init__(self, window_size=3):
        """
        :param window_size: Number of candles to consider for pattern detection
        """
        self.window_size = window_size
        self.candles = []

    def add_candle(self, candle):
        """Add a new candle and check for CRT pattern."""
        self.candles.append(candle)

        # Only keep last N candles
        if len(self.candles) > self.window_size:
            self.candles.pop(0)

        if len(self.candles) == self.window_size:
            return self._check_crt_pattern()

        return None

    def _check_crt_pattern(self):
        """
        Basic CRT detection logic:
        - Candle range increases.
        - Final candle closes above or below previous range.
        """
        ranges = [c['high'] - c['low'] for c in self.candles]
        increasing = all(ranges[i] < ranges[i + 1] for i in range(len(ranges) - 1))

        if not increasing:
            return None

        prev_highs = [c['high'] for c in self.candles[:-1]]
        prev_lows = [c['low'] for c in self.candles[:-1]]

        last_close = self.candles[-1]['close']

        if last_close > max(prev_highs):
            return {'type': 'BREAKOUT_UP', 'candle': self.candles[-1]}
        elif last_close < min(prev_lows):
            return {'type': 'BREAKOUT_DOWN', 'candle': self.candles[-1]}

        return None
