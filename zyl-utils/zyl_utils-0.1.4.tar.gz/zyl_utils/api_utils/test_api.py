# encoding: utf-8
"""
@author: zyl
@file: test_api.py
@time: 2021/12/10 17:06
@desc:
"""
import asyncio
import time
from typing import List

import aiohttp
import requests


class TestAPI:
    def __init__(self):
        pass

    @staticmethod
    def test_api_sample(url, data):
        """

        Args:
            url: str
            data: a json fata

        Returns:
        >>> to_predict = {"sentences": to_predict})  # type:json
        >>> url = "http://0.0.0.0:3245/predict/"
        >>> TestAPI.test_api_sample(url=url, data=to_predict)
        """
        t1 = time.time()
        response = requests.post(url, json=data)
        print(response)
        t2 = time.time()
        print('spend time:' + str((t2 - t1) / 60) + 'minutes.')
        return response

    @staticmethod
    async def one_request(client, url, json):
        resp = await client.post(url=url, json=json)
        result = resp.json
        return result

    @staticmethod
    async def parallel_request(url, json: List[list]):
        """
        并行请求
        Args:
            url: url
            json: 准备的并行数据，每组数据都可以单独请求

        Returns:
        >>> url = "http://0.0.0.0:3245/predict/"
        >>> json =  [list(range(10)},list(range(10)},list(range(10)},]
        >>> asyncio.run(TestAPI.parallel_request(url,json))
        """
        # timeout = aiohttp.ClientTimeout(total=200)
        async with aiohttp.ClientSession() as client:
            start_time = time.time()
            task_list = []
            for i in json:
                req = TestAPI.one_request(client, url, [i])
                task = asyncio.create_task(req)
                task_list.append(task)
            res = await asyncio.gather(*task_list)
            end_time = time.time()
        print('spend time:' + str((end_time - start_time) / 60) + 'minutes.')
        return res
