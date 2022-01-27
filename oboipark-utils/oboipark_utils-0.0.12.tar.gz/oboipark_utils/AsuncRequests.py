import asyncio
import random
import sys

from bs4 import BeautifulSoup
from aiohttp.client_reqrep import ClientResponse, ClientRequest
from aiohttp.client_exceptions import ClientConnectionError
from aiohttp import ClientSession
from typing import Union
from aiohttp.client_exceptions import ContentTypeError


class RequestError(Exception):
    ...


class RepeatRequestError(Exception):
    ...


def response_type_convert_error(func):
    async def wrap(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except ContentTypeError:
            return None
    return wrap


def error_detect(func):
    async def wrap(*args, **kwargs):
        if kwargs.get('max_requests', 5) > sys.getrecursionlimit():
            raise RepeatRequestError(
                f'Слишком большой max_requests, его максимальное значение - {sys.getrecursionlimit()}'
            )
        try:
            return await func(*args, **kwargs)
        except ClientConnectionError:
            raise RequestError(f'Ошибка в запросе, скорее всего использован несуществующий url - {args}, {kwargs}')

    return wrap


class RingBuffer:
    def __init__(self, dat: Union[list, None] = None):
        if not isinstance(dat, list):
            dat = [None, ]
        self.buffer = dat
        self.n = random.randint(0, len(dat) - 1)

    def __iter__(self):
        return self

    def __next__(self):
        self.n += 1
        if self.n > len(self.buffer) - 1:
            self.n = 0
        return self.buffer[self.n]


class SettingRequest:

    _proxy_buffer = None
    _header_buffer = None
    session = None

    async def get_request(self, url: str, new_session: bool = False, use_proxy: bool = False, ssl: bool = False,
                          *args, **kwargs):
        session, proxy = await self._setting_request(
            new_session=new_session,
            use_proxy=use_proxy,
        )
        return session.get(url, proxy=proxy, ssl=ssl, **kwargs)

    async def post_request(self, url: str, new_session: bool = False, data: Union[list, dict, None] = None,
                           use_proxy: bool = False, ssl: bool = False, *args, **kwargs):
        session, proxy = await self._setting_request(
            new_session=new_session,
            use_proxy=use_proxy,
        )
        return session.post(url, proxy=proxy, ssl=ssl, data=data, **kwargs)

    async def put_request(self, url: str, new_session: bool = False, data: Union[list, dict, None] = None,
                          use_proxy: bool = False, ssl: bool = False, *args, **kwargs):
        session, proxy = await self._setting_request(
            new_session=new_session,
            use_proxy=use_proxy,
        )
        return session.put(url, proxy=proxy, ssl=ssl, data=data, **kwargs)

    async def delete_request(self, url: str, new_session: bool = False, use_proxy: bool = False,
                             ssl: bool = False, *args, **kwargs):
        session, proxy = await self._setting_request(
            new_session=new_session,
            use_proxy=use_proxy,
        )
        return session.delete(url, proxy=proxy, ssl=ssl, **kwargs)

    async def _setting_request(self, new_session: bool, use_proxy: bool) -> [ClientSession, str]:
        session = await self._setting_session(new_session=new_session)
        proxy = await self._setting_proxy(use_proxy=use_proxy)
        return [session, proxy]

    async def _setting_session(self, new_session: bool, *args, **kwargs) -> ClientSession:
        if self.session is None:
            self.session = ClientSession()
        if new_session:
            return ClientSession()  # разобраться как можно закрывать новую сессию
        return self.session

    async def _setting_proxy(self, use_proxy: bool, *args, **kwargs):
        if use_proxy:
            return next(self._proxy_buffer)
        return None


class Response:
    def __init__(self, text_data: Union[str, None], json_data: Union[list, dict, None], status_code: int, *args, **kwargs):
        self.__json = json_data
        self.__text = text_data
        self.__status_code = status_code

    @property
    def status_code(self):
        return self.__status_code

    @property
    async def soup(self):
        return BeautifulSoup(self.__text, 'lxml')

    @property
    async def json(self):
        return self.__json

    @property
    async def text(self):
        return self.__text


class Request(SettingRequest):
    def __init__(self, proxy: Union[list, None] = None, headers: Union[list, None] = None, *args, **kwargs):
        self._proxy_buffer = RingBuffer(proxy)
        self._header_buffer = RingBuffer(headers)
        self.session = ClientSession()

    @error_detect
    async def get(self, url: str, new_session: bool = False, headers: Union[dict, None] = None, use_proxy: bool = True,
                  max_requests: int = 5, n_requests: int = 0,
                  await_status_code: int = 200, ssl: bool = False, *args, **kwargs) -> Response:
        async with await self.get_request(
            url=url,
            new_session=new_session,
            headers=headers,
            use_proxy=use_proxy,
            ssl=ssl,
        ) as resp:
            if resp.status != await_status_code and max_requests != n_requests:
                return await self.get(url, new_session=new_session, headers=headers, use_proxy=use_proxy,
                                      max_requests=max_requests, n_requests=n_requests+1, status_code=await_status_code,
                                      ssl=ssl, *args, **kwargs)
            return Response(
                text_data=await self.__get_text_response(resp),
                json_data=await self.__get_json_response(resp),
                status_code=resp.status
            )

    @error_detect
    async def post(self, url: str, new_session: bool = False, data: Union[list, dict, None] = None,
                   use_proxy: bool = False, await_status_code: int = 201, ssl: bool = False,
                   headers: Union[dict, None] = None, max_requests: int = 5, n_requests: int = 0,
                   *args, **kwargs) -> Response:
        async with await self.post_request(
                url=url,
                data=data,
                new_session=new_session,
                headers=headers,
                use_proxy=use_proxy,
                ssl=ssl,
        ) as resp:
            if resp.status != await_status_code and max_requests != n_requests:
                return await self.post(url, new_session=new_session, data=data, use_proxy=use_proxy,
                                       await_status_code=await_status_code, ssl=ssl, headers=headers,
                                       max_requests=max_requests, n_requests=n_requests + 1, *args, **kwargs)
            return Response(
                text_data=await self.__get_text_response(resp),
                json_data=await self.__get_json_response(resp),
                status_code=resp.status
            )

    @error_detect
    async def put(self, url: str, new_session: bool = False, data: Union[list, dict, None] = None,
                  use_proxy: bool = False, await_status_code: int = 201, ssl: bool = False,
                  headers: Union[dict, None] = None, max_requests: int = 5, n_requests: int = 0,
                  *args, **kwargs) -> Response:
        async with await self.put_request(
                url=url,
                data=data,
                new_session=new_session,
                headers=headers,
                use_proxy=use_proxy,
                ssl=ssl,
        ) as resp:
            if resp.status != await_status_code and max_requests != n_requests:
                return await self.put(url, new_session=new_session, data=data, use_proxy=use_proxy,
                                      await_status_code=await_status_code, ssl=ssl, headers=headers,
                                      max_requests=max_requests, n_requests=n_requests + 1, *args, **kwargs)
            return Response(
                text_data=await self.__get_text_response(resp),
                json_data=await self.__get_json_response(resp),
                status_code=resp.status
            )

    @error_detect
    async def delete(self, url: str, new_session: bool = False,
                     use_proxy: bool = False, await_status_code: int = 201, ssl: bool = False,
                     headers: Union[dict, None] = None, max_requests: int = 5, n_requests: int = 0,
                     *args, **kwargs) -> Response:
        async with await self.delete_request(
                url=url,
                new_session=new_session,
                headers=headers,
                use_proxy=use_proxy,
                ssl=ssl,
        ) as resp:
            if resp.status != await_status_code and max_requests != n_requests:
                return await self.delete(url, new_session=new_session, use_proxy=use_proxy,
                                         await_status_code=await_status_code, ssl=ssl, headers=headers,
                                         max_requests=max_requests, n_requests=n_requests + 1, *args, **kwargs)
            return Response(
                text_data=await self.__get_text_response(resp),
                json_data=await self.__get_json_response(resp),
                status_code=resp.status
            )

    @staticmethod
    @response_type_convert_error
    async def __get_json_response(response: ClientResponse, *args, **kwargs) -> Union[list, dict, None]:
        return await response.json()

    @staticmethod
    @response_type_convert_error
    async def __get_text_response(response: ClientResponse, *args, **kwargs) -> Union[str, None]:
        return await response.text()

    async def close(self):
        await self.session.close()
