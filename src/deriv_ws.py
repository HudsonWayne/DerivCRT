# deriv_ws.py

import websocket
import threading
import json


class DerivLiveStreamer:
    def __init__(self, stream_symbol="R_100", callback=None, granularity=60):
        self.stream_symbol = stream_symbol
        self.callback = callback
        self.granularity = granularity
        self.running = False
        self.ws = None

    def on_open(self, ws):
        print("[DEBUG] WebSocket opened")
        payload = {
            "ticks_history": self.stream_symbol,
            "style": "candles",
            "granularity": self.granularity,
            "count": 1,
            "subscribe": 1
        }
        ws.send(json.dumps(payload))
        print(f"[DEBUG] Sent subscription request: {payload}")

    def on_message(self, ws, message):
        data = json.loads(message)
        msg_type = data.get("msg_type", "")

        if msg_type == "history":
            candles = data.get("candles", [])
            for candle in candles:
                parsed = self.parse_candle(candle)
                if self.callback:
                    self.callback(parsed)

        elif msg_type == "candles":
            candle = data.get("candles", [None])[0]
            if candle:
                parsed = self.parse_candle(candle)
                if self.callback:
                    self.callback(parsed)

        else:
            print(f"[DEBUG] Ignored msg_type: {msg_type}")
            if "error" in data:
                print("[ERROR] Message:", data["error"])

    def parse_candle(self, candle):
        return {
            "epoch": int(candle["epoch"]),
            "open": float(candle["open"]),
            "high": float(candle["high"]),
            "low": float(candle["low"]),
            "close": float(candle["close"]),
        }

    def on_error(self, ws, error):
        print("[ERROR] WebSocket error:", error)

    def on_close(self, ws, close_status_code, close_msg):
        print("[DEBUG] WebSocket closed")

    def run(self):
        websocket.enableTrace(False)
        self.ws = websocket.WebSocketApp(
            "wss://ws.derivws.com/websockets/v3?app_id=80707",
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )
        self.running = True
        self.ws.run_forever()

    def start(self):
        thread = threading.Thread(target=self.run)
        thread.daemon = True
        thread.start()
        print("[INFO] DerivLiveStreamer started")

    def stop(self):
        self.running = False
        if self.ws:
            self.ws.close()
