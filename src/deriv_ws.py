import websocket
import json
import threading
import time
from datetime import datetime

class DerivLiveStreamer:
    def __init__(self, symbol, on_candle_callback):
        self.symbol = symbol
        self.on_candle_callback = on_candle_callback
        self.ws = None

    def _on_message(self, ws, message):
        data = json.loads(message)
        if data.get("msg_type") == "ohlc":
            ohlc = data["ohlc"]
            candle = {
                "timestamp": datetime.fromtimestamp(ohlc["epoch"]),
                "open": float(ohlc["open"]),
                "high": float(ohlc["high"]),
                "low": float(ohlc["low"]),
                "close": float(ohlc["close"]),
            }
            self.on_candle_callback(candle)

    def _on_error(self, ws, error):
        print(f"WebSocket error: {error}")

    def _on_close(self, ws, close_status_code, close_msg):
        print("WebSocket closed")

    def _on_open(self, ws):
        req = {
            "ticks_history": self.symbol,
            "end": "latest",
            "count": "5000",
            "granularity": 60,
            "style": "candles",
            "subscribe": 1
        }
        ws.send(json.dumps(req))

    def start(self):
        websocket.enableTrace(False)
        self.ws = websocket.WebSocketApp(
            "wss://ws.binaryws.com/websockets/v3?app_id=1089",
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close
        )
        wst = threading.Thread(target=self.ws.run_forever)
        wst.daemon = True
        wst.start()
        while True:
            time.sleep(1)
