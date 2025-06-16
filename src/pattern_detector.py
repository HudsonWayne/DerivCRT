# src/pattern_detector.py

class CRTPatternDetector:
    def __init__(self):
        self.candles = []

    def add_candle(self, candle):
        self.candles.append(candle)
        if len(self.candles) < 3:
            return None

        if len(self.candles) > 3:
            self.candles.pop(0)

        c1, c2, c3 = self.candles

        # Phase logic (can refine later)
        if (abs(c1['high'] - c1['low']) < 1 and
            abs(c2['high'] - c2['low']) > 2 and
            abs(c3['close'] - c1['high']) > 1):
            
            return {
                "phase": "CRT",
                "accumulation": c1,
                "manipulation": c2,
                "distribution": c3,
                "type": "BREAKOUT_UP" if c3['close'] > c2['open'] else "BREAKOUT_DOWN"
            }

        return None
