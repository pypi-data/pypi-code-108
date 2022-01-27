import websocket
from .yaticker_pb2 import yaticker
import base64
import json
from threading import Thread

class YahooStreamer:
    def __init__(self, tickers, bar_update_callback):
        self.tickers = tickers


        self.ws = websocket.WebSocketApp(
            "wss://streamer.finance.yahoo.com/",
            on_message = lambda ws, msg: self.on_message(ws, msg),
            on_open = lambda ws: self.on_open(ws),
        )


        self.bar_update_callback = bar_update_callback
        self.pb = yaticker()

    def start(self, threaded=True):
        if threaded:
            self._thread = Thread(target=self.ws.run_forever, daemon=True).start()
        else:
            self.ws.run_forever()

    def stop(self):
        self.ws.close()

    def on_open(self, ws):
        ws.send(json.dumps({"subscribe": self.tickers}))

    def on_message(self, ws, message):
        message_bytes = base64.b64decode(message)
        self.pb.ParseFromString(message_bytes)

        data = {
            "id": self.pb.id,
            "exchange": self.pb.exchange,
            "quoteType": self.pb.quoteType,
            "price": self.pb.price,
            "timestamp": self.pb.time,
            "marketHours": self.pb.marketHours,
            "changePercent": self.pb.changePercent,
            "dayVolume": self.pb.dayVolume,
            "change": self.pb.change,
            "priceHint": self.pb.priceHint
        }

        self.bar_update_callback(data)

    def add_ticker(self, ticker):
        self.ws.send(json.dumps({"subscribe": [ticker]}))
        self.tickers.append(ticker)

    def remove_ticker(self, ticker):
        self.ws.send(json.dumps({"unsubscribe": [ticker]}))
        self.tickers.remove(ticker)
    