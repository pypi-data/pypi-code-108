from typing import List
from requests import Response
from smsit import Message


class Gateway:
    _gateway_name = ""
    _config_params = []
    config = None

    def __init__(self, config: dict):  # pragma: nocover
        self.config = config

    def _call(self, *args, **kwargs) -> Response:  # pragma: nocover
        pass

    def send(self, message: Message) -> List[Response]:  # pragma: nocover
        raise NotImplementedError
