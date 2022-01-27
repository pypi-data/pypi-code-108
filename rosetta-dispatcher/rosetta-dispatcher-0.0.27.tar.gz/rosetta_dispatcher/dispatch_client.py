import json
import redis

from rosetta_dispatcher.idtool import idtool
from rosetta_dispatcher.model.dispatch_response_model import DispatchResponseModel
from rosetta_dispatcher.model.dispatch_types import DispatchRequestType, DispatchResponseStatus


class DispatchClient:
    def __init__(self, redis_host: str, redis_port: int):
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.pool = redis.ConnectionPool(host=redis_host, port=redis_port, decode_responses=True)

    def process(self, service_queue: str, data: str, timeout: int = 500) -> DispatchResponseModel:
        r = redis.Redis(connection_pool=self.pool)

        reply_to = idtool.gen_uuid()
        correlation_id = idtool.gen_uuid()
        request = {
            'content_type': DispatchRequestType.JSON,
            'reply_to': reply_to,
            'correlation_id': correlation_id,
            'timeout': timeout,
            'data': data
        }

        r.rpush(service_queue, json.dumps(request, ensure_ascii=False))
        result = r.blpop(reply_to, timeout=timeout)
        if result and result[0] == reply_to:
            response = DispatchResponseModel.parse_obj(json.loads(result[1]))
            if response.correlation_id == correlation_id:
                return response
        return DispatchResponseModel(status=DispatchResponseStatus.NO_RESPONSE_ERROR, data='Failed to get response from server')
