import os
import sys
import re
import json
import traceback
import user_agent
import socket
import websocket
import ssl
import time
import random
import requests
import collections
import urllib
import aiohttp
import asyncio
import functools
from copy import deepcopy
from retry import retry
from urllib.parse import urlparse

from kwtools.settings import logger




METHOD_LOCKERS = {} # Coroutine lockers. e.g. {"locker_name": locker}


def async_method_locker(name, wait=True, timeout=1):
    """ In order to share memory between any asynchronous coroutine methods, we should use locker to lock our method,
        so that we can avoid some un-prediction actions.

    Args:
        name: Locker name.
        wait: If waiting to be executed when the locker is locked? if True, waiting until to be executed, else return
            immediately (do not execute).
        timeout: Timeout time to be locked, default is 1s.

    NOTE:
        This decorator must to be used on `async method`. [必须是协程函数]
    """
    assert isinstance(name, str)

    def decorating_function(method):
        global METHOD_LOCKERS
        locker = METHOD_LOCKERS.get(name)
        if not locker:
            locker = asyncio.Lock()
            METHOD_LOCKERS[name] = locker

        @functools.wraps(method)
        async def wrapper(*args, **kwargs):
            if not wait and locker.locked():
                return # QUESTION: 直接返回None会有问题吗?
            try:
                await locker.acquire()
                return await asyncio.wait_for(method(*args, **kwargs), timeout)
                # return await method(*args, **kwargs)
            finally:
                locker.release()
        return wrapper
    return decorating_function



class AsyncRequests(object):
    """ Asynchronous HTTP Request Client.
    """

    # Every domain name holds a connection session, for less system resource utilization and faster request speed.
    _SESSIONS = {}  # {"domain-name": session, ... }

    @classmethod
    async def ensure_aio_req(cls, url, method="GET", retry_times=1, timeout=15, **kwargs):
        """ Retry asyncio request
        Function: 重试多次请求, 确保访问正常
        Tips:
            - 因为aio_req对预期内和预期外都做了捕获, 所以ensure_aio_req就不需要做这层异常捕获了
        """
        error = None
        i = 1
        while i <= retry_times:
            try:
                if i != 1:
                    logger.info("====================================================")
                    logger.info(f"[网络请求异常] 尝试第 {i} 次访问....")
                    logger.info("====================================================")
                    await asyncio.sleep(5)
                code, success, error = await cls.aio_req(method=method, url=url, timeout=timeout, **kwargs)
                if error:
                    raise IOError(error)
                elif isinstance(success, str):
                    try:
                        success = json.loads(success)
                    except:
                        pass
                return code, success, None
            except Exception as e:
                try:
                    error = json.loads(str(e))
                except:
                    error = str(e)
                logger.warning(error)
                logger.warning(f"[Req Error] ({i}/{retry_times} retry request)")
            i += 1
        return code, None, error


    @classmethod
    async def aio_req(cls, url, method="GET", params={}, data=None, headers={}, timeout=15, **kwargs):
        """ Create a HTTP request.

        Args:
            method: HTTP request method. `GET` / `POST` / `PUT` / `DELETE`
            url: Request url.
            params: HTTP query params.
            data: HTTP request body, dict format.
            headers: HTTP request header.
            timeout: HTTP request timeout(seconds), default is 10s.

            **kwargs:
                cookies: pass
                proxy: HTTP proxy. (no proxy need to pass None, not "") <str>
                auth: pass
                allow_redirects: default is True;
                verify_ssl: pass

        Return:
            code: HTTP response code.
            success: HTTP response data. If something wrong, this field is None.
            error: If something wrong, this field will holding a Error information, otherwise it's None.
                    (调用者: 'success为空'不一定表示异常; 但'error为真'一定表示异常)

        Raises:
            HTTP request exceptions or response data parse exceptions. All the exceptions will be captured and return
            Error information.

        Notices:
            1. data: if `data` is not passed, must be `None`, can not be `{}`. [Careful!!]

        Tips:
            1. 对请求过程做了完备的异常处理 (预期内和预期外都做了捕获)
            2. error_type:
                    <class 'OSError'>: 预期内的异常
                    <class 'Exception'>: 预期外的异常
        """
        session = cls._get_session(url)
        try:
            if method.upper() == "GET":
                response = await session.get(url, params=params, headers=headers, timeout=timeout, **kwargs)
            elif method.upper() == "POST":
                response = await session.post(url, params=params, json=data, headers=headers, timeout=timeout, **kwargs)
            elif method.upper() == "PUT":
                response = await session.put(url, params=params, json=data, headers=headers, timeout=timeout, **kwargs)
            elif method.upper() == "DELETE":
                response = await session.delete(url, params=params, json=data, headers=headers, timeout=timeout, **kwargs)
            else:
                raise IOError(f"[Http Method Error] method:{method}")

            try:
                code = float(response.status) # type: int # status_code
            except:
                raise IOError(f"[Response object is error] response:{response}")

            if code // 100 != 2:
                error = await response.text()
                raise IOError(error)
            else:
                try:
                    result = await response.json()
                except:
                    result = await response.text()
                logger.verbose("--------[SUCCESS]--------->>")
                logger.verbose(f"[method]: {method}")
                logger.verbose(f"[url]: {url}")
                logger.verbose(f"[params]: {params}")
                logger.verbose(f"[data]: {data}")
                logger.verbose(f"[headers]: {headers}")
                logger.verbose(f"[timeout]: {timeout}")
                logger.verbose(f"[kwargs]: {kwargs}")
                logger.verbose(f"[proxy]: {kwargs.get('proxy')}")
                logger.verbose(f"[code]: {code}")
                logger.verbose(f"[result]: {result}")
                logger.verbose("<<--------[SUCCESS]---------")
                return code, result, None

        except Exception as e:
            error_type = type(e)
            if error_type is asyncio.TimeoutError:
                error = f"[asyncio.TimeoutError] 请求超时...."
            else:
                error = str(e)
            if not error:
                error = f"[未知错误] 没有错误内容...."
            try:
                code
            except:
                code = 400
            logger.warning("---------[ERROR]--------->>")
            logger.warning(f"[error_type]: {error_type}")
            logger.warning(f"[error]: {error}")
            logger.warning(f"[method]: {method}")
            logger.warning(f"[url]: {url}")
            logger.warning(f"[params]: {params}")
            logger.warning(f"[data]: {data}")
            logger.warning(f"[headers]: {headers}")
            logger.warning(f"[timeout]: {timeout}")
            logger.warning(f"[kwargs]: {kwargs}")
            logger.warning(f"[proxy]: {kwargs.get('proxy')}")
            logger.warning("<<--------[ERROR]---------")
            return 400, None, error


    @classmethod
    def _get_session(cls, url):
        """ Get the connection session for url's domain, if no session, create a new.

        Args:
            url: HTTP request url.

        Returns:
            session: HTTP request session.
        """
        parsed_url = urlparse(url)
        key = parsed_url.netloc or parsed_url.hostname
        if key not in cls._SESSIONS:
            session = aiohttp.ClientSession()
            cls._SESSIONS[key] = session
        return cls._SESSIONS[key]


    @classmethod
    @async_method_locker("AsyncRequests.close.locker", timeout=5)
    async def close(cls):
        for key in list(cls._SESSIONS.keys()):
            await cls._SESSIONS[key].close()
            del cls._SESSIONS[key]



class Requests(object):
    """ Synchronous HTTP Request Client.
    """

    # Every domain name holds a connection session, for less system resource utilization and faster request speed.
    _SESSIONS = {}  # {"domain-name": session, ... }

    @classmethod
    def ensure_req(cls, url, method="GET", retry_times=1, timeout=15, **kwargs):
        """ Retry asyncio request
        Function: 重试多次请求, 确保访问正常
        Tips:
            - 因为aio_req对预期内和预期外都做了捕获, 所以ensure_aio_req就不需要做这层异常捕获了
        """
        error = None
        i = 1
        while i <= retry_times:
            try:
                if i != 1:
                    logger.info("====================================================")
                    logger.info(f"[网络请求异常] 尝试第 {i} 次访问....")
                    logger.info("====================================================")
                    time.sleep(3)
                code, success, error = cls.req(method=method, url=url, timeout=timeout, **kwargs)
                if error:
                    raise IOError(error)
                elif isinstance(success, str):
                    try:
                        success = json.loads(success)
                    except:
                        pass
                return code, success, None
            except Exception as e:
                try:
                    error = json.loads(str(e))
                except:
                    error = str(e)
                logger.warning(error)
                logger.warning(f"[Req Error] ({i}/{retry_times} retry request)")
            i += 1
        return code, None, error


    @classmethod
    def req(cls, url, method="GET", params={}, data=None, headers={}, timeout=15, **kwargs):
        """ Create a HTTP request.

        Args:
            method: HTTP request method. `GET` / `POST` / `PUT` / `DELETE`
            url: Request url.
            params: HTTP query params.
            data: HTTP request body, dict format.
            headers: HTTP request header.
            timeout: HTTP request timeout(seconds), default is 10s.

            **kwargs:
                cookies: pass
                proxy: don't have this parameter, the correct parameter is `proxies` (为了和aio_req的参数统一, 保留在这)
                proxies: <dict>; eg: {"http" : "http://127.0.0.1:7890"}
                auth: pass; (default is None)
                allow_redirects: (default is True)
                verify: <bool>; eg: True or False


        Return:
            code: HTTP response code.
            success: HTTP response data. If something wrong, this field is None.
            error: If something wrong, this field will holding a Error information, otherwise it's None.
                    (调用者: 'success为空'不一定表示异常; 但'error为真'一定表示异常)

        Raises:
            HTTP request exceptions or response data parse exceptions. All the exceptions will be captured and return
            Error information.

        Notices:
            1. data: if `data` is not passed, must be `None`, can not be `{}`. [Careful!!]
            2. params: can merged into `url` parameter (so `params` is always empty)

        Tips:
            1. 对请求过程做了完备的异常处理 (预期内和预期外都做了捕获)
            2. error_type:
                    <class 'OSError'>: 预期内的异常
                    <class 'Exception'>: 预期外的异常
        """
        # 创建会话对象
        session = cls._get_session(url)

        # 参数处理
        if "proxy" in kwargs.keys():
            proxy = kwargs.pop("proxy")
            if isinstance(proxy, str):
                if proxy.split("://")[0] == "https":
                    kwargs["proxies"] = {"https":proxy}
                elif proxy.split("://")[0] == "http":
                    kwargs["proxies"] = {"http":proxy}
        if "verify" in kwargs.keys():
            verify = kwargs.get("verify")
            kwargs.pop("verify")
        else:
            verify = False
        if isinstance(data, dict):
            data = json.dumps(data)

        try:
            if method.upper() == "GET":
                response = session.get(url, params=params, headers=headers, timeout=timeout, verify=verify, **kwargs)
            elif method.upper() == "POST":
                response = session.post(url, params=params, data=data, headers=headers, timeout=timeout, verify=verify, **kwargs)
            elif method.upper() == "PUT":
                response = session.put(url, params=params, data=data, headers=headers, timeout=timeout, verify=verify, **kwargs)
            elif method.upper() == "DELETE":
                response = session.delete(url, params=params, data=data, headers=headers, timeout=timeout, verify=verify, **kwargs)
            else:
                raise IOError(f"[Http Method Error] method:{method}")

            try:
                code = float(response.status_code) # type: int
            except:
                raise IOError(f"[Response object is error] response:{response}")

            if code // 100 != 2:
                error = response.text
                raise IOError(error)
            else:
                try:
                    result = response.json()
                except:
                    result = response.text
                logger.verbose("--------[SUCCESS]--------->>")
                logger.verbose(f"[method]: {method}")
                logger.verbose(f"[url]: {url}")
                logger.verbose(f"[params]: {params}")
                logger.verbose(f"[data]: {data}")
                logger.verbose(f"[headers]: {headers}")
                logger.verbose(f"[timeout]: {timeout}")
                logger.verbose(f"[kwargs]: {kwargs}")
                logger.verbose(f"[proxies]: {kwargs.get('proxies')}")
                logger.verbose(f"[code]: {code}")
                logger.verbose(f"[result]: {result}")
                logger.verbose("<<--------[SUCCESS]---------")
                return code, result, None

        except Exception as e:
            error_type = type(e)
            if error_type is requests.ReadTimeout:
                error = f"[requests.ReadTimeout] 请求超时...."
            else:
                error = str(e)
            if not error:
                error = f"[未知错误] 没有错误内容...."
            try:
                code
            except:
                code = 400
            logger.warning("---------[ERROR]--------->>")
            logger.warning(f"[error_type]: {error_type}")
            logger.warning(f"[error]: {error}")
            logger.warning(f"[method]: {method}")
            logger.warning(f"[url]: {url}")
            logger.warning(f"[params]: {params}")
            logger.warning(f"[data]: {data}")
            logger.warning(f"[headers]: {headers}")
            logger.warning(f"[timeout]: {timeout}")
            logger.warning(f"[kwargs]: {kwargs}")
            logger.warning(f"[proxies]: {kwargs.get('proxies')}")
            logger.warning("<<--------[ERROR]---------")
            return 400, None, error


    @classmethod
    def _get_session(cls, url):
        """ Get the connection session for url's domain, if no session, create a new.

        Args:
            url: HTTP request url.

        Returns:
            session: HTTP request session.
        """
        parsed_url = urlparse(url)
        key = parsed_url.netloc or parsed_url.hostname
        if key not in cls._SESSIONS:
            session = requests.Session()
            cls._SESSIONS[key] = session
        return cls._SESSIONS[key]





class UtilsRequests():
    def  __init__(self):
        pass

utils_requests = UtilsRequests()



async def test_AsyncRequests():
    # # CASE1:
    # # url = 'https://explorer.roninchain.com/address/ronin:3a19d7a2ab8a42f4db502f5cfab0391916e311d7/tokentxns?ps=100&p=1' # 可以正常访问
    # url = "https://explorer.roninchain.com/token/ronin:c6344bc1604fcab1a5aad712d766796e2b7a70b9" # 目前无法正常访问 (返回code:500页面)
    # proxy = None
    # code, success, error  = await AsyncRequests.ensure_aio_req(retry_times=3, method="GET", url=url, proxy=proxy)
    # print(f"code:{code}")
    # print(f"success:{success}")
    # print(f"error:{error}")
    # await AsyncRequests.close() # 记得关闭session (否则会有报错)


    # # CASE2:
    # task_lst = []
    # proxy="http://127.0.0.1:7890"
    #
    # url = 'https://api.binance.com/api/v3/time'
    # coro = AsyncRequests.ensure_aio_req(retry_times=3, method="GET", url=url, proxy=proxy)
    # task_lst.append(coro)
    #
    # url = 'https://api.binance.com/api/v3/time'
    # coro = AsyncRequests.ensure_aio_req(retry_times=3, method="GET", url=url, proxy=proxy)
    # task_lst.append(coro)
    #
    # x = await asyncio.gather(*task_lst) # [(200, {'serverTime': 1636306335397}, None), (200, {'serverTime': 1636306335398}, None)]
    # print("==============================================")
    # print(f"x {type(x)} : {x}")
    # for x, y, z in x:
    #     print(x)
    #     print(y)
    #     print(z)
    # print("==============================================")
    # await AsyncRequests.close() # 一定要记得close


    # # # CASE3:
    # url = "https://explorer.roninchain.com/_next/data/lNQyeI8jVUhj9VU9VhQ-a/tx/0x2e7f3b06b0fffafde76584fdd5b4d20ae5edae1e196d7eec20dd000cdecf83a0.json"
    # url = 'https://explorer.roninchain.com/address/ronin:3a19d7a2ab8a42f4db502f5cfab0391916e311d7/tokentxns?ps=100&p=1' # 可以正常访问
    # url = "https://explorer.roninchain.com/_next/data/2NTrPf5Ptvob5eLzOX2y2/tx/0xac5b46fd556767543e705a31bade534c358442f22919ab1833326d7e196c10d2.json"
    # url = "https://explorer.roninchain.com/_next/data/2NTrPf5Ptvob5eLzOX2y2/tx/0xf3a9debe3a56d1df6a412711aada4d7cd8c7be009a23aaa08a94a8b319de64b9.json"
    # proxy = None
    # code, success, error  = await AsyncRequests.ensure_aio_req(retry_times=3, method="GET", url=url, proxy=proxy)
    # print(f"code:{code}")
    # print(f"success:{success}")
    # print(f"error:{error}")
    # await AsyncRequests.close() # 记得关闭session (否则会有报错)


    # # CASE4:
    url = "http://127.0.0.1:8008/assets?user=LSH&marketplace=BN_SPOT"
    # c, s, e = await AsyncRequests.ensure_aio_req(url=url, timeout=0.001)
    c, s, e = await AsyncRequests.ensure_aio_req(url=url)
    print(c)
    print(s)
    print(e)
    await AsyncRequests.close()



def test_Requests():

    # Case1
    url = "http://127.0.0.1:8008/assets?user=LSH&marketplace=BN_SPOT"
    # c, s, e = Requests.ensure_req(url=url, timeout=0.001)
    c, s, e = Requests.ensure_req(url=url)
    print(c)
    print(s)
    print(e)




if __name__ == '__main__':
    pass
    # asyncio.run(test_AsyncRequests())
    test_Requests()
