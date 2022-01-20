import abc
from typing import TypeVar, Generic, Callable
import requests

URL_V1 = "https://graph.microsoft.com/v1.0/"
URL_BETA = "https://graph.microsoft.com/beta/"


T = TypeVar('T')


class GraphResponse(Generic[T]):

    @property
    @abc.abstractmethod
    def ready(self) -> bool:
        return NotImplemented

    @property
    @abc.abstractmethod
    def ok(self) -> bool:
        return NotImplemented

    @property
    @abc.abstractmethod
    def text(self) -> str:
        return NotImplemented

    @property
    @abc.abstractmethod
    def headers(self) -> dict:
        return NotImplemented

    @property
    @abc.abstractmethod
    def value(self) -> T:
        return NotImplemented


class RequestsGraphResponse(GraphResponse[T]):
    def __init__(self, response: requests.Response, response_type: T):
        self.__response = response
        self.__response_type = response_type

    @property
    def ready(self) -> bool:
        return True

    @property
    def ok(self) -> bool:
        return self.__response.ok

    @property
    def text(self) -> str:
        return self.__response.text

    @property
    def headers(self) -> dict:
        return self.__response.headers

    @property
    def response(self) -> requests.Response:
        return self.__response

    @property
    def value(self) -> T:
        self.__response.raise_for_status()
        if hasattr(self.__response_type, 'from_response'):
            return self.__response_type.from_response(self.__response)
        else:
            data = self.__response.json()
            return self.__response_type(data)


class GraphClient(abc.ABC):
    @abc.abstractmethod
    def make_request(self, url, method="get", headers=None, response_type: T = dict, **kwargs) -> GraphResponse[T]:
        return NotImplemented

    @property
    def single_client(self) -> "GraphClient":
        return NotImplemented


class RequestsGraphClient(GraphClient):
    DEFAULTS = dict(
        root_url=URL_V1,
        scope='https://graph.microsoft.com/.default',
        grant_type='client_credentials',
        timeout=5,
    )

    def __init__(self, token_fetcher: Callable, **kwargs):
        self._config = {**RequestsGraphClient.DEFAULTS, **kwargs}
        self.__token_fetcher = token_fetcher

    @property
    def single_client(self) -> GraphClient:
        return self

    def make_request(self, url, method="get", headers=None, response_type: T = dict, use_auth=True, **kwargs) -> GraphResponse[T]:
        if use_auth:
            headers = headers if headers else {}
            headers = {**headers, "Authorization": f'Bearer {self.__token_fetcher()}'}

        if not url.startswith("http"):
            if url.startswith("/"):
                url = url[1:]
            url = f"{self._config['root_url']}{url}"

        request_args = {"timeout": self._config['timeout'], **kwargs}

        @timeout_retry(self._config.get("timeout_retry", 0))
        def _make_request():
            return requests.request(method, url, headers=headers, **request_args)

        response = _make_request()
        return RequestsGraphResponse(response, response_type)


def timeout_retry(retries):
    left = dict(retries=int(retries))

    def decorator(f):
        def inner(*args, **kwargs):
            while True:
                try:
                    return f(*args, **kwargs)
                except (
                        requests.exceptions.ReadTimeout,
                        requests.exceptions.ConnectTimeout,
                        requests.exceptions.ConnectionError,
                ) as e:
                    if left['retries'] <= 0:
                        raise e
                    left['retries'] -= 1
        return inner
    return decorator
