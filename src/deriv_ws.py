import websocket
import json
import threading
from datetime import datetime

class DerivLiveStreamer:
    def __init__(self, symbol, callback):
        self.symbol = symbol
        self.callback = callback
        self.ws = None

    def _on_message(self, ws, message):
        print("[DEBUG] Message received:", message)
        data = json.loads(message)

        if data.get('msg_type') == 'candles':
            ohlc = data['candles'][0]  # First (latest) candle in list
            candle = {
                'timestamp': datetime.utcfromtimestamp(ohlc['epoch']),
                'open': float(ohlc['open']),
                'high': float(ohlc['high']),
                'low': float(ohlc['low']),
                'close': float(ohlc['close']),
            }
            print(f"[DEBUG] Candle received: {candle}")
            self.callback(candle)
        else:
            print(f"[DEBUG] Unhandled msg_type = {data.get('msg_type')}")
            print("[DEBUG] Full response:", json.dumps(data, indent=2))

    def _on_open(self, ws):
        print("[DEBUG] WebSocket connection opened.")
        request = {
            "ticks_history": self.symbol,
            "granularity": 60,            # 1-minute candles
            "style": "candles",
            "end": "latest",
            "subscribe": 1
        }
        ws.send(json.dumps(request))
        print("[DEBUG] Sent subscription request:", request)

    def _on_error(self, ws, error):
        print(f"[ERROR] WebSocket error: {error}")

    def _on_close(self, ws, close_status_code, close_msg):
        print(f"[INFO] WebSocket closed: {close_status_code}, {close_msg}")

    def start(self):
        print("[DEBUG] Starting WebSocket...")
        self.ws = websocket.WebSocketApp(
            "wss://ws.binaryws.com/websockets/v3?app_id=1089",
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close
        )
        threading.Thread(target=self.ws.run_forever, daemon=True).start()

    def stop(self):
        if self.ws:
            self.ws.close()
