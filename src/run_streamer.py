import asyncio
import datetime
import websockets
import json
import random

APP_ID = 80707
SYMBOLS = ["R_10", "R_25", "R_50", "R_75", "R_100"]
URL = f"wss://ws.binaryws.com/websockets/v3?app_id={APP_ID}"

REWARD_RATIO = 4
MAX_SL_PERCENTAGE_SWING = 0.0025
MAX_SL_PERCENTAGE_SCALP = 0.002
MIN_BODY_RATIO_4H = 0.0045  # stricter min body size for high confidence
MIN_BODY_RATIO_3H = 0.004

GRANULARITIES = {
    "4h": 14400,
    "3h": 10800,
}

# Each candle stores: start time, open, high, low, close, signaled flag, plus history for pattern detection
candle_data = {
    symbol: {
        tf: {
            "start": None,
            "open": None,
            "high": None,
            "low": None,
            "close": None,
            "signaled": False,
            "history": []  # last 3 candles for pattern detection
        }
        for tf in GRANULARITIES
    } | {"next_4h_signal_sent": False, "next_3h_signal_sent": False}
    for symbol in SYMBOLS
}

def epoch_to_local_candle_time(epoch, granularity_seconds):
    dt = datetime.datetime.fromtimestamp(epoch).astimezone()
    hours = granularity_seconds // 3600
    base_hour = (dt.hour // hours) * hours
    return dt.replace(hour=base_hour, minute=0, second=0, microsecond=0)

def update_candle(symbol, epoch, price, granularity_name):
    seconds = GRANULARITIES[granularity_name]
    start = epoch_to_local_candle_time(epoch, seconds)
    candle = candle_data[symbol][granularity_name]

    if candle["start"] != start:
        # Shift history and add old candle to history for pattern detection
        if candle["open"] is not None:
            candle["history"].append({
                "open": candle["open"],
                "high": candle["high"],
                "low": candle["low"],
                "close": candle["close"]
            })
            if len(candle["history"]) > 3:
                candle["history"].pop(0)

        # Reset current candle
        candle.update({"start": start, "open": price, "high": price, "low": price, "close": price, "signaled": False})
        if granularity_name == "4h":
            candle_data[symbol]["next_4h_signal_sent"] = False
        if granularity_name == "3h":
            candle_data[symbol]["next_3h_signal_sent"] = False
    else:
        candle["high"] = max(candle["high"], price)
        candle["low"] = min(candle["low"], price)
        candle["close"] = price

def candle_body_size(candle):
    return abs(candle["close"] - candle["open"])

def candle_body_ratio(candle):
    if candle["open"] == 0:
        return 0
    return candle_body_size(candle) / candle["open"]

def candle_direction(candle):
    if candle["close"] > candle["open"]:
        return "buy"
    elif candle["close"] < candle["open"]:
        return "sell"
    else:
        return None

def wick_sizes(candle):
    upper_wick = candle["high"] - max(candle["open"], candle["close"])
    lower_wick = min(candle["open"], candle["close"]) - candle["low"]
    total_range = candle["high"] - candle["low"]
    return upper_wick, lower_wick, total_range

def is_accumulation_phase(history):
    # Accumulation phase = 3 candles with small bodies, small range, alternating or indecision
    if len(history) < 3:
        return False
    for c in history:
        body_r = candle_body_ratio(c)
        if body_r > 0.002:  # small bodies
            return False
    return True

def is_manipulation_phase(history):
    # Manipulation = one candle with a wick trap against direction, often longer wick on opposite side
    if len(history) < 3:
        return False
    c = history[-1]
    direction = candle_direction(c)
    upper_wick, lower_wick, total_range = wick_sizes(c)
    if total_range == 0:
        return False
    upper_wick_ratio = upper_wick / total_range
    lower_wick_ratio = lower_wick / total_range

    # For buy manipulation: long lower wick (liquidity grab)
    # For sell manipulation: long upper wick
    if direction == "buy" and lower_wick_ratio > 0.5:
        return True
    if direction == "sell" and upper_wick_ratio > 0.5:
        return True
    return False

def is_expansion_phase(candle, min_body_ratio):
    # Expansion: strong body, small wick, directional
    body_r = candle_body_ratio(candle)
    upper_wick, lower_wick, total_range = wick_sizes(candle)
    if total_range == 0:
        return False
    upper_wick_ratio = upper_wick / total_range
    lower_wick_ratio = lower_wick / total_range

    if body_r < min_body_ratio:
        return False
    # Small wicks less than 0.3 total range (30%)
    if upper_wick_ratio > 0.3 or lower_wick_ratio > 0.3:
        return False
    return True

def explain_failure(symbol, candle, tf, history):
    reasons = []
    body_r = candle_body_ratio(candle)
    min_body = MIN_BODY_RATIO_4H if tf == "4h" else MIN_BODY_RATIO_3H
    if body_r < min_body:
        reasons.append(f"Body too small ({body_r:.4f} < {min_body})")
    upper_wick, lower_wick, total_range = wick_sizes(candle)
    if total_range == 0:
        reasons.append("Flat candle (no range)")
    else:
        if upper_wick / total_range > 0.5:
            reasons.append("Long upper wick")
        if lower_wick / total_range > 0.5:
            reasons.append("Long lower wick")

    if not is_accumulation_phase(history[:-1]):
        reasons.append("No accumulation phase (last 2 candles bodies too large)")
    if not is_manipulation_phase(history):
        reasons.append("No manipulation wick trap in last candle")
    if not is_expansion_phase(candle, min_body):
        reasons.append("Expansion phase fail (body/wick ratio)")

    return reasons

def calculate_tp_sl(entry, direction, sl_pct):
    sl = entry * (1 - sl_pct) if direction == "buy" else entry * (1 + sl_pct)
    tp = entry + REWARD_RATIO * (entry - sl) if direction == "buy" else entry - REWARD_RATIO * (sl - entry)
    return round(sl, 2), round(tp, 2)

def print_signal(symbol, start, direction, entry, sl, tp, tf):
    emoji = "🟢" if direction == "buy" else "🔴"
    label = f"{tf.upper()} CRT SNIPER"
    print(f"\n{emoji} [{symbol}] {label} SIGNAL")
    print(f"🕓 Candle Start: {start.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📈 Direction: {direction.upper()}")
    print(f"🎯 Entry: {entry:.2f}")
    print(f"🛑 SL: {sl:.2f}")
    print(f"✅ TP: {tp:.2f}\n")

def next_candle_start(granularity):
    now = datetime.datetime.now(datetime.timezone.utc).astimezone()
    seconds = GRANULARITIES[granularity]
    base = now.replace(minute=0, second=0, microsecond=0)
    return base + datetime.timedelta(seconds=(seconds - (now.timestamp() % seconds)))

async def check_signal(symbol, tf):
    while True:
        target_time = next_candle_start(tf) - datetime.timedelta(minutes=5)
        now = datetime.datetime.now(datetime.timezone.utc).astimezone()
        sleep_time = max(1, (target_time - now).total_seconds())
        print(f"⏳ [{symbol} {tf.upper()}] Next check in {int(sleep_time)}s at {target_time.strftime('%H:%M:%S')}")
        await asyncio.sleep(sleep_time)

        candle = candle_data[symbol][tf]
        history = candle["history"]

        # Validate candle presence
        if not candle["open"] or not candle["close"]:
            print(f"❌ [{symbol} {tf.upper()}] Missing open/close price")
            await asyncio.sleep(60)
            continue

        if candle["signaled"] or candle_data[symbol][f"next_{tf}_signal_sent"]:
            print(f"⛔ [{symbol} {tf.upper()}] Signal already sent for this candle")
            await asyncio.sleep(60)
            continue

        # CRT Phases Check
        fails = explain_failure(symbol, candle, tf, history)
        if fails:
            print(f"❌ [{symbol} {tf.upper()}] CRT check failed: {', '.join(fails)}")
            await asyncio.sleep(60)
            continue

        direction = candle_direction(candle)
        if not direction:
            print(f"❌ [{symbol} {tf.upper()}] No clear candle direction")
            await asyncio.sleep(60)
            continue

        entry = candle["close"]
        sl_pct = MAX_SL_PERCENTAGE_SWING if tf == "4h" else MAX_SL_PERCENTAGE_SCALP
        sl, tp = calculate_tp_sl(entry, direction, sl_pct)

        print_signal(symbol, candle["start"], direction, entry, sl, tp, tf)
        candle_data[symbol][f"next_{tf}_signal_sent"] = True
        candle["signaled"] = True

        await asyncio.sleep(60)  # wait before next check

async def subscribe_ticks(ws, symbol):
    await ws.send(json.dumps({"ticks": symbol, "subscribe": 1}))
    print(f"✅ Subscribed to ticks for {symbol}")

async def run():
    print("🚀 CRT SNIPER TRACKER (4H & 3H) - HIGH CONFIDENCE MODE")
    async with websockets.connect(URL) as ws:
        for s in SYMBOLS:
            await subscribe_ticks(ws, s)

        tasks = [
            asyncio.create_task(check_signal(s, tf))
            for s in SYMBOLS for tf in ["4h", "3h"]
        ]

        while True:
            msg = json.loads(await ws.recv())
            if 'tick' in msg:
                t = msg['tick']
                for tf in GRANULARITIES:
                    update_candle(t['symbol'], t['epoch'], t['quote'], tf)
            elif 'error' in msg:
                print("❌ Error:", msg['error'].get('message'))

# ---------------------------
# Optional: Simulated candles generator for instant testing

def simulate_candle(symbol, tf, direction="buy"):
    base = datetime.datetime.now().astimezone().replace(minute=0, second=0, microsecond=0)
    price = random.uniform(1000, 1100)
    body_size = price * 0.006  # Strong body for expansion
    wick_size = price * 0.001

    if direction == "buy":
        open_ = price
        close = price + body_size
    else:
        close = price
        open_ = price + body_size

    high = max(open_, close) + wick_size
    low = min(open_, close) - wick_size

    candle = {
        "start": base,
        "open": open_,
        "high": high,
        "low": low,
        "close": close,
        "signaled": False,
        "history": [
            # Simulate accumulation - 2 small body candles
            {"open": open_ - 1, "high": open_ + 0.2, "low": open_ - 1.2, "close": open_ - 0.5},
            {"open": open_ - 0.5, "high": open_ + 0.1, "low": open_ - 0.7, "close": open_ - 0.6},
            # Manipulation candle with wick trap opposite direction
            {"open": open_ - 0.6, "high": high + 0.4, "low": open_ - 1.0, "close": open_ - 0.7},
        ],
    }

    candle_data[symbol][tf] = candle
    candle_data[symbol][f"next_{tf}_signal_sent"] = False
    print(f"🧪 Simulated {tf.upper()} {direction.upper()} candle for {symbol}")

# Uncomment to generate instant test candles:
# simulate_candle("R_50", "4h", "buy")
# simulate_candle("R_75", "3h", "sell")

if __name__ == "__main__":
    asyncio.run(run())
