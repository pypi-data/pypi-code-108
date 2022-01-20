import asyncio
import binascii
import hashlib
import os
from functools import wraps
from typing import Any, Coroutine

import aiofiles
import aiohttp
from async_timeout import timeout

from beniutils import makeFolder
from beniutils.http import getHeaderByDefault
from beniutils.log import warning

_maxAsyncFileNum: int = 50
_currentAsyncFileNum: int = 0


def setAsyncFileMaxNum(value: int):
    global _maxAsyncFileNum
    _maxAsyncFileNum = value


_asyncAwaitList: list[Coroutine[Any, Any, Any]] = []


def asyncAppend(task: Coroutine[Any, Any, Any]):
    _asyncAwaitList.append(task)


async def asyncAwait():
    result = await asyncio.gather(*_asyncAwaitList)
    _asyncAwaitList.clear()
    return result


async def asyncWriteFile(file: str, content: str, encoding: str = 'utf8', newline: str = '\n'):
    makeFolder(os.path.dirname(file))
    global _currentAsyncFileNum
    while _currentAsyncFileNum > _maxAsyncFileNum:
        await asyncio.sleep(0)
    _currentAsyncFileNum += 1
    async with aiofiles.open(file, 'w', encoding=encoding, newline=newline) as f:
        await f.write(content)
        # await f.flush()
        # await f.close()
    _currentAsyncFileNum -= 1


async def asyncWriteBinFile(file: str, data: bytes):
    makeFolder(os.path.dirname(file))
    global _currentAsyncFileNum
    while _currentAsyncFileNum > _maxAsyncFileNum:
        await asyncio.sleep(0)
    _currentAsyncFileNum += 1
    async with aiofiles.open(file, 'wb') as f:
        await f.write(data)
        # await f.flush()
        # await f.close()
    _currentAsyncFileNum -= 1


async def asyncReadFile(file: str, encoding: str = 'utf8', newline: str = '\n'):
    global _currentAsyncFileNum
    while _currentAsyncFileNum > _maxAsyncFileNum:
        await asyncio.sleep(0)
    _currentAsyncFileNum += 1
    async with aiofiles.open(file, 'r', encoding=encoding, newline=newline) as f:
        data = await f.read()
        # await f.close()
    _currentAsyncFileNum -= 1
    return data


async def asyncReadBinFile(file: str):
    global _currentAsyncFileNum
    while _currentAsyncFileNum > _maxAsyncFileNum:
        await asyncio.sleep(0)
    _currentAsyncFileNum += 1
    async with aiofiles.open(file, 'rb') as f:
        data = await f.read()
        # await f.close()
    _currentAsyncFileNum -= 1
    return data


async def asyncGetFileMD5(file: str):
    data = await asyncReadBinFile(file)
    return hashlib.md5(data).hexdigest()


async def asyncGetFileCRC32(file: str):
    data = await asyncReadBinFile(file)
    return binascii.crc32(data)


async def asyncGetFileCRCHex(file: str):
    return hex(await asyncGetFileCRC32(file))[2:].zfill(8)


async def asyncExecute(*parList: str):
    # 注意：针对windows，版本是3.8以下需要使用asyncio.subprocess，在执行main之前就要执行
    # 注意：在3.7如果调用对aiohttp有异常报错
    # asyncio.set_event_loop_policy(
    #    asyncio.WindowsProactorEventLoopPolicy()
    # )

    proc = await asyncio.create_subprocess_shell(
        ' '.join(parList),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    return proc.returncode, stdout, stderr


_maxAsyncHttpNum: int = 3
_currentAsyncHttpNum: int = 0
_waitAsyncHttpTime: float = 0.1


def setAsyncHttpMaxNum(value: int):
    global _maxAsyncHttpNum
    _maxAsyncHttpNum = value


async def asyncHttpGet(url: str, headers: dict[str, str] | None = None, timeout: int = 30, retry: int = 3):
    # initAioHttp()
    global _currentAsyncHttpNum
    headers = getHeaderByDefault(headers)
    result: bytes = b""
    response = None
    currentTry = 0
    while _currentAsyncHttpNum >= _maxAsyncHttpNum:
        await asyncio.sleep(_waitAsyncHttpTime)
    _currentAsyncHttpNum += 1
    while currentTry < retry:
        currentTry += 1
        try:
            response = None
            async with aiohttp.ClientSession() as session:
                response = await session.get(
                    url,
                    headers=headers,
                    timeout=timeout,
                )
                result = await response.read()
                response.close()
                # await session.close()
                if not result:
                    continue
                break
        except Exception:
            if response:
                response.close()
            warning(f'async http get exception url={url} times={currentTry}')
    _currentAsyncHttpNum -= 1
    return result, response


async def asyncHttpPost(url: str, data: Any = None, headers: dict[str, str] | None = None, timeout: int = 30, retry: int = 3):
    # initAioHttp()
    global _currentAsyncHttpNum
    headers = getHeaderByDefault(headers)
    result = None
    response = None
    currentTry = 0
    while _currentAsyncHttpNum >= _maxAsyncHttpNum:
        await asyncio.sleep(_waitAsyncHttpTime)
    _currentAsyncHttpNum += 1
    while currentTry < retry:
        currentTry += 1
        try:
            response = None
            async with aiohttp.ClientSession() as session:
                response = await session.post(
                    url,
                    data=data,
                    headers=headers,
                    timeout=timeout,
                )
                result = await response.read()
                response.close()
                # await session.close()
                if not result:
                    continue
                break
        except Exception:
            if response:
                response.close()
            warning(f'async http get exception url={url} times={currentTry}')
    _currentAsyncHttpNum -= 1
    return result, response


async def asyncDownload(url: str, file: str):
    result, _ = await asyncHttpGet(url)
    await asyncWriteBinFile(file, result)


def asyncTimeout(waitSeconds: float):
    def _log(func: Any):
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any):
            async with timeout(waitSeconds):
                return await func(*args, **kwargs)
        return wrapper
    return _log


def asyncRun(coroutine: Coroutine[Any, Any, None]):
    # asyncio.run(coroutine)
    asyncio.get_event_loop().run_until_complete(coroutine)

# 两个方案都能解决问题
# asyncio.run(runAsync())
# =>
# asyncio.get_event_loop().run_until_complete(runAsync())

# --------------------------------------------------------------------

# _isInitAioHttp = True

# def initAioHttp():

#     global _isInitAioHttp
#     if _isInitAioHttp:
#         _isInitAioHttp = False
#     else:
#         return

#     from asyncio.proactor_events import _ProactorBasePipeTransport
#     from functools import wraps

#     # 尝试优化报错：RuntimeError: Event loop is closed

#     def silence_event_loop_closed(func):
#         @wraps(func)
#         def wrapper(self, *args, **kwargs):
#             try:
#                 return func(self, *args, **kwargs)
#             except RuntimeError as e:
#                 if str(e) != 'Event loop is closed':
#                     raise
#         return wrapper

#     _ProactorBasePipeTransport.__del__ = silence_event_loop_closed(_ProactorBasePipeTransport.__del__)
