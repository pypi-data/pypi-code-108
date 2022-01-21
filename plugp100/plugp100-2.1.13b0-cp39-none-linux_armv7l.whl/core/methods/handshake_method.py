from . import taporequest
from typing import Any


class HandshakeMethod(taporequest.TapoRequest):
    def __init__(self, params: Any):
        super().__init__("handshake", params)
