#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

from typing import (
	Any,
	TYPE_CHECKING,
	Tuple,
	Union,
	List,
	Optional,
	Dict
)

from tgsdk import (
	BotCommand,
	MessageId,
	InputFile,
	PhotoSize,
	Video,
	VideoNote,
	Audio,
	Voice,
	Sticker,
	Contact,
	Location,
	Document,
	ChatPhoto,
	ChatMember,
	ChatInviteLink,
	UserProfilePhotos,
	File,
	Chat,
	InlineKeyboardMarkup,
	ChatPermissions,
	User,
	ReplyMarkup,
	Message,
	WebhookInfo
)
from tgsdk import TelegramEntity
from tgsdk.network.request import Request
from tgsdk.utils import constants
from tgsdk.utils.get_input_file import get_input_file
from tgsdk.utils.types import (
	FileInput,
	ID
)

if TYPE_CHECKING:
	from tgsdk import (
		InputMedia,
		InputMediaDocument,
		InputMediaVideo,
		InputMediaPhoto,
		InputMediaAudio
	)


class Bot(TelegramEntity):
	__slots__ = ("token", "base_url", "base_file_url", "_me")

	def __init__(
		self,
		token: str,
		base_url: str = None,
		base_file_url: str = None,

		**_kwargs: Any
	):

		self.token = token

		if not base_url:
			base_url = "https://api.telegram.org/bot"

		if not base_file_url:
			base_file_url = "https://api.telegram.org/file/bot"

		self.base_url = base_url + self.token
		self.base_file_url = base_file_url + self.token

		self._me = None  # type: Optional[User]

	@property
	def request(self) -> Request:
		return Request()

	@property
	def me(self) -> User:
		"""

		"""
		if not self._me:
			self._me = self.get_me()

		return self._me

	@me.setter
	def me(self, value):
		"""

		:param value:
		"""
		if not isinstance(value, User):
			raise ValueError

		self._me = value

	@property
	def id(self) -> Union[ID, None]:
		"""
		Unique ID of the bot

		"""
		if self.me:
			return self.me.id

		return None

	@property
	def first_name(self) -> Union[str, None]:
		"""
		First name of the bot

		"""
		if self.me:
			return self.me.first_name

		return None

	@property
	def username(self) -> Union[str, None]:
		"""
		Username of the bot

		"""
		if self.me:
			return self.me.username

		return None

	@property
	def link(self) -> str:
		"""
		Default link to bot by service "t.me"

		"""
		return "https://t.me/%s" % self.username

	@property
	def tg_link(self) -> str:
		"""
		Link to bot by Telegram protocol "tg://"

		"""
		return "tg://resolve?domain=%s" % self.username

	def to_dict(self) -> Union[Dict, None]:
		"""

		"""
		data = None

		if not self.me:
			self.get_me()

		if self.me:
			data = {
				"id": self.id,
				"username": self.username,
				"first_name": self.first_name
			}

		return data

	def _post(
		self,
		endpoint: str,
		payload: Optional[Dict] = None,
		timeout: Optional[float] = None,
		kwargs: Optional[Dict] = None
	) -> Union[Dict, bool, str, None]:
		"""

		:param str endpoint:
		:param dict payload: (Optional)
		:param float timeout: (Optional)
		:param dict kwargs: (Optional)
		"""
		if not payload:
			payload = {}

		if kwargs:
			payload.update(kwargs)

		url = "%s/%s" % (self.base_url, endpoint)

		return self.request.post(url, payload=payload, timeout=timeout)

	def _send(
		self,
		endpoint: str,
		payload: Dict,
		allow_sending_without_reply: bool = None,
		reply_to_message_id: ID = None,
		disable_notification: bool = None,
		reply_markup: ReplyMarkup = None,
		timeout: float = None,
		kwargs: Dict = None
	) -> Union[bool, Message]:
		"""

		:param str endpoint:
		:param dict payload:
		:param bool allow_sending_without_reply:
		:param ID reply_to_message_id:
		:param bool disable_notification:
		:param ReplyMarkup reply_markup:
		:param float timeout:
		:param dict kwargs:
		:return:
		"""
		if reply_to_message_id:
			payload["reply_to_message_id"] = reply_to_message_id

		if disable_notification is not None:
			payload["disable_notification"] = disable_notification

		if reply_markup:
			payload["reply_markup"] = reply_markup.to_json()

		if allow_sending_without_reply is not None:
			payload["allow_sending_without_reply"] = allow_sending_without_reply

		_result = self._post(endpoint=endpoint, payload=payload, timeout=timeout, kwargs=kwargs)

		if _result is True:
			return _result

		return Message.de_json(_result)

	@staticmethod
	def build_chat_id(chat_id: ID) -> ID:
		"""
		Forming Chat ID independence of type and value in attribute "chat_id"

		Ex., 1234567890 will be as -1234567890 and "chat_username" will be as "@chat_username" also -1234567890 and "@chat_username" will not be changed

		:param ID chat_id:
		:return:
		"""
		try:
			chat_id = int(chat_id)
			if chat_id > 0:
				chat_id = -chat_id
		except ValueError:
			if not chat_id.startswith("@"):
				chat_id = "@%s" % chat_id

		return chat_id

	def get_me(self, timeout: float = None, **kwargs: None) -> User:
		"""
		https://core.telegram.org/bots/api#getme

		:param timeout:
		:param kwargs:
		:return:
		"""
		result = self._post("getMe", timeout=timeout, kwargs=kwargs)

		self._me = User.de_json(result)

		return self._me

	def send_message(
		self,
		chat_id: ID,
		text: str,
		parse_mode: str = None,
		reply_markup: ReplyMarkup = None,
		reply_to_message_id: ID = None,
		disable_web_page_preview: bool = None,
		disable_notification: bool = None,
		protect_content: bool = None,
		allow_sending_without_reply: bool = None,
		timeout: float = None,
		kwargs: Dict = None
	) -> Union[Message, bool]:
		"""
		https://core.telegram.org/bots/api#sendmessage

		:param chat_id:
		:param text:
		:param parse_mode:
		:param reply_markup:
		:param reply_to_message_id:
		:param disable_web_page_preview:
		:param disable_notification:
		:param protect_content:
		:param allow_sending_without_reply:
		:param timeout:
		:param kwargs:
		:return:
		"""

		if len(text) > constants.MAX_MESSAGE_LENGTH:
			text = text[:constants.MAX_MESSAGE_LENGTH]

		payload = {
			"chat_id": chat_id,
			"text": text
		}

		if parse_mode:
			payload["parse_mode"] = parse_mode

		if disable_web_page_preview is not None:
			payload["disable_web_page_preview"] = disable_web_page_preview

		if protect_content is not None:
			payload["protect_content"] = protect_content

		return self._send(
			"sendMessage",
			payload,
			timeout=timeout,
			reply_markup=reply_markup,
			reply_to_message_id=reply_to_message_id,
			disable_notification=disable_notification,
			allow_sending_without_reply=allow_sending_without_reply,
			kwargs=kwargs
		)

	def delete_message(
		self,
		chat_id: ID,
		message_id: ID,
		timeout: float = None,
		kwargs: Dict = None
	) -> bool:
		"""
		https://core.telegram.org/bots/api#deletemessage

		:param chat_id:
		:param message_id:
		:param timeout:
		:param kwargs:
		:return:
		"""
		payload = {
			"chat_id": chat_id,
			"message_id": message_id
		}

		return self._post("deleteMessage", payload, timeout=timeout, kwargs=kwargs)

	def forward_message(
		self,
		chat_id: ID,
		from_chat_id: ID,
		message_id: ID,
		disable_notification: bool = None,
		protect_content: bool = None,
		timeout: float = None,
		kwargs: Dict = None
	) -> Message:
		"""
		https://core.telegram.org/bots/api#forwardmessage

		:param chat_id:
		:param from_chat_id:
		:param message_id:
		:param disable_notification:
		:param protect_content:
		:param timeout:
		:param kwargs:
		:return:
		"""

		payload = dict()

		if chat_id:
			payload["chat_id"] = chat_id

		if from_chat_id:
			payload["from_chat_id"] = from_chat_id

		if message_id:
			payload["message_id"] = message_id

		if protect_content is not None:
			payload["protect_content"] = protect_content

		return self._send(
			"forwardMessage",
			payload,
			disable_notification=disable_notification,
			timeout=timeout,
			kwargs=kwargs
		)

	def copy_message(
		self,
		chat_id: ID,
		from_chat_id: ID,
		message_id: ID,
		caption: str = None,
		parse_mode: str = None,
		reply_markup: ReplyMarkup = None,
		disable_notification: bool = None,
		protect_content: bool = None,
		reply_to_message_id: ID = None,
		allow_sending_without_reply: bool = None,
		timeout: float = None,
		kwargs: Dict = None
	) -> MessageId:
		"""
		https://core.telegram.org/bots/api#copymessage

		:param chat_id:
		:param from_chat_id:
		:param message_id:
		:param caption:
		:param parse_mode:
		:param reply_markup:
		:param disable_notification:
		:param protect_content:
		:param reply_to_message_id:
		:param allow_sending_without_reply:
		:param timeout:
		:param kwargs:
		:return:
		"""
		payload = {
			"chat_id": chat_id,
			"from_chat_id": from_chat_id,
			"message_id": message_id
		}

		if caption:
			if len(caption) > constants.MAX_CAPTION_LENGTH:
				caption = caption[:constants.MAX_CAPTION_LENGTH]

			payload["caption"] = caption

		if parse_mode:
			payload["parse_mode"] = parse_mode

		if disable_notification is not None:
			payload["disable_notification"] = disable_notification

		if reply_to_message_id:
			payload["reply_to_message_id"] = reply_to_message_id

		if allow_sending_without_reply is not None:
			payload["allow_sending_without_reply"] = allow_sending_without_reply

		if protect_content is not None:
			payload["protect_content"] = protect_content

		if reply_markup:
			payload["reply_markup"] = reply_markup.to_json()

		_result = self._post("copyMessage", payload=payload, timeout=timeout, kwargs=kwargs)
		return MessageId.de_json(_result)

	def send_photo(
		self,
		chat_id: ID,
		photo: Union[FileInput, "PhotoSize"],
		file_name: str = None,
		caption: str = None,
		parse_mode: str = None,
		reply_markup: ReplyMarkup = None,
		disable_notification: bool = None,
		protect_content: bool = None,
		reply_to_message_id: ID = None,
		allow_sending_without_reply: bool = None,
		timeout: float = None,
		kwargs: Dict = None
	) -> Message:
		"""
		https://core.telegram.org/bots/api#sendphoto

		:param chat_id:
		:param photo:
		:param file_name:
		:param caption:
		:param parse_mode:
		:param reply_markup:
		:param disable_notification:
		:param protect_content:
		:param reply_to_message_id:
		:param allow_sending_without_reply:
		:param timeout:
		:param kwargs:
		:return:
		"""
		payload = {
			"chat_id": chat_id,
			"photo": get_input_file(photo, PhotoSize, file_name=file_name)
		}

		if caption:
			if len(caption) > constants.MAX_CAPTION_LENGTH:
				caption = caption[:constants.MAX_CAPTION_LENGTH]

			payload["caption"] = caption

		if parse_mode:
			payload["parse_mode"] = parse_mode

		if protect_content is not None:
			payload["protect_content"] = protect_content

		return self._send(
			"sendPhoto",
			payload,
			reply_markup=reply_markup,
			disable_notification=disable_notification,
			reply_to_message_id=reply_to_message_id,
			allow_sending_without_reply=allow_sending_without_reply,
			timeout=timeout,
			kwargs=kwargs
		)

	def send_audio(
		self,
		chat_id: ID,
		audio: Union[FileInput, "Audio"],
		duration: int = None,
		performer: str = None,
		title: str = None,
		caption: str = None,
		file_name: str = None,
		parse_mode: str = None,
		reply_markup: ReplyMarkup = None,
		disable_notification: bool = None,
		protect_content: bool = None,
		reply_to_message_id: ID = None,
		allow_sending_without_reply: bool = None,
		thumb: InputFile = None,
		timeout: float = None,
		kwargs: Dict = None
	) -> Message:
		"""
		https://core.telegram.org/bots/api#sendaudio

		:param chat_id:
		:param audio:
		:param duration:
		:param performer:
		:param title:
		:param caption:
		:param file_name:
		:param parse_mode:
		:param reply_markup:
		:param disable_notification:
		:param protect_content:
		:param reply_to_message_id:
		:param allow_sending_without_reply:
		:param thumb:
		:param timeout:
		:param kwargs:
		:return:
		"""
		payload = {
			"chat_id": chat_id,
			"audio": get_input_file(audio, Audio, file_name=file_name)
		}

		if duration:
			payload["duration"] = duration

		if performer:
			payload["performer"] = performer

		if title:
			payload["title"] = title

		if caption:
			if len(caption) > constants.MAX_CAPTION_LENGTH:
				caption = caption[:constants.MAX_CAPTION_LENGTH]

			payload["caption"] = caption

		if parse_mode:
			payload["parse_mode"] = parse_mode

		if thumb:
			payload["thumb"] = get_input_file(thumb, as_attach=True)

		if protect_content is not None:
			payload["protect_content"] = protect_content

		return self._send(
			"sendAudio",
			payload,
			reply_markup=reply_markup,
			disable_notification=disable_notification,
			reply_to_message_id=reply_to_message_id,
			allow_sending_without_reply=allow_sending_without_reply,
			timeout=timeout,
			kwargs=kwargs
		)

	def send_document(
		self,
		chat_id: ID,
		document: Union[FileInput, "Document"],
		file_name: str = None,
		caption: str = None,
		parse_mode: str = None,
		reply_markup: ReplyMarkup = None,
		disable_notification: bool = None,
		protect_content: bool = None,
		reply_to_message_id: ID = None,
		disable_content_type_detection: bool = None,
		allow_sending_without_reply: bool = None,
		thumb: InputFile = None,
		timeout: float = None,
		kwargs: Dict = None
	) -> Message:
		"""
		https://core.telegram.org/bots/api#senddocument

		:param chat_id:
		:param document:
		:param file_name:
		:param caption:
		:param parse_mode:
		:param reply_markup:
		:param disable_notification:
		:param protect_content:
		:param reply_to_message_id:
		:param disable_content_type_detection:
		:param allow_sending_without_reply:
		:param thumb:
		:param timeout:
		:param kwargs:
		:return:
		"""
		payload = {
			"chat_id": chat_id,
			"document": get_input_file(document, Document, file_name=file_name)
		}

		if caption:
			if len(caption) > constants.MAX_CAPTION_LENGTH:
				caption = caption[:constants.MAX_CAPTION_LENGTH]

			payload["caption"] = caption

		if parse_mode:
			payload["parse_mode"] = parse_mode

		if thumb:
			payload["thumb"] = thumb

		if disable_content_type_detection is not None:
			payload["disable_content_type_detection"] = disable_content_type_detection

		if protect_content is not None:
			payload["protect_content"] = protect_content

		return self._send(
			"sendDocument",
			payload,
			reply_markup=reply_markup,
			disable_notification=disable_notification,
			reply_to_message_id=reply_to_message_id,
			allow_sending_without_reply=allow_sending_without_reply,
			timeout=timeout,
			kwargs=kwargs
		)

	def send_sticker(
		self,
		chat_id: ID,
		sticker: Union[FileInput, "Sticker"],
		reply_markup: ReplyMarkup = None,
		disable_notification: bool = None,
		protect_content: bool = None,
		reply_to_message_id: ID = None,
		allow_sending_without_reply: bool = None,
		timeout: float = None,
		kwargs: Dict = None
	) -> Message:
		"""
		https://core.telegram.org/bots/api#sendsticker

		:param chat_id:
		:param sticker:
		:param reply_markup:
		:param disable_notification:
		:param protect_content:
		:param reply_to_message_id:
		:param allow_sending_without_reply:
		:param timeout:
		:param kwargs:
		:return:
		"""

		payload = {
			"chat_id": chat_id,
			"sticker": get_input_file(sticker, Sticker)
		}

		if protect_content is not None:
			payload["protect_content"] = protect_content

		return self._send(
			"sendSticker",
			payload,
			reply_markup=reply_markup,
			disable_notification=disable_notification,
			reply_to_message_id=reply_to_message_id,
			allow_sending_without_reply=allow_sending_without_reply,
			timeout=timeout,
			kwargs=kwargs
		)

	def send_video(
		self,
		chat_id: ID,
		video: Union[FileInput, "Video"],
		duration: int = None,
		caption: str = None,
		parse_mode: str = None,
		reply_markup: ReplyMarkup = None,
		file_name: str = None,
		width: int = None,
		height: int = None,
		disable_notification: bool = None,
		protect_content: bool = None,
		reply_to_message_id: ID = None,
		supports_streaming: bool = None,
		thumb: InputFile = None,
		allow_sending_without_reply: bool = None,
		timeout: float = None,
		kwargs: Dict = None
	) -> Message:
		"""
		https://core.telegram.org/bots/api#sendvideo

		:param chat_id:
		:param video:
		:param duration:
		:param caption:
		:param parse_mode:
		:param reply_markup:
		:param file_name:
		:param width:
		:param height:
		:param disable_notification:
		:param protect_content:
		:param reply_to_message_id:
		:param supports_streaming:
		:param thumb:
		:param allow_sending_without_reply:
		:param timeout:
		:param kwargs:
		:return:
		"""

		payload = {
			"chat_id": chat_id,
			"video": get_input_file(video, Video, file_name=file_name)
		}

		if caption:
			if len(caption) > constants.MAX_CAPTION_LENGTH:
				caption = caption[:constants.MAX_CAPTION_LENGTH]

			payload["caption"] = caption

		if parse_mode:
			payload["parse_mode"] = parse_mode

		if duration:
			payload["duration"] = duration

		if width:
			payload["width"] = width

		if height:
			payload["height"] = height

		if supports_streaming is not None:
			payload["supports_streaming"] = supports_streaming

		if protect_content is not None:
			payload["protect_content"] = protect_content

		if thumb:
			payload["thumb"] = get_input_file(thumb, as_attach=True)

		return self._send(
			"sendVideo",
			payload,
			reply_markup=reply_markup,
			disable_notification=disable_notification,
			reply_to_message_id=reply_to_message_id,
			allow_sending_without_reply=allow_sending_without_reply,
			timeout=timeout,
			kwargs=kwargs
		)

	def send_video_note(
		self,
		chat_id: ID,
		video_note: Union[FileInput, "VideoNote"],
		duration: int = None,
		length: int = None,
		file_name: str = None,
		reply_markup: ReplyMarkup = None,
		disable_notification: bool = None,
		protect_content: bool = None,
		reply_to_message_id: ID = None,
		allow_sending_without_reply: bool = None,
		thumb: InputFile = None,
		timeout: float = None,
		kwargs: Dict = None
	) -> Message:
		"""
		https://core.telegram.org/bots/api#sendvideonote

		:param chat_id:
		:param video_note:
		:param duration:
		:param length:
		:param file_name:
		:param reply_markup:
		:param disable_notification:
		:param protect_content:
		:param reply_to_message_id:
		:param allow_sending_without_reply:
		:param thumb:
		:param timeout:
		:param kwargs:
		:return:
		"""
		payload = {
			"chat_id": chat_id,
			"video_note": get_input_file(video_note, VideoNote, file_name=file_name)
		}

		if duration:
			payload["duration"] = duration

		if length:
			payload["length"] = length

		if thumb:
			payload["thumb"] = get_input_file(thumb, as_attach=True)

		if protect_content is not None:
			payload["protect_content"] = protect_content

		return self._send(
			"sendVideoNote",
			payload,
			reply_markup=reply_markup,
			disable_notification=disable_notification,
			allow_sending_without_reply=allow_sending_without_reply,
			reply_to_message_id=reply_to_message_id,
			timeout=timeout,
			kwargs=kwargs
		)

	def send_voice(
		self,
		chat_id: ID,
		voice: Union[FileInput, "Voice"],
		duration: int = None,
		caption: str = None,
		file_name: str = None,
		reply_markup: ReplyMarkup = None,
		parse_mode: str = None,
		disable_notification: bool = None,
		protect_content: bool = None,
		reply_to_message_id: ID = None,
		allow_sending_without_reply: bool = None,
		timeout: float = None,
		kwargs: Dict = None
	) -> Message:
		"""
		https://core.telegram.org/bots/api#sendvoice

		:param chat_id:
		:param voice:
		:param duration:
		:param caption:
		:param file_name:
		:param reply_markup:
		:param parse_mode:
		:param disable_notification:
		:param protect_content:
		:param reply_to_message_id:
		:param allow_sending_without_reply:
		:param timeout:
		:param kwargs:
		:return:
		"""
		payload = {
			"chat_id": chat_id,
			"voice": get_input_file(voice, Voice, file_name=file_name)
		}

		if duration:
			payload["duration"] = duration

		if caption:
			if len(caption) > constants.MAX_CAPTION_LENGTH:
				caption = caption[:constants.MAX_CAPTION_LENGTH]

			payload["caption"] = caption

		if parse_mode:
			payload["parse_mode"] = parse_mode

		if protect_content is not None:
			payload["protect_content"] = protect_content

		return self._send(
			"sendVoice",
			payload,
			reply_markup=reply_markup,
			disable_notification=disable_notification,
			allow_sending_without_reply=allow_sending_without_reply,
			reply_to_message_id=reply_to_message_id,
			timeout=timeout,
			kwargs=kwargs
		)

	def send_media_group(
		self,
		chat_id: ID,
		media: List[Union["InputMediaAudio", "InputMediaDocument", "InputMediaPhoto", "InputMediaVideo"]],
		disable_notification: bool = None,
		protect_content: bool = None,
		reply_to_message_id: ID = None,
		allow_sending_without_reply: bool = None,
		timeout: float = None,
		kwargs: Dict = None
	) -> List[Message]:
		"""
		https://core.telegram.org/bots/api#sendmediagroup

		:param chat_id:
		:param media:
		:param disable_notification:
		:param protect_content:
		:param reply_to_message_id:
		:param allow_sending_without_reply:
		:param timeout:
		:param kwargs:
		:return:
		"""
		payload = {
			"chat_id": chat_id,
			"media": media
		}

		if disable_notification is not None:
			payload["disable_notification"] = disable_notification

		if reply_to_message_id:
			payload["reply_to_message_id"] = reply_to_message_id

		if allow_sending_without_reply is not None:
			payload["allow_sending_without_reply"] = allow_sending_without_reply

		if protect_content is not None:
			payload["protect_content"] = protect_content

		_result = self._post(
			"sendMediaGroup",
			payload,
			timeout=timeout,
			kwargs=kwargs
		)

		return [Message.de_json(message) for message in _result]

	def send_location(
		self,
		chat_id: ID,
		latitude: float = None,
		longitude: float = None,
		reply_markup: ReplyMarkup = None,
		disable_notification: bool = None,
		protect_content: bool = None,
		reply_to_message_id: ID = None,
		location: Location = None,
		live_period: int = None,
		horizontal_accuracy: float = None,
		heading: int = None,
		proximity_alert_radius: int = None,
		allow_sending_without_reply: bool = None,
		timeout: float = None,
		kwargs: Dict = None
	) -> Message:
		"""
		https://core.telegram.org/bots/api#sendlocation

		:param chat_id:
		:param latitude:
		:param longitude:
		:param reply_markup:
		:param disable_notification:
		:param protect_content:
		:param reply_to_message_id:
		:param location:
		:param live_period:
		:param horizontal_accuracy:
		:param heading:
		:param proximity_alert_radius:
		:param allow_sending_without_reply:
		:param timeout:
		:param kwargs:
		:return:
		"""

		if isinstance(location, Location):
			latitude = location.latitude
			longitude = location.longitude
		else:
			if not isinstance(latitude, float):
				latitude = float(str(latitude).replace(",", "."))

			if not isinstance(longitude, float):
				longitude = float(str(longitude).replace(",", "."))

		payload = {
			"chat_id": chat_id,
			"latitude": latitude,
			"longitude": longitude
		}

		if live_period:
			payload["live_period"] = live_period

		if horizontal_accuracy:
			payload["horizontal_accuracy"] = horizontal_accuracy

		if heading:
			payload["heading"] = heading

		if proximity_alert_radius:
			payload["proximity_alert_radius"] = proximity_alert_radius

		if protect_content is not None:
			payload["protect_content"] = protect_content

		return self._send(
			"sendLocation",
			payload,
			reply_markup=reply_markup,
			disable_notification=disable_notification,
			reply_to_message_id=reply_to_message_id,
			allow_sending_without_reply=allow_sending_without_reply,
			timeout=timeout,
			kwargs=kwargs
		)

	def edit_message_live_location(self):
		pass

	def stop_message_live_location(self):
		pass

	def send_contact(
		self,
		chat_id: ID = None,
		phone_number: str = None,
		first_name: str = None,
		last_name: str = None,
		contact: Contact = None,
		vcard: str = None,
		reply_markup: ReplyMarkup = None,
		disable_notification: bool = None,
		protect_content: bool = None,
		reply_to_message_id: ID = None,
		allow_sending_without_reply: bool = None,
		timeout: float = None,
		kwargs: Dict = None
	) -> Message:
		"""
		https://core.telegram.org/bots/api#sendcontact

		:param chat_id:
		:param phone_number:
		:param first_name:
		:param last_name:
		:param contact:
		:param vcard:
		:param reply_markup:
		:param disable_notification:
		:param protect_content:
		:param reply_to_message_id:
		:param allow_sending_without_reply:
		:param timeout:
		:param kwargs:
		:return:
		"""

		if isinstance(contact, Contact):
			phone_number = contact.phone_number
			first_name = contact.first_name
			last_name = contact.last_name
			vcard = contact.vcard

		payload = {
			"chat_id": chat_id,
			"phone_number": phone_number,
			"first_name": first_name
		}

		if last_name:
			payload["last_name"] = last_name

		if vcard:
			payload["vcard"] = vcard

		if protect_content is not None:
			payload["protect_content"] = protect_content

		return self._send(
			"sendContact",
			payload,
			reply_markup=reply_markup,
			disable_notification=disable_notification,
			allow_sending_without_reply=allow_sending_without_reply,
			reply_to_message_id=reply_to_message_id,
			timeout=timeout,
			kwargs=kwargs
		)

	def send_chat_action(
		self,
		chat_id: ID,
		action: str,
		timeout: float = None,
		kwargs: Dict = None
	) -> bool:
		"""
		https://core.telegram.org/bots/api#sendchataction

		:param chat_id:
		:param action:
		:param timeout:
		:param kwargs:
		:return:
		"""
		payload = {
			"chat_id": chat_id,
			"action": action
		}

		return self._post(
			"sendChatAction",
			payload,
			timeout=timeout,
			kwargs=kwargs
		)

	def answer_inline_query(self):
		pass

	def get_user_profile_photos(
		self,
		user_id: ID,
		offset: int = None,
		limit: int = 100,
		timeout: float = None,
		kwargs: Dict = None
	) -> UserProfilePhotos:
		"""
		https://core.telegram.org/bots/api#getuserprofilephotos

		:param user_id:
		:param offset:
		:param limit:
		:param timeout:
		:param kwargs:
		:return:
		"""
		payload = {
			"user_id": user_id
		}

		if offset:
			payload["offset"] = offset

		if limit:
			payload["limit"] = limit

		_result = self._post(
			"getUserProfilePhotos",
			payload,
			timeout=timeout,
			kwargs=kwargs
		)

		return UserProfilePhotos.de_json(_result)

	def get_file(
		self,
		file_id: Union[str, Audio, ChatPhoto, Document, PhotoSize, Video, VideoNote, Voice],
		timeout: float = None,
		kwargs: Dict = None
	) -> File:
		"""
		https://core.telegram.org/bots/api#getfile

		:param file_id:
		:param timeout:
		:param kwargs:
		:return:
		"""
		try:
			file_id = file_id.file_id
		except AttributeError:
			pass

		payload = {
			"file_id": file_id
		}

		_result = self._post(
			"getFile",
			payload,
			timeout=timeout,
			kwargs=kwargs
		)

		if _result.get("file_path"):
			_result["file_path"] = "%s/%s" % (self.base_file_url, _result["file_path"])

		return File.de_json(_result)

	# TODO: DEPRECATED
	def kick_chat_member(
		self,
		chat_id: ID,
		user_id: ID,
		until_date: int = None,
		revoke_messages: Optional[bool] = None,
		timeout: float = None,
		kwargs: Dict = None
	) -> bool:
		"""
		https://core.telegram.org/bots/api#banchatmember

		:param ID chat_id:
		:param ID user_id:
		:param int until_date:
		:param bool revoke_messages:
		:param float timeout:
		:param kwargs:
		:return:
		"""
		payload = {
			"chat_id": self.build_chat_id(chat_id=chat_id),
			"user_id": user_id
		}

		if until_date:
			payload["until_date"] = until_date

		if revoke_messages is not None:
			payload["revoke_messages"] = revoke_messages

		return self._post(
			"banChatMember",
			payload,
			timeout=timeout,
			kwargs=kwargs
		)

	def ban_chat_member(
		self,
		chat_id: ID,
		user_id: ID,
		until_date: int = None,
		revoke_messages: Optional[bool] = None,
		timeout: float = None,
		kwargs: Dict = None
	) -> bool:
		"""
		https://core.telegram.org/bots/api#banchatmember

		:param ID chat_id:
		:param ID user_id:
		:param int until_date:
		:param bool revoke_messages:
		:param float timeout:
		:param kwargs:
		:return:
		"""
		payload = {
			"chat_id": self.build_chat_id(chat_id=chat_id),
			"user_id": user_id
		}

		if until_date:
			payload["until_date"] = until_date

		if revoke_messages is not None:
			payload["revoke_messages"] = revoke_messages

		return self._post(
			"banChatMember",
			payload,
			timeout=timeout,
			kwargs=kwargs
		)

	def unban_chat_member(
		self,
		chat_id: ID,
		user_id: ID,
		only_if_banned: bool = None,
		timeout: float = None,
		kwargs: Dict = None
	) -> bool:
		"""
		https://core.telegram.org/bots/api#unbanchatmember

		:param chat_id:
		:param user_id:
		:param only_if_banned:
		:param timeout:
		:param kwargs:
		:return:
		"""

		payload = {
			"chat_id": self.build_chat_id(chat_id=chat_id),
			"user_id": user_id
		}

		if only_if_banned is not None:
			payload["only_if_banned"] = only_if_banned

		return self._post(
			"unbanChatMember",
			payload,
			timeout=timeout,
			kwargs=kwargs
		)

	def answer_callback_query(
		self,
		callback_query_id: str,
		text: str = None,
		show_alert: bool = None,
		url: str = None,
		cache_time: int = None,
		timeout: float = None,
		kwargs: Dict = None
	) -> bool:
		"""
		https://core.telegram.org/bots/api#answercallbackquery

		:param callback_query_id:
		:param text:
		:param show_alert:
		:param url:
		:param cache_time:
		:param timeout:
		:param kwargs:
		:return:
		"""
		payload = {
			"callback_query_id": callback_query_id
		}

		if text:
			payload["text"] = text

		if show_alert is not None:
			payload["show_alert"] = show_alert

		if url:
			payload["url"] = url

		if cache_time:
			payload["cache_time"] = cache_time

		return self._post(
			"answerCallbackQuery",
			payload,
			timeout=timeout,
			kwargs=kwargs
		)

	def edit_message_text(
		self,
		text: str,
		chat_id: ID = None,
		message_id: ID = None,
		inline_message_id: ID = None,
		parse_mode: str = None,
		disable_web_page_preview: bool = None,
		reply_markup: InlineKeyboardMarkup = None,
		timeout: float = None,
		kwargs: Dict = None
	) -> Union[Message, bool]:
		"""
		https://core.telegram.org/bots/api#editmessagetext

		:param text:
		:param chat_id:
		:param message_id:
		:param inline_message_id:
		:param parse_mode:
		:param disable_web_page_preview:
		:param reply_markup:
		:param timeout:
		:param kwargs:
		:return:
		"""
		payload = {
			"text": text
		}

		if chat_id:
			payload["chat_id"] = chat_id

		if message_id:
			payload["message_id"] = message_id

		if inline_message_id:
			payload["inline_message_id"] = inline_message_id

		if parse_mode:
			payload["parse_mode"] = parse_mode

		if disable_web_page_preview is not None:
			payload["disable_web_page_preview"] = disable_web_page_preview

		return self._send(
			"editMessageText",
			payload,
			reply_markup=reply_markup,
			timeout=timeout,
			kwargs=kwargs
		)

	def edit_message_caption(
		self,
		chat_id: ID = None,
		message_id: ID = None,
		inline_message_id: ID = None,
		caption: str = None,
		parse_mode: str = None,
		reply_markup: InlineKeyboardMarkup = None,
		timeout: float = None,
		kwargs: Dict = None
	) -> Union[Message, bool]:
		"""
		https://core.telegram.org/bots/api#editmessagecaption

		:param chat_id:
		:param message_id:
		:param inline_message_id:
		:param caption:
		:param parse_mode:
		:param reply_markup:
		:param timeout:
		:param kwargs:
		:return:
		"""
		payload = dict()

		if chat_id:
			payload["chat_id"] = chat_id

		if message_id:
			payload["message_id"] = message_id

		if inline_message_id:
			payload["inline_message_id"] = inline_message_id

		if caption:
			if len(caption) > constants.MAX_CAPTION_LENGTH:
				caption = caption[:constants.MAX_CAPTION_LENGTH]

			payload["caption"] = caption

		if parse_mode:
			payload["parse_mode"] = parse_mode

		return self._send(
			"editMessageCaption",
			payload,
			reply_markup=reply_markup,
			timeout=timeout,
			kwargs=kwargs
		)

	def edit_message_media(
		self,
		chat_id: ID = None,
		message_id: ID = None,
		inline_message_id: ID = None,
		media: "InputMedia" = None,
		reply_markup: InlineKeyboardMarkup = None,
		timeout: float = None,
		kwargs: Dict = None
	) -> Union[Message, bool]:
		"""
		https://core.telegram.org/bots/api#editmessagemedia

		:param chat_id:
		:param message_id:
		:param inline_message_id:
		:param media:
		:param reply_markup:
		:param timeout:
		:param kwargs:
		:return:
		"""

		payload = {
			"media": media
		}

		if chat_id:
			payload["chat_id"] = chat_id

		if message_id:
			payload["message_id"] = message_id

		if inline_message_id:
			payload["inline_message_id"] = inline_message_id

		return self._send(
			"editMessageMedia",
			payload,
			reply_markup=reply_markup,
			timeout=timeout,
			kwargs=kwargs
		)

	def edit_message_reply_markup(
		self,
		chat_id: ID = None,
		message_id: ID = None,
		inline_message_id: ID = None,
		reply_markup: InlineKeyboardMarkup = None,
		timeout: float = None,
		kwargs: Dict = None
	) -> Union[Message, bool]:
		"""
		https://core.telegram.org/bots/api#editmessagereplymarkup

		:param chat_id:
		:param message_id:
		:param inline_message_id:
		:param reply_markup:
		:param timeout:
		:param kwargs:
		:return:
		"""
		payload = dict()

		if chat_id:
			payload["chat_id"] = chat_id

		if message_id:
			payload["message_id"] = message_id

		if inline_message_id:
			payload["inline_message_id"] = inline_message_id

		return self._send(
			"editMessageReplyMarkup",
			payload,
			reply_markup=reply_markup,
			timeout=timeout,
			kwargs=kwargs
		)

	def set_webhook(
		self,
		url: str,
		certificate: InputFile = None,
		max_connections: int = 50,
		allowed_updates: List[str] = None,
		ip_address: str = None,
		drop_pending_updates: bool = None,
		timeout: float = None,
		kwargs: Dict = None
	) -> bool:
		"""
		https://core.telegram.org/bots/api#setwebhook

		:param url:
		:param certificate:
		:param max_connections:
		:param allowed_updates:
		:param ip_address:
		:param drop_pending_updates:
		:param timeout:
		:param kwargs:
		:return:
		"""
		payload = {
			"url": url
		}

		if certificate:
			payload["certificate"] = get_input_file(certificate)

		if max_connections:
			payload["max_connections"] = max_connections

		if allowed_updates:
			payload["allowed_updates"] = allowed_updates

		if allowed_updates is None:
			# To not receive all updates which is not necessary
			payload["allowed_updates"] = [
				constants.ALLOWED_TYPE_MESSAGE,
				constants.ALLOWED_TYPE_CALLBACK_QUERY
			]

		if ip_address:
			payload["ip_address"] = ip_address

		if drop_pending_updates is not None:
			payload["drop_pending_updates"] = drop_pending_updates

		return self._post("setWebhook", payload=payload, timeout=timeout, kwargs=kwargs)

	def get_webhook_info(self, timeout: float = None, kwargs: Dict = None) -> WebhookInfo:
		"""
		https://core.telegram.org/bots/api#getwebhookinfo

		:param timeout:
		:param kwargs:
		:return:
		"""
		_result = self._post("getWebhookInfo", timeout=timeout, kwargs=kwargs)

		return WebhookInfo.de_json(_result)

	def delete_webhook(self, drop_pending_updates: bool = None, timeout: float = None, kwargs: Dict = None) -> bool:
		"""
		https://core.telegram.org/bots/api#deletewebhook

		:param drop_pending_updates:
		:param timeout:
		:param kwargs:
		:return:
		"""
		payload = dict()

		if drop_pending_updates is not None:
			payload["drop_pending_updates"] = drop_pending_updates

		return self._post("deleteWebhook", payload=payload, timeout=timeout, kwargs=kwargs)

	def leave_chat(
		self,
		chat_id: ID,
		timeout: float = None,
		kwargs: Dict = None
	) -> bool:
		"""
		https://core.telegram.org/bots/api#leavechat

		:param chat_id:
		:param timeout:
		:param kwargs:
		:return:
		"""
		payload = {
			"chat_id": self.build_chat_id(chat_id=chat_id),
		}

		return self._post(
			"leaveChat",
			payload,
			timeout=timeout,
			kwargs=kwargs
		)

	def get_chat(
		self,
		chat_id: ID,
		timeout: float = None,
		kwargs: Dict = None
	) -> Chat:
		"""
		https://core.telegram.org/bots/api#getchat

		:param chat_id:
		:param timeout:
		:param kwargs:
		:return:
		"""
		payload = {
			"chat_id": self.build_chat_id(chat_id=chat_id),
		}

		_result = self._post(
			"getChat",
			payload,
			timeout=timeout,
			kwargs=kwargs
		)

		return Chat.de_json(_result)

	def get_chat_administrators(
		self,
		chat_id: ID,
		timeout: float = None,
		kwargs: Dict = None
	) -> List[ChatMember]:
		"""
		https://core.telegram.org/bots/api#getchatadministrators

		:param chat_id:
		:param timeout:
		:param kwargs:
		:return:
		"""
		payload = {
			"chat_id": self.build_chat_id(chat_id=chat_id),
		}

		_result = self._post(
			"getChatAdministrators",
			payload,
			timeout=timeout,
			kwargs=kwargs
		)

		return [ChatMember.de_json(chat_member) for chat_member in _result]

	# TODO: DEPRECATED
	def get_chat_members_count(
		self,
		chat_id: ID,
		timeout: float = None,
		kwargs: Dict = None
	) -> int:
		"""
		https://core.telegram.org/bots/api#getchatmembercount

		:param chat_id:
		:param timeout:
		:param kwargs:
		:return:
		"""
		payload = {
			"chat_id": self.build_chat_id(chat_id=chat_id),
		}

		return self._post(
			"getChatMemberCount",
			payload,
			timeout=timeout,
			kwargs=kwargs
		)

	def get_chat_member_count(
		self,
		chat_id: ID,
		timeout: float = None,
		kwargs: Dict = None
	) -> int:
		"""
		https://core.telegram.org/bots/api#getchatmembercount

		:param chat_id:
		:param timeout:
		:param kwargs:
		:return:
		"""
		payload = {
			"chat_id": self.build_chat_id(chat_id=chat_id),
		}

		return self._post(
			"getChatMemberCount",
			payload,
			timeout=timeout,
			kwargs=kwargs
		)

	def get_chat_member(
		self,
		chat_id: ID,
		user_id: ID,
		timeout: float = None,
		kwargs: Dict = None
	) -> ChatMember:
		"""
		https://core.telegram.org/bots/api#getchatmember

		:param chat_id:
		:param user_id:
		:param timeout:
		:param kwargs:
		:return:
		"""
		payload = {
			"chat_id": self.build_chat_id(chat_id=chat_id),
			"user_id": user_id
		}

		_result = self._post(
			"getChatMember",
			payload,
			timeout=timeout,
			kwargs=kwargs
		)

		return ChatMember.de_json(_result)

	def restrict_chat_member(
		self,
		chat_id: ID,
		user_id: ID,
		permissions: ChatPermissions,
		until_date: int = None,
		timeout: float = None,
		kwargs: Dict = None
	) -> bool:
		"""
		https://core.telegram.org/bots/api#restrictchatmember

		:param chat_id:
		:param user_id:
		:param permissions:
		:param until_date:
		:param timeout:
		:param kwargs:
		:return:
		"""
		payload = {
			"chat_id": self.build_chat_id(chat_id=chat_id),
			"user_id": user_id,
			"permissions": permissions.to_dict()
		}

		if until_date:
			payload["until_date"] = until_date

		return self._post(
			"restrictChatMember",
			payload,
			timeout=timeout,
			kwargs=kwargs
		)

	def promote_chat_member(
		self,
		chat_id: ID,
		user_id: ID,
		can_change_info: bool = None,
		can_post_messages: bool = None,
		can_edit_messages: bool = None,
		can_delete_messages: bool = None,
		can_invite_users: bool = None,
		can_restrict_members: bool = None,
		can_pin_messages: bool = None,
		can_promote_members: bool = None,
		is_anonymous: bool = None,
		timeout: float = None,
		kwargs: Dict = None
	) -> bool:
		"""
		https://core.telegram.org/bots/api#promotechatmember

		:param chat_id:
		:param user_id:
		:param can_change_info:
		:param can_post_messages:
		:param can_edit_messages:
		:param can_delete_messages:
		:param can_invite_users:
		:param can_restrict_members:
		:param can_pin_messages:
		:param can_promote_members:
		:param is_anonymous:
		:param timeout:
		:param kwargs:
		:return:
		"""
		payload = {
			"chat_id": self.build_chat_id(chat_id=chat_id),
			"user_id": user_id
		}

		if is_anonymous is not None:
			payload["is_anonymous"] = is_anonymous

		if can_change_info is not None:
			payload["can_change_info"] = can_change_info

		if can_post_messages is not None:
			payload["can_post_messages"] = can_post_messages

		if can_edit_messages is not None:
			payload["can_edit_messages"] = can_edit_messages

		if can_delete_messages is not None:
			payload["can_delete_messages"] = can_delete_messages

		if can_invite_users is not None:
			payload["can_invite_users"] = can_invite_users

		if can_restrict_members is not None:
			payload["can_restrict_members"] = can_restrict_members

		if can_pin_messages is not None:
			payload["can_pin_messages"] = can_pin_messages

		if can_promote_members is not None:
			payload["can_promote_members"] = can_promote_members

		return self._post(
			"promoteChatMember",
			payload,
			timeout=timeout,
			kwargs=kwargs
		)

	def set_chat_permissions(
		self,
		chat_id: ID,
		permissions: ChatPermissions,
		timeout: float = None,
		kwargs: Dict = None
	) -> bool:
		"""
		https://core.telegram.org/bots/api#setchatpermissions

		:param chat_id:
		:param permissions:
		:param timeout:
		:param kwargs:
		:return:
		"""
		payload = {
			"chat_id": self.build_chat_id(chat_id=chat_id),
			"permissions": permissions.to_dict()
		}

		return self._post(
			"setChatPermissions",
			payload,
			timeout=timeout,
			kwargs=kwargs
		)

	def set_chat_administrator_custom_title(
		self,
		chat_id: ID,
		user_id: ID,
		custom_title: str,
		timeout: float = None,
		kwargs: Dict = None
	) -> bool:
		"""
		https://core.telegram.org/bots/api#setchatadministratorcustomtitle

		:param chat_id:
		:param user_id:
		:param custom_title:
		:param timeout:
		:param kwargs:
		:return:
		"""
		payload = {
			"chat_id": self.build_chat_id(chat_id=chat_id),
			"user_id": user_id,
			"custom_title": custom_title
		}

		return self._post(
			"setChatAdministratorCustomTitle",
			payload,
			timeout=timeout,
			kwargs=kwargs
		)

	def export_chat_invite_link(
		self,
		chat_id: ID,
		timeout: float = None,
		kwargs: Dict = None
	) -> str:
		"""
		https://core.telegram.org/bots/api#exportchatinvitelink

		:param chat_id:
		:param timeout:
		:param kwargs:
		:return:
		"""
		payload = {
			"chat_id": self.build_chat_id(chat_id=chat_id),
		}

		return self._post(
			"exportChatInviteLink",
			payload,
			timeout=timeout,
			kwargs=kwargs
		)

	def set_chat_photo(
		self,
		chat_id: ID,
		photo: InputFile,
		timeout: float = None,
		kwargs: Dict = None
	) -> bool:
		"""
		https://core.telegram.org/bots/api#setchatphoto

		:param chat_id:
		:param photo:
		:param timeout:
		:param kwargs:
		:return:
		"""
		payload = {
			"chat_id": self.build_chat_id(chat_id=chat_id),
			"photo": get_input_file(photo)
		}

		return self._post(
			"setChatPhoto",
			payload,
			timeout=timeout,
			kwargs=kwargs
		)

	def delete_chat_photo(
		self,
		chat_id: ID,
		timeout: float = None,
		kwargs: Dict = None
	) -> bool:
		"""
		https://core.telegram.org/bots/api#deletechatphoto

		:param chat_id:
		:param timeout:
		:param kwargs:
		:return:
		"""
		payload = {
			"chat_id": self.build_chat_id(chat_id=chat_id),
		}

		return self._post(
			"deleteChatPhoto",
			payload,
			timeout=timeout,
			kwargs=kwargs
		)

	def set_chat_title(
		self,
		chat_id: ID,
		title: str,
		timeout: float = None,
		kwargs: Dict = None
	) -> bool:
		"""
		https://core.telegram.org/bots/api#setchattitle

		:param chat_id:
		:param title:
		:param timeout:
		:param kwargs:
		:return:
		"""
		payload = {
			"chat_id": self.build_chat_id(chat_id=chat_id),
			"title": title
		}

		return self._post(
			"setChatTitle",
			payload,
			timeout=timeout,
			kwargs=kwargs
		)

	def set_chat_description(
		self,
		chat_id: ID,
		description: str,
		timeout: float = None,
		kwargs: Dict = None
	) -> bool:
		"""
		https://core.telegram.org/bots/api#setchatdescription

		:param chat_id:
		:param description:
		:param timeout:
		:param kwargs:
		:return:
		"""
		payload = {
			"chat_id": self.build_chat_id(chat_id=chat_id),
			"description": description
		}

		return self._post(
			"setChatDescription",
			payload,
			timeout=timeout,
			kwargs=kwargs
		)

	def create_chat_invite_link(
		self,
		chat_id: ID,
		expire_date: Optional[int] = None,
		member_limit: Optional[int] = None,
		timeout: float = None,
		kwargs: Dict = None
	) -> ChatInviteLink:
		"""
		https://core.telegram.org/bots/api#createchatinvitelink

		"""
		payload = {
			"chat_id": self.build_chat_id(chat_id)
		}

		if expire_date is not None:
			payload["expire_date"] = expire_date

		if member_limit is not None:
			if member_limit > 99999:
				member_limit = 99999

			payload["member_limit"] = member_limit

		_result = self._post(
			"createChatInviteLink",
			payload,
			timeout=timeout,
			kwargs=kwargs
		)
		return ChatInviteLink.de_json(_result)

	def edit_chat_invite_link(
		self,
		chat_id: ID,
		invite_link: str,
		expire_date: Optional[int] = None,
		member_limit: Optional[int] = None,
		timeout: float = None,
		kwargs: Dict = None
	) -> ChatInviteLink:
		"""
		https://core.telegram.org/bots/api#createchatinvitelink

		"""
		payload = {
			"chat_id": self.build_chat_id(chat_id),
			"invite_link": invite_link
		}

		if expire_date is not None:
			payload["expire_date"] = expire_date

		if member_limit is not None:
			if member_limit > 99999:
				member_limit = 99999

			payload["member_limit"] = member_limit

		_result = self._post(
			"editChatInviteLink",
			payload,
			timeout=timeout,
			kwargs=kwargs
		)
		return ChatInviteLink.de_json(_result)

	def revoke_chat_invite_link(
		self,
		chat_id: ID,
		invite_link: str,
		timeout: float = None,
		kwargs: Dict = None
	) -> ChatInviteLink:
		"""
		https://core.telegram.org/bots/api#createchatinvitelink

		"""
		payload = {
			"chat_id": self.build_chat_id(chat_id),
			"invite_link": invite_link
		}

		_result = self._post(
			"revokeChatInviteLink",
			payload,
			timeout=timeout,
			kwargs=kwargs
		)
		return ChatInviteLink.de_json(_result)

	def pin_chat_message(self):
		pass

	def unpin_chat_message(self):
		pass

	def unpin_all_chat_messages(self):
		pass

	def set_passport_data_errors(self):
		pass

	def send_invoice(self):
		pass

	def answer_shipping_query(self):
		pass

	def answer_pre_checkout_query(self):
		pass

	def get_my_commands(
		self,
		timeout: float = None,
		kwargs: Dict = None
	) -> List[BotCommand]:
		"""
		https://core.telegram.org/bots/api#getmycommands

		:param timeout:
		:param kwargs:
		:return:
		"""
		_result = self._post("getMyCommands", timeout=timeout, kwargs=kwargs)

		return [BotCommand.de_json(command) for command in _result]

	def set_my_commands(
		self,
		commands: List[Union[BotCommand, Tuple[str, str]]],
		timeout: float = None,
		kwargs: Dict = None
	) -> bool:
		"""
		https://core.telegram.org/bots/api#setmycommands

		:param kwargs:
		:param timeout:
		:param commands:
		:return:
		"""
		commands = [command if isinstance(command, BotCommand) else BotCommand(command[0], command[1]) for command in commands]

		payload = {
			"commands": [command.to_dict() for command in commands]
		}

		return self._post("setMyCommands", payload=payload, timeout=timeout, kwargs=kwargs)

	def log_out(self) -> bool:
		"""
		https://core.telegram.org/bots/api#logout

		:return:
		"""
		return self._post("logOut")

	def close(self) -> bool:
		"""
		https://core.telegram.org/bots/api#close

		:return:
		"""
		return self._post("close")
