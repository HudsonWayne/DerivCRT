import websocket
import threading
import json
import time

class DerivLiveStreamer:
    def __init__(self, app_id, symbol, granularity, callback):
        self.app_id = str(app_id)
        self.symbol = symbol
        self.granularity = granularity
        self.callback = callback
        self.ws = None
        self._running = False

    def start(self):
        self._running = True
        thread = threading.Thread(target=self._run_websocket, daemon=True)
        thread.start()

    def _on_message(self, ws, message):
        data = json.loads(message)
        if 'msg_type' in data and data['msg_type'] == 'candles':
            candles = data.get('candles', [])
            if candles:
                last_candle = candles[-1]
                candle_data = {
                    "open": float(last_candle['open']),
                    "high": float(last_candle['high']),
                    "low": float(last_candle['low']),
                    "close": float(last_candle['close']),
                    "epoch": int(last_candle['epoch']),
                }
                self.callback(candle_data)

    def _on_error(self, ws, error):
        print("[WebSocket error]:", error)

    def _on_close(self, ws, close_status_code, close_msg):
        print("[WebSocket closed]:", close_status_code, close_msg)
        self._running = False

    def _on_open(self, ws):
        print("[WebSocket connected]")
        subscribe_msg = {
            "ticks_history": self.symbol,
            "end": "latest",
            "start": 1,
            "style": "candles",
            "granularity": self.granularity,
            "req_id": 1,
            "subscribe": 1,
        }
        ws.send(json.dumps(subscribe_msg))

    def _run_websocket(self):
        ws_url = f"wss://ws.binaryws.com/websockets/v3?app_id={self.app_id}"
        self.ws = websocket.WebSocketApp(
            ws_url,
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
        )
        while self._running:
            self.ws.run_forever()
            print("[Reconnecting in 5 seconds...]")
            time.sleep(5)

    def stop(self):
        self._running = False
        if self.ws:
            self.ws.close()
