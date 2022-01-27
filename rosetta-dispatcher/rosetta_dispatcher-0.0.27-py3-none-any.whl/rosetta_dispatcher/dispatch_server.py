import json
import time
from typing import List

import redis

from rosetta_dispatcher.idtool import idtool
from rosetta_dispatcher.model.dispatch_request_model import DispatchRequestModel
from rosetta_dispatcher.model.dispatch_response_model import DispatchResponseModel
from rosetta_dispatcher.redis_client import RedisClient


class DispatchServer:
    def __init__(self, redis_host: str, redis_port: int, response_timeout: int = 60, password=None):
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.password = password
        self.response_timeout = response_timeout
        self.client = RedisClient(host=redis_host, port=redis_port, password=self.password, decode_responses=True)


    def preprocess_request(self, strrequest: str) -> DispatchRequestModel:
        if strrequest:
            dict_request = json.loads(strrequest)
            request = DispatchRequestModel.parse_obj(dict_request)
            if request.correlation_id:
                start_time = idtool.get_timestamp(request.correlation_id)
                ts_now = time.time()
                if ts_now < start_time + request.timeout:
                    return request

        return None

    def __fetch_one__(self, r: redis.Redis, service_queue: str):
        return

    def __batch_fetch__(self, r: redis.Redis, service_queue: str, batch_count: int = 16):
        p = r.pipeline()
        p.multi()  # starts transactional block of pipeline
        items = p.lrange(service_queue, 0, batch_count - 1)
        p.ltrim(service_queue, batch_count, -1)
        messages, trim_success = p.execute()  # ends transactional block of pipeline

        result = []
        for strrequest in messages:
            request = self.preprocess_request(strrequest)
            if request:
                result.append(request)
            else:
                print('drop time out request')
        return result

    def fetch(self, service_queue: str, batch_count=16, timeout: int = 10) -> List[DispatchRequestModel]:
        r = self.client.conn
        result = self.__batch_fetch__(r, service_queue, batch_count)

        if result:
            return result

        # block and wait data.
        trequest = r.blpop(keys=service_queue, timeout=timeout)
        # None data fetched.
        if not trequest:
            return result

        request = self.preprocess_request(trequest[1])
        if request:
            result.append(request)

        batch_requests = self.__batch_fetch__(r, service_queue, batch_count-1)
        if batch_requests:
            result += batch_requests
        return result

    def send_response(self, response_queue: str, response: DispatchResponseModel):
        r = self.client.conn
        data = response.dict(exclude_none=True)
        r.rpush(response_queue, json.dumps(data, ensure_ascii=True))
        r.expire(response_queue, time=self.response_timeout)

    def batch_send_response(self, response_queue_list: List[DispatchRequestModel], response_list: List[DispatchResponseModel]):
        if len(response_queue_list) != len(response_queue_list):
            raise Exception("response queue list is not equal response_list")

        r = self.client.conn
        p = r.pipeline()
        for request, response in zip(response_queue_list, response_list):
            data = response.dict(exclude_none=True)
            p.rpush(request.reply_to, json.dumps(data, ensure_ascii=True))
            p.expire(request.reply_to, time=self.response_timeout)
        p.execute()  # ends transactional block of pipeline
