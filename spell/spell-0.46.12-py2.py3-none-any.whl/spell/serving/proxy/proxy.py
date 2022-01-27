import asyncio
from collections.abc import Sequence
import json
import logging
import pickle
from typing import Any, Awaitable, Callable, Iterable, List, Optional, Tuple, Union

from aiohttp import ClientSession, UnixConnector
from starlette.applications import Starlette
from starlette.exceptions import HTTPException
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from starlette.requests import Request
from starlette.responses import PlainTextResponse, Response
from starlette.routing import Route

from spell.serving.api import BatchedAPI
from spell.serving.log import create_logging_config, get_loggers
from spell.serving.proxy import settings
from spell.serving.responses import wrap_response
from spell.serving.types import (
    PredictorResponse,
    ProxyPredictCallback,
    ProxyPredictCallbackResponse,
)
from spell.serving.utils import retry

logger, error_logger = get_loggers("proxy")


class BatchProcessingError(Exception):
    def __init__(self, result: Any) -> None:
        self.result = result


class BatchDispatcher:
    """This class wraps a function which accepts batches, batches incoming requests, then calls the
    function with those batches

    When a request comes into handle_request, it starts a new timeout task if none is running. It
    then creates a future for the request and pushes both the future and the request onto a queue
    and awaits the future's result. If the queue has exceeded its maximum size, it creates a batch
    and cancels the timeout task. It then calls the callback with the batch. This callback returns
    a list of results, one per request, and therefore one per future. It then assigns the futures
    the appropriate result. A timeout task creates a batch from whatever requests are in the queue.
    """

    class _InitialTimeoutTask:
        # This is a dummy task which is already marked as done. Only used for initial request.
        # It's so we don't have to do a none check on every request when it's only necessary
        # for the very first request
        def done(self):
            return True

        def cancel(self):
            pass

    __slots__ = [
        "max_batch_size",
        "timeout_ms",
        "callback",
        "requests_queue",
        "futures_queue",
        "_timeout_task",
        "_loop",
    ]

    def __init__(self, max_batch_size: int, timeout_ms: int) -> None:
        self.max_batch_size = max_batch_size
        self.timeout_ms = timeout_ms
        self.requests_queue = []
        self.futures_queue = []
        self._timeout_task = self._InitialTimeoutTask()

        # These syncronization primitives must be created after an async loop is avaialble
        # This async loop is created after Starlette is initialized
        self._loop = None

        # This callback is set when the class is used as a decorator
        self.callback = None

    @classmethod
    def from_settings(cls):
        return cls(settings.MAX_BATCH_SIZE, settings.REQUEST_TIMEOUT_MS)

    def initialize_async_primitives(self, loop: Optional[asyncio.BaseEventLoop] = None) -> None:
        self._loop = loop if loop else asyncio.get_event_loop()

    def __call__(self, func: ProxyPredictCallback) -> Callable[[Any], Awaitable[PredictorResponse]]:
        self.callback = func
        return self.handle_request

    async def handle_request(self, request: Any) -> asyncio.Future:
        # The data in this request is fully arbitrary so long as self.callback can accept a list
        # of it.
        # If no timer is running, start one
        future = self._loop.create_future()
        self.requests_queue.append(request)
        self.futures_queue.append(future)

        if len(self.requests_queue) >= self.max_batch_size:
            batch, futures = self.make_batch()
            await self.execute_batch(batch, futures)
        elif self._timeout_task.done():
            self._timeout_task = self._loop.create_task(self.schedule_timeout())
        return await future

    async def schedule_timeout(self) -> None:
        try:
            await asyncio.sleep(self.timeout_ms / 1000)
            batch, futures = self.make_batch()
            await asyncio.shield(self.execute_batch(batch, futures))
        except asyncio.CancelledError:
            pass

    def make_batch(self) -> Tuple[List[asyncio.Future], List[Any]]:
        self._timeout_task.cancel()
        batch = self.requests_queue
        futures = self.futures_queue
        self.requests_queue = []
        self.futures_queue = []
        return batch, futures

    async def execute_batch(self, batch: List[Any], futures: List[asyncio.Future]) -> None:
        done = False
        try:
            logger.debug(f"Executing batch of length {len(batch)}")
            responses = await self.callback(batch)
            self.set_futures_to_responses(futures, responses, expected_length=len(batch))
            done = True
        # This would happen if Starlette cancels this task (on server shutdown)
        except asyncio.CancelledError:
            pass  # rely on the finally block to cancel all futures
        except BatchProcessingError as e:
            self.set_all_futures_to_value(futures, e.result)
            done = True
        except Exception as e:
            for future in futures:
                if not future.done():
                    future.set_result(e)
            done = True
        finally:
            if not done:
                for future in futures:
                    if not future.done():
                        # This returns a 0-length 500 status response to the user
                        future.cancel()

    def set_futures_to_responses(
        self,
        futures: List[asyncio.Future],
        responses: List[Any],
        expected_length: int,
    ) -> None:
        # It is possible that a user returned something which isn't list-like from
        # their predict. We check that here
        if not isinstance(responses, Sequence):
            msg = "Batch predict responses must be iterable and support len()"
            self.set_user_error_responses(futures, msg)
        elif len(responses) != expected_length:
            msg = f"Response length mismatch! Expected {expected_length}, but got {len(responses)}"
            self.set_user_error_responses(futures, msg)
        else:
            for future, response in zip(futures, responses):
                future.set_result(response)

    @staticmethod
    def set_user_error_responses(futures: Iterable[asyncio.Future], error_msg: str) -> None:
        error_logger.error(error_msg)
        BatchDispatcher.set_all_futures_to_value(futures, PlainTextResponse(error_msg, status_code=500))

    @staticmethod
    def set_all_futures_to_value(futures: List[asyncio.Future], value: Any) -> None:
        for future in futures:
            future.set_result(value)

    def reset(self):
        # This is only used for testing
        self._timeout_task.cancel()
        while self.futures_queue:
            future = self.futures_queue.pop()
            future.cancel()


class ProxyBase:
    __slots__ = [
        "dispatcher",
        "_base_url",
        "_session",
        "_dispatch_predict",
    ]

    def __init__(
        self,
        dispatcher: BatchDispatcher,
        outbound_host: str,
        outbound_port: int,
    ) -> None:
        self.dispatcher = dispatcher
        self._base_url = f"http://{outbound_host}:{outbound_port}"
        self._session = None
        self._dispatch_predict = self.dispatcher(self.predict_batch)

    async def initialize_async_primitives(
        self,
        loop: Optional[asyncio.BaseEventLoop] = None,
        session: Optional[ClientSession] = None,
    ) -> None:
        self.dispatcher.initialize_async_primitives(loop=loop)
        if session:
            self._session = session
        else:
            if settings.MODEL_SERVER_SOCKET:
                self._session = ClientSession(connector=UnixConnector(settings.MODEL_SERVER_SOCKET))
            else:
                self._session = ClientSession()
        self._session = await self._session.__aenter__()

    async def shutdown(self) -> None:
        await self._session.close()

    @classmethod
    def from_settings(cls, dispatcher: BatchDispatcher):
        return cls(
            dispatcher=dispatcher,
            outbound_host=settings.MODEL_SERVER_HOST,
            outbound_port=settings.MODEL_SERVER_PORT,
        )

    def predict_endpoint(self, request: Request) -> Response:
        raise NotImplementedError

    def predict_batch(self, data: List[Any]) -> Response:
        raise NotImplementedError

    async def passthrough(self, request: Request) -> Response:
        """This method handles all requests except those to /predict and passes them directly to
        the model server"""
        body = await request.body()
        headers = dict(request.headers)
        url = self._get_full_url(request.url.path, request)
        method = request.method

        @retry(request.url.path, error_logger)
        async def call():
            async with self._session.request(method, url, headers=headers, data=body) as response:
                return Response(
                    content=await response.read(),
                    headers=dict(response.headers),
                    status_code=response.status,
                )

        return await call()

    async def _do_dispatch(self, prepared_request: Any) -> Response:
        resp = await self._dispatch_predict(prepared_request)
        # This will handle exceptions thrown in dispatcher
        if isinstance(resp, Exception):
            raise resp
        # Here we use wrapped response because the result of the /predict method
        # is any pickleable type supported by wrap_response
        return await wrap_response(resp)

    async def _do_predict_batch(self, serialized_batch: Union[str, bytes]) -> ProxyPredictCallbackResponse:
        predict_url = f"{self._base_url}/predict"

        @retry("/predict", error_logger)
        async def call_predict():
            async with self._session.post(
                predict_url,
                headers={"Content-Type": self.PREDICT_CONTENT_TYPE},
                data=serialized_batch,
            ) as response:
                return (
                    await response.read(),
                    response.headers,
                    response.status,
                )

        body, headers, status = await call_predict()
        if status >= 400:
            return BatchProcessingError(Response(content=body, headers=dict(headers), status_code=status))
        return pickle.loads(body)

    def _get_full_url(self, endpoint: str, request: Request) -> str:
        url = f"{self._base_url}{endpoint}"
        # Micro-optimization. query params impl is a mapping in which len() is faster than str()
        # which does url-encoding
        if len(request.query_params) > 0:
            url += f"?{str(request.query_params)}"
        return url

    def get_routes(self) -> List[Route]:
        return [
            Route("/predict", self.predict_endpoint, methods=["POST"]),
            Route("/{path:path}", self.passthrough),
        ]


class JSONProxy(ProxyBase):
    """This proxy is used for Predictors which do not provide a prepare method"""

    PREDICT_CONTENT_TYPE = "application/json"

    async def predict_endpoint(self, request: Request) -> Response:
        try:
            json_content = await request.json()
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Request must contain a JSON object")
        return await self._do_dispatch(json_content)

    async def predict_batch(self, data: List[Any]) -> ProxyPredictCallbackResponse:
        return await self._do_predict_batch(json.dumps(data))


class PreparedProxy(ProxyBase):
    """This proxy is used for Predictors which provide a prepare method, and therefore
    require pickle serialization methods"""

    PREDICT_CONTENT_TYPE = "application/octet-stream"

    async def predict_endpoint(self, request: Request) -> Response:
        body = await request.body()
        headers = dict(request.headers)
        prepare_url = self._get_full_url("/prepare", request)

        @retry(request.url.path, error_logger)
        async def call_prepare():
            async with self._session.post(prepare_url, headers=headers, data=body) as response:
                return await response.read(), response.headers, response.status

        body, headers, status = await call_prepare()
        if status >= 400:
            return Response(content=body, headers=dict(headers), status_code=status)
        return await self._do_dispatch(pickle.loads(body))

    async def predict_batch(self, data: List[Any]) -> ProxyPredictCallbackResponse:
        return await self._do_predict_batch(pickle.dumps(data))


def print_config() -> None:
    logger.debug(f"Using Proxy configuration:\n{settings.config}")


def setup_logger() -> None:
    logging.config.dictConfig(create_logging_config("proxy"))
    if settings.DEBUG:
        logger.setLevel(logging.DEBUG)
        error_logger.setLevel(logging.DEBUG)


def make_proxy() -> ProxyBase:
    # While we aren't running any user code directly, because we are unpickling objects from user
    # code, we could attempt to unpickle a user-defined data type. This would cause an import
    # error if we don't load their module. This also ensures that any third-party data structures
    # returned by /prepare are in our runtime. This from_settings will import the user code
    api = BatchedAPI.from_settings()
    dispatcher = BatchDispatcher.from_settings()
    proxy_class = PreparedProxy if api.has_prepare else JSONProxy
    return proxy_class.from_settings(dispatcher)


def make_app(proxy: Optional[ProxyBase] = None) -> Starlette:
    if not proxy:
        proxy = make_proxy()
    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
            allow_credentials=True,
        ),
        Middleware(GZipMiddleware),
    ]
    return Starlette(
        debug=settings.DEBUG,
        routes=proxy.get_routes(),
        middleware=middleware,
        on_startup=[setup_logger, print_config, proxy.initialize_async_primitives],
        on_shutdown=[proxy.shutdown],
    )
