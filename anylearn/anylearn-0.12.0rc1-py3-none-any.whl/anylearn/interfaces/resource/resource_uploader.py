from abc import ABC, abstractmethod
import asyncio

import aiohttp
import requests
from tqdm import tqdm

from anylearn.config import AnylearnConfig
from anylearn.utils import logger
from anylearn.utils.api import url_base


class ResourceUploader(ABC):
    """
    资源上传工具接口
    """

    @abstractmethod
    def run(self, resource_id: str, chunks: list):
        """
        执行资源上传,自定义资源上传需实现此方法

        Parameters
        ----------
        resource_id
            资源ID
        chunks
            被切割后的文件内容列表
        """
        raise NotImplementedError


class AsyncResourceUploader(ResourceUploader):
    """
    资源异步上传工具类
    """

    def __init__(self, on_start=None, on_progress=None):
        self.__counter = 0
        self.__total = 0
        self.__on_start = on_start
        self.__on_progress = on_progress
        super().__init__()

    def run(self, resource_id: str, chunks: list):
        """
        执行资源上传
        """
        return asyncio.run(self.__run(resource_id=resource_id,
                                      chunks=chunks))

    async def __run(self, resource_id: str, chunks: list):
        """执行异步上传请求

        Args:
            resource_id: 后端资源ID
            chunks: 被切割后的文件内容列表

        Returns:
            bool: 上传成功与否
        
        Raises:
            ClientResponseError: 当上传过程中出错时由aiohttp包（默认情况）抛出错误
        """

        self.__counter = 0
        self.__total = len(chunks)
        if callable(self.__on_start):
            self.__on_start(self.__total)

        headers = {'Authorization': f"Bearer {AnylearnConfig.token}"}
        async with aiohttp.ClientSession(headers=headers) as session:
            tasks = [self.__do_upload(session=session,
                                      resource_id=resource_id,
                                      chunk=chunk,
                                      chunk_index=i)
                        for (i, chunk) in enumerate(chunks)]
            res = await asyncio.gather(*tasks)
        return all(res)

    async def __do_upload(self,
                          session: aiohttp.ClientSession,
                          resource_id: str,
                          chunk: str,
                          chunk_index: int):
        res = await session.request(method="POST",
                                    url=f"{url_base()}/resource/upload",
                                    raise_for_status=True,
                                    data={
                                        'file_id': resource_id,
                                        'file': chunk,
                                        'chunk': str(chunk_index),
                                    })
        self.__counter += 1
        if callable(self.__on_progress):
            self.__on_progress(self.__counter, self.__total)
        return res.ok


class SyncResourceUploader(ResourceUploader):
    def run(self, resource_id: str, chunks: list):
        for i, chunk in enumerate(tqdm(chunks)):
            url = f"{url_base()}/resource/upload"
            headers = {'Authorization': f"Bearer {AnylearnConfig.token}"}
            files = {'file': chunk}
            data = {'file_id': resource_id, 'chunk': str(i)}
            res = requests.post(url, headers=headers, files=files, data=data)
            res.raise_for_status()
