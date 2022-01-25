import logging
from abc import ABC, abstractmethod
from enum import Enum
from itertools import count
from typing import Any, Dict, Final, Iterable, Optional, Tuple, Union

import attr

from .api_types import (APIResponse, BaseTelegram, BotCommand, BotCommandScope,
                        Chat, ChatInviteLink, ChatMember, ChatPermissions,
                        File, GameHighScore, InlineKeyboardMarkup,
                        InlineQueryResult, InputFile, InputMedia,
                        InputMediaAudio, InputMediaDocument, InputMediaPhoto,
                        InputMediaVideo, LabeledPrice, MaskPosition, Message,
                        MessageEntity, MessageId, PassportElementError, Poll,
                        ReplyMarkup, ShippingOption, StickerSet, Update, User,
                        UserProfilePhotos, WebhookInfo)
from .constants import (ChatAction, DiceEmoji, ParseMode, PollType,
                        RequestMethod, UpdateType)
from .helpers import json_dumps

__all__ = ('ParamType', 'ApiMethods')

api_logger: Final[logging.Logger] = logging.getLogger('aiotgbot.api')


_ItemType = Union[BaseTelegram, str, int, Enum]


def _unstructure_item(
    item: Union[BaseTelegram, str, int, Enum]
) -> Union[Dict[str, Any], str, int]:
    if isinstance(item, BaseTelegram):
        return item.to_dict()
    elif isinstance(item, Enum) and isinstance(item.value, str):
        return item.value
    elif isinstance(item, Enum):
        raise TypeError(f'Unsupported enum type: {item!r}')
    elif isinstance(item, (str, int)):
        return item
    else:
        raise TypeError(f'Unsupported item type: {item!r}')


def _json_dumps(
    value: Union[BaseTelegram, Iterable[_ItemType], None]
) -> Optional[str]:
    if value is None:
        return None
    elif isinstance(value, Iterable):
        return json_dumps(tuple(_unstructure_item(item) for item in value))
    elif isinstance(value, BaseTelegram):
        return json_dumps(value.to_dict())
    else:
        raise TypeError(f'Unsupported value type: {value!r}')


def _enum_to_str(item: Optional[Enum]) -> Optional[str]:
    assert item is None or isinstance(item.value, str)
    return item.value if item is not None else None


ParamType = Union[int, float, str, InputFile, None]


class ApiMethods(ABC):

    @abstractmethod
    async def _request(self, http_method: RequestMethod, api_method: str,
                       **params: ParamType) -> APIResponse: ...

    @abstractmethod
    async def _safe_request(
            self, http_method: RequestMethod, api_method: str,
            chat_id: Union[int, str], **params: ParamType
    ) -> APIResponse: ...

    async def get_updates(
        self, offset: Optional[int] = None,
        limit: Optional[int] = None,
        timeout: Optional[int] = None,
        allowed_updates: Optional[Iterable[UpdateType]] = None
    ) -> Tuple[Update, ...]:
        api_logger.debug(f'Get updates offset: {offset}, limit: {limit}, '
                         f'timeout: {timeout}, '
                         f'allowed_updates: {allowed_updates}')
        response = await self._request(
            RequestMethod.GET, 'getUpdates', offset=offset, limit=limit,
            timeout=timeout, allowed_updates=_json_dumps(allowed_updates))

        return tuple(Update.from_dict(item) for item in response.result)

    async def set_webhook(
        self, url: Optional[str] = None,
        certificate: Optional[InputFile] = None,
        ip_address: Optional[str] = None,
        max_connections: Optional[int] = None,
        allowed_updates: Optional[Iterable[UpdateType]] = None,
        drop_pending_updates: Optional[bool] = None
    ) -> bool:
        api_logger.debug('Set webhook')
        response = await self._request(
            RequestMethod.POST, 'setWebhook', url=url, certificate=certificate,
            ip_address=ip_address, max_connections=max_connections,
            allowed_updates=_json_dumps(allowed_updates),
            drop_pending_updates=drop_pending_updates)
        assert isinstance(response.result, bool)
        return response.result

    async def delete_webhook(
        self, drop_pending_updates: Optional[bool] = None
    ) -> bool:
        api_logger.debug('Delete webhook')
        response = await self._request(
            RequestMethod.POST, 'deleteWebhook',
            drop_pending_updates=drop_pending_updates)
        assert isinstance(response.result, bool)
        return response.result

    async def get_webhook_info(self) -> WebhookInfo:
        api_logger.debug('Get webhook info')
        response = await self._request(RequestMethod.GET, 'getWebhookInfo')

        return WebhookInfo.from_dict(response.result)

    async def get_me(self) -> User:
        api_logger.debug('Get me')
        response = await self._request(RequestMethod.GET, 'getMe')
        return User.from_dict(response.result)

    async def log_out(self) -> bool:
        api_logger.debug('Log out')
        response = await self._request(RequestMethod.POST, 'logOut')
        assert isinstance(response.result, bool)
        return response.result

    async def close(self) -> bool:
        api_logger.debug('Close')
        response = await self._request(RequestMethod.POST, 'close')
        assert isinstance(response.result, bool)
        return response.result

    async def send_message(
        self, chat_id: Union[int, str], text: str,
        parse_mode: Optional[ParseMode] = None,
        entities: Optional[Iterable[MessageEntity]] = None,
        disable_web_page_preview: Optional[bool] = None,
        disable_notification: Optional[bool] = None,
        protect_content: Optional[bool] = None,
        reply_to_message_id: Optional[int] = None,
        allow_sending_without_reply: Optional[bool] = None,
        reply_markup: Optional[ReplyMarkup] = None
    ) -> Message:
        api_logger.debug('Send message %r to chat "%s"', text, chat_id)
        response = await self._safe_request(
            RequestMethod.POST, 'sendMessage', chat_id, text=text,
            parse_mode=_enum_to_str(parse_mode),
            entities=_json_dumps(entities),
            disable_web_page_preview=disable_web_page_preview,
            disable_notification=disable_notification,
            protect_content=protect_content,
            reply_to_message_id=reply_to_message_id,
            allow_sending_without_reply=allow_sending_without_reply,
            reply_markup=_json_dumps(reply_markup))

        return Message.from_dict(response.result)

    async def forward_message(
        self, chat_id: Union[int, str], from_chat_id: Union[int, str],
        message_id: int, disable_notification: Optional[bool] = None,
        protect_content: Optional[bool] = None,
    ) -> Message:
        api_logger.debug('Forward message %s to "%s" from "%s"', message_id,
                         chat_id, from_chat_id)
        response = await self._safe_request(
            RequestMethod.POST, 'forwardMessage', chat_id,
            from_chat_id=from_chat_id, message_id=message_id,
            disable_notification=disable_notification,
            protect_content=protect_content)

        return Message.from_dict(response.result)

    async def copy_message(
        self, chat_id: Union[int, str], from_chat_id: Union[int, str],
        message_id: int, caption: Optional[str] = None,
        parse_mode: Optional[ParseMode] = None,
        caption_entities: Optional[Iterable[MessageEntity]] = None,
        disable_notification: Optional[bool] = None,
        protect_content: Optional[bool] = None,
        reply_to_message_id: Optional[int] = None,
        allow_sending_without_reply: Optional[bool] = None,
        reply_markup: Optional[ReplyMarkup] = None
    ) -> MessageId:
        api_logger.debug('Copy message %s to "%s" from "%s"', message_id,
                         chat_id, from_chat_id)
        response = await self._safe_request(
            RequestMethod.POST, 'copyMessage', chat_id,
            from_chat_id=from_chat_id, message_id=message_id,
            parse_mode=parse_mode,
            caption_entities=_json_dumps(caption_entities),
            caption=caption, disable_notification=disable_notification,
            protect_content=protect_content,
            reply_to_message_id=reply_to_message_id,
            allow_sending_without_reply=allow_sending_without_reply,
            reply_markup=_json_dumps(reply_markup))

        return MessageId.from_dict(response.result)

    async def send_photo(
        self, chat_id: Union[int, str],
        photo: Union[InputFile, str],
        caption: Optional[str] = None,
        parse_mode: Optional[ParseMode] = None,
        caption_entities: Optional[Iterable[MessageEntity]] = None,
        disable_notification: Optional[bool] = None,
        protect_content: Optional[bool] = None,
        reply_to_message_id: Optional[int] = None,
        allow_sending_without_reply: Optional[bool] = None,
        reply_markup: Optional[ReplyMarkup] = None
    ) -> Message:
        api_logger.debug('Send photo to "%s"', chat_id)
        response = await self._safe_request(
            RequestMethod.POST, 'sendPhoto', chat_id, photo=photo,
            caption=caption, parse_mode=_enum_to_str(parse_mode),
            caption_entities=_json_dumps(caption_entities),
            disable_notification=disable_notification,
            protect_content=protect_content,
            reply_to_message_id=reply_to_message_id,
            allow_sending_without_reply=allow_sending_without_reply,
            reply_markup=_json_dumps(reply_markup))

        return Message.from_dict(response.result)

    async def send_audio(
        self, chat_id: Union[int, str],
        audio: Union[InputFile, str],
        caption: Optional[str] = None,
        parse_mode: Optional[ParseMode] = None,
        caption_entities: Optional[Iterable[MessageEntity]] = None,
        disable_notification: Optional[bool] = None,
        protect_content: Optional[bool] = None,
        duration: Optional[int] = None,
        performer: Optional[str] = None,
        title: Optional[str] = None,
        thumb: Optional[Union[InputFile, str]] = None,
        reply_to_message_id: Optional[int] = None,
        allow_sending_without_reply: Optional[bool] = None,
        reply_markup: Optional[ReplyMarkup] = None
    ) -> Message:
        api_logger.debug('Send audio to "%s"', chat_id)
        response = await self._safe_request(
            RequestMethod.POST, 'sendAudio', chat_id, audio=audio,
            caption=caption, parse_mode=_enum_to_str(parse_mode),
            caption_entities=_json_dumps(caption_entities),
            disable_notification=disable_notification,
            protect_content=protect_content,
            duration=duration, performer=performer,
            title=title, thumb=thumb,
            reply_to_message_id=reply_to_message_id,
            allow_sending_without_reply=allow_sending_without_reply,
            reply_markup=_json_dumps(reply_markup))

        return Message.from_dict(response.result)

    async def send_document(
        self, chat_id: Union[int, str],
        document: Union[InputFile, str],
        thumb: Optional[Union[InputFile, str]],
        caption: Optional[str] = None,
        parse_mode: Optional[ParseMode] = None,
        caption_entities: Optional[Iterable[MessageEntity]] = None,
        disable_content_type_detection: Optional[bool] = None,
        disable_notification: Optional[bool] = None,
        protect_content: Optional[bool] = None,
        duration: Optional[int] = None,
        performer: Optional[str] = None,
        title: Optional[str] = None,
        reply_to_message_id: Optional[int] = None,
        allow_sending_without_reply: Optional[bool] = None,
        reply_markup: Optional[ReplyMarkup] = None
    ) -> Message:
        api_logger.debug('Send document to "%s"', chat_id)
        response = await self._safe_request(
            RequestMethod.POST, 'sendDocument', chat_id,
            document=document, thumb=thumb, caption=caption,
            parse_mode=_enum_to_str(parse_mode),
            caption_entities=_json_dumps(caption_entities),
            disable_content_type_detection=disable_content_type_detection,
            disable_notification=disable_notification,
            protect_content=protect_content,
            duration=duration, performer=performer, title=title,
            reply_to_message_id=reply_to_message_id,
            allow_sending_without_reply=allow_sending_without_reply,
            reply_markup=_json_dumps(reply_markup))

        return Message.from_dict(response.result)

    async def send_video(
        self, chat_id: Union[int, str],
        video: Union[InputFile, str],
        duration: Optional[int] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        thumb: Optional[Union[InputFile, str]] = None,
        caption: Optional[str] = None,
        parse_mode: Optional[ParseMode] = None,
        caption_entities: Optional[Iterable[MessageEntity]] = None,
        supports_streaming: Optional[bool] = None,
        disable_notification: Optional[bool] = None,
        protect_content: Optional[bool] = None,
        reply_to_message_id: Optional[int] = None,
        allow_sending_without_reply: Optional[bool] = None,
        reply_markup: Optional[ReplyMarkup] = None
    ) -> Message:
        api_logger.debug('Send video to "%s"', chat_id)
        response = await self._safe_request(
            RequestMethod.POST, 'sendVideo', chat_id,
            video=video, duration=duration, width=width,
            height=height, thumb=thumb, caption=caption,
            parse_mode=_enum_to_str(parse_mode),
            caption_entities=_json_dumps(caption_entities),
            supports_streaming=supports_streaming,
            disable_notification=disable_notification,
            protect_content=protect_content,
            reply_to_message_id=reply_to_message_id,
            allow_sending_without_reply=allow_sending_without_reply,
            reply_markup=_json_dumps(reply_markup))

        return Message.from_dict(response.result)

    async def send_animation(
        self, chat_id: Union[int, str],
        animation: Union[InputFile, str],
        duration: Optional[int] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        thumb: Optional[Union[InputFile, str]] = None,
        caption: Optional[str] = None,
        parse_mode: Optional[ParseMode] = None,
        caption_entities: Optional[Iterable[MessageEntity]] = None,
        disable_notification: Optional[bool] = None,
        protect_content: Optional[bool] = None,
        reply_to_message_id: Optional[int] = None,
        allow_sending_without_reply: Optional[bool] = None,
        reply_markup: Optional[ReplyMarkup] = None
    ) -> Message:
        api_logger.debug('Send animation to "%s"', chat_id)
        response = await self._safe_request(
            RequestMethod.POST, 'sendAnimation', chat_id,
            animation=animation, duration=duration, width=width,
            height=height, thumb=thumb, caption=caption,
            parse_mode=_enum_to_str(parse_mode),
            caption_entities=_json_dumps(caption_entities),
            disable_notification=disable_notification,
            protect_content=protect_content,
            reply_to_message_id=reply_to_message_id,
            allow_sending_without_reply=allow_sending_without_reply,
            reply_markup=_json_dumps(reply_markup))

        return Message.from_dict(response.result)

    async def send_voice(
        self, chat_id: Union[int, str],
        voice: Union[InputFile, str],
        caption: Optional[str] = None,
        parse_mode: Optional[ParseMode] = None,
        caption_entities: Optional[Iterable[MessageEntity]] = None,
        duration: Optional[int] = None,
        disable_notification: Optional[bool] = None,
        protect_content: Optional[bool] = None,
        reply_to_message_id: Optional[int] = None,
        allow_sending_without_reply: Optional[bool] = None,
        reply_markup: Optional[ReplyMarkup] = None
    ) -> Message:
        api_logger.debug('Send voice to "%s"', chat_id)
        response = await self._safe_request(
            RequestMethod.POST, 'sendVoice', chat_id,
            voice=voice, caption=caption,
            parse_mode=_enum_to_str(parse_mode),
            caption_entities=_json_dumps(caption_entities),
            duration=duration,
            disable_notification=disable_notification,
            protect_content=protect_content,
            reply_to_message_id=reply_to_message_id,
            allow_sending_without_reply=allow_sending_without_reply,
            reply_markup=_json_dumps(reply_markup))

        return Message.from_dict(response.result)

    async def send_video_note(
        self, chat_id: Union[int, str],
        video_note: Union[InputFile, str],
        duration: Optional[int] = None,
        length: Optional[int] = None,
        thumb: Optional[Union[InputFile, str]] = None,
        disable_notification: Optional[bool] = None,
        protect_content: Optional[bool] = None,
        reply_to_message_id: Optional[int] = None,
        allow_sending_without_reply: Optional[bool] = None,
        reply_markup: Optional[ReplyMarkup] = None
    ) -> Message:
        api_logger.debug('Send video not to "%s"', chat_id)
        response = await self._safe_request(
            RequestMethod.POST, 'sendVideoNote', chat_id,
            video_note=video_note, duration=duration,
            length=length, thumb=thumb,
            disable_notification=disable_notification,
            protect_content=protect_content,
            reply_to_message_id=reply_to_message_id,
            allow_sending_without_reply=allow_sending_without_reply,
            reply_markup=_json_dumps(reply_markup))

        return Message.from_dict(response.result)

    async def send_media_group(
        self, chat_id: Union[int, str],
        media: Iterable[Union[InputMediaAudio, InputMediaDocument,
                              InputMediaPhoto, InputMediaVideo]],
        disable_notification: Optional[bool] = None,
        protect_content: Optional[bool] = None,
        reply_to_message_id: Optional[int] = None,
        allow_sending_without_reply: Optional[bool] = None
    ) -> Tuple[Message, ...]:
        api_logger.debug('Send media group to "%s"', chat_id)
        attached_media = []
        attachments = {}
        counter = count()
        for item in media:
            if isinstance(item.media, str):
                attached_media.append(item)
            else:
                attachment_name = f'attachment{next(counter)}'
                attachments[attachment_name] = item.media
                attached_media.append(attr.evolve(
                    item, media=f'attach://{attachment_name}'))
        response = await self._safe_request(
            RequestMethod.POST, 'sendMediaGroup', chat_id,
            media=_json_dumps(attached_media),
            disable_notification=disable_notification,
            protect_content=protect_content,
            reply_to_message_id=reply_to_message_id,
            allow_sending_without_reply=allow_sending_without_reply,
            **attachments
        )

        return tuple(Message.from_dict(item) for item in response.result)

    async def send_location(
        self, chat_id: Union[int, str],
        latitude: float,
        longitude: float,
        horizontal_accuracy: Optional[float] = None,
        live_period: Optional[int] = None,
        heading: Optional[int] = None,
        proximity_alert_radius: Optional[int] = None,
        length: Optional[int] = None,
        disable_notification: Optional[bool] = None,
        protect_content: Optional[bool] = None,
        reply_to_message_id: Optional[int] = None,
        allow_sending_without_reply: Optional[bool] = None,
        reply_markup: Optional[ReplyMarkup] = None
    ) -> Message:
        api_logger.debug('Send location to "%s"', chat_id)
        response = await self._safe_request(
            RequestMethod.POST, 'sendLocation', chat_id,
            latitude=latitude, longitude=longitude,
            horizontal_accuracy=horizontal_accuracy,
            live_period=live_period, heading=heading,
            proximity_alert_radius=proximity_alert_radius, length=length,
            disable_notification=disable_notification,
            protect_content=protect_content,
            reply_to_message_id=reply_to_message_id,
            allow_sending_without_reply=allow_sending_without_reply,
            reply_markup=_json_dumps(reply_markup))

        return Message.from_dict(response.result)

    async def edit_message_live_location(
        self,
        latitude: float,
        longitude: float,
        horizontal_accuracy: Optional[float] = None,
        heading: Optional[int] = None,
        proximity_alert_radius: Optional[int] = None,
        chat_id: Optional[Union[int, str]] = None,
        message_id: Optional[int] = None,
        inline_message_id: Optional[str] = None,
        reply_markup: Optional[ReplyMarkup] = None
    ) -> Union[Message, bool]:
        api_logger.debug('Edit live location %s in "%s"', message_id, chat_id)
        response = await self._request(
            RequestMethod.POST, 'editMessageLiveLocation',
            chat_id=chat_id, message_id=message_id,
            inline_message_id=inline_message_id,
            latitude=latitude, longitude=longitude,
            horizontal_accuracy=horizontal_accuracy, heading=heading,
            proximity_alert_radius=proximity_alert_radius,
            reply_markup=_json_dumps(reply_markup))

        if isinstance(response.result, bool):
            return response.result
        else:
            return Message.from_dict(response.result)

    async def stop_message_live_location(
        self, chat_id: Optional[Union[int, str]] = None,
        message_id: Optional[int] = None,
        inline_message_id: Optional[str] = None,
        reply_markup: Optional[ReplyMarkup] = None
    ) -> Union[Message, bool]:
        api_logger.debug('Stop live location %s in "%s"', message_id, chat_id)
        response = await self._request(
            RequestMethod.POST, 'stopMessageLiveLocation',
            chat_id=chat_id, message_id=message_id,
            inline_message_id=inline_message_id,
            reply_markup=_json_dumps(reply_markup))

        if isinstance(response.result, bool):
            return response.result
        else:
            return Message.from_dict(response.result)

    async def send_venue(
        self, chat_id: Union[int, str],
        latitude: float,
        longitude: float,
        title: str,
        address: str,
        foursquare_id: Optional[str] = None,
        foursquare_type: Optional[str] = None,
        disable_notification: Optional[bool] = None,
        protect_content: Optional[bool] = None,
        reply_to_message_id: Optional[int] = None,
        allow_sending_without_reply: Optional[bool] = None,
        reply_markup: Optional[ReplyMarkup] = None
    ) -> Message:
        api_logger.debug('Send venue to "%s"', chat_id)
        response = await self._safe_request(
            RequestMethod.POST, 'sendVenue', chat_id,
            latitude=latitude, longitude=longitude, title=title,
            address=address, foursquare_id=foursquare_id,
            foursquare_type=foursquare_type,
            disable_notification=disable_notification,
            protect_content=protect_content,
            reply_to_message_id=reply_to_message_id,
            allow_sending_without_reply=allow_sending_without_reply,
            reply_markup=_json_dumps(reply_markup))

        return Message.from_dict(response.result)

    async def send_contact(
        self, chat_id: Union[int, str],
        phone_number: str,
        first_name: str,
        last_name: Optional[str] = None,
        vcard: Optional[str] = None,
        disable_notification: Optional[bool] = None,
        protect_content: Optional[bool] = None,
        reply_to_message_id: Optional[int] = None,
        allow_sending_without_reply: Optional[bool] = None,
        reply_markup: Optional[ReplyMarkup] = None
    ) -> Message:
        api_logger.debug('Send contact to "%s"', chat_id)
        response = await self._safe_request(
            RequestMethod.POST, 'sendContact', chat_id,
            phone_number=phone_number, first_name=first_name,
            last_name=last_name, vcard=vcard,
            disable_notification=disable_notification,
            protect_content=protect_content,
            reply_to_message_id=reply_to_message_id,
            allow_sending_without_reply=allow_sending_without_reply,
            reply_markup=_json_dumps(reply_markup))

        return Message.from_dict(response.result)

    async def send_poll(
        self, chat_id: Union[int, str], question: str,
        options: Iterable[str], is_anonymous: Optional[bool] = None,
        type_: Optional[PollType] = None,
        allows_multiple_answers: Optional[bool] = None,
        correct_option_id: Optional[int] = None,
        is_closed: Optional[bool] = None,
        explanation: Optional[str] = None,
        explanation_parse_mode: Optional[ParseMode] = None,
        explanation_entities: Optional[Iterable[MessageEntity]] = None,
        open_period: Optional[int] = None,
        close_date: Optional[int] = None,
        disable_notification: Optional[bool] = None,
        protect_content: Optional[bool] = None,
        reply_to_message_id: Optional[int] = None,
        allow_sending_without_reply: Optional[bool] = None,
        reply_markup: Optional[ReplyMarkup] = None
    ) -> Message:
        api_logger.debug('Send poll to chat "%s"', chat_id)
        response = await self._safe_request(
            RequestMethod.POST, 'sendPoll', chat_id,
            question=question, options=_json_dumps(options),
            is_anonymous=is_anonymous, type=type_,
            allows_multiple_answers=allows_multiple_answers,
            correct_option_id=correct_option_id,
            is_closed=is_closed, explanation=explanation,
            explanation_parse_mode=explanation_parse_mode,
            explanation_entities=_json_dumps(explanation_entities),
            open_period=open_period, close_date=close_date,
            disable_notification=disable_notification,
            protect_content=protect_content,
            reply_to_message_id=reply_to_message_id,
            allow_sending_without_reply=allow_sending_without_reply,
            reply_markup=_json_dumps(reply_markup))

        return Message.from_dict(response.result)

    async def send_dice(self, chat_id: Union[int, str],
                        emoji: Optional[DiceEmoji] = None,
                        disable_notification: Optional[bool] = None,
                        protect_content: Optional[bool] = None,
                        reply_to_message_id: Optional[int] = None,
                        allow_sending_without_reply: Optional[bool] = None,
                        reply_markup: Optional[ReplyMarkup] = None) -> Message:
        api_logger.debug('Send dice "%s" to chat "%s"', emoji, chat_id)
        response = await self._safe_request(
            RequestMethod.POST, 'sendDice', chat_id,
            emoji=_enum_to_str(emoji),
            disable_notification=disable_notification,
            protect_content=protect_content,
            reply_to_message_id=reply_to_message_id,
            allow_sending_without_reply=allow_sending_without_reply,
            reply_markup=_json_dumps(reply_markup))

        return Message.from_dict(response.result)

    async def send_chat_action(self, chat_id: Union[int, str],
                               action: ChatAction) -> bool:
        api_logger.debug('Send action "%s" to chat "%s"', action, chat_id)
        response = await self._safe_request(
            RequestMethod.POST, 'sendChatAction', chat_id, action=action.value)
        assert isinstance(response.result, bool)
        return response.result

    async def get_user_profile_photos(
        self, user_id: int,
        offset: Optional[int] = None,
        limit: Optional[int] = None
    ) -> UserProfilePhotos:
        api_logger.debug('Get user profile photos %s offset %s limit %s',
                         user_id, offset, limit)
        response = await self._request(
            RequestMethod.GET, 'getUserProfilePhotos',
            user_id=user_id, offset=offset, limit=limit)

        return UserProfilePhotos.from_dict(response.result)

    async def get_file(self, file_id: str) -> File:
        api_logger.debug('Get file "%s"', file_id)
        response = await self._request(RequestMethod.GET, 'getFile',
                                       file_id=file_id)
        return File.from_dict(response.result)

    async def ban_chat_member(self, chat_id: Union[int, str], user_id: int,
                              until_date: Optional[int] = None,
                              revoke_messages: Optional[bool] = None) -> bool:
        response = await self._request(
            RequestMethod.POST, 'banChatMember',
            chat_id=chat_id, user_id=user_id, until_date=until_date,
            revoke_messages=revoke_messages)
        assert isinstance(response.result, bool)
        return response.result

    async def unban_chat_member(self, chat_id: Union[int, str], user_id: int,
                                only_if_banned: Optional[bool] = None) -> bool:
        api_logger.debug('Unban member %s in "%s"', user_id, chat_id)
        response = await self._request(RequestMethod.POST, 'unbanChatMember',
                                       chat_id=chat_id, user_id=user_id,
                                       only_if_banned=only_if_banned)
        assert isinstance(response.result, bool)
        return response.result

    async def restrict_chat_member(
        self, chat_id: Union[int, str],
        user_id: int,
        permissions: ChatPermissions,
        until_date: Optional[int] = None,
    ) -> bool:
        api_logger.debug('Restrict member %s in "%s"', user_id, chat_id)
        response = await self._request(
            RequestMethod.POST, 'restrictChatMember', chat_id=chat_id,
            user_id=user_id, permissions=_json_dumps(permissions),
            until_date=until_date)
        assert isinstance(response.result, bool)
        return response.result

    async def promote_chat_member(
        self, chat_id: Union[int, str],
        user_id: int,
        is_anonymous: Optional[int] = None,
        can_manage_chat: Optional[int] = None,
        can_change_info: Optional[int] = None,
        can_post_messages: Optional[bool] = None,
        can_edit_messages: Optional[bool] = None,
        can_delete_messages: Optional[bool] = None,
        can_manage_voice_chats: Optional[bool] = None,
        can_invite_users: Optional[bool] = None,
        can_restrict_members: Optional[bool] = None,
        can_pin_messages: Optional[bool] = None,
        can_promote_members: Optional[bool] = None
    ) -> bool:
        api_logger.debug('Promote member %s in "%s"', user_id, chat_id)
        response = await self._request(
            RequestMethod.POST, 'promoteChatMember',
            chat_id=chat_id, user_id=user_id, is_anonymous=is_anonymous,
            can_manage_chat=can_manage_chat,
            can_change_info=can_change_info,
            can_post_messages=can_post_messages,
            can_edit_messages=can_edit_messages,
            can_delete_messages=can_delete_messages,
            can_manage_voice_chats=can_manage_voice_chats,
            can_invite_users=can_invite_users,
            can_restrict_members=can_restrict_members,
            can_pin_messages=can_pin_messages,
            can_promote_members=can_promote_members)
        assert isinstance(response.result, bool)
        return response.result

    async def set_chat_administrator_custom_title(
        self, chat_id: Union[int, str],
        user_id: int,
        custom_title: str
    ) -> bool:
        api_logger.debug('Set title "%s" for admin %s in "%s"',
                         custom_title, user_id, chat_id)
        response = await self._request(
            RequestMethod.POST, 'setChatAdministratorCustomTitle',
            chat_id=chat_id, user_id=user_id, custom_title=custom_title)
        assert isinstance(response.result, bool)
        return response.result

    async def ban_chat_sender_chat(
        self, chat_id: Union[int, str],
        sender_chat_id: int,
        until_date: Optional[int]
    ) -> bool:
        api_logger.debug('Ban chat "%s" sender chat "%s"',
                         chat_id, sender_chat_id)
        response = await self._request(
            RequestMethod.POST, 'banChatSenderChat',
            chat_id=chat_id, sender_chat_id=sender_chat_id,
            until_date=until_date)
        assert isinstance(response.result, bool)
        return response.result

    async def unban_chat_sender_chat(
        self, chat_id: Union[int, str],
        sender_chat_id: int
    ) -> bool:
        api_logger.debug('Unban chat "%s" sender chat "%s"',
                         chat_id, sender_chat_id)
        response = await self._request(
            RequestMethod.POST, 'unbanChatSenderChat',
            chat_id=chat_id, sender_chat_id=sender_chat_id)
        assert isinstance(response.result, bool)
        return response.result

    async def export_chat_invite_link(self, chat_id: Union[int, str]) -> str:
        api_logger.debug('Export chat "%s" invite link', chat_id)
        response = await self._request(
            RequestMethod.POST, 'exportChatInviteLink', chat_id=chat_id)
        assert isinstance(response.result, str)
        return response.result

    async def create_chat_invite_link(
        self, chat_id: Union[int, str], name: Optional[str] = None,
        expire_date: Optional[int] = None,
        member_limit: Optional[int] = None,
        creates_join_request: Optional[bool] = None
    ) -> ChatInviteLink:
        api_logger.debug('Create chat "%s" invite link', chat_id)
        response = await self._request(
            RequestMethod.POST, 'createChatInviteLink', chat_id=chat_id,
            name=name, expire_date=expire_date, member_limit=member_limit,
            creates_join_request=creates_join_request)
        return ChatInviteLink.from_dict(response.result)

    async def edit_chat_invite_link(
        self, chat_id: Union[int, str], invite_link: str,
        name: Optional[str] = None,
        expire_date: Optional[int] = None,
        member_limit: Optional[int] = None,
        creates_join_request: Optional[bool] = None
    ) -> ChatInviteLink:
        api_logger.debug('Edit chat "%s" invite link', chat_id)
        response = await self._request(
            RequestMethod.POST, 'editChatInviteLink', chat_id=chat_id,
            invite_link=invite_link, name=name, expire_date=expire_date,
            member_limit=member_limit,
            creates_join_request=creates_join_request)
        return ChatInviteLink.from_dict(response.result)

    async def revoke_chat_invite_link(
        self, chat_id: Union[int, str], invite_link: str
    ) -> ChatInviteLink:
        api_logger.debug('Revoke chat "%s" invite link', chat_id)
        response = await self._request(
            RequestMethod.POST, 'revokeChatInviteLink', chat_id=chat_id,
            invite_link=invite_link)
        return ChatInviteLink.from_dict(response.result)

    async def approve_chat_join_request(
        self, chat_id: Union[int, str], user_id: int
    ) -> bool:
        api_logger.debug('Approve "%s" chat "%s" join request', chat_id,
                         user_id)
        response = await self._request(
            RequestMethod.POST, 'approveChatJoinRequest', chat_id=chat_id,
            user_id=user_id)
        assert isinstance(response.result, bool)
        return response.result

    async def decline_chat_join_request(
        self, chat_id: Union[int, str], user_id: int
    ) -> bool:
        api_logger.debug('Decline "%s" chat "%s" join request', chat_id,
                         user_id)
        response = await self._request(
            RequestMethod.POST, 'declineChatJoinRequest', chat_id=chat_id,
            user_id=user_id)
        assert isinstance(response.result, bool)
        return response.result

    async def set_chat_permissions(
        self, chat_id: Union[int, str],
        permissions: ChatPermissions
    ) -> bool:
        api_logger.debug('Set chat "%s" permissions', chat_id)
        response = await self._safe_request(
            RequestMethod.POST, 'setChatPermissions', chat_id,
            permissions=_json_dumps(permissions))
        assert isinstance(response.result, bool)
        return response.result

    async def set_chat_photo(
        self, chat_id: Union[int, str],
        photo: InputFile
    ) -> bool:
        api_logger.debug('Set chat "%s" photo', chat_id)
        response = await self._safe_request(RequestMethod.POST, 'setChatPhoto',
                                            chat_id, photo=photo)
        assert isinstance(response.result, bool)
        return response.result

    async def delete_chat_photo(self, chat_id: Union[int, str]) -> bool:
        api_logger.debug('Delete chat "%s" photo', chat_id)
        response = await self._request(RequestMethod.POST, 'deleteChatPhoto',
                                       chat_id=chat_id)
        assert isinstance(response.result, bool)
        return response.result

    async def set_chat_title(self, chat_id: Union[int, str],
                             title: str) -> bool:
        api_logger.debug('Set title "%s" for chat "%s"', title, chat_id)
        response = await self._request(RequestMethod.POST, 'setChatTitle',
                                       chat_id=chat_id, title=title)
        assert isinstance(response.result, bool)
        return response.result

    async def set_chat_description(self, chat_id: Union[int, str],
                                   description: str) -> bool:
        api_logger.debug('Set chat "%s" description', chat_id)
        response = await self._request(
            RequestMethod.POST, 'setChatDescription', chat_id=chat_id,
            description=description)
        assert isinstance(response.result, bool)
        return response.result

    async def pin_chat_message(
        self, chat_id: Union[int, str], message_id: int,
        disable_notification: Optional[bool] = None
    ) -> bool:
        api_logger.debug('Pin message %s in chat "%s"', message_id, chat_id)
        response = await self._request(
            RequestMethod.POST, 'pinChatMessage',
            chat_id=chat_id, message_id=message_id,
            disable_notification=disable_notification)
        assert isinstance(response.result, bool)
        return response.result

    async def unpin_chat_message(self, chat_id: Union[int, str],
                                 message_id: Optional[int]) -> bool:
        api_logger.debug('Unpin message "%s" in chat "%s"',
                         message_id, chat_id)
        response = await self._request(RequestMethod.POST, 'unpinChatMessage',
                                       chat_id=chat_id, message_id=message_id)
        assert isinstance(response.result, bool)
        return response.result

    async def unpin_all_chat_messages(self, chat_id: Union[int, str]) -> bool:
        api_logger.debug('Unpin all messages in chat "%s"', chat_id)
        response = await self._request(RequestMethod.POST,
                                       'unpinAllChatMessages', chat_id=chat_id)
        assert isinstance(response.result, bool)
        return response.result

    async def leave_chat(self, chat_id: Union[int, str]) -> bool:
        api_logger.debug('Leave chat "%s"', chat_id)
        response = await self._request(RequestMethod.POST, 'leaveChat',
                                       chat_id=chat_id)
        assert isinstance(response.result, bool)
        return response.result

    async def get_chat(self, chat_id: Union[int, str]) -> Chat:
        api_logger.debug('Get chat "%s"', chat_id)
        response = await self._request(RequestMethod.GET, 'getChat',
                                       chat_id=chat_id)
        return Chat.from_dict(response.result)

    async def get_chat_administrators(
        self, chat_id: Union[int, str]
    ) -> Tuple[ChatMember, ...]:
        api_logger.debug('Get chat administrators "%s"', chat_id)
        response = await self._request(
            RequestMethod.GET, 'getChatAdministrators', chat_id=chat_id)

        return tuple(ChatMember.from_dict(item) for item in response.result)

    async def get_chat_member_count(self, chat_id: Union[int, str]) -> int:
        api_logger.debug('Get chat member count "%s"', chat_id)
        response = await self._request(
            RequestMethod.GET, 'getChatMemberCount', chat_id=chat_id)
        assert isinstance(response.result, int)
        return response.result

    async def get_chat_member(self, chat_id: Union[int, str],
                              user_id: int) -> ChatMember:
        api_logger.debug('Get chat "%s" member %s', chat_id, user_id)
        response = await self._request(RequestMethod.GET, 'getChatMember',
                                       chat_id=chat_id, user_id=user_id)

        return ChatMember.from_dict(response.result)

    async def set_chat_sticker_set(self, chat_id: Union[int, str],
                                   sticker_set_name: str) -> bool:
        api_logger.debug('Set chat "%s" sticker set "%s"', chat_id,
                         sticker_set_name)
        response = await self._request(
            RequestMethod.POST, 'setChatStickerSet', chat_id=chat_id,
            sticker_set_name=sticker_set_name)
        assert isinstance(response.result, bool)
        return response.result

    async def delete_chat_sticker_set(self, chat_id: Union[int, str]) -> bool:
        api_logger.debug('Delete chat "%s" sticker set', chat_id)
        response = await self._request(RequestMethod.POST,
                                       'deleteChatStickerSet', chat_id=chat_id)
        assert isinstance(response.result, bool)
        return response.result

    async def answer_callback_query(self, callback_query_id: str,
                                    text: Optional[str] = None,
                                    show_alert: Optional[bool] = None,
                                    url: Optional[str] = None,
                                    cache_time: Optional[int] = None) -> bool:
        api_logger.debug('Answer callback query "%s"', callback_query_id)
        response = await self._request(
            RequestMethod.POST, 'answerCallbackQuery',
            callback_query_id=callback_query_id, text=text,
            show_alert=show_alert, url=url, cache_time=cache_time)
        assert isinstance(response.result, bool)
        return response.result

    async def set_my_commands(self, commands: Iterable[BotCommand],
                              scope: Optional[BotCommandScope] = None,
                              language_code: Optional[str] = None) -> bool:
        api_logger.debug('Set my commands "%s"', commands)
        response = await self._request(
            RequestMethod.POST, 'setMyCommands',
            commands=_json_dumps(commands), scope=_json_dumps(scope),
            language_code=language_code)
        assert isinstance(response.result, bool)
        return response.result

    async def get_my_commands(
        self, scope: Optional[BotCommandScope] = None,
        language_code: Optional[str] = None
    ) -> Tuple[BotCommand, ...]:
        api_logger.debug('Get my commands')
        response = await self._request(
            RequestMethod.GET, 'getMyCommands', scope=_json_dumps(scope),
            language_code=language_code)

        return tuple(BotCommand.from_dict(item) for item in response.result)

    async def delete_my_commands(
        self, scope: Optional[BotCommandScope] = None,
        language_code: Optional[str] = None
    ) -> bool:
        api_logger.debug('Delete my commands')
        response = await self._request(
            RequestMethod.GET, 'deleteMyCommands', scope=_json_dumps(scope),
            language_code=language_code)
        assert isinstance(response.result, bool)
        return response.result

    async def edit_message_text(
        self,
        text: str,
        chat_id: Optional[Union[int, str]] = None,
        message_id: Optional[int] = None,
        inline_message_id: Optional[str] = None,
        parse_mode: Optional[ParseMode] = None,
        entities: Optional[Iterable[MessageEntity]] = None,
        disable_web_page_preview: Optional[bool] = None,
        reply_markup: Optional[InlineKeyboardMarkup] = None
    ) -> Union[Message, bool]:
        if (
            (chat_id is None or message_id is None) and
            inline_message_id is None
        ):
            raise RuntimeError('chat_id or message_id and '
                               'inline_message_id is None')
        if inline_message_id is None:
            api_logger.debug('Edit message %s in "%s" text',
                             message_id, chat_id)
        else:
            api_logger.debug('Edit inline message "%s" text',
                             inline_message_id)
        response = await self._request(
            RequestMethod.POST, 'editMessageText',
            chat_id=chat_id, message_id=message_id,
            inline_message_id=inline_message_id, text=text,
            parse_mode=_enum_to_str(parse_mode),
            entities=_json_dumps(entities),
            disable_web_page_preview=disable_web_page_preview,
            reply_markup=_json_dumps(reply_markup))

        if isinstance(response.result, bool):
            return response.result
        else:
            return Message.from_dict(response.result)

    async def edit_message_caption(
        self,
        chat_id: Optional[Union[int, str]] = None,
        message_id: Optional[int] = None,
        inline_message_id: Optional[str] = None,
        caption: Optional[str] = None,
        parse_mode: Optional[ParseMode] = None,
        caption_entities: Optional[Iterable[MessageEntity]] = None,
        reply_markup: Optional[InlineKeyboardMarkup] = None
    ) -> Union[Message, bool]:
        if (
            (chat_id is None or message_id is None) and
            inline_message_id is None
        ):
            raise RuntimeError('chat_id or message_id and '
                               'inline_message_id is None')
        if inline_message_id is None:
            api_logger.debug('Edit message %s in "%s" caption',
                             message_id, chat_id)
        else:
            api_logger.debug('Edit inline message "%s" caption',
                             inline_message_id)
        response = await self._request(
            RequestMethod.POST, 'editMessageCaption',
            chat_id=chat_id, message_id=message_id,
            inline_message_id=inline_message_id,
            caption=caption, parse_mode=_enum_to_str(parse_mode),
            caption_entities=_json_dumps(caption_entities),
            reply_markup=_json_dumps(reply_markup))

        if isinstance(response.result, bool):
            return response.result
        else:
            return Message.from_dict(response.result)

    async def edit_message_media(
        self, media: InputMedia,
        chat_id: Optional[Union[int, str]] = None,
        message_id: Optional[int] = None,
        inline_message_id: Optional[str] = None,
        reply_markup: Optional[InlineKeyboardMarkup] = None
    ) -> Union[Message, bool]:
        if (
            (chat_id is None or message_id is None) and
            inline_message_id is None
        ):
            raise RuntimeError('chat_id or message_id and '
                               'inline_message_id is None')
        if inline_message_id is None:
            api_logger.debug('Edit message %s in "%s" media',
                             message_id, chat_id)
        else:
            api_logger.debug('Edit inline message "%s" media',
                             inline_message_id)
        attachments = {}
        if not isinstance(media.media, str):
            attachment_name = 'attachment0'
            attachments[attachment_name] = media.media
            media = attr.evolve(media, media=f'attach://{attachment_name}')
        response = await self._request(
            RequestMethod.POST, 'editMessageMedia', chat_id=chat_id,
            message_id=message_id, inline_message_id=inline_message_id,
            media=_json_dumps(media), reply_markup=_json_dumps(reply_markup),
            **attachments)
        if isinstance(response.result, bool):
            return response.result
        else:
            return Message.from_dict(response.result)

    async def edit_message_reply_markup(
        self, chat_id: Optional[Union[int, str]] = None,
        message_id: Optional[int] = None,
        inline_message_id: Optional[str] = None,
        reply_markup: Optional[InlineKeyboardMarkup] = None
    ) -> Union[Message, bool]:
        if (
            (chat_id is None or message_id is None) and
            inline_message_id is None
        ):
            raise RuntimeError('chat_id or message_id and '
                               'inline_message_id is None')
        if inline_message_id is None:
            api_logger.debug('Edit message %s in "%s" reply markup',
                             message_id, chat_id)
        else:
            api_logger.debug('Edit inline message "%s" reply markup',
                             inline_message_id)
        response = await self._request(
            RequestMethod.POST, 'editMessageReplyMarkup',
            chat_id=chat_id, message_id=message_id,
            inline_message_id=inline_message_id,
            reply_markup=_json_dumps(reply_markup))

        if isinstance(response.result, bool):
            return response.result
        else:
            return Message.from_dict(response.result)

    async def stop_poll(
        self, chat_id: Union[int, str], message_id: int,
        reply_markup: Optional[InlineKeyboardMarkup] = None
    ) -> Poll:
        api_logger.debug('Stop poll %s in "%s"', message_id, chat_id)
        response = await self._request(
            RequestMethod.POST, 'stopPoll',
            chat_id=chat_id, message_id=message_id,
            reply_markup=_json_dumps(reply_markup))

        return Poll.from_dict(response.result)

    async def delete_message(self, chat_id: Optional[Union[int, str]] = None,
                             message_id: Optional[int] = None) -> bool:
        api_logger.debug('Delete message %s in "%s"', message_id, chat_id)
        response = await self._request(RequestMethod.POST, 'deleteMessage',
                                       chat_id=chat_id, message_id=message_id)
        assert isinstance(response.result, bool)
        return response.result

    async def send_sticker(
        self, chat_id: Union[int, str],
        sticker: Union[InputFile, str],
        disable_notification: Optional[bool] = None,
        protect_content: Optional[bool] = None,
        reply_to_message_id: Optional[int] = None,
        allow_sending_without_reply: Optional[bool] = None,
        reply_markup: Optional[ReplyMarkup] = None
    ) -> Message:
        api_logger.debug('Send sticker to "%s"', chat_id)
        response = await self._request(
            RequestMethod.POST, 'sendSticker',
            chat_id=chat_id, sticker=sticker,
            disable_notification=disable_notification,
            protect_content=protect_content,
            reply_to_message_id=reply_to_message_id,
            allow_sending_without_reply=allow_sending_without_reply,
            reply_markup=_json_dumps(reply_markup))

        return Message.from_dict(response.result)

    async def get_sticker_set(self, name: str) -> StickerSet:
        api_logger.debug('Get sticker set "%s"', name)
        response = await self._request(RequestMethod.GET, 'getStickerSet',
                                       name=name)

        return StickerSet.from_dict(response.result)

    async def upload_sticker_file(self, user_id: int,
                                  png_sticker: InputFile) -> File:
        api_logger.debug('Upload sticker file for %s', user_id)
        response = await self._request(
            RequestMethod.POST, 'uploadStickerFile',
            user_id=user_id, png_sticker=png_sticker)

        return File.from_dict(response.result)

    async def create_new_sticker_set(
        self, user_id: int, name: str, title: str, emojis: str,
        png_sticker: Union[InputFile, str, None] = None,
        tgs_sticker: Optional[InputFile] = None,
        contains_masks: Optional[bool] = None,
        mask_position: Optional[MaskPosition] = None
    ) -> bool:
        api_logger.debug('Create new sticker set "%s" for %s', name, user_id)
        response = await self._request(
            RequestMethod.POST, 'createNewStickerSet',
            user_id=user_id, name=name, title=title, emojis=emojis,
            png_sticker=png_sticker, tgs_sticker=tgs_sticker,
            contains_masks=contains_masks,
            mask_position=_json_dumps(mask_position))
        assert isinstance(response.result, bool)
        return response.result

    async def add_sticker_to_set(
        self, user_id: int, name: str, title: str,
        png_sticker: Union[InputFile, str], emojis: str,
        mask_position: Optional[MaskPosition] = None
    ) -> File:
        api_logger.debug('Add sticker to set "%s" for %s', name, user_id)
        response = await self._request(
            RequestMethod.POST, 'addStickerToSet',
            user_id=user_id, name=name, title=title, png_sticker=png_sticker,
            emojis=emojis, mask_position=_json_dumps(mask_position))

        return File.from_dict(response.result)

    async def set_sticker_position_in_set(self, sticker: str,
                                          position: int) -> bool:
        api_logger.debug('Set sticker "%s" position to %s', sticker, position)
        response = await self._request(
            RequestMethod.POST, 'setStickerPositionInSet',
            sticker=sticker, position=position)
        assert isinstance(response.result, bool)
        return response.result

    async def delete_sticker_from_set(self, sticker: str) -> bool:
        api_logger.debug('Delete sticker "%s" from set', sticker)
        response = await self._request(
            RequestMethod.POST, 'deleteStickerFromSet', sticker=sticker)
        assert isinstance(response.result, bool)
        return response.result

    async def set_sticker_set_thumb(
            self, name: str, user_id: int,
            thumb: Union[InputFile, str, None] = None
    ) -> bool:
        api_logger.debug('Set sticker set "%s" owned by "%s" thumb',
                         name, user_id)
        response = await self._request(
            RequestMethod.POST, 'setStickerSetThumb',
            name=name, user_id=user_id, thumb=thumb)
        assert isinstance(response.result, bool)
        return response.result

    async def answer_inline_query(
        self, inline_query_id: str, results: Iterable[InlineQueryResult],
        cache_time: Optional[int] = None, is_personal: Optional[bool] = None,
        next_offset: Optional[str] = None,
        switch_pm_text: Optional[str] = None,
        switch_pm_parameter: Optional[str] = None
    ) -> bool:
        api_logger.debug('Answer inline query "%s"', inline_query_id)
        response = await self._request(
            RequestMethod.POST, 'answerInlineQuery',
            inline_query_id=inline_query_id,
            results=_json_dumps(results),
            cache_time=cache_time, is_personal=is_personal,
            next_offset=next_offset, switch_pm_text=switch_pm_text,
            switch_pm_parameter=switch_pm_parameter)
        assert isinstance(response.result, bool)
        return response.result

    async def send_invoice(
        self, chat_id: int, title: str, description: str, payload: str,
        provider_token: str, currency: str, prices: Iterable[LabeledPrice],
        max_tip_amount: Optional[int] = None,
        suggested_tip_amounts: Optional[Tuple[int, ...]] = None,
        start_parameter: Optional[str] = None,
        provider_data: Optional[str] = None,
        photo_url: Optional[str] = None, photo_size: Optional[int] = None,
        photo_width: Optional[int] = None, photo_height: Optional[int] = None,
        need_name: Optional[bool] = None,
        need_phone_number: Optional[bool] = None,
        need_email: Optional[bool] = None,
        need_shipping_address: Optional[bool] = None,
        send_phone_number_to_provider: Optional[bool] = None,
        send_email_to_provider: Optional[bool] = None,
        is_flexible: Optional[bool] = None,
        disable_notification: Optional[bool] = None,
        protect_content: Optional[bool] = None,
        reply_to_message_id: Optional[int] = None,
        allow_sending_without_reply: Optional[bool] = None,
        reply_markup: Optional[InlineKeyboardMarkup] = None
    ) -> Message:
        api_logger.debug('Send invoice to %s', chat_id)
        response = await self._safe_request(
            RequestMethod.POST, 'sendInvoice', chat_id,
            title=title, description=description, payload=payload,
            provider_token=provider_token,
            currency=currency,
            prices=_json_dumps(prices),
            max_tip_amount=max_tip_amount,
            suggested_tip_amounts=_json_dumps(suggested_tip_amounts),
            start_parameter=start_parameter,
            provider_data=provider_data, photo_url=photo_url,
            photo_size=photo_size, photo_width=photo_width,
            photo_height=photo_height, need_name=need_name,
            need_phone_number=need_phone_number, need_email=need_email,
            need_shipping_address=need_shipping_address,
            send_phone_number_to_provider=send_phone_number_to_provider,
            send_email_to_provider=send_email_to_provider,
            is_flexible=is_flexible,
            disable_notification=disable_notification,
            protect_content=protect_content,
            reply_to_message_id=reply_to_message_id,
            allow_sending_without_reply=allow_sending_without_reply,
            reply_markup=_json_dumps(reply_markup))

        return Message.from_dict(response.result)

    async def answer_shipping_query(
        self, inline_query_id: str, ok: bool,
        shipping_options: Optional[Iterable[ShippingOption]] = None,
        error_message: Optional[str] = None
    ) -> bool:
        api_logger.debug('Answer shipping query "%s"', inline_query_id)
        response = await self._request(
            RequestMethod.POST, 'answerShippingQuery',
            inline_query_id=inline_query_id, ok=ok,
            shipping_options=_json_dumps(shipping_options),
            error_message=error_message)
        assert isinstance(response.result, bool)
        return response.result

    async def answer_pre_checkout_query(
        self, pre_checkout_query_id: str, ok: bool,
        error_message: Optional[str] = None
    ) -> bool:
        api_logger.debug('Answer pre checkout query "%s"',
                         pre_checkout_query_id)
        response = await self._request(
            RequestMethod.POST, 'answerPreCheckoutQuery',
            pre_checkout_query_id=pre_checkout_query_id, ok=ok,
            error_message=error_message)
        assert isinstance(response.result, bool)
        return response.result

    async def set_passport_data_errors(
        self, user_id: int,
        errors: Iterable[PassportElementError]
    ) -> bool:
        api_logger.debug('Set passport data errors %s', user_id)
        response = await self._request(
            RequestMethod.POST, 'setPassportDataErrors',
            user_id=user_id,
            errors=_json_dumps(errors))
        assert isinstance(response.result, bool)
        return response.result

    async def send_game(
        self, chat_id: int, game_short_name: str,
        disable_notification: Optional[bool] = None,
        protect_content: Optional[bool] = None,
        reply_to_message_id: Optional[int] = None,
        allow_sending_without_reply: Optional[bool] = None,
        reply_markup: Optional[InlineKeyboardMarkup] = None
    ) -> Message:
        api_logger.debug('Send game "%s" to %s', chat_id, game_short_name)
        response = await self._safe_request(
            RequestMethod.POST, 'sendGame', chat_id,
            game_short_name=game_short_name,
            disable_notification=disable_notification,
            protect_content=protect_content,
            reply_to_message_id=reply_to_message_id,
            allow_sending_without_reply=allow_sending_without_reply,
            reply_markup=_json_dumps(reply_markup))

        return Message.from_dict(response.result)

    async def set_game_score(
        self, user_id: int, score: int,
        force: Optional[bool] = None,
        disable_edit_message: Optional[bool] = None,
        chat_id: Optional[int] = None, message_id: Optional[int] = None,
        inline_message_id: Optional[str] = None
    ) -> Union[Message, bool]:
        api_logger.debug('Set game score %s for %s', score, user_id)
        response = await self._request(
            RequestMethod.POST, 'setGameScore',
            user_id=user_id, score=score, force=force,
            disable_edit_message=disable_edit_message,
            chat_id=chat_id, message_id=message_id,
            inline_message_id=inline_message_id)

        if isinstance(response.result, bool):
            return response.result
        else:
            return Message.from_dict(response.result)

    async def get_game_high_scores(
        self, user_id: int, chat_id: Optional[int] = None,
        message_id: Optional[int] = None,
        inline_message_id: Optional[str] = None
    ) -> Tuple[GameHighScore, ...]:
        api_logger.debug('Get game high scores for %s', user_id)
        response = await self._request(
            RequestMethod.POST, 'getGameHighScores',
            user_id=user_id, chat_id=chat_id, message_id=message_id,
            inline_message_id=inline_message_id)

        return tuple(GameHighScore.from_dict(item) for item in response.result)
