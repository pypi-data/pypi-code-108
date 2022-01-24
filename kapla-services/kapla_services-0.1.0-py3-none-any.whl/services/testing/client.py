from __future__ import annotations

from types import TracebackType
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Type, TypeVar, overload

from anyio import create_task_group
from loguru import logger
from pydantic import ValidationError

from kapla.services.errors import NoResponderError
from kapla.services.headers import HeaderTypes
from kapla.services.io import dump, dumps
from kapla.services.requests import Request
from kapla.services.responses import Response
from kapla.services.senders import Sender
from kapla.services.utils.subjects import match_subject
from kapla.services.validation import validate

if TYPE_CHECKING:  # pragma: no cover
    from kapla.services.application import BaseBrokerApp  # pragma: no cover


T = TypeVar("T")


class TestClient:
    __test__ = False

    def __init__(self, app: BaseBrokerApp) -> None:
        self.app = app
        self.__subscriptions__: List[Dict[str, Any]] = []
        self.__reply_subscriptions__: List[Dict[str, Any]] = []
        self._sender = Sender(
            publish=self._send_publish,
            request=self._send_request,
            middlewares=app._default_router.send_middlewares,
        )

    def _start(self) -> None:
        self.__subscriptions__ = []
        self.__reply_subscriptions__ = []
        for router in self.app.routers:
            for spec in router.subscriptions:
                options = self.app.broker.listener.prepare_subscribe_cb(**spec)
                self.__subscriptions__.append(
                    {"subject": options["subject"], "cb": options["cb"]}
                )
            for spec in router.reply_suscriptions:
                options = self.app.broker.listener.prepare_subscribe_and_reply_cb(
                    **spec
                )
                self.__reply_subscriptions__.append(
                    {"subject": options["subject"], "cb": options["cb"]}
                )

    def _stop(self) -> None:
        del self.__subscriptions__
        del self.__reply_subscriptions__

    async def connect(self) -> None:
        self._start()

    async def close(self) -> None:
        self._stop()

    async def _send_publish(self, request: Request) -> None:
        logger.warning(f"Publishing test request: {request.scope}")
        async with create_task_group() as tg:
            for sub in self.__subscriptions__:
                if match_subject(request.subject, sub["subject"]):
                    tg.start_soon(sub["cb"], request)
            for sub in self.__reply_subscriptions__:
                if match_subject(request.subject, sub["subject"]):
                    tg.start_soon(sub["cb"], request)

    async def publish(
        self,
        subject: str,
        payload: Optional[Any] = None,
        reply: Optional[str] = None,
        headers: Optional[HeaderTypes] = None,
        timeout: Optional[float] = None,
        process_timeout: Optional[float] = None,
    ) -> None:
        # Generate fake request
        await self._sender.publish(
            subject=subject,
            payload=payload,
            reply=reply,
            headers=headers,
            process_timeout=process_timeout,
        )

    async def _send_request(self, request: Request) -> Response[bytes]:
        for sub in self.__reply_subscriptions__:
            if match_subject(request.subject, sub["subject"]):
                logger.warning(f"Requesting test request: {request.scope}")
                response: Response[bytes] = await sub["cb"](request)
                return response.copy(update={"data": dump(response.data)})

        raise NoResponderError(f"No responder on subject {request.subject}")

    @overload
    async def request(
        self,
        subject: str,
        payload: Optional[Any] = None,
        *,
        headers: Optional[HeaderTypes] = None,
        timeout: float = 1.0,
        process_timeout: Optional[float] = None,
        validator: Type[T],
    ) -> Response[T]:
        ...  # pragma: no cover

    @overload
    async def request(
        self,
        subject: str,
        payload: Optional[Any] = None,
        *,
        headers: Optional[HeaderTypes] = None,
        timeout: float = 1.0,
        process_timeout: Optional[float] = None,
        validator: None = None,
    ) -> Response[bytes]:
        ...  # pragma: no cover

    async def request(
        self,
        subject: str,
        payload: Optional[Any] = None,
        *,
        headers: Optional[HeaderTypes] = None,
        timeout: float = 1.0,
        process_timeout: Optional[float] = None,
        validator: Optional[Type[Any]] = None,
    ) -> Response[Any]:
        try:
            response = await self._sender.request(
                subject,
                payload,
                headers=headers,
                timeout=timeout,
                process_timeout=process_timeout,
            )
        except NoResponderError as err:
            return Response(
                success=False,
                code=404,
                error="NoResponderError",
                details=str(err),
                exception=err,
            )

        if response.success and validator:
            try:
                return response.copy(
                    update={"data": validate(validator, response.data)}
                )
            except ValidationError as err:
                return Response(
                    success=False,
                    exception=err,
                    code=417,
                    error="ValidationError",
                    details=dumps(err.errors()),
                    # Still send data which failed validation
                    data=response.data,
                )

        return response

    async def __aenter__(self) -> TestClient:
        await self.connect()
        return self

    async def __aexit__(
        self,
        exc_type: Type[BaseException],
        exc_val: BaseException,
        exc_tb: Optional[TracebackType],
    ) -> None:
        await self.close()

    def __enter__(self) -> TestClient:
        self._start()
        return self

    def __exit__(
        self,
        exc_type: Type[BaseException],
        exc_val: BaseException,
        exc_tb: Optional[TracebackType],
    ) -> None:
        self._stop()
