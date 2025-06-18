from flask import Flask, render_template, jsonify
import threading
import time
import random
from datetime import datetime, timedelta

app = Flask(__name__)

# Shared candle storage
datastore = {
    "candles": []
}

# --- CRT pattern detector ---
def detect_crt_zones(candles):
    if len(candles) < 3:
        return []
    zones = []
    for i in range(2, len(candles)):
        c1, c2, c3 = candles[i-2], candles[i-1], candles[i]
        if c3["close"] > c2["close"] and c3["close"] > c1["close"]:
            zones.append({"index": i, "type": "buy", "price": c3["close"]})
        elif c3["close"] < c2["close"] and c3["close"] < c1["close"]:
            zones.append({"index": i, "type": "sell", "price": c3["close"]})
    return zones

# --- Candle generator (simulate 4H) ---
def candle_generator():
    last_close = 100
    while True:
        now = datetime.now()
        next_4h = now.replace(minute=0, second=0, microsecond=0)
        while next_4h <= now or next_4h.hour % 4 != 0:
            next_4h += timedelta(minutes=1)

        wait_sec = (next_4h - now).total_seconds()
        time.sleep(wait_sec)

        open_price = last_close
        high_price = open_price + random.uniform(1, 5)
        low_price = open_price - random.uniform(1, 5)
        close_price = random.uniform(low_price, high_price)

        new_candle = {
            "timestamp": next_4h.strftime("%Y-%m-%d %H:%M:%S"),
            "open": open_price,
            "high": high_price,
            "low": low_price,
            "close": close_price
        }

        last_close = close_price
        datastore["candles"].append(new_candle)
        if len(datastore["candles"]) > 100:
            datastore["candles"].pop(0)

@app.route("/")
def index():
    return render_template("chart.html")

@app.route("/data")
def get_data():
    candles = datastore["candles"]
    zones = detect_crt_zones(candles)
    return jsonify({"candles": candles, "zones": zones})

if __name__ == "__main__":
    threading.Thread(target=candle_generator, daemon=True).start()
    app.run(debug=True)
