from zappix.dstream import _Dstream
from zappix.protocol import ServerRequest
from enum import Enum
import json
from typing import Dict


class ServerRequestTypeEnum(Enum):
    OVERVIEW = "overview"
    OVERVIEW_BY_PROXY = "overwiew by proxy"
    DETAILS = "details"
    PING = "ping"


class Server(_Dstream):
    def __init__(self, address: str, sid: str, port: int=10051):
        super().__init__(address, port=port)
        self._sid = sid

    def get_queue(self, queue_type: ServerRequestTypeEnum, **kwargs) -> Dict:
        if queue_type not in (
                ServerRequestTypeEnum.OVERVIEW,
                ServerRequestTypeEnum.OVERVIEW_BY_PROXY,
                ServerRequestTypeEnum.DETAILS
        ):
            raise ValueError("Wrong queue type")
        if queue_type == ServerRequestTypeEnum.DETAILS and 'limit' not in kwargs:
            kwargs['limit'] = "100"
        payload = ServerRequest('queue.get', queue_type.value, self._sid, **kwargs)
        response = self._send(payload.to_bytes())
        return json.loads(response)

    @property
    def is_alive(self) -> bool:
        payload = ServerRequest('status.get', "ping", self._sid)
        response = self._send(payload.to_bytes())
        if json.loads(response) == {"response": "success", "data": {}}:
            return True
        return False
