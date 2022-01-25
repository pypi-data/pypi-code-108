import asyncio
import json
import logging
from ipaddress import IPv4Address, IPv4Network
from secrets import compare_digest, token_urlsafe
from typing import Any, Final, Optional, Tuple, Union

from aiohttp import BaseConnector
from aiohttp.web import (Application, HTTPInternalServerError, HTTPNotFound,
                         Request, Response, StreamResponse)
from yarl import URL

from .api_types import InputFile, Update
from .bot import Bot, HandlerTableProtocol
from .storage import StorageProtocol

NETWORKS: Final[Tuple[IPv4Network, ...]] = (IPv4Network('149.154.160.0/20'),
                                            IPv4Network('91.108.4.0/22'))

bot_logger: Final[logging.Logger] = logging.getLogger('aiotgbot.bot')


class ListenBot(Bot):

    def __init__(
        self,
        url: Union[str, URL],
        token: str,
        handler_table: 'HandlerTableProtocol',
        storage: StorageProtocol,
        certificate: Optional[InputFile] = None,
        ip_address: Optional[str] = None,
        connector: Optional[BaseConnector] = None,
        check_address: bool = False,
        address_header: Optional[str] = None,
        **application_args: Any
    ) -> None:
        super().__init__(token, handler_table, storage, connector)
        self._url: URL = URL(url) if isinstance(url, str) else url
        self._certificate = certificate
        self._ip_address = ip_address
        self._webhook_token: Optional[str] = None
        self._check_address: Final[bool] = check_address
        self._address_header: Final[Optional[str]] = address_header
        self._application = Application(**application_args)
        self._application.router.add_post('/{token}', self._handler)

    @property
    def application(self) -> Application:
        return self._application

    def _address_is_allowed(self, request: Request) -> bool:
        if self._address_header is not None:
            address = IPv4Address(request.headers[self._address_header])
        else:
            address = IPv4Address(request.remote)
        return any(address in network for network in NETWORKS)

    async def _handler(self, request: Request) -> StreamResponse:
        if not self._started:
            raise HTTPInternalServerError()
        assert self._scheduler is not None
        assert self._webhook_token is not None
        if self._check_address and not self._address_is_allowed(request):
            raise HTTPNotFound()
        if not compare_digest(self._webhook_token,
                              request.match_info['token']):
            raise HTTPNotFound()
        update_data = json.loads(await request.read())
        update = Update.from_dict(update_data)
        await self._scheduler.spawn(self._handle_update(update))
        return Response()

    async def start(self) -> None:
        if self._started:
            raise RuntimeError('Polling already started')
        await self._start()
        assert self._me is not None
        loop = asyncio.get_running_loop()
        self._webhook_token = await loop.run_in_executor(None, token_urlsafe)
        assert isinstance(self._webhook_token, str)
        url = str(self._url / self._webhook_token)
        await self.set_webhook(url, self._certificate, self._ip_address)
        bot_logger.info('Bot %s (%s) start listen', self._me.first_name,
                        self._me.username)

    async def stop(self) -> None:
        if not self._started:
            raise RuntimeError('Polling not started')
        if self._stopped:
            raise RuntimeError('Polling already stopped')
        assert self._me is not None
        self._stopped = True
        await self.delete_webhook()
        await self._cleanup()
        bot_logger.info('Bot %s (%s) stop listen', self._me.first_name,
                        self._me.username)
