#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

from typing import (
	TYPE_CHECKING,
	Optional,
	List,
	Union,
	Dict,
	Any
)

from tgsdk import (
	Animation,
	Audio,
	Chat,
	Contact,
	Document,
	InlineKeyboardMarkup,
	MessageEntity,
	Location,
	PhotoSize,
	Sticker,
	User,
	Venue,
	Video,
	VideoNote,
	Voice,
	Invoice,
	PassportData,
	SuccessfulPayment,
	ProximityAlertTriggered
)
from tgsdk import TelegramEntity

if TYPE_CHECKING:
	from tgsdk import (
		Bot,
		InputMedia
	)


class Message(TelegramEntity):
	"""
	https://core.telegram.org/bots/api#message

	"""

	__slots__ = (
		"message_id", "from_user", "sender_chat", "date", "chat", "forward_from", "forward_from_chat", "forward_from_message_id", "forward_signature",
		"forward_sender_name", "forward_date", "reply_to_message", "via_bot", "edit_date", "media_group_id", "author_signature", "text", "entities",
		"animation", "audio", "document", "photo", "bot", "sticker", "video", "video_note", "voice", "caption", "caption_entities", "contact", "venue",
		"location", "new_chat_members", "left_chat_member", "new_chat_title", "new_chat_photo", "delete_chat_photo", "group_chat_created",
		"supergroup_chat_created", "channel_chat_created", "migrate_to_chat_id", "migrate_from_chat_id", "pinned_message", "invoice", "successful_payment",
		"connected_website", "passport_data", "proximity_alert_triggered", "reply_markup"
	)

	def __init__(
		self,
		message_id: int,
		from_user: User,
		date: int,
		chat: Chat,
		sender_chat: Optional[Chat] = None,
		forward_from: User = None,
		forward_from_chat: Chat = None,
		forward_from_message_id: int = None,
		forward_signature: str = None,
		forward_sender_name: str = None,
		forward_date: int = None,
		reply_to_message: "Message" = None,
		via_bot: User = None,
		edit_date: int = None,
		media_group_id: str = None,
		author_signature: str = None,
		text: str = None,
		entities: List["MessageEntity"] = None,
		animation: Animation = None,
		audio: Audio = None,
		document: Document = None,
		photo: List[PhotoSize] = None,
		sticker: Sticker = None,
		video: Video = None,
		video_note: VideoNote = None,
		voice: Voice = None,
		caption: str = None,
		caption_entities: List[MessageEntity] = None,
		contact: Contact = None,
		# dice: Dice = None,
		# game: Game = None,
		# poll: Poll = None,
		venue: Venue = None,
		location: Location = None,
		new_chat_members: List[User] = None,
		left_chat_member: User = None,
		new_chat_title: str = None,
		new_chat_photo: List[PhotoSize] = None,
		delete_chat_photo: bool = None,
		group_chat_created: bool = None,
		supergroup_chat_created: bool = None,
		channel_chat_created: bool = None,
		# message_auto_delete_timer_changed: MessageAutoDeleteTimerChanged = None,
		migrate_to_chat_id: int = None,
		migrate_from_chat_id: int = None,
		pinned_message: "Message" = None,
		invoice: Invoice = None,
		successful_payment: SuccessfulPayment = None,
		connected_website: str = None,
		passport_data: PassportData = None,
		proximity_alert_triggered: ProximityAlertTriggered = None,
		# voice_chat_scheduled: VoiceChatScheduled = None,
		# voice_chat_started: VoiceChatStarted = None,
		# voice_chat_ended: VoiceChatEnded = None,
		# voice_chat_participants_invited: VoiceChatParticipantsInvited = None,
		reply_markup: InlineKeyboardMarkup = None,

		bot: "Bot" = None,

		**_kwargs: Any
	):
		self.message_id = int(message_id)
		self.from_user = from_user
		self.sender_chat = sender_chat
		self.date = date
		self.chat = chat
		self.forward_from = forward_from
		self.forward_from_chat = forward_from_chat
		self.forward_from_message_id = forward_from_message_id
		self.forward_signature = forward_signature
		self.forward_sender_name = forward_sender_name
		self.forward_date = forward_date
		self.reply_to_message = reply_to_message
		self.via_bot = via_bot
		self.edit_date = edit_date
		self.media_group_id = media_group_id
		self.author_signature = author_signature
		self.text = text
		self.entities = entities
		self.animation = animation
		self.audio = audio
		self.document = document
		self.photo = photo
		self.sticker = sticker
		self.video = video
		self.video_note = video_note
		self.voice = voice
		self.caption = caption
		self.caption_entities = caption_entities
		self.contact = contact
		self.venue = venue
		self.location = location
		self.new_chat_members = new_chat_members
		self.left_chat_member = left_chat_member
		self.new_chat_title = new_chat_title
		self.new_chat_photo = new_chat_photo
		self.delete_chat_photo = delete_chat_photo
		self.group_chat_created = group_chat_created
		self.supergroup_chat_created = supergroup_chat_created
		self.channel_chat_created = channel_chat_created
		self.migrate_to_chat_id = migrate_to_chat_id
		self.migrate_from_chat_id = migrate_from_chat_id
		self.pinned_message = pinned_message
		self.invoice = invoice
		self.successful_payment = successful_payment
		self.connected_website = connected_website
		self.passport_data = passport_data
		self.proximity_alert_triggered = proximity_alert_triggered
		self.reply_markup = reply_markup

		self.bot = bot

	@classmethod
	def de_json(cls, data: Optional[Dict] = None) -> Union["Message", None]:
		"""

		:param data:
		:return:
		"""
		if not data:
			return None

		data["from_user"] = User.de_json(data.get("from"))
		data["sender_chat"] = Chat.de_json(data.get("sender_chat"))
		data["chat"] = Chat.de_json(data.get("chat"))
		data["forward_from"] = User.de_json(data.get("forward_from"))
		data["forward_from_chat"] = Chat.de_json(data.get("forward_from_chat"))
		data["reply_to_message"] = Message.de_json(data.get("reply_to_message"))
		data["via_bot"] = User.de_json(data.get("via_bot"))
		data["entities"] = MessageEntity.de_list(data.get("entities"))
		data["animation"] = Animation.de_json(data.get("animation"))
		data["audio"] = Audio.de_json(data.get("audio"))
		data["document"] = Document.de_json(data.get("document"))
		data["photo"] = PhotoSize.de_list(data.get("photo"))
		data["sticker"] = Sticker.de_json(data.get("sticker"))
		data["video"] = Video.de_json(data.get("video"))
		data["video_note"] = VideoNote.de_json(data.get("video_note"))
		data["voice"] = Voice.de_json(data.get("voice"))
		data["caption_entities"] = MessageEntity.de_list(data.get("caption_entities"))
		data["contact"] = Contact.de_json(data.get("contact"))
		data["venue"] = Venue.de_json(data.get("venue"))
		data["location"] = Location.de_json(data.get("location"))
		data["new_chat_members"] = User.de_list(data.get("new_chat_members"))
		data["left_chat_member"] = User.de_json(data.get("left_chat_member"))
		data["new_chat_photo"] = PhotoSize.de_list(data.get("new_chat_photo"))
		data["pinned_message"] = Message.de_json(data.get("pinned_message"))
		data["invoice"] = Invoice.de_json(data.get("invoice"))
		data["successful_payment"] = SuccessfulPayment.de_json(data.get("successful_payment"))
		data["passport_data"] = PassportData.de_json(data.get("passport_data"))
		data["proximity_alert_triggered"] = ProximityAlertTriggered.de_json(data.get("proximity_alert_triggered"))
		data["reply_markup"] = InlineKeyboardMarkup.de_json(data.get("reply_markup"))

		return cls(**data)

	def to_dict(self) -> Dict:
		"""

		:return:
		"""
		data = super().to_dict()

		if self.photo:
			data["photo"] = [photo.to_dict() for photo in self.photo]

		if self.entities:
			data["entities"] = [entity.to_dict() for entity in self.entities]

		if self.caption_entities:
			data["caption_entities"] = [caption_entity.to_dict() for caption_entity in self.caption_entities]

		if self.new_chat_photo:
			data["new_chat_photo"] = [new_chat_photo.to_dict() for new_chat_photo in self.new_chat_photo]

		if self.new_chat_members:
			data["new_chat_members"] = [new_chat_member.to_dict() for new_chat_member in self.new_chat_members]

		return data

	def edit_text(
		self,
		text: str,
		parse_mode: str = None,
		reply_markup: InlineKeyboardMarkup = None,
		disable_web_page_preview: bool = None,
		timeout: float = None,
		kwargs: Dict = None,
	) -> Union["Message", bool]:
		"""
		https://core.telegram.org/bots/api#editmessagetext

		:param text:
		:param parse_mode:
		:param disable_web_page_preview:
		:param reply_markup:
		:param timeout:
		:param kwargs:
		:return:
		"""

		return self.bot.edit_message_text(
			chat_id=self.chat.id,
			message_id=self.message_id,
			inline_message_id=None,
			text=text,
			parse_mode=parse_mode,
			disable_web_page_preview=disable_web_page_preview,
			reply_markup=reply_markup,
			timeout=timeout,
			kwargs=kwargs
		)

	def edit_caption(
		self,
		caption: str = None,
		reply_markup: InlineKeyboardMarkup = None,
		timeout: float = None,
		parse_mode: str = None,
		kwargs: Dict = None
	) -> Union["Message", bool]:
		"""
		https://core.telegram.org/bots/api#editmessagecaption
		
		:param caption: 
		:param reply_markup: 
		:param timeout: 
		:param parse_mode: 
		:param kwargs: 
		:return: 
		"""
		return self.bot.edit_message_caption(
			chat_id=self.chat.id,
			message_id=self.message_id,
			caption=caption,
			reply_markup=reply_markup,
			timeout=timeout,
			parse_mode=parse_mode,
			kwargs=kwargs,
			inline_message_id=None,
		)

	def edit_media(
		self,
		media: "InputMedia" = None,
		reply_markup: InlineKeyboardMarkup = None,
		timeout: float = None,
		kwargs: Dict = None,
	) -> Union["Message", bool]:
		"""
		https://core.telegram.org/bots/api#editmessagemedia

		:param media:
		:param reply_markup:
		:param timeout:
		:param kwargs:
		:return:
		"""
		return self.bot.edit_message_media(
			chat_id=self.chat.id,
			message_id=self.message_id,
			inline_message_id=None,
			media=media,
			reply_markup=reply_markup,
			timeout=timeout,
			kwargs=kwargs,
		)

	def edit_reply_markup(
		self,
		reply_markup: Optional["InlineKeyboardMarkup"] = None,
		timeout: float = None,
		kwargs: Dict = None,
	) -> Union["Message", bool]:
		"""
		https://core.telegram.org/bots/api#editmessagereplymarkup

		:param reply_markup:
		:param timeout:
		:param kwargs:
		:return:
		"""
		return self.bot.edit_message_reply_markup(
			chat_id=self.chat.id,
			message_id=self.message_id,
			inline_message_id=None,
			reply_markup=reply_markup,
			timeout=timeout,
			kwargs=kwargs,
		)

	def delete(
		self,
		timeout: float = None,
		kwargs: Dict = None,
	) -> bool:
		"""
		https://core.telegram.org/bots/api#deletemessage

		:param timeout:
		:param kwargs:
		:return:
		"""
		return self.bot.delete_message(
			chat_id=self.chat.id,
			message_id=self.message_id,
			timeout=timeout,
			kwargs=kwargs,
		)
