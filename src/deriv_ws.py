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
        data = json.loads(message)
        if data.get('msg_type') == 'ohlc':
            ohlc = data['ohlc']
            candle = {
                'timestamp': datetime.utcfromtimestamp(ohlc['open_time']),
                'open': float(ohlc['open']),
                'high': float(ohlc['high']),
                'low': float(ohlc['low']),
                'close': float(ohlc['close']),
            }
            self.callback(candle)

    def _on_open(self, ws):
        request = {
            "ticks_history": self.symbol,
            "style": "candles",
            "granularity": 60,  # 1-minute candles
            "count": 1,
            "subscribe": 1
        }
        ws.send(json.dumps(request))

    def start(self):
        self.ws = websocket.WebSocketApp(
            "wss://ws.binaryws.com/websockets/v3?app_id=1089",
            on_message=self._on_message,
            on_open=self._on_open
        )
        threading.Thread(target=self.ws.run_forever).start()

    def stop(self):
        if self.ws:
            self.ws.close()
