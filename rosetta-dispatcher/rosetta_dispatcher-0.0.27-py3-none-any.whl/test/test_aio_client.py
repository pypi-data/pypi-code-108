import json
from datetime import datetime
import asyncio

from rosetta_dispatcher.aio_dispatch_client import AioDispatchClient


async def main():
    print('main1')
    host = '61.160.36.168'
    port = 4032
    dc = await AioDispatchClient.create(redis_host=host, redis_port=port)

    data = {
        "source_language": "zh",
        "target_language": "en",
        "terminology_list": [
        ],
        "chapter_content": [
            ""
        ]
    }

    async def process():
        while True:
            # print('before process')
            start = datetime.utcnow()
            result = await dc.process(service_queue='NMT_RPC_QUEUE_DEV', data=json.dumps(data), timeout=100)
            end = datetime.utcnow()
            if not result:
               print(end - start, result)

    tasks = [process() for i in range(16)]
    await asyncio.wait(tasks)


futures = [main()]
loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.wait(futures))
