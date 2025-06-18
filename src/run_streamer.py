import asyncio
import datetime
import websockets
import json

APP_ID = 80707
SYMBOLS = ["R_10", "R_25", "R_50", "R_75", "R_100"]
URL = f"wss://ws.binaryws.com/websockets/v3?app_id={APP_ID}"

REWARD_RATIO = 4
MAX_SL_PERCENTAGE = 0.0025  # Max 0.25% risk
LOOKBACK_CANDLES = 4  # Number of candles to analyze for pattern

# Store candles history per symbol (for 4H timeframe)
candles_history = {symbol: [] for symbol in SYMBOLS}

def epoch_to_local_candle_time(epoch, granularity):
    dt = datetime.datetime.fromtimestamp(epoch).astimezone()
    if granularity == 14400:  # 4H
        hour = (dt.hour // 4) * 4
        return dt.replace(hour=hour, minute=0, second=0, microsecond=0)
    return dt

def add_new_candle(symbol, candle_start, open_p):
    candles_history[symbol].append({
        "start": candle_start,
        "open": open_p,
        "high": open_p,
        "low": open_p,
        "close": open_p,
        "signaled": False,
        "entry_sent": False,
        "signal_time": None,
    })
    # Keep only recent N candles
    if len(candles_history[symbol]) > 100:
        candles_history[symbol].pop(0)

def update_current_candle(symbol, price):
    candle = candles_history[symbol][-1]
    if price > candle["high"]:
        candle["high"] = price
    if price < candle["low"]:
        candle["low"] = price
    candle["close"] = price

def get_last_candles(symbol, n):
    return candles_history[symbol][-n:] if len(candles_history[symbol]) >= n else []

def predict_direction(candles):
    """
    Simple CRT-inspired pattern:
    - Check if last 3 candles show accumulation and then breakout sign
    - For demonstration, if last candle closes higher than open => buy signal
    - If closes lower => sell signal
    - Could be extended with more complex logic
    """
    if len(candles) < 3:
        return None

    c1, c2, c3 = candles[-3], candles[-2], candles[-1]

    # Example pattern:
    # Accumulation: small bodies c1 and c2 (body < threshold)
    # Then breakout candle c3 with big body and direction
    body1 = abs(c1["close"] - c1["open"]) / c1["open"]
    body2 = abs(c2["close"] - c2["open"]) / c2["open"]
    body3 = abs(c3["close"] - c3["open"]) / c3["open"]

    SMALL_BODY = 0.001  # 0.1%
    BIG_BODY = 0.0025   # 0.25%

    if body1 < SMALL_BODY and body2 < SMALL_BODY and body3 > BIG_BODY:
        return "buy" if c3["close"] > c3["open"] else "sell"

    return None

async def run():
    print("🚀 Starting sniper entry CRT tracker with prediction 30s before 4H candle move...")

    async with websockets.connect(URL) as ws:
        # Subscribe to ticks
        for symbol in SYMBOLS:
            await ws.send(json.dumps({"ticks": symbol, "subscribe": 1}))
            print(f"✅ Subscribed to ticks for {symbol}")

        while True:
            msg = await ws.recv()
            data = json.loads(msg)

            if 'tick' in data:
                tick = data['tick']
                symbol = tick['symbol']
                price = tick['quote']
                epoch = tick['epoch']

                candle_start = epoch_to_local_candle_time(epoch, 14400)

                # New candle started?
                if not candles_history[symbol] or candles_history[symbol][-1]["start"] != candle_start:
                    add_new_candle(symbol, candle_start, price)
                    print(f"🕓 New 4H candle started for {symbol} at {candle_start}")

                else:
                    update_current_candle(symbol, price)

                current_candle = candles_history[symbol][-1]

                now = datetime.datetime.now(datetime.timezone.utc).astimezone()
                seconds_after_open = (now - candle_start).total_seconds()

                # We want to send sniper entry signal approx 30 seconds after candle open, before big moves
                if 25 <= seconds_after_open <= 35 and not current_candle["entry_sent"]:
                    # Predict direction using last candles except current incomplete candle
                    past_candles = get_last_candles(symbol, LOOKBACK_CANDLES + 1)[:-1]  # exclude current candle
                    direction = predict_direction(past_candles)

                    if direction is not None:
                        entry = current_candle["open"]
                        if direction == "buy":
                            sl = entry * (1 - MAX_SL_PERCENTAGE)
                            tp = entry + REWARD_RATIO * (entry - sl)
                        else:
                            sl = entry * (1 + MAX_SL_PERCENTAGE)
                            tp = entry - REWARD_RATIO * (sl - entry)

                        risk = abs(entry - sl)
                        if risk <= entry * MAX_SL_PERCENTAGE:
                            current_candle["entry_sent"] = True
                            print(f"\n🔫 [{symbol}] SNIPER ENTRY SIGNAL ({direction.upper()}) 30s after candle open")
                            print(f"🕓 Candle Start: {candle_start.strftime('%Y-%m-%d %H:%M:%S')}")
                            print(f"🎯 Entry: {entry:.2f}")
                            print(f"🛑 Stop Loss: {sl:.2f}")
                            print(f"✅ Take Profit: {tp:.2f}\n")

            elif 'error' in data:
                print("❌ Error:", data['error'].get('message'))

if __name__ == "__main__":
    asyncio.run(run())
