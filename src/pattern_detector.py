# pattern_detector.py

def detect_crt_pattern(candles):
    patterns = []
    labels = []
    if len(candles) < 3:
        return patterns, labels

    for i in range(2, len(candles)):
        c1 = candles[i - 2]
        c2 = candles[i - 1]
        c3 = candles[i]

        # Detect a simple Accumulation → Manipulation → Distribution pattern
        if (
            c1["high"] - c1["low"] < 2  # low range
            and c2["high"] > c1["high"] + 1  # manipulation up
            and c3["close"] < c1["low"]  # distribution closes low
        ):
            entry = c3["close"]
            sl = c2["high"]
            tp = entry - (sl - entry) * 2

            patterns.append(
                {
                    "time": c3["epoch"],
                    "entry": entry,
                    "sl": sl,
                    "tp": tp,
                    "direction": "sell",
                }
            )

            # record labels with index and phase name
            labels.append((i - 2, "ACCUMULATION"))
            labels.append((i - 1, "MANIPULATION"))
            labels.append((i, "DISTRIBUTION"))

    return patterns, labels
