import websocket
import threading
import json
import time

class DerivLiveStreamer:
    def __init__(self, app_id, symbol, granularity, callback):
        self.url = f"wss://ws.binaryws.com/websockets/v3?app_id={app_id}"
        self.symbol = symbol
        self.granularity = granularity
        self.callback = callback
        self.ws = None
        self.running = False

    def start(self):
        self.running = True
        thread = threading.Thread(target=self._run)
        thread.start()

    def _run(self):
        self.ws = websocket.WebSocketApp(
            self.url,
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close
        )
        while self.running:
            self.ws.run_forever()
            time.sleep(5)

    def _on_open(self, ws):
        print("[Connected to Deriv WS]")
        req = {
            "ticks_history": self.symbol,
            "end": "latest",
            "count": 1,
            "subscribe": 1,
            "granularity": self.granularity,
            "style": "candles"
        }
        ws.send(json.dumps(req))

    def _on_message(self, ws, message):
        data = json.loads(message)
        if data.get("candles"):
            c = data["candles"][-1]
            candle = {
                "open": float(c["open"]),
                "high": float(c["high"]),
                "low": float(c["low"]),
                "close": float(c["close"]),
                "epoch": c["epoch"]
            }
            self.callback(candle)

    def _on_error(self, ws, err): print("[WS Error]:", err)
    def _on_close(self, ws, *args): print("[WS Closed]")

    def stop(self):
        self.running = False
        if self.ws:
            self.ws.close()
