import re
from typing import Final, Tuple

import attr

from . import Bot, FilterProtocol
from .bot_update import BotUpdate
from .constants import ChatType, ContentType, UpdateType

__all__ = ('UpdateTypeFilter', 'StateFilter', 'CommandsFilter',
           'ContentTypeFilter', 'MessageTextFilter', 'CallbackQueryDataFilter',
           'PrivateChatFilter', 'GroupChatFilter', 'ORFilter', 'ANDFilter')


@attr.s(frozen=True, auto_attribs=True)
class UpdateTypeFilter:
    update_type: UpdateType

    async def check(self, _: Bot, update: BotUpdate) -> bool:
        return getattr(update, self.update_type.value) is not None


@attr.s(frozen=True, auto_attribs=True)
class StateFilter:
    state: str

    async def check(self, _: Bot, update: BotUpdate) -> bool:
        return update.state == self.state


@attr.s(frozen=True, auto_attribs=True)
class CommandsFilter:
    commands: Tuple[str, ...]

    async def check(self, _: Bot, update: BotUpdate) -> bool:
        if update.message is None or update.message.text is None:
            return False
        if any(update.message.text.startswith(f'/{command}')
               for command in self.commands):
            return True
        return False


@attr.s(frozen=True, auto_attribs=True)
class ContentTypeFilter:
    content_types: Tuple[ContentType, ...]

    async def check(self, _: Bot, update: BotUpdate) -> bool:
        if update.message is not None:
            message = update.message
        elif update.edited_message is not None:
            message = update.edited_message
        elif update.channel_post is not None:
            message = update.channel_post
        elif update.edited_channel_post is not None:
            message = update.edited_channel_post
        else:
            return False
        for content_type in self.content_types:
            if getattr(message, content_type.value) is not None:
                return True
        return False


@attr.s(frozen=True, auto_attribs=True)
class MessageTextFilter:
    pattern: 're.Pattern[str]'

    async def check(self, _: Bot, update: BotUpdate) -> bool:
        return (update.message is not None and
                update.message.text is not None and
                self.pattern.match(update.message.text) is not None)


@attr.s(frozen=True, auto_attribs=True)
class CallbackQueryDataFilter:
    pattern: 're.Pattern[str]'

    async def check(self, _: Bot, update: BotUpdate) -> bool:
        return (update.callback_query is not None and
                update.callback_query.data is not None and
                self.pattern.match(update.callback_query.data) is not None)


@attr.s(frozen=True)
class PrivateChatFilter:

    async def check(self, _: Bot, update: BotUpdate) -> bool:  # noqa
        return (update.message is not None and
                update.message.chat is not None and
                update.message.chat.type == ChatType.PRIVATE)


@attr.s(frozen=True)
class GroupChatFilter:

    async def check(self, _: Bot, update: BotUpdate) -> bool:  # noqa
        group_types = (ChatType.GROUP, ChatType.SUPERGROUP)
        return (update.message is not None and
                update.message.chat is not None and
                update.message.chat.type in group_types)


class ORFilter:

    def __init__(self, *filters: FilterProtocol) -> None:
        self._filters: Final[Tuple[FilterProtocol, ...]] = filters

    async def check(self, bot: Bot, update: BotUpdate) -> bool:
        return any([await _filter.check(bot, update)
                    for _filter in self._filters])


class ANDFilter:

    def __init__(self, *filters: FilterProtocol) -> None:
        self._filters: Final[Tuple[FilterProtocol, ...]] = filters

    async def check(self, bot: Bot, update: BotUpdate) -> bool:
        return all([await _filter.check(bot, update)
                    for _filter in self._filters])
