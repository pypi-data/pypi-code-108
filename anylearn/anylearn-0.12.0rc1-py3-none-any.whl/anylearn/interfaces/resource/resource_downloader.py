from abc import ABC, abstractmethod
import asyncio
import cgi
import time
from typing import Optional, Union

import aiofiles
import aiohttp
import requests

from anylearn.config import AnylearnConfig
from anylearn.utils.errors import AnyLearnException
from anylearn.utils.api import get_with_token, post_with_token, url_base


class ResourceDownloader(ABC):
    """
    资源下载接口
    """
    @abstractmethod
    def run(self,
            resource_id: str,
            polling: Union[float, int],
            save_path: Optional[str]=None,
           ):
        """
        执行资源下载,自定义资源上传需实现此方法

        Parameters
        ----------
        resource_id
            资源ID
        save_path
            保存路径
        """
        raise NotImplementedError


class AsyncResourceDownloader(ResourceDownloader):
    """
    资源异步下载工具类
    """

    def run(self,
            resource_id: str,
            save_path: str,
            polling: Union[float, int],
           ):
        return asyncio.run(self.__run(resource_id=resource_id,
                                      save_path=save_path,
                                      polling=polling,
                                     ))

    async def __run(self,
                    resource_id: str,
                    save_path: str,
                    polling: Union[float, int]=5,
                   ):
        """执行异步下载请求

        Args:
            resource_id: 后端资源ID
            save_path: 资源下载保存路径

        Returns:
            bool: 下载成功与否

        Raises:
            ClientResponseError: 当下载过程中出错时由aiohttp包（默认情况）抛出错误
        """

        compress_res = _compress_file(resource_id=resource_id)
        print(f"Resource compress {compress_res}")

        compress_state_res = _compress_complete(resource_id=resource_id, compression_id=compress_res['data'])
        print(f"Resource compress state {compress_state_res}")

        while not compress_state_res['data']:
            time.sleep(polling)
            compress_state_res = _compress_complete(resource_id=resource_id, compression_id=compress_res['data'])
            print(f"Resource compress state {compress_state_res}")

        headers = {'Authorization': f"Bearer {AnylearnConfig.token}"}
        async with aiohttp.ClientSession(headers=headers) as session:
            task = self.__do_download(session=session,
                                      resource_id=resource_id,
                                      compression_id=compress_res['data'],
                                      save_path=save_path)
            res = await asyncio.gather(task)
        return res

    async def __do_download(self, session: aiohttp.ClientSession,
                            resource_id: str,
                            compression_id: str,
                            save_path: str):

        res = await session.get(url=f"{url_base()}/resource/download",
                                raise_for_status=True,
                                params={
                                    'file_id': resource_id,
                                    'compression_id': compression_id,
                                    'token': AnylearnConfig.token
                                })

        content_header = res.headers.get('Content-Disposition')
        if content_header:
            _, params = cgi.parse_header(content_header)
            fileName = params['filename']
            f = await aiofiles.open(f"{save_path}/{fileName}", mode='wb')
            await f.write(await res.read())
            await f.close()
            return fileName
        else:
            return "文件下载失败"


class SyncResourceDownloader(ResourceDownloader):
    """
    资源同步下载工具类
    """

    def run(self,
            resource_id: str,
            save_path: str,
            polling: Union[float, int]=5,
           ):

        compress_res = _compress_file(resource_id=resource_id)
        print(f"Resource compress {compress_res}")

        compress_state_res = _compress_complete(resource_id=resource_id, compression_id=compress_res['data'])
        print(f"Resource compress state {compress_state_res}")

        while not compress_state_res['data']:
            time.sleep(polling)
            compress_state_res = _compress_complete(resource_id=resource_id, compression_id=compress_res['data'])
            print(f"Resource compress state {compress_state_res}")

        headers = {'Authorization': f"Bearer {AnylearnConfig.token}"}

        res = requests.get(url=f"{url_base()}/resource/download",
                           headers=headers,
                           params={
                               'file_id': resource_id,
                               'compression_id': compress_res['data'],
                               'token': AnylearnConfig.token,
                           })
        res.raise_for_status()

        content_header = res.headers.get('Content-Disposition')
        if content_header:
            _, params = cgi.parse_header(content_header)
            fileName = params['filename']
            with open(f"{save_path}/{fileName}", 'wb') as f:
                f.write(res.content)
            return fileName
        else:
            return "文件下载失败"


def _compress_file(resource_id: str):
    res = post_with_token(f"{url_base()}/resource/compression",
                          data={'file_id': resource_id})
    if not res or 'data' not in res:
        raise AnyLearnException("请求未能得到有效响应")
    return res
    
def _compress_complete(resource_id: str, compression_id: str):
    res = get_with_token(f"{url_base()}/resource/compression",
                         data={
                             'file_id': resource_id,
                             'compression_id': compression_id,
                             })
    if not res or 'data' not in res:
        raise AnyLearnException("请求未能得到有效响应")
    return res
