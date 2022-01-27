#!/usr/bin/python3
import json
from datetime import datetime

from fastapi import FastAPI, Response, status

from rosetta_dispatcher.aio_dispatch_client import AioDispatchClient
from rosetta_dispatcher.model.dispatch_response_model import DispatchResponseModel
from rosetta_dispatcher.model.dispatch_types import DispatchResponseStatus

app = FastAPI()
dc: AioDispatchClient = None


@app.get("/")
async def root(response: Response):
    # return "hello world"
    data = {
        "source_language": "zh",
        "target_language": "en",
        "terminology_list": [
        ],
        "chapter_content": [
            ""
        ]
    }

    # print('before process')
    start = datetime.utcnow()
    result: DispatchResponseModel = await dc.process(service_queue='BATCH_WORKER_QUEUE_DEV', data=json.dumps(data), timeout=60)
    end = datetime.utcnow()
    if not result:
        print(end - start, result)

    if result.status == DispatchResponseStatus.OK:
        return result.data
    else:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR



@app.on_event("startup")
async def init_service():
    global dc
    print('init_server')
    host = '10.130.64.132'
    port = 4012
    dc = await AioDispatchClient.create(redis_host=host, redis_port=port)
