import asyncio
import datetime
import websockets
import json

APP_ID = 80707
SYMBOLS = ["R_10", "R_25", "R_50", "R_75", "R_100"]
URL = f"wss://ws.binaryws.com/websockets/v3?app_id={APP_ID}"

REWARD_RATIO = 4
MAX_SL_PERCENTAGE_SWING = 0.0035  # Reasonable SL for swing trades
MAX_SL_PERCENTAGE_SCALP = 0.0025
MIN_BODY_RATIO_4H = 0.0045  # Original stricter threshold
MIN_BODY_RATIO_3H = 0.004

GRANULARITIES = {
    "4h": 14400,
    "3h": 10800,
}

candle_data = {
    symbol: {
        tf: {
            "start": None,
            "open": None,
            "high": None,
            "low": None,
            "close": None,
            "signaled": False,
            "history": []
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
        if candle["open"] is not None:
            candle["history"].append({
                "open": candle["open"],
                "high": candle["high"],
                "low": candle["low"],
                "close": candle["close"]
            })
            if len(candle["history"]) > 3:
                candle["history"].pop(0)

        candle.update({"start": start, "open": price, "high": price, "low": price, "close": price, "signaled": False})
        if granularity_name == "4h":
            candle_data[symbol]["next_4h_signal_sent"] = False
        if granularity_name == "3h":
            candle_data[symbol]["next_3h_signal_sent"] = False
    else:
        candle["high"] = max(candle["high"], price)
        candle["low"] = min(candle["low"], price)
        candle["close"] = price

def candle_body_ratio(candle):
    return abs(candle["close"] - candle["open"]) / candle["open"] if candle["open"] else 0

def candle_direction(candle):
    if candle["close"] > candle["open"]:
        return "buy"
    elif candle["close"] < candle["open"]:
        return "sell"
    return None

def wick_sizes(candle):
    upper = candle["high"] - max(candle["open"], candle["close"])
    lower = min(candle["open"], candle["close"]) - candle["low"]
    total = candle["high"] - candle["low"]
    return upper, lower, total

def is_accumulation_phase(history):
    # All last 3 candles must have very small bodies <= 0.002 (strict)
    return len(history) >= 3 and all(candle_body_ratio(c) <= 0.002 for c in history)

def is_manipulation_phase(history):
    if len(history) < 3:
        return False
    c = history[-1]
    dir = candle_direction(c)
    upper, lower, total = wick_sizes(c)
    if total == 0:
        return False
    # For buy direction, strong lower wick >50%, for sell strong upper wick >50%
    return (dir == "buy" and lower / total > 0.5) or (dir == "sell" and upper / total > 0.5)

def is_expansion_phase(candle, min_ratio):
    body_r = candle_body_ratio(candle)
    upper, lower, total = wick_sizes(candle)
    if total == 0:
        return False
    # Body ratio must meet min threshold & wicks <=30%
    return body_r >= min_ratio and upper / total <= 0.3 and lower / total <= 0.3

def explain_failure(symbol, candle, tf, history):
    reasons = []
    body_r = candle_body_ratio(candle)
    min_body = MIN_BODY_RATIO_4H if tf == "4h" else MIN_BODY_RATIO_3H
    if body_r < min_body:
        reasons.append(f"Body too small ({body_r:.4f} < {min_body})")
    upper, lower, total = wick_sizes(candle)
    if total == 0:
        reasons.append("Flat candle")
    if not is_accumulation_phase(history[:-1]):
        reasons.append("No accumulation phase")
    if not is_manipulation_phase(history):
        reasons.append("No manipulation trap")
    if not is_expansion_phase(candle, min_body):
        reasons.append("Expansion phase fail")
    return reasons

def calculate_tp_sl(entry, direction, sl_pct):
    sl = entry * (1 - sl_pct) if direction == "buy" else entry * (1 + sl_pct)
    tp = entry + REWARD_RATIO * (entry - sl) if direction == "buy" else entry - REWARD_RATIO * (sl - entry)
    return round(sl, 2), round(tp, 2)

def print_signal(symbol, start, direction, entry, sl, tp, tf):
    emoji = "🟢" if direction == "buy" else "🔴"
    label = f"{tf.upper()} CRT"
    print(f"\n{emoji} [{symbol}] {label} SIGNAL")
    print(f"🕓 Start: {start.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📈 Direction: {direction.upper()}")
    print(f"🎯 Entry: {entry:.2f} | 🛑 SL: {sl:.2f} | ✅ TP: {tp:.2f}\n")

async def check_signal(symbol, tf):
    while True:
        candle = candle_data[symbol][tf]
        history = candle["history"]

        if not candle["open"] or not candle["close"]:
            await asyncio.sleep(60)
            continue

        if candle["signaled"] or candle_data[symbol][f"next_{tf}_signal_sent"]:
            await asyncio.sleep(60)
            continue

        fails = explain_failure(symbol, candle, tf, history)
        direction = candle_direction(candle)

        if fails:
            print(f"❌ [{symbol} {tf.upper()}] CRT fail: {', '.join(fails)}")
            await asyncio.sleep(60)
            continue

        if not direction:
            await asyncio.sleep(60)
            continue

        entry = candle["close"]
        sl_pct = MAX_SL_PERCENTAGE_SWING if tf == "4h" else MAX_SL_PERCENTAGE_SCALP
        sl, tp = calculate_tp_sl(entry, direction, sl_pct)
        print_signal(symbol, candle["start"], direction, entry, sl, tp, tf)
        candle_data[symbol][f"next_{tf}_signal_sent"] = True
        candle["signaled"] = True

        await asyncio.sleep(60)

async def subscribe_ticks(ws, symbol):
    await ws.send(json.dumps({"ticks": symbol, "subscribe": 1}))
    print(f"✅ Subscribed to ticks for {symbol}")

async def run():
    print("🚀 CRT SNIPER TRACKER (4H & 3H) - STRICT MODE ONLY CRT SIGNALS")
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

if __name__ == "__main__":
    asyncio.run(run())
