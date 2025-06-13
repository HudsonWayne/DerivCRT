# src/timeframe_manager.py

class TimeframeManager:
    def __init__(self):
        self.granularities = {
            "1s": 1,
            "5s": 5,
            "15s": 15,
            "1m": 60,
            "5m": 300,
            "15m": 900,
            "1h": 3600
        }
        self.current = "1m"

    def set_timeframe(self, tf_label):
        if tf_label in self.granularities:
            self.current = tf_label
        else:
            raise ValueError(f"Unsupported timeframe: {tf_label}")

    def get_granularity(self):
        return self.granularities[self.current]

    def list_timeframes(self):
        return list(self.granularities.keys())

    def __str__(self):
        return f"Current timeframe: {self.current} ({self.get_granularity()}s)"
