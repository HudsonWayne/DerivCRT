import websocket
import json
import threading

class DerivLiveStreamer:
    def __init__(self, stream_symbol, callback, granularity=60):
        self.symbol = stream_symbol
        self.callback = callback
        self.granularity = granularity
        self.ws = None

    def start(self):
        def on_message(ws, message):
            data = json.loads(message)
            if 'candles' in data:
                for candle in data['candles']:
                    self.callback({
                        'epoch': candle['epoch'],
                        'open': candle['open'],
                        'high': candle['high'],
                        'low': candle['low'],
                        'close': candle['close']
                    })

        def on_open(ws):
            ws.send(json.dumps({
                "ticks_history": self.symbol,
                "style": "candles",
                "granularity": self.granularity,
                "count": 100,
                "subscribe": 1
            }))

        self.ws = websocket.WebSocketApp(
            "wss://ws.binaryws.com/websockets/v3?app_id=1089",
            on_message=on_message,
            on_open=on_open
        )
        threading.Thread(target=self.ws.run_forever).start()
