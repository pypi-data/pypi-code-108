from fabrique_actor.actors import Collector
import json  # or another serialization lib


class Actor(Collector):
    def __init__(self):
        """here can be db connection, or query connection, or something else"""
        super().__init__()

    def _collect(self, mes_body: bytes) -> None:
        """your custom method for collecting message, returns nothing"""
        payload = json.loads(mes_body)  # can be any binary data, here we require json
        self.logger.info(payload)  # just print to stout in this example

    def process_message(self, mes_body: bytes):
        self._collect(mes_body)
