from nautilus_trader.core.correctness import PyCondition

from nacre.adapters.zb.http.client import ZbHttpClient


class ZbSpotAccountHttpAPI:
    def __init__(self, client: ZbHttpClient):
        """
        Initialize a new instance of the ``ZbSpotAccountHttpAPI`` class.

        Parameters
        ----------
        client : ZbHttpClient
            The Binance REST API client.

        """
        PyCondition.not_none(client, "client")

        self.client = client
