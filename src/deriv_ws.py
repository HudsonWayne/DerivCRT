class DerivLiveStreamer:
    def __init__(self, stream_symbol, callback):
        self.symbol = stream_symbol
        self.callback = callback
        self.ws = None

    def start(self):
        def on_message(ws, message):
            data = json.loads(message)
            if 'candles' in data:
                candle = data['candles'][-1]
                self.callback(candle)

        def on_open(ws):
            print("[DEBUG] WebSocket connection opened.")
            request = {
                "subscribe": 1,
                "candles": self.symbol,
                "style": "candles",
                "granularity": 60
            }
            ws.send(json.dumps(request))

        self.ws = websocket.WebSocketApp(
            "wss://ws.derivws.com/websockets/v3",
            on_open=on_open,
            on_message=on_message
        )
        self.ws.run_forever()
