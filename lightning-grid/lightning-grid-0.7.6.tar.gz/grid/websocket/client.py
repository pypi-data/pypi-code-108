from dataclasses import dataclass
import urllib.parse

from websocket import create_connection, WebSocketBadStatusException
from requests.models import PreparedRequest


@dataclass
class WebSocketClient:
    base_url: str
    token: str

    def connect(self, subscription_path, query_params=None):
        url = urllib.parse.urljoin(self.base_url, subscription_path)
        req = PreparedRequest()
        query_params["token"] = self.token
        req.prepare_url(url, query_params)
        # change the scheme only after prepare_url
        ws_url = req.url.replace("http", "ws", 1)
        # TODO - connection exception messages are ignored by the websocket-client package. We must be able to push a
        # fix upstream - https://github.com/websocket-client/websocket-client/issues/758
        return create_connection(ws_url)
