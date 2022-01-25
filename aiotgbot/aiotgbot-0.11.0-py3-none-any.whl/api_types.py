import asyncio
from enum import Enum
from io import BufferedReader
from pathlib import Path
from typing import (Any, AsyncIterator, Dict, Final, Generator, Iterable, List,
                    Optional, Set, Tuple, Type, TypeVar, Union, cast, get_args,
                    get_origin, get_type_hints)

import attr

from aiotgbot.constants import InputMediaType, ParseMode, PollType

__all__ = ('DataMappingError', 'StreamFile', 'LocalFile', 'BaseTelegram',
           'ResponseParameters', 'APIResponse', 'Update', 'WebhookInfo',
           'User', 'Chat', 'Message', 'MessageId', 'MessageEntity',
           'PhotoSize', 'Audio', 'Document', 'Video', 'Animation', 'Voice',
           'VideoNote', 'Contact', 'Dice', 'Location', 'Venue',
           'ProximityAlertTriggered', 'PollOption', 'PollAnswer', 'Poll',
           'UserProfilePhotos', 'File', 'ReplyMarkup', 'ReplyKeyboardMarkup',
           'KeyboardButton', 'KeyboardButtonPollType', 'ReplyKeyboardRemove',
           'InlineKeyboardMarkup', 'InlineKeyboardButton', 'LoginUrl',
           'CallbackQuery', 'ForceReply', 'ChatPhoto', 'ChatInviteLink',
           'ChatMember', 'ChatMemberUpdated', 'ChatPermissions',
           'ChatLocation', 'BotCommand', 'BotCommandScopeDefault',
           'BotCommandScopeAllPrivateChats', 'BotCommandScopeAllGroupChats',
           'BotCommandScopeChatAdministrators', 'BotCommandScopeChat',
           'BotCommandScopeAllChatAdministrators', 'BotCommandScopeChatMember',
           'InputFile', 'BotCommandScope', 'InputMedia', 'InputMediaPhoto',
           'InputMediaVideo', 'InputMediaAnimation', 'InputMediaAudio',
           'InputMediaDocument', 'Sticker', 'StickerSet', 'MaskPosition',
           'InlineQuery', 'InlineQueryResult', 'InlineQueryResultArticle',
           'InlineQueryResultPhoto', 'InlineQueryResultGif',
           'InlineQueryResultMpeg4Gif', 'InlineQueryResultVideo',
           'InlineQueryResultAudio', 'InlineQueryResultVoice',
           'InlineQueryResultDocument', 'InlineQueryResultLocation',
           'InlineQueryResultVenue', 'InlineQueryResultContact',
           'InlineQueryResultGame', 'InlineQueryResultCachedPhoto',
           'InlineQueryResultCachedGif', 'InlineQueryResultCachedMpeg4Gif',
           'InlineQueryResultCachedSticker', 'InlineQueryResultCachedDocument',
           'InlineQueryResultCachedVideo', 'InlineQueryResultCachedVoice',
           'InlineQueryResultCachedAudio', 'InputMessageContent',
           'InputTextMessageContent', 'InputLocationMessageContent',
           'InputVenueMessageContent', 'InputContactMessageContent',
           'ChosenInlineResult', 'LabeledPrice', 'Invoice', 'ShippingAddress',
           'OrderInfo', 'ShippingOption', 'SuccessfulPayment', 'ShippingQuery',
           'PreCheckoutQuery', 'PassportData', 'PassportFile',
           'EncryptedPassportElement', 'EncryptedCredentials',
           'PassportElementError', 'PassportElementErrorDataField',
           'PassportElementErrorFrontSide', 'PassportElementErrorReverseSide',
           'PassportElementErrorSelfie', 'PassportElementErrorFile',
           'PassportElementErrorFiles', 'PassportElementErrorTranslationFile',
           'PassportElementErrorTranslationFiles',
           'PassportElementErrorUnspecified', 'Game', 'CallbackGame',
           'GameHighScore')


class DataMappingError(BaseException):
    pass


@attr.s(frozen=True, auto_attribs=True)
class StreamFile:
    content: AsyncIterator[bytes]
    name: str
    content_type: Optional[str] = None


class LocalFile:

    def __init__(
        self, path: Union[str, Path], content_type: Optional[str] = None,
    ) -> None:
        self._path: Final[Path] = (path if isinstance(path, Path)
                                   else Path(path))
        self._content_type: Final[Optional[str]] = content_type

    @property
    def name(self) -> str:
        return self._path.name

    @property
    def content_type(self) -> Optional[str]:
        return self._content_type

    @property
    async def content(self) -> AsyncIterator[bytes]:
        loop = asyncio.get_running_loop()
        reader = cast(BufferedReader, await loop.run_in_executor(
            None, self._path.open, 'rb'))
        try:
            chunk = await loop.run_in_executor(None, reader.read, 2 ** 16)
            while len(chunk) > 0:
                yield chunk
                chunk = await loop.run_in_executor(None, reader.read, 2 ** 16)
        finally:
            await loop.run_in_executor(None, reader.close)


def _is_tuple(_type: Any) -> bool:
    return get_origin(_type) is tuple


def _is_list(_type: Any) -> bool:
    return get_origin(_type) is list


def _is_union(_type: Any) -> bool:
    return get_origin(_type) is Union


def _is_optional(_type: Any) -> bool:
    return _type is Any or (_is_union(_type) and type(None) in get_args(_type))


def _is_attr_union(_type: Any) -> bool:
    return _is_union(_type) and all(attr.has(arg_type) or arg_type is _NoneType
                                    for arg_type in get_args(_type))


_NoneType: Type[None] = type(None)
_FieldType = Union[int, str, bool, float, Tuple[Any, ...], List[Any],
                   Dict[str, Any], 'BaseTelegram']
_HintsGenerator = Generator[Tuple[str, str, Any], None, None]


@attr.s(frozen=True)
class BaseTelegram:

    def to_dict(self) -> Dict[str, Any]:
        _dict: Dict[str, Any] = {}
        for _attr in attr.fields(type(self)):
            value = getattr(self, _attr.name)
            key = _attr.name.rstrip('_')
            if isinstance(value, BaseTelegram):
                _dict[key] = value.to_dict()
            elif isinstance(value, (tuple, list)):
                _dict[key] = BaseTelegram._to_list(value)
            elif isinstance(value, (int, str, bool, float)):
                _dict[key] = value
            elif isinstance(value, Enum):
                _dict[key] = value.value
            elif value is None:
                continue
            else:
                raise TypeError(f'"{value}" has unsupported type')

        return _dict

    @classmethod
    def from_dict(cls: Type['_Telegram'], data: Dict[str, Any]) -> '_Telegram':
        return cast(_Telegram, BaseTelegram._handle_object(cls, data))

    @staticmethod
    def _to_list(value: Iterable[Any]) -> List[Any]:
        _list: List[Any] = []
        for item in value:
            if isinstance(item, (int, str, bool, float)):
                _list.append(item)
            elif isinstance(item, (tuple, list)):
                _list.append(BaseTelegram._to_list(item))
            elif isinstance(item, BaseTelegram):
                _list.append(item.to_dict())
            elif isinstance(value, Enum):
                _list.append(value.value)
            else:
                raise TypeError(f'"{item}" has unsupported type')

        return _list

    @staticmethod
    def _get_type_hints(_type: Any) -> Tuple[Tuple[str, str, Any], ...]:
        return tuple((field.rstrip('_'), field, _type)
                     for field, _type in get_type_hints(_type).items())

    @staticmethod
    def _handle_object(_type: Any, data: Dict[str, Any]) -> Any:
        assert issubclass(_type, BaseTelegram)
        assert attr.has(_type)
        type_hints = _type._get_type_hints(_type)
        required = frozenset(field for field, _, _type in type_hints
                             if not _is_optional(_type))
        filled = frozenset(key for key, value in data.items()
                           if value is not None)
        if not required <= filled:
            keys = ', '.join(required - filled)
            raise DataMappingError(f'Data without required keys: {keys}')
        params = {field: BaseTelegram._handle_field(_type, data.get(key))
                  for key, field, _type in type_hints}

        return cast(Any, _type)(**params)

    @staticmethod
    def _handle_field(_type: Any, value: Any) -> Optional[_FieldType]:
        if _type in (int, str, bool, float) and isinstance(value, _type):
            return cast(_FieldType, value)
        elif _type in (int, str, bool, float):
            message = f'"{value}" is not instance of type "{_type.__name__}"'
            raise DataMappingError(message)
        elif _type is _NoneType and value is None:
            return None
        elif _type is _NoneType:
            raise DataMappingError(f'"{value}" is not None')
        elif _type is Any:
            return cast(_FieldType, value)
        elif _is_tuple(_type) and isinstance(value, list):
            return tuple(BaseTelegram._handle_field(get_args(_type)[0], item)
                         for item in value)
        elif _is_list(_type) and isinstance(value, list):
            return [BaseTelegram._handle_field(get_args(_type)[0], item)
                    for item in value]
        elif _is_list(_type) or _is_tuple(_type):
            raise DataMappingError(f'Data "{value}" is not list')
        elif _is_optional(_type) and value is None:
            return None
        elif _is_optional(_type) and len(get_args(_type)) == 2:
            return BaseTelegram._handle_field(get_args(_type)[0], value)
        elif _is_attr_union(_type) and isinstance(value, dict):
            types: List[Tuple[int, Any]] = []
            for arg_type in get_args(_type):
                fields: Set[str] = set(key.rstrip('_') for key
                                       in get_type_hints(arg_type).keys())
                data_keys: Set[str] = set(value.keys())
                if not data_keys <= fields:
                    continue
                types.append((len(fields & data_keys), arg_type))
            if len(types) == 0:
                arg_types = ', '.join(t.__name__ for t in get_args(_type))
                message = f'Data "{value}" not match any of "{arg_types}"'
                raise DataMappingError(message)
            types = sorted(types, key=lambda t: t[0], reverse=True)
            return BaseTelegram._handle_field(types[0][1], value)
        elif attr.has(_type) and isinstance(value, dict):
            return cast(
                BaseTelegram,
                BaseTelegram._handle_object(_type, value)
            )
        else:
            message = f'Data "{value}" not match field type "{_type}"'
            raise DataMappingError(message)


_Telegram = TypeVar('_Telegram', bound=BaseTelegram)


@attr.s(auto_attribs=True)
class ResponseParameters(BaseTelegram):
    migrate_to_chat_id: Optional[int] = None
    retry_after: Optional[int] = None


@attr.s(auto_attribs=True)
class APIResponse(BaseTelegram):
    ok: bool
    result: Any
    error_code: Optional[int] = None
    description: Optional[str] = None
    parameters: Optional[ResponseParameters] = None


@attr.s(auto_attribs=True)
class Update(BaseTelegram):
    update_id: int
    message: Optional['Message'] = None
    edited_message: Optional['Message'] = None
    channel_post: Optional['Message'] = None
    edited_channel_post: Optional['Message'] = None
    inline_query: Optional['InlineQuery'] = None
    chosen_inline_result: Optional['ChosenInlineResult'] = None
    callback_query: Optional['CallbackQuery'] = None
    shipping_query: Optional['ShippingQuery'] = None
    pre_checkout_query: Optional['PreCheckoutQuery'] = None
    poll: Optional['Poll'] = None
    poll_answer: Optional['PollAnswer'] = None
    my_chat_member: Optional['ChatMemberUpdated'] = None
    chat_member: Optional['ChatMemberUpdated'] = None
    chat_join_request: Optional['ChatJoinRequest'] = None


@attr.s(auto_attribs=True)
class WebhookInfo(BaseTelegram):
    allowed_updates: Tuple[str, ...]
    url: Optional[str] = None
    has_custom_certificate: Optional[bool] = None
    pending_update_count: Optional[int] = None
    ip_address: Optional[str] = None
    last_error_date: Optional[int] = None
    last_error_message: Optional[str] = None
    max_connections: Optional[int] = None


@attr.s(auto_attribs=True)
class User(BaseTelegram):
    id: int
    is_bot: bool
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    language_code: Optional[str] = None
    can_join_groups: Optional[bool] = None
    can_read_all_group_messages: Optional[bool] = None
    supports_inline_queries: Optional[bool] = None


@attr.s(auto_attribs=True)
class Chat(BaseTelegram):
    id: int
    type: str
    title: Optional[str] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    photo: Optional['ChatPhoto'] = None
    bio: Optional[str] = None
    has_private_forwards: Optional[bool] = None
    description: Optional[str] = None
    invite_link: Optional[str] = None
    pinned_message: Optional['Message'] = None
    permissions: Optional['ChatPermissions'] = None
    slow_mode_delay: Optional[int] = None
    has_protected_content: Optional[bool] = None
    sticker_set_name: Optional[str] = None
    can_set_sticker_set: Optional[bool] = None
    linked_chat_id: Optional[int] = None
    location: Optional['ChatLocation'] = None


@attr.s(auto_attribs=True)
class Message(BaseTelegram):
    message_id: int
    date: int
    chat: Chat
    from_: Optional[User] = None
    sender_chat: Optional[Chat] = None
    forward_from: Optional[User] = None
    forward_from_chat: Optional[Chat] = None
    forward_from_message_id: Optional[int] = None
    forward_signature: Optional[str] = None
    forward_sender_name: Optional[str] = None
    forward_date: Optional[int] = None
    is_automatic_forward: Optional[bool] = None
    reply_to_message: Optional['Message'] = None
    via_bot: Optional[User] = None
    edit_date: Optional[int] = None
    has_protected_content: Optional[bool] = None
    media_group_id: Optional[str] = None
    author_signature: Optional[str] = None
    text: Optional[str] = None
    entities: Optional[Tuple['MessageEntity', ...]] = None
    caption_entities: Optional[Tuple['MessageEntity', ...]] = None
    audio: Optional['Audio'] = None
    document: Optional['Document'] = None
    animation: Optional['Animation'] = None
    game: Optional['Game'] = None
    photo: Optional[Tuple['PhotoSize', ...]] = None
    sticker: Optional['Sticker'] = None
    video: Optional['Video'] = None
    voice: Optional['Voice'] = None
    video_note: Optional['VideoNote'] = None
    caption: Optional[str] = None
    contact: Optional['Contact'] = None
    dice: Optional['Dice'] = None
    location: Optional['Location'] = None
    venue: Optional['Venue'] = None
    poll: Optional['Poll'] = None
    new_chat_members: Optional[Tuple[User, ...]] = None
    left_chat_member: Optional[User] = None
    new_chat_title: Optional[str] = None
    new_chat_photo: Optional[Tuple['PhotoSize', ...]] = None
    delete_chat_photo: Optional[bool] = None
    group_chat_created: Optional[bool] = None
    supergroup_chat_created: Optional[bool] = None
    channel_chat_created: Optional[bool] = None
    message_auto_delete_timer_changed: Optional['MADTC'] = None
    migrate_to_chat_id: Optional[int] = None
    migrate_from_chat_id: Optional[int] = None
    pinned_message: Optional['Message'] = None
    invoice: Optional['Invoice'] = None
    successful_payment: Optional['SuccessfulPayment'] = None
    connected_website: Optional[str] = None
    passport_data: Optional['PassportData'] = None
    proximity_alert_triggered: Optional['ProximityAlertTriggered'] = None
    voice_chat_scheduled: Optional['VoiceChatScheduled'] = None
    voice_chat_started: Optional['VoiceChatStarted'] = None
    voice_chat_ended: Optional['VoiceChatEnded'] = None
    voice_chat_participants_invited: Optional['VCPI'] = None
    reply_markup: Optional['InlineKeyboardMarkup'] = None


@attr.s(auto_attribs=True)
class MessageId(BaseTelegram):
    message_id: int


@attr.s(auto_attribs=True)
class MessageEntity(BaseTelegram):
    type: str
    offset: int
    length: int
    url: Optional[str] = None
    user: Optional[User] = None
    language: Optional[str] = None


@attr.s(auto_attribs=True)
class PhotoSize(BaseTelegram):
    file_id: str
    file_unique_id: str
    width: int
    height: int
    file_size: int


@attr.s(auto_attribs=True)
class Audio(BaseTelegram):
    file_id: str
    file_unique_id: str
    duration: int
    performer: Optional[str] = None
    title: Optional[str] = None
    file_name: Optional[str] = None
    mime_type: Optional[str] = None
    file_size: Optional[int] = None
    thumb: Optional[PhotoSize] = None


@attr.s(auto_attribs=True)
class Document(BaseTelegram):
    file_id: str
    file_unique_id: str
    thumb: Optional[PhotoSize] = None
    file_name: Optional[str] = None
    mime_type: Optional[str] = None
    file_size: Optional[int] = None


@attr.s(auto_attribs=True)
class Video(BaseTelegram):
    file_id: str
    file_unique_id: str
    width: int
    height: int
    duration: int
    thumb: Optional[PhotoSize] = None
    file_name: Optional[str] = None
    mime_type: Optional[str] = None
    file_size: Optional[int] = None


@attr.s(auto_attribs=True)
class Animation(BaseTelegram):
    file_id: str
    file_unique_id: str
    thumb: Optional[PhotoSize] = None
    file_name: Optional[str] = None
    mime_type: Optional[str] = None
    file_size: Optional[int] = None


@attr.s(auto_attribs=True)
class Voice(BaseTelegram):
    file_id: str
    file_unique_id: str
    duration: int
    mime_type: Optional[str] = None
    file_size: Optional[int] = None


@attr.s(auto_attribs=True)
class VideoNote(BaseTelegram):
    file_id: str
    file_unique_id: str
    length: int
    duration: int
    thumb: Optional[PhotoSize] = None
    file_size: Optional[int] = None


@attr.s(auto_attribs=True)
class Contact(BaseTelegram):
    phone_number: str
    first_name: str
    last_name: Optional[str] = None
    user_id: Optional[int] = None
    vcard: Optional[int] = None


@attr.s(auto_attribs=True)
class Dice(BaseTelegram):
    emoji: str
    value: int


@attr.s(auto_attribs=True)
class Location(BaseTelegram):
    longitude: float
    latitude: float
    horizontal_accuracy: Optional[float] = None
    live_period: Optional[int] = None
    heading: Optional[int] = None
    proximity_alert_radius: Optional[int] = None


@attr.s(auto_attribs=True)
class Venue(BaseTelegram):
    location: Location
    title: str
    address: str
    foursquare_id: Optional[str] = None
    foursquare_type: Optional[str] = None
    google_place_id: Optional[str] = None
    google_place_type: Optional[str] = None


@attr.s(auto_attribs=True)
class VoiceChatStarted(BaseTelegram):
    pass


@attr.s(auto_attribs=True)
class VoiceChatEnded(BaseTelegram):
    duration: int


@attr.s(auto_attribs=True)
class VoiceChatParticipantsInvited(BaseTelegram):
    users: Optional[Tuple[User, ...]] = None


VCPI = VoiceChatParticipantsInvited


@attr.s(auto_attribs=True)
class ProximityAlertTriggered(BaseTelegram):
    traveler: User
    watcher: User
    distance: int


@attr.s(auto_attribs=True)
class MessageAutoDeleteTimerChanged(BaseTelegram):
    message_auto_delete_time: int


MADTC = MessageAutoDeleteTimerChanged


@attr.s(auto_attribs=True)
class VoiceChatScheduled(BaseTelegram):
    start_date: int


@attr.s(auto_attribs=True)
class PollOption(BaseTelegram):
    text: str
    voter_count: int


@attr.s(auto_attribs=True)
class PollAnswer(BaseTelegram):
    poll_id: str
    user: User
    option_ids: Tuple[int, ...]


@attr.s(auto_attribs=True)
class Poll(BaseTelegram):
    id: str
    question: str
    options: Tuple[PollOption, ...]
    total_voter_count: int
    is_closed: bool
    is_anonymous: bool
    type_: str
    allows_multiple_answers: bool
    correct_option_id: Optional[int] = None
    explanation: Optional[str] = None
    explanation_entities: Optional[Tuple[MessageEntity, ...]] = None
    open_period: Optional[int] = None
    close_date: Optional[int] = None


@attr.s(auto_attribs=True)
class UserProfilePhotos(BaseTelegram):
    total_count: int
    photos: Tuple[Tuple[PhotoSize, ...], ...]


@attr.s(auto_attribs=True)
class File(BaseTelegram):
    file_id: str
    file_unique_id: str
    file_size: Optional[int] = None
    file_path: Optional[str] = None


ReplyMarkup = Union['InlineKeyboardMarkup',
                    'ReplyKeyboardMarkup',
                    'ReplyKeyboardRemove',
                    'ForceReply']


@attr.s(auto_attribs=True)
class ReplyKeyboardMarkup(BaseTelegram):
    keyboard: List[List['KeyboardButton']]
    resize_keyboard: Optional[bool] = None
    one_time_keyboard: Optional[bool] = None
    input_field_placeholder: Optional[str] = None
    selective: Optional[bool] = None


@attr.s(auto_attribs=True)
class KeyboardButton(BaseTelegram):
    text: str
    request_contact: Optional[bool] = None
    request_location: Optional[bool] = None
    request_poll: Optional['KeyboardButtonPollType'] = None


@attr.s(auto_attribs=True)
class KeyboardButtonPollType(BaseTelegram):
    type_: PollType


@attr.s(auto_attribs=True)
class ReplyKeyboardRemove(BaseTelegram):
    remove_keyboard: bool
    selective: Optional[bool] = None


@attr.s(auto_attribs=True)
class InlineKeyboardMarkup(BaseTelegram):
    inline_keyboard: List[List['InlineKeyboardButton']]


@attr.s(auto_attribs=True)
class InlineKeyboardButton(BaseTelegram):
    text: str
    url: Optional[str] = None
    login_url: Optional['LoginUrl'] = None
    callback_data: Optional[str] = None
    switch_inline_query: Optional[str] = None
    switch_inline_query_current_chat: Optional[str] = None
    callback_game: Optional['CallbackGame'] = None
    pay: Optional[bool] = None


@attr.s(auto_attribs=True)
class LoginUrl(BaseTelegram):
    url: str
    forward_text: Optional[str] = None
    bot_username: Optional[str] = None
    request_write_access: Optional[bool] = None


@attr.s(auto_attribs=True)
class CallbackQuery(BaseTelegram):
    id: str
    from_: User
    chat_instance: str
    message: Optional[Message] = None
    inline_message_id: Optional[str] = None
    data: Optional[str] = None
    game_short_name: Optional[str] = None


@attr.s(auto_attribs=True)
class ForceReply(BaseTelegram):
    force_reply: bool
    input_field_placeholder: Optional[str] = None
    selective: Optional[bool] = None


@attr.s(auto_attribs=True)
class ChatPhoto(BaseTelegram):
    small_file_id: str
    small_file_unique_id: str
    big_file_id: str
    big_file_unique_id: str


@attr.s(auto_attribs=True)
class ChatInviteLink(BaseTelegram):
    invite_link: str
    creator: User
    creates_join_request: bool
    is_primary: bool
    is_revoked: bool
    name: Optional[str] = None
    expire_date: Optional[int] = None
    member_limit: Optional[int] = None
    pending_join_request_count: Optional[int] = None


@attr.s(auto_attribs=True)
class ChatMember(BaseTelegram):
    user: User
    status: str
    custom_title: Optional[str] = None
    is_anonymous: Optional[bool] = None
    until_date: Optional[int] = None
    can_be_edited: Optional[bool] = None
    can_manage_chat: Optional[bool] = None
    can_change_info: Optional[bool] = None
    can_post_messages: Optional[bool] = None
    can_edit_messages: Optional[bool] = None
    can_delete_messages: Optional[bool] = None
    can_manage_voice_chats: Optional[bool] = None
    can_invite_users: Optional[bool] = None
    can_restrict_members: Optional[bool] = None
    can_pin_messages: Optional[bool] = None
    can_promote_members: Optional[bool] = None
    is_member: Optional[bool] = None
    can_send_messages: Optional[bool] = None
    can_send_media_messages: Optional[bool] = None
    can_send_other_messages: Optional[bool] = None
    can_add_web_page_previews: Optional[bool] = None
    can_send_polls: Optional[bool] = None


@attr.s(auto_attribs=True)
class ChatMemberUpdated(BaseTelegram):
    chat: Chat
    from_: User
    date: int
    old_chat_member: ChatMember
    new_chat_member: ChatMember
    invite_link: Optional[ChatInviteLink] = None


@attr.s(auto_attribs=True)
class ChatJoinRequest(BaseTelegram):
    chat: Chat
    from_: User
    date: int
    bio: Optional[str] = None
    invite_link: Optional[ChatInviteLink] = None


@attr.s(auto_attribs=True)
class ChatPermissions(BaseTelegram):
    can_send_messages: Optional[bool] = None
    can_send_media_messages: Optional[bool] = None
    can_send_polls: Optional[bool] = None
    can_send_other_messages: Optional[bool] = None
    can_add_web_page_previews: Optional[bool] = None
    can_change_info: Optional[bool] = None
    can_invite_users: Optional[bool] = None
    can_pin_messages: Optional[bool] = None


@attr.s(auto_attribs=True)
class ChatLocation(BaseTelegram):
    location: Location
    address: str


@attr.s(auto_attribs=True)
class BotCommand(BaseTelegram):
    command: str
    description: str


@attr.s(auto_attribs=True)
class BotCommandScopeDefault(BaseTelegram):
    type: str = 'default'


@attr.s(auto_attribs=True)
class BotCommandScopeAllPrivateChats(BaseTelegram):
    type: str = 'all_private_chats'


@attr.s(auto_attribs=True)
class BotCommandScopeAllGroupChats(BaseTelegram):
    type: str = 'all_group_chats'


@attr.s(auto_attribs=True)
class BotCommandScopeAllChatAdministrators(BaseTelegram):
    type: str = 'all_chat_administrators'


@attr.s(auto_attribs=True)
class BotCommandScopeChat(BaseTelegram):
    chat_id: Union[int, str]
    type: str = 'chat'


@attr.s(auto_attribs=True)
class BotCommandScopeChatAdministrators(BaseTelegram):
    chat_id: Union[int, str]
    type: str = 'chat'


@attr.s(auto_attribs=True)
class BotCommandScopeChatMember(BaseTelegram):
    chat_id: Union[int, str]
    user_id: int
    type: str = 'chat'


BotCommandScope = Union[BotCommandScopeDefault,
                        BotCommandScopeAllPrivateChats,
                        BotCommandScopeAllGroupChats,
                        BotCommandScopeAllChatAdministrators,
                        BotCommandScopeChat,
                        BotCommandScopeChatAdministrators,
                        BotCommandScopeChatMember]

InputFile = Union[LocalFile, StreamFile]


@attr.s(auto_attribs=True)
class InputMedia(BaseTelegram):
    media: Union[str, InputFile]
    caption: Optional[str] = None
    parse_mode: Optional[str] = None
    caption_entities: Optional[Iterable[MessageEntity]] = None

    def to_dict(self) -> Dict[str, Any]:
        if not isinstance(self.media, str):
            raise TypeError('To serialize this object, the media attribute '
                            'type must be a string')
        return super().to_dict()


@attr.s(auto_attribs=True)
class InputMediaPhoto(InputMedia):
    type: str = attr.ib(default=InputMediaType.PHOTO, init=False)


@attr.s(auto_attribs=True)
class InputMediaVideo(InputMedia):
    type: str = attr.ib(default=InputMediaType.VIDEO, init=False)
    thumb: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    duration: Optional[int] = None
    supports_streaming: Optional[bool] = None


@attr.s(auto_attribs=True)
class InputMediaAnimation(InputMedia):
    type: str = attr.ib(default=InputMediaType.ANIMATION, init=False)
    thumb: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    duration: Optional[int] = None


@attr.s(auto_attribs=True)
class InputMediaAudio(InputMedia):
    type: str = attr.ib(default=InputMediaType.AUDIO, init=False)
    thumb: Optional[str] = None
    duration: Optional[int] = None
    performer: Optional[str] = None
    title: Optional[str] = None


@attr.s(auto_attribs=True)
class InputMediaDocument(InputMedia):
    type: str = attr.ib(default=InputMediaType.DOCUMENT, init=False)
    thumb: Optional[str] = None
    disable_content_type_detection: Optional[bool] = None


@attr.s(auto_attribs=True)
class Sticker(BaseTelegram):
    file_id: str
    file_unique_id: str
    width: int
    height: int
    is_animated: bool
    thumb: Optional[PhotoSize] = None
    emoji: Optional[str] = None
    set_name: Optional[str] = None
    mask_position: Optional['MaskPosition'] = None
    file_size: Optional[int] = None


@attr.s(auto_attribs=True)
class StickerSet(BaseTelegram):
    name: str
    title: str
    is_animated: bool
    contains_masks: bool
    stickers: Tuple[Sticker, ...]
    thumb: Optional[PhotoSize] = None


@attr.s(auto_attribs=True)
class MaskPosition(BaseTelegram):
    point: str
    x_shift: float
    y_shift: float
    scale: float


@attr.s(auto_attribs=True)
class InlineQuery(BaseTelegram):
    id: str
    from_: User
    query: str
    offset: str
    chat_type: Optional[str] = None
    location: Optional[Location] = None


InlineQueryResult = Union['InlineQueryResultCachedAudio',
                          'InlineQueryResultCachedDocument',
                          'InlineQueryResultCachedGif',
                          'InlineQueryResultCachedMpeg4Gif',
                          'InlineQueryResultCachedPhoto',
                          'InlineQueryResultCachedSticker',
                          'InlineQueryResultCachedVideo',
                          'InlineQueryResultCachedVoice',
                          'InlineQueryResultArticle',
                          'InlineQueryResultAudio',
                          'InlineQueryResultContact',
                          'InlineQueryResultGame',
                          'InlineQueryResultDocument',
                          'InlineQueryResultGif',
                          'InlineQueryResultLocation',
                          'InlineQueryResultMpeg4Gif',
                          'InlineQueryResultPhoto',
                          'InlineQueryResultVenue',
                          'InlineQueryResultVideo',
                          'InlineQueryResultVoice']


@attr.s(auto_attribs=True)
class InlineQueryResultArticle(BaseTelegram):
    type: str
    id: str
    title: str
    input_message_content: 'InputMessageContent'
    reply_markup: Optional[InlineKeyboardMarkup] = None
    url: Optional[str] = None
    hide_url: Optional[bool] = None
    description: Optional[str] = None
    thumb_url: Optional[str] = None
    thumb_width: Optional[int] = None
    thumb_height: Optional[int] = None


@attr.s(auto_attribs=True)
class InlineQueryResultPhoto(BaseTelegram):
    type: str
    td: str
    photo_url: str
    thumb_url: str
    photo_width: Optional[int] = None
    photo_height: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    caption: Optional[str] = None
    parse_mode: Optional[ParseMode] = None
    caption_entities: Optional[Iterable[MessageEntity]] = None
    reply_markup: Optional[InlineKeyboardMarkup] = None
    input_message_content: Optional['InputMessageContent'] = None


@attr.s(auto_attribs=True)
class InlineQueryResultGif(BaseTelegram):
    type: str
    id: str
    gif_url: str
    thumb_url: str
    gif_width: Optional[int] = None
    gif_height: Optional[int] = None
    title: Optional[str] = None
    caption: Optional[str] = None
    parse_mode: Optional[ParseMode] = None
    caption_entities: Optional[Iterable[MessageEntity]] = None
    reply_markup: Optional[InlineKeyboardMarkup] = None
    input_message_content: Optional['InputMessageContent'] = None


@attr.s(auto_attribs=True)
class InlineQueryResultMpeg4Gif(BaseTelegram):
    type: str
    id: str
    mpeg4_url: str
    thumb_url: str
    mpeg4_width: Optional[int] = None
    mpeg4_height: Optional[int] = None
    title: Optional[str] = None
    caption: Optional[str] = None
    parse_mode: Optional[ParseMode] = None
    caption_entities: Optional[Iterable[MessageEntity]] = None
    reply_markup: Optional[InlineKeyboardMarkup] = None
    input_message_content: Optional['InputMessageContent'] = None


@attr.s(auto_attribs=True)
class InlineQueryResultVideo(BaseTelegram):
    type: str
    id: str
    video_url: str
    mime_type: str
    thumb_url: str
    title: str
    caption: Optional[str] = None
    parse_mode: Optional[ParseMode] = None
    caption_entities: Optional[Iterable[MessageEntity]] = None
    video_width: Optional[int] = None
    video_height: Optional[int] = None
    video_duration: Optional[int] = None
    description: Optional[str] = None
    reply_markup: Optional[InlineKeyboardMarkup] = None
    input_message_content: Optional['InputMessageContent'] = None


@attr.s(auto_attribs=True)
class InlineQueryResultAudio(BaseTelegram):
    type: str
    id: str
    audio_url: str
    title: str
    caption: Optional[str] = None
    parse_mode: Optional[ParseMode] = None
    caption_entities: Optional[Iterable[MessageEntity]] = None
    performer: Optional[str] = None
    audio_duration: Optional[int] = None
    reply_markup: Optional[InlineKeyboardMarkup] = None
    input_message_content: Optional['InputMessageContent'] = None


@attr.s(auto_attribs=True)
class InlineQueryResultVoice(BaseTelegram):
    type: str
    id: str
    voice_url: str
    title: str
    caption: Optional[str] = None
    parse_mode: Optional[ParseMode] = None
    caption_entities: Optional[Iterable[MessageEntity]] = None
    voice_duration: Optional[int] = None
    reply_markup: Optional[InlineKeyboardMarkup] = None
    input_message_content: Optional['InputMessageContent'] = None


@attr.s(auto_attribs=True)
class InlineQueryResultDocument(BaseTelegram):
    type: str
    id: str
    title: str
    document_url: str
    mime_type: str
    caption: Optional[str] = None
    parse_mode: Optional[ParseMode] = None
    caption_entities: Optional[Iterable[MessageEntity]] = None
    description: Optional[str] = None
    reply_markup: Optional[InlineKeyboardMarkup] = None
    input_message_content: Optional['InputMessageContent'] = None
    thumb_url: Optional[str] = None
    thumb_width: Optional[int] = None
    thumb_height: Optional[int] = None


@attr.s(auto_attribs=True)
class InlineQueryResultLocation(BaseTelegram):
    type: str
    id: str
    latitude: float
    longitude: float
    title: str
    horizontal_accuracy: Optional[float] = None
    live_period: Optional[int] = None
    heading: Optional[int] = None
    proximity_alert_radius: Optional[int] = None
    reply_markup: Optional[InlineKeyboardMarkup] = None
    input_message_content: Optional['InputMessageContent'] = None
    thumb_url: Optional[str] = None
    thumb_width: Optional[int] = None
    thumb_height: Optional[int] = None


@attr.s(auto_attribs=True)
class InlineQueryResultVenue(BaseTelegram):
    type: str
    id: str
    latitude: float
    longitude: float
    title: str
    address: str
    foursquare_id: Optional[str] = None
    foursquare_type: Optional[str] = None
    google_place_id: Optional[str] = None
    google_place_type: Optional[str] = None
    reply_markup: Optional[InlineKeyboardMarkup] = None
    input_message_content: Optional['InputMessageContent'] = None
    thumb_url: Optional[str] = None
    thumb_width: Optional[int] = None
    thumb_height: Optional[int] = None


@attr.s(auto_attribs=True)
class InlineQueryResultContact(BaseTelegram):
    type: str
    id: str
    phone_number: str
    first_name: str
    last_name: Optional[str] = None
    vcard: Optional[str] = None
    reply_markup: Optional[InlineKeyboardMarkup] = None
    input_message_content: Optional['InputMessageContent'] = None
    thumb_url: Optional[str] = None
    thumb_width: Optional[int] = None
    thumb_height: Optional[int] = None


@attr.s(auto_attribs=True)
class InlineQueryResultGame(BaseTelegram):
    type: str
    id: str
    game_short_name: str
    reply_markup: Optional[InlineKeyboardMarkup] = None


@attr.s(auto_attribs=True)
class InlineQueryResultCachedPhoto(BaseTelegram):
    type: str
    id: str
    photofileid: str
    title: Optional[str] = None
    description: Optional[str] = None
    caption: Optional[str] = None
    parse_mode: Optional[ParseMode] = None
    caption_entities: Optional[Iterable[MessageEntity]] = None
    reply_markup: Optional[InlineKeyboardMarkup] = None
    input_message_content: Optional['InputMessageContent'] = None


@attr.s(auto_attribs=True)
class InlineQueryResultCachedGif(BaseTelegram):
    type: str
    id: str
    gif_file_id: str
    title: Optional[str] = None
    caption: Optional[str] = None
    parse_mode: Optional[ParseMode] = None
    caption_entities: Optional[Iterable[MessageEntity]] = None
    reply_markup: Optional[InlineKeyboardMarkup] = None
    input_message_content: Optional['InputMessageContent'] = None


@attr.s(auto_attribs=True)
class InlineQueryResultCachedMpeg4Gif(BaseTelegram):
    type: str
    id: str
    mpeg4_file_id: str
    title: Optional[str] = None
    caption: Optional[str] = None
    parse_mode: Optional[ParseMode] = None
    caption_entities: Optional[Iterable[MessageEntity]] = None
    reply_markup: Optional[InlineKeyboardMarkup] = None
    input_message_content: Optional['InputMessageContent'] = None


@attr.s(auto_attribs=True)
class InlineQueryResultCachedSticker(BaseTelegram):
    type: str
    id: str
    sticker_file_id: str
    reply_markup: Optional[InlineKeyboardMarkup] = None
    input_message_content: Optional['InputMessageContent'] = None


@attr.s(auto_attribs=True)
class InlineQueryResultCachedDocument(BaseTelegram):
    type: str
    id: str
    title: str
    document_file_id: str
    description: Optional[str] = None
    caption: Optional[str] = None
    parse_mode: Optional[ParseMode] = None
    caption_entities: Optional[Iterable[MessageEntity]] = None
    reply_markup: Optional[InlineKeyboardMarkup] = None
    input_message_content: Optional['InputMessageContent'] = None


@attr.s(auto_attribs=True)
class InlineQueryResultCachedVideo(BaseTelegram):
    type: str
    id: str
    video_file_id: str
    title: str
    description: Optional[str] = None
    caption: Optional[str] = None
    parse_mode: Optional[ParseMode] = None
    caption_entities: Optional[Iterable[MessageEntity]] = None
    reply_markup: Optional[InlineKeyboardMarkup] = None
    input_message_content: Optional['InputMessageContent'] = None


@attr.s(auto_attribs=True)
class InlineQueryResultCachedVoice(BaseTelegram):
    type: str
    id: str
    voice_file_id: str
    title: str
    caption: Optional[str] = None
    parse_mode: Optional[ParseMode] = None
    caption_entities: Optional[Iterable[MessageEntity]] = None
    reply_markup: Optional[InlineKeyboardMarkup] = None
    input_message_content: Optional['InputMessageContent'] = None


@attr.s(auto_attribs=True)
class InlineQueryResultCachedAudio(BaseTelegram):
    type: str
    id: str
    audio_file_id: str
    caption: Optional[str] = None
    parse_mode: Optional[ParseMode] = None
    caption_entities: Optional[Iterable[MessageEntity]] = None
    reply_markup: Optional[InlineKeyboardMarkup] = None
    input_message_content: Optional['InputMessageContent'] = None


InputMessageContent = Union['InputTextMessageContent',
                            'InputLocationMessageContent',
                            'InputVenueMessageContent',
                            'InputContactMessageContent']


@attr.s(auto_attribs=True)
class InputTextMessageContent(BaseTelegram):
    message_text: str
    parse_mode: Optional[ParseMode] = None
    entities: Optional[Iterable[MessageEntity]] = None
    disable_web_page_preview: Optional[bool] = None


@attr.s(auto_attribs=True)
class InputLocationMessageContent(BaseTelegram):
    latitude: float
    longitude: float
    horizontal_accuracy: Optional[float] = None
    live_period: Optional[int] = None
    heading: Optional[int] = None
    proximity_alert_radius: Optional[int] = None


@attr.s(auto_attribs=True)
class InputVenueMessageContent(BaseTelegram):
    latitude: float
    longitude: float
    title: str
    address: str
    foursquare_id: Optional[str] = None
    foursquare_type: Optional[str] = None
    google_place_id: Optional[str] = None
    google_place_type: Optional[str] = None


@attr.s(auto_attribs=True)
class InputContactMessageContent(BaseTelegram):
    phone_number: str
    first_name: str
    last_name: Optional[str] = None
    vcard: Optional[str] = None


@attr.s(auto_attribs=True)
class InputInvoiceMessageContent:
    title: str
    description: str
    payload: str
    provider_token: str
    currency: str
    prices: Tuple['LabeledPrice', ...]
    max_tip_amount: Optional[int] = None
    suggested_tip_amounts: Optional[Tuple[int, ...]] = None
    provider_data: Optional[str] = None
    photo_url: Optional[str] = None
    photo_size: Optional[int] = None
    photo_width: Optional[int] = None
    photo_height: Optional[int] = None
    need_name: Optional[bool] = None
    need_phone_number: Optional[bool] = None
    need_email: Optional[bool] = None
    need_shipping_address: Optional[bool] = None
    send_phone_number_to_provider: Optional[bool] = None
    send_email_to_provider: Optional[bool] = None
    is_flexible: Optional[bool] = None


@attr.s(auto_attribs=True)
class ChosenInlineResult(BaseTelegram):
    result_id: str
    from_: User
    query: str
    location: Optional[Location] = None
    inline_message_id: Optional[str] = None


@attr.s(auto_attribs=True)
class LabeledPrice(BaseTelegram):
    label: str
    amount: int


@attr.s(auto_attribs=True)
class Invoice(BaseTelegram):
    title: str
    description: str
    start_parameter: str
    currency: str
    total_amount: int


@attr.s(auto_attribs=True)
class ShippingAddress(BaseTelegram):
    country_code: str
    state: str
    city: str
    street_line1: str
    street_line2: str
    post_code: str


@attr.s(auto_attribs=True)
class OrderInfo(BaseTelegram):
    name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    shipping_address: Optional[ShippingAddress] = None


@attr.s(auto_attribs=True)
class ShippingOption(BaseTelegram):
    id: str
    title: str
    prices: Tuple[LabeledPrice, ...]


@attr.s(auto_attribs=True)
class SuccessfulPayment(BaseTelegram):
    currency: str
    total_amount: int
    invoice_payload: str
    telegram_payment_charge_id: str
    provider_payment_charge_id: str
    shipping_option_id: Optional[str] = None
    order_info: Optional[OrderInfo] = None


@attr.s(auto_attribs=True)
class ShippingQuery(BaseTelegram):
    id: str
    from_: User
    invoice_payload: str
    shipping_address: ShippingAddress


@attr.s(auto_attribs=True)
class PreCheckoutQuery(BaseTelegram):
    id: str
    from_: User
    currency: str
    total_amount: int
    invoice_payload: str
    shipping_option_id: Optional[str] = None
    order_info: Optional[OrderInfo] = None


@attr.s(auto_attribs=True)
class PassportData(BaseTelegram):
    data: Tuple['EncryptedPassportElement', ...]
    credentials: 'EncryptedCredentials'


@attr.s(auto_attribs=True)
class PassportFile(BaseTelegram):
    file_id: str
    file_unique_id: str
    file_date: int
    file_size: Optional[int] = None


@attr.s(auto_attribs=True)
class EncryptedPassportElement(BaseTelegram):
    type: str
    data: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    files: Optional[Tuple[PassportFile, ...]] = None
    front_side: Optional[PassportFile] = None
    reverse_side: Optional[PassportFile] = None
    selfie: Optional[PassportFile] = None
    translation: Optional[Tuple[PassportFile, ...]] = None
    hash: Optional[str] = None


@attr.s(auto_attribs=True)
class EncryptedCredentials(BaseTelegram):
    data: str
    hash: str
    secret: str


PassportElementError = Union['PassportElementErrorDataField',
                             'PassportElementErrorFrontSide',
                             'PassportElementErrorReverseSide',
                             'PassportElementErrorSelfie',
                             'PassportElementErrorFile',
                             'PassportElementErrorFiles',
                             'PassportElementErrorTranslationFile',
                             'PassportElementErrorTranslationFiles',
                             'PassportElementErrorUnspecified']


@attr.s(auto_attribs=True)
class PassportElementErrorDataField(BaseTelegram):
    source: str
    type: str
    field_name: str
    data_hash: str
    message: str


@attr.s(auto_attribs=True)
class PassportElementErrorFrontSide(BaseTelegram):
    source: str
    type: str
    file_hash: str
    message: str


@attr.s(auto_attribs=True)
class PassportElementErrorReverseSide(BaseTelegram):
    source: str
    type: str
    file_hash: str
    message: str


@attr.s(auto_attribs=True)
class PassportElementErrorSelfie(BaseTelegram):
    source: str
    type: str
    file_hash: str
    message: str


@attr.s(auto_attribs=True)
class PassportElementErrorFile(BaseTelegram):
    source: str
    type: str
    file_hash: str
    message: str


@attr.s(auto_attribs=True)
class PassportElementErrorFiles(BaseTelegram):
    source: str
    type: str
    file_hashes: List[str]
    message: str


@attr.s(auto_attribs=True)
class PassportElementErrorTranslationFile(BaseTelegram):
    source: str
    type: str
    file_hash: str
    message: str


@attr.s(auto_attribs=True)
class PassportElementErrorTranslationFiles(BaseTelegram):
    source: str
    type: str
    file_hashes: List[str]
    message: str


@attr.s(auto_attribs=True)
class PassportElementErrorUnspecified(BaseTelegram):
    source: str
    type: str
    element_hash: str
    message: str


@attr.s(auto_attribs=True)
class Game(BaseTelegram):
    title: str
    description: str
    photo: Tuple[PhotoSize, ...]
    text: Optional[str] = None
    text_entities: Optional[Tuple[MessageEntity, ...]] = None
    animation: Optional['Animation'] = None


@attr.s(auto_attribs=True)
class CallbackGame(BaseTelegram):
    pass


@attr.s(auto_attribs=True)
class GameHighScore(BaseTelegram):
    position: int
    user: User
    score: int
