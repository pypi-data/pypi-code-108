import asyncio
import json
import logging
from abc import abstractmethod
from functools import partial
from http import HTTPStatus
from typing import (Any, Awaitable, Callable, Dict, Final, Iterator,
                    MutableMapping, Optional, Protocol, Tuple, Union,
                    runtime_checkable)

import aiojobs
import attr
import backoff
from aiofreqlimit import FreqLimit
from aiohttp import (BaseConnector, ClientError, ClientSession, FormData,
                     TCPConnector)
from aiojobs_protocols import SchedulerProtocol

from .api_methods import ApiMethods, ParamType
from .api_types import APIResponse, LocalFile, StreamFile, Update, User
from .bot_update import BotUpdate, Context
from .constants import ChatType, RequestMethod
from .exceptions import (BadGateway, BotBlocked, BotKicked, MigrateToChat,
                         RestartingTelegram, RetryAfter, TelegramError)
from .helpers import KeyLock, get_software, json_dumps
from .storage import StorageProtocol

__all__ = ('Bot', 'PollBot', 'HandlerCallable', 'Handler',
           'HandlerTableProtocol', 'FilterProtocol')

SOFTWARE: Final[str] = get_software()
TG_API_URL: Final[str] = 'https://api.telegram.org/bot{token}/{method}'
TG_FILE_URL: Final[str] = 'https://api.telegram.org/file/bot{token}/{path}'
TG_GET_UPDATES_TIMEOUT: Final[int] = 60
STATE_PREFIX: Final[str] = 'state'
CONTEXT_PREFIX: Final[str] = 'context'
MESSAGE_INTERVAL: Final[float] = 1 / 30
CHAT_INTERVAL: Final[float] = 1
GROUP_INTERVAL: Final[float] = 3

bot_logger: Final[logging.Logger] = logging.getLogger('aiotgbot.bot')
response_logger: Final[logging.Logger] = logging.getLogger('aiotgbot.response')

EventHandler = Callable[['Bot'], Awaitable[None]]


class Bot(MutableMapping[str, Any], ApiMethods):

    def __init__(
        self,
        token: str,
        handler_table: 'HandlerTableProtocol',
        storage: StorageProtocol,
        connector: Optional[BaseConnector] = None
    ) -> None:
        if not handler_table.frozen:
            raise RuntimeError('Can\'t use unfrozen handler table')
        if not isinstance(handler_table, HandlerTableProtocol):
            raise RuntimeError('Handler table is not HandlerTableProtocol '
                               'instance')
        if not isinstance(storage, StorageProtocol):
            raise RuntimeError('Storage parameter is not StorageProtocol '
                               'instance')
        self._token: Final[str] = token
        self._handler_table: Final['HandlerTableProtocol'] = handler_table
        self._storage: Final[StorageProtocol] = storage
        if connector is not None:
            _connector: BaseConnector = connector
        else:
            _connector = TCPConnector(keepalive_timeout=60)
        self._client: Final[ClientSession] = ClientSession(
            connector=_connector,
            json_serialize=json_dumps,
            headers={'User-Agent': SOFTWARE}
        )
        self._context_lock: Final[KeyLock] = KeyLock()
        self._message_limit: Final[FreqLimit] = FreqLimit(MESSAGE_INTERVAL)
        self._chat_limit: Final[FreqLimit] = FreqLimit(CHAT_INTERVAL)
        self._group_limit: Final[FreqLimit] = FreqLimit(GROUP_INTERVAL)
        self._scheduler: Optional[SchedulerProtocol] = None
        self._started: bool = False
        self._stopped: bool = False
        self._updates_offset: int = 0
        self._me: Optional[User] = None
        self._data: Final[Dict[str, Any]] = {}

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self._data[key] = value

    def __delitem__(self, key: str) -> None:
        del self._data[key]

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[str]:
        return iter(self._data)

    @property
    def id(self) -> int:
        return int(self._token.split(':')[0])

    @property
    def storage(self) -> StorageProtocol:
        return self._storage

    @property
    def client(self) -> ClientSession:
        if self._client is None:
            raise RuntimeError('Access to client during bot is not running.')
        else:
            return self._client

    def file_url(self, path: str) -> str:
        return TG_FILE_URL.format(token=self._token, path=path)

    @staticmethod
    def _scheduler_exception_handler(_: SchedulerProtocol,
                                     context: Dict[str, Any]) -> None:
        bot_logger.exception('Update handle error',
                             exc_info=context['exception'])

    @staticmethod
    def _telegram_exception(api_response: APIResponse) -> TelegramError:
        assert api_response.error_code is not None
        assert api_response.description is not None
        error_code = api_response.error_code
        description = api_response.description
        if (
            api_response.parameters is not None and
            api_response.parameters.retry_after is not None
        ):
            retry_after = api_response.parameters.retry_after
            assert retry_after is not None
            return RetryAfter(error_code, description, retry_after)
        elif (api_response.parameters is not None and
              api_response.parameters.migrate_to_chat_id is not None):
            return MigrateToChat(error_code, description,
                                 api_response.parameters.migrate_to_chat_id)
        elif (error_code >= HTTPStatus.INTERNAL_SERVER_ERROR and
              RestartingTelegram.match(description)):
            return RestartingTelegram(error_code, description)
        elif BadGateway.match(description):
            return BadGateway(error_code, description)
        elif BotBlocked.match(description):
            return BotBlocked(error_code, description)
        elif BotKicked.match(description):
            return BotKicked(error_code, description)
        else:
            return TelegramError(error_code, description)

    @backoff.on_exception(backoff.expo, ClientError)
    async def _request(
            self,
            http_method: RequestMethod,
            api_method: str,
            **params: ParamType
    ) -> APIResponse:
        data = {
            name: str(value) if isinstance(value, (int,  float)) else value
            for name, value in params.items() if value is not None
        }
        bot_logger.debug('Request %s %s %r', http_method, api_method, data)
        if http_method == RequestMethod.GET:
            if len(data) > 0:
                assert all(isinstance(value, str) for value in data.values())
                request = partial(self.client.get, params=data)
            else:
                request = partial(self.client.get)
        else:
            form_data = FormData()
            for name, value in data.items():
                if isinstance(value, (StreamFile, LocalFile)):
                    form_data.add_field(name, value.content,
                                        content_type=value.content_type,
                                        filename=value.name)
                else:
                    form_data.add_field(name, value)
            request = partial(self.client.post, data=form_data)

        url = TG_API_URL.format(token=self._token, method=api_method)
        async with request(url) as response:
            response_dict = json.loads(await response.read())
        response_logger.debug(response_dict)
        api_response = APIResponse.from_dict(response_dict)

        if api_response.ok:
            return api_response
        else:
            raise Bot._telegram_exception(api_response)

    async def _safe_request(
            self,
            http_method: RequestMethod,
            api_method: str,
            chat_id: Union[int, str],
            **params: ParamType
    ) -> APIResponse:
        retry_allowed = all(not isinstance(param, StreamFile)
                            for param in params.values())
        request = partial(self._request, http_method, api_method,
                          chat_id=chat_id, **params)

        chat = await self.get_chat(chat_id)
        while True:
            try:
                message_limit = self._message_limit.resource()
                if chat.type in (ChatType.GROUP, ChatType.SUPERGROUP):
                    group_limit = self._group_limit.resource(chat.id)
                    async with message_limit, group_limit:
                        return await request()
                else:
                    chat_limit = self._chat_limit.resource(chat.id)
                    async with message_limit, chat_limit:
                        return await request()
            except RetryAfter as retry_after:
                if retry_allowed:
                    await asyncio.sleep(retry_after.retry_after)
                else:
                    bot_logger.error('RetryAfter error during '
                                     'retry not allowed')
                    raise

    @staticmethod
    def _update_state(update: Update) -> str:
        user_id: Optional[int] = None
        chat_id: Optional[int] = None

        if update.message is not None:
            assert update.message.from_ is not None
            user_id = update.message.from_.id
            assert update.message.chat is not None
            chat_id = update.message.chat.id
        elif update.edited_message is not None:
            assert update.edited_message.from_ is not None
            user_id = update.edited_message.from_.id
            assert update.edited_message.chat is not None
            chat_id = update.edited_message.chat.id
        elif update.channel_post is not None:
            assert update.channel_post.chat is not None
            chat_id = update.channel_post.chat.id
        elif update.edited_channel_post is not None:
            assert update.edited_channel_post.chat is not None
            chat_id = update.edited_channel_post.chat.id
        elif update.inline_query is not None:
            user_id = update.inline_query.from_.id
        elif update.chosen_inline_result is not None:
            user_id = update.chosen_inline_result.from_.id
        elif (update.callback_query is not None and
              update.callback_query.message is not None):
            user_id = update.callback_query.from_.id
            assert update.callback_query.message.chat is not None
            chat_id = update.callback_query.message.chat.id
        elif update.callback_query is not None:
            user_id = update.callback_query.from_.id
        elif update.shipping_query is not None:
            user_id = update.shipping_query.from_.id
        elif update.pre_checkout_query is not None:
            user_id = update.pre_checkout_query.from_.id
        elif update.poll is not None:
            pass
        elif update.poll_answer is not None:
            user_id = update.poll_answer.user.id
        elif update.my_chat_member is not None:
            assert update.my_chat_member.from_ is not None
            user_id = update.my_chat_member.from_.id
            assert update.my_chat_member.chat is not None
            chat_id = update.my_chat_member.chat.id
        elif update.chat_member is not None:
            assert update.chat_member.from_ is not None
            user_id = update.chat_member.from_.id
            assert update.chat_member.chat is not None
            chat_id = update.chat_member.chat.id

        return '{}|{}'.format(str(user_id) if user_id is not None else '',
                              str(chat_id) if chat_id is not None else '')

    async def _handle_update(self, update: Update) -> None:
        assert self._handler_table.frozen
        assert self._context_lock is not None, 'Context lock not initialized'
        bot_logger.debug('Dispatch update "%s"', update.update_id)
        update_state = self._update_state(update)
        state_key = f'{STATE_PREFIX}|{update_state}'
        context_key = f'{CONTEXT_PREFIX}|{update_state}'
        async with self._context_lock.resource(state_key):
            state = await self._storage.get(state_key)
            assert isinstance(state, str) or state is None
            context_dict = await self._storage.get(context_key)
            assert isinstance(context_dict, dict) or context_dict is None
            context = Context(context_dict if context_dict is not None else {})
            bot_update = BotUpdate(state, context, update)
            handler = await self._handler_table.get_handler(self, bot_update)
            if handler is not None:
                bot_logger.debug('Dispatched update "%s" to "%s"',
                                 update.update_id,
                                 handler.__name__)
                await handler(self, bot_update)
                await self._storage.set(state_key, bot_update.state)
                await self._storage.set(context_key,
                                        bot_update.context.to_dict())
                bot_logger.debug('Set context for update "%s"',
                                 update.update_id)
            else:
                bot_logger.debug('Not found handler for update "%s". Skip.',
                                 update.update_id)

    async def _start(self) -> None:
        self._started = True

        self._me = await self.get_me()
        self._scheduler = await aiojobs.create_scheduler(
            exception_handler=self._scheduler_exception_handler)

    async def _cleanup(self) -> None:
        assert self._client is not None
        assert self._scheduler is not None
        await self._scheduler.close()
        await self._client.close()
        await self._message_limit.clear()
        await self._chat_limit.clear()
        await self._group_limit.clear()

    @abstractmethod
    async def start(self) -> None: ...

    @abstractmethod
    async def stop(self) -> None: ...


class PollBot(Bot):

    def __init__(
        self,
        token: str,
        handler_table: 'HandlerTableProtocol',
        storage: StorageProtocol,
        connector: Optional[BaseConnector] = None
    ) -> None:
        super().__init__(token, handler_table, storage, connector)
        self._poll_task: Optional[asyncio.Task[None]] = None

    async def start(self) -> None:
        if self._started:
            raise RuntimeError('Polling already started')
        await self._start()
        assert self._me is not None
        self._poll_task = asyncio.create_task(self._poll_wrapper())
        bot_logger.info('Bot %s (%s) start polling', self._me.first_name,
                        self._me.username)

    async def stop(self) -> None:
        if not self._started:
            raise RuntimeError('Polling not started')
        if self._stopped:
            raise RuntimeError('Polling already stopped')
        assert self._poll_task is not None
        bot_logger.debug('Stop polling')
        self._stopped = True
        if not self._poll_task.done():
            self._poll_task.cancel()

    async def _poll_wrapper(self) -> None:
        assert self._me is not None
        try:
            await self._poll()
        except asyncio.CancelledError:
            pass
        except Exception as exception:
            bot_logger.exception('Error while polling updates',
                                 exc_info=exception)
        await self._cleanup()
        bot_logger.info('Bot %s (%s) stop polling', self._me.first_name,
                        self._me.username)

    @backoff.on_exception(backoff.expo, TelegramError)
    async def _poll(self) -> None:
        assert self._scheduler is not None, 'Scheduler not initialized'
        bot_logger.debug('Get updates from: %s', self._updates_offset)
        while not self._stopped:
            updates = await self.get_updates(offset=self._updates_offset,
                                             timeout=TG_GET_UPDATES_TIMEOUT)
            for update in updates:
                await self._scheduler.spawn(self._handle_update(update))
            if len(updates) > 0:
                self._updates_offset = updates[-1].update_id + 1


HandlerCallable = Callable[[Bot, BotUpdate], Awaitable[None]]
FiltersType = Tuple['FilterProtocol', ...]


@attr.s(frozen=True, auto_attribs=True)
class Handler:
    callable: HandlerCallable
    filters: FiltersType

    async def check(self, bot: Bot, update: BotUpdate) -> bool:
        return all([await _filter.check(bot, update)
                    for _filter in self.filters])


@runtime_checkable
class HandlerTableProtocol(Protocol):

    def freeze(self) -> None: ...

    @property
    def frozen(self) -> bool: ...  # noqa

    @abstractmethod
    async def get_handler(
        self, bot: Bot, update: BotUpdate
    ) -> Optional[HandlerCallable]: ...


@runtime_checkable
class FilterProtocol(Protocol):

    @abstractmethod
    async def check(self, bot: Bot, update: BotUpdate) -> bool: ...
