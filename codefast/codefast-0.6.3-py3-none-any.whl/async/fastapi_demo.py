import random
import aiohttp
import redis
import json
from fastapi import FastAPI
import asyncio
import codefast as cf
from typing import Any
import time


class TaskData:
    def __init__(self,
                 task_id: str,
                 task_type: str,
                 task_data: Any,
                 is_finished: False = False):
        self.__task_id = task_id
        self.task_type = task_type
        self.task_data = task_data
        self.is_finished = is_finished

    @property
    def task_id(self):
        """Bind task_id to task_type to facilitate indexing"""
        if not self.__task_id.startswith(self.task_type):
            self.__task_id = '_'.join(
                [self.task_type, str(int(time.time())), self.__task_id])
        return self.__task_id

    def __repr__(self) -> str:
        return json.dumps({**self.__dict__, 'task_id': self.task_id})


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class Shared(metaclass=SingletonMeta):
    """ objects shared between tasks """

    def __init__(self) -> None:
        self.client = redis.Redis(host='localhost', port=6379, db=0)
        self.memcache = asyncio.Queue(maxsize=1000)
        # To limit the number of working tasks
        self.wip_queue = asyncio.Queue(maxsize=10)


class TaskConsumer:
    async def get_ipinfo(self):
        """Get ipinfo asynchronously"""
        _instance = Shared()
        await _instance.wip_queue.put('')
        data = await _instance.memcache.get()
        cf.info('working in progress: {}'.format(
            _instance.wip_queue.qsize()))
        cf.info('Queue data', data)
        async with aiohttp.ClientSession() as session:
            await asyncio.sleep(random.randint(1, 3))
            async with session.get(
                    'https://ipinfo.io/json?token=772c4af07ae51f') as resp:
                ipinfo = await resp.json()
                cf.info(ipinfo)
                await _instance.wip_queue.get()
                return ipinfo['ip']


app = FastAPI()


@app.get("/users/me")
async def read_user_me():
    return {"user_id": "the current user"}


@app.get("/task/{task_id}")
async def create_task(task_id: str):
    consumer = TaskConsumer()
    uuid = cf.uuid()
    task = TaskData(uuid,
                    task_type="get_ipinfo",
                    task_data={"task_id": task_id})
    # client.set(task.task_id, json.dumps(task, default=vars))
    _instance = Shared()
    await _instance.memcache.put(task)
    asyncio.create_task(consumer.get_ipinfo())
    cf.info('current queue size', _instance.memcache.qsize())
    return {'message': 'Ok', 'code': 200}


'''
start with uvicorn
uvicorn fastapi_demo:app --reload
'''
