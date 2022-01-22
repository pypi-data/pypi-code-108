#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

import os

try:
	import ujson as json
except ImportError:
	import json

import time

from tgsdk import (
	InlineKeyboardButton,
	InlineKeyboardMarkup,
	ReplyKeyboardRemove,
	KeyboardButton,
	ReplyKeyboardMarkup,
	ParseMode,
	PhotoSize,
	MessageEntity,
	Message,
	Video,
	Audio,
	Sticker,
	Document,
	Voice,
	VideoNote,
	Contact,
	Location,
	Venue,
	Chat,
	Bot,
	User
)
from tgsdk.utils.constants import MAX_CAPTION_LENGTH, MAX_MESSAGE_LENGTH
from tgsdk.network.request import Request
from .constants import TestValues


def test__bot__init():
	_ = Bot(token=TestValues.BOT_API_TOKEN)

	assert _.token == TestValues.BOT_API_TOKEN
	assert _.base_url == "https://api.telegram.org/bot%s" % TestValues.BOT_API_TOKEN
	assert _.base_file_url == "https://api.telegram.org/file/bot%s" % TestValues.BOT_API_TOKEN

	assert isinstance(_.request, Request)

	assert _._me is None

	assert _.to_dict() == {
		"id": TestValues.BOT_ID,
		"username": TestValues.BOT_USERNAME,
		"first_name": TestValues.BOT_FIRST_NAME
	}
	assert _.me is not None
	assert isinstance(_.me, User)
	assert _.me.id == TestValues.BOT_ID
	assert _.me.username == TestValues.BOT_USERNAME
	assert _.me.first_name == TestValues.BOT_FIRST_NAME

	assert json.loads(_.to_json()) == {
		"id": TestValues.BOT_ID,
		"username": TestValues.BOT_USERNAME,
		"first_name": TestValues.BOT_FIRST_NAME
	}


def test__bot__init__with_urls():
	_ = Bot(
		token=TestValues.BOT_API_TOKEN,
		base_url="https://api.telegram.org/bot",
		base_file_url="https://api.telegram.org/file/bot"
	)

	assert _.token == TestValues.BOT_API_TOKEN
	assert _.base_url == "https://api.telegram.org/bot%s" % TestValues.BOT_API_TOKEN
	assert _.base_file_url == "https://api.telegram.org/file/bot%s" % TestValues.BOT_API_TOKEN
	assert _._me is None

	assert isinstance(_.request, Request)

	assert _._me is None

	assert _.to_dict() == {
		"id": TestValues.BOT_ID,
		"username": TestValues.BOT_USERNAME,
		"first_name": TestValues.BOT_FIRST_NAME
	}
	assert _.me is not None
	assert isinstance(_.me, User)
	assert _.me.id == TestValues.BOT_ID
	assert _.me.username == TestValues.BOT_USERNAME
	assert _.me.first_name == TestValues.BOT_FIRST_NAME

	assert json.loads(_.to_json()) == {
		"id": TestValues.BOT_ID,
		"username": TestValues.BOT_USERNAME,
		"first_name": TestValues.BOT_FIRST_NAME
	}


def test__bot__init__get_me():
	_ = Bot(
		token=TestValues.BOT_API_TOKEN,
		base_url="https://api.telegram.org/bot",
		base_file_url="https://api.telegram.org/file/bot"
	)

	assert _.token == TestValues.BOT_API_TOKEN
	assert _.base_url == "https://api.telegram.org/bot%s" % TestValues.BOT_API_TOKEN
	assert _.base_file_url == "https://api.telegram.org/file/bot%s" % TestValues.BOT_API_TOKEN
	assert _._me is None

	assert isinstance(_.request, Request)

	assert _.me.id == TestValues.BOT_ID
	assert _.me.first_name == TestValues.BOT_FIRST_NAME
	assert _.me.username == TestValues.BOT_USERNAME
	assert isinstance(_._me, User)

	assert _.link == "https://t.me/%s" % TestValues.BOT_USERNAME
	assert _.tg_link == "tg://resolve?domain=%s" % TestValues.BOT_USERNAME

	assert _.to_dict() == {
		"id": TestValues.BOT_ID,
		"username": TestValues.BOT_USERNAME,
		"first_name": TestValues.BOT_FIRST_NAME
	}
	assert json.loads(_.to_json()) == {
		"id": TestValues.BOT_ID,
		"username": TestValues.BOT_USERNAME,
		"first_name": TestValues.BOT_FIRST_NAME
	}

def test__bot__get_me():
	_ = Bot(token=TestValues.BOT_API_TOKEN)

	result = _.get_me()

	assert result.is_bot is True
	assert result.id == TestValues.BOT_ID
	assert result.first_name == TestValues.BOT_FIRST_NAME
	assert result.username == TestValues.BOT_USERNAME


def test__bot__build_chat_id__int_above_zero():
	chat_id = Bot.build_chat_id(chat_id=123)

	assert chat_id == -123


def test__bot__build_chat_id__int_below_zero():
	chat_id = Bot.build_chat_id(chat_id=-123)

	assert chat_id == -123


def test__bot__build_chat_id__username_without_at():
	chat_id = Bot.build_chat_id(chat_id="username")

	assert chat_id == "@username"


def test__bot__build_chat_id__username_with_at():
	chat_id = Bot.build_chat_id(chat_id="@username")

	assert chat_id == "@username"


def test__bot__webhook():
	_ = Bot(token=TestValues.BOT_API_TOKEN)

	result = _.set_webhook(
		url="https://telegram.org",
		max_connections=100
	)
	assert result is True

	result = _.get_webhook_info()
	assert result.url == "https://telegram.org"
	assert result.max_connections == 100
	assert result.allowed_updates == ["message", "callback_query"]
	assert result.has_custom_certificate is False
	assert result.pending_update_count == 0
	assert result.ip_address is not None
	assert result.ip_address == "149.154.167.99"  # TODO:
	assert result.last_error_date is None
	assert result.last_error_message is None

	result = _.delete_webhook()
	assert result is True

	result = _.get_webhook_info()
	assert result.url == ""
	assert result.max_connections is None
	assert result.allowed_updates == ["message", "callback_query"]
	assert result.has_custom_certificate is False
	assert result.pending_update_count == 0
	assert result.ip_address is None
	assert result.last_error_date is None
	assert result.last_error_message is None

	time.sleep(2)

	result = _.set_webhook(
		url="https://telegram.org",
		allowed_updates=["message"],
		ip_address="149.154.167.99",
		drop_pending_updates=True
	)
	assert result is True

	result = _.get_webhook_info()
	assert result.url == "https://telegram.org"
	assert result.max_connections == 50
	assert result.allowed_updates == ["message"]
	assert result.has_custom_certificate is False
	assert result.pending_update_count == 0
	assert result.ip_address == "149.154.167.99"
	assert result.last_error_date is None
	assert result.last_error_message is None

	result = _.delete_webhook()
	assert result is True


def test__bot__sendMessage():
	_ = Bot(token=TestValues.BOT_API_TOKEN)

	result = _.send_message(
		chat_id=TestValues.USER_CHAT_ID,
		text="Test 1",
		disable_web_page_preview=None,
		parse_mode=ParseMode.HTML,
		reply_markup=ReplyKeyboardMarkup(
			keyboard=[
				[
					KeyboardButton(
						text="Button"
					)
				]
			],
			resize_keyboard=True
		)
	)

	assert isinstance(result, Message) is True
	assert result.chat.id == TestValues.USER_CHAT_ID
	assert result.chat.type == Chat.PRIVATE
	assert result.text == "Test 1"
	assert result.from_user.first_name == TestValues.BOT_FIRST_NAME
	assert result.from_user.username == TestValues.BOT_USERNAME
	assert result.from_user.is_bot is True
	assert result.from_user.id == TestValues.BOT_ID
	assert result.date is not None
	assert isinstance(result.date, int) is True
	assert result.message_id is not None
	assert isinstance(result.message_id, int) is True
	assert result.reply_markup is None

	# Long text. More than 4000
	text = "".join((str(i) for i in range(MAX_MESSAGE_LENGTH + 10)))
	result = _.send_message(
		chat_id=TestValues.USER_CHAT_ID,
		text=text,
		disable_web_page_preview=None,
		parse_mode=ParseMode.HTML,
		reply_markup=ReplyKeyboardMarkup(
			keyboard=[
				[
					KeyboardButton(
						text="Button"
					)
				]
			],
			resize_keyboard=True
		)
	)

	assert isinstance(result, Message) is True
	assert result.chat.id == TestValues.USER_CHAT_ID
	assert result.chat.type == Chat.PRIVATE
	assert result.text == text[:4096]
	assert result.from_user.first_name == TestValues.BOT_FIRST_NAME
	assert result.from_user.username == TestValues.BOT_USERNAME
	assert result.from_user.is_bot is True
	assert result.from_user.id == TestValues.BOT_ID
	assert result.date is not None
	assert isinstance(result.date, int) is True
	assert result.message_id is not None
	assert isinstance(result.message_id, int) is True
	assert result.reply_markup is None


	# With inline
	result = _.send_message(
		chat_id=TestValues.USER_CHAT_ID,
		text="Test 2",
		disable_web_page_preview=True,
		reply_markup=InlineKeyboardMarkup(
			inline_keyboard=[
				[
					InlineKeyboardButton(
						text="Button",
						callback_data="callback_data"
					)
				]
			]
		)
	)

	assert isinstance(result, Message) is True
	assert result.chat.id == TestValues.USER_CHAT_ID
	assert result.chat.type == Chat.PRIVATE
	assert result.text == "Test 2"
	assert result.from_user.first_name == TestValues.BOT_FIRST_NAME
	assert result.from_user.username == TestValues.BOT_USERNAME
	assert result.from_user.is_bot is True
	assert result.from_user.id == TestValues.BOT_ID
	assert result.date is not None
	assert isinstance(result.date, int) is True
	assert result.message_id is not None
	assert isinstance(result.message_id, int) is True
	assert result.reply_markup is not None
	assert isinstance(result.reply_markup, InlineKeyboardMarkup) is True
	assert isinstance(result.reply_markup.inline_keyboard[0][0], InlineKeyboardButton) is True
	assert result.reply_markup.inline_keyboard[0][0].text == "Button"
	assert result.reply_markup.inline_keyboard[0][0].callback_data == "callback_data"


def test__bot__sendPhoto():
	_ = Bot(token=TestValues.BOT_API_TOKEN)

	result = _.send_photo(
		chat_id=TestValues.USER_CHAT_ID,
		photo=open("./tests/data/img.jpeg", "rb").read(),
		file_name="img.jpeg",
		caption="<b>caption</b>",
		parse_mode=ParseMode.HTML,
		disable_notification=None
	)

	assert isinstance(result, Message) is True
	assert result.caption == "caption"
	assert result.caption_entities is not None
	assert isinstance(result.caption_entities, list)
	assert isinstance(result.caption_entities[0], MessageEntity)
	assert result.caption_entities[0].type == "bold"
	assert result.caption_entities[0].offset == 0
	assert result.caption_entities[0].length == 7
	assert isinstance(result.photo, list) is True
	assert isinstance(result.photo[0], PhotoSize) is True

	# No caption
	result = _.send_photo(
		chat_id=TestValues.USER_CHAT_ID,
		photo=open("./tests/data/img.jpeg", "rb").read(),
		file_name="img.jpeg"
	)

	assert isinstance(result, Message) is True
	assert result.caption is None
	assert result.caption_entities == []
	assert isinstance(result.photo, list) is True
	assert isinstance(result.photo[0], PhotoSize) is True

	# Caption max length
	caption = "".join(str(i) for i in range(MAX_CAPTION_LENGTH + 10))
	result = _.send_photo(
		chat_id=TestValues.USER_CHAT_ID,
		photo=open("./tests/data/img.jpeg", "rb").read(),
		file_name="img.jpeg",
		caption=caption,
		parse_mode=None,
		disable_notification=None
	)

	assert isinstance(result, Message) is True
	assert result.caption == caption[:MAX_CAPTION_LENGTH]
	assert result.caption_entities == []
	assert isinstance(result.photo, list) is True
	assert isinstance(result.photo[0], PhotoSize) is True


def test__bot__sendVideo():
	_ = Bot(token=TestValues.BOT_API_TOKEN)

	result = _.send_video(
		chat_id=TestValues.USER_CHAT_ID,
		video=open("./tests/data/mp4.mp4", "rb").read(),
		file_name="mp4.mp4",
		caption="<b>Video caption</b>",
		parse_mode=ParseMode.HTML,
		disable_notification=None,
		width=600,
		height=600,
		duration=100,
		supports_streaming=False
	)

	assert isinstance(result, Message) is True
	assert result.caption == "Video caption"
	assert result.caption_entities is not None
	assert isinstance(result.caption_entities, list)
	assert isinstance(result.caption_entities[0], MessageEntity)
	assert result.caption_entities[0].type == "bold"
	assert result.caption_entities[0].offset == 0
	assert result.caption_entities[0].length == 13
	assert isinstance(result.video, Video) is True
	assert result.video.width == 600
	assert result.video.height == 600
	assert result.video.duration == 100

	# No caption
	result = _.send_video(
		chat_id=TestValues.USER_CHAT_ID,
		video=open("./tests/data/mp4.mp4", "rb").read(),
		file_name="mp4.mp4"
	)

	assert isinstance(result, Message) is True
	assert result.caption is None
	assert result.caption_entities == []
	assert isinstance(result.video, Video) is True

	# Caption max length
	caption = "".join(str(i) for i in range(MAX_CAPTION_LENGTH + 10))
	result = _.send_video(
		chat_id=TestValues.USER_CHAT_ID,
		video=open("./tests/data/mp4.mp4", "rb").read(),
		file_name="mp4.mp4",
		caption=caption,
		parse_mode=None,
		disable_notification=None
	)

	assert isinstance(result, Message) is True
	assert result.caption == caption[:MAX_CAPTION_LENGTH]
	assert result.caption_entities == []
	assert isinstance(result.video, Video) is True

	# Just Video
	result = _.send_video(
		chat_id=TestValues.USER_CHAT_ID,
		video=open("./tests/data/mp4.mp4", "rb").read(),
		file_name="mp4.mp4"
	)

	assert isinstance(result, Message) is True
	assert result.caption is None
	assert result.caption_entities == []
	assert isinstance(result.video, Video) is True

	# assert result.video.duration == 126  # From meta  0
	assert result.video.height == 320  # From meta
	assert result.video.width == 320  # From meta
	assert result.video.file_unique_id is not None
	assert result.video.file_id is not None
	assert result.video.file_name == "mp4.mp4"
	assert result.video.file_size == 10546620  # From meta
	assert result.video.mime_type == "video/mp4"  # From meta


def test__bot__sendAudio():
	_ = Bot(token=TestValues.BOT_API_TOKEN)

	result = _.send_audio(
		chat_id=TestValues.USER_CHAT_ID,
		audio=open("./tests/data/mp3.mp3", "rb").read(),
		file_name="mp3.mp3",
		title="Audio 1",
		performer="Evgeniy Privalov",
		duration=100,
		caption="<b>Audio caption</b>",
		parse_mode=ParseMode.HTML,
		disable_notification=None
	)

	assert isinstance(result, Message) is True
	assert result.caption == "Audio caption"
	assert result.caption_entities is not None
	assert isinstance(result.caption_entities, list)
	assert isinstance(result.caption_entities[0], MessageEntity)
	assert result.caption_entities[0].type == "bold"
	assert result.caption_entities[0].offset == 0
	assert result.caption_entities[0].length == 13

	assert isinstance(result.audio, Audio) is True
	assert result.audio.file_id is not None
	assert result.audio.title == "Audio 1"
	assert result.audio.duration == 100
	assert result.audio.performer == "Evgeniy Privalov"

	# No caption
	result = _.send_audio(
		chat_id=TestValues.USER_CHAT_ID,
		audio=open("./tests/data/mp3.mp3", "rb").read(),
		file_name="mp3.mp3",
		duration=101,
		title="Audio 2",
		performer="Evgeniy Privalov"
	)

	assert isinstance(result, Message) is True
	assert result.caption is None
	assert result.caption_entities == []

	assert isinstance(result.audio, Audio) is True
	assert result.audio.file_id is not None
	assert result.audio.title == "Audio 2"
	assert result.audio.duration == 101
	assert result.audio.performer == "Evgeniy Privalov"

	# Caption max length
	caption = "".join(str(i) for i in range(MAX_CAPTION_LENGTH + 10))
	result = _.send_audio(
		chat_id=TestValues.USER_CHAT_ID,
		audio=open("./tests/data/mp3.mp3", "rb").read(),
		file_name="mp3.mp3",
		title="Audio 3",
		performer="Evgeniy Privalov",
		duration=102,
		caption=caption,
		parse_mode=None,
		disable_notification=None
	)

	assert isinstance(result, Message) is True
	assert result.caption == caption[:MAX_CAPTION_LENGTH]
	assert result.caption_entities == []

	assert isinstance(result.audio, Audio) is True
	assert result.audio.file_id is not None
	assert result.audio.title == "Audio 3"
	assert result.audio.duration == 102
	assert result.audio.performer == "Evgeniy Privalov"

	# Just Audio
	result = _.send_audio(
		chat_id=TestValues.USER_CHAT_ID,
		audio=open("./tests/data/mp3.mp3", "rb").read(),
		file_name="mp3.mp3"
	)

	assert isinstance(result, Message) is True
	assert result.caption is None
	assert result.caption_entities == []

	assert isinstance(result.audio, Audio) is True
	assert result.audio.file_id is not None
	assert result.audio.title == "Impact Moderato"  # From meta
	assert result.audio.duration == 27  # From meta
	assert result.audio.performer == "Kevin MacLeod"  # From meta
	assert result.audio.file_id is not None
	assert result.audio.file_name == "mp3.mp3"
	assert result.audio.file_size == 764176  # From meta
	assert result.audio.file_unique_id is not None
	assert result.audio.mime_type == "audio/mpeg"


def test__bot__sendVoice():
	_ = Bot(token=TestValues.BOT_API_TOKEN)

	result = _.send_voice(
		chat_id=TestValues.USER_CHAT_ID,
		voice=open("./tests/data/ogg.ogg", "rb").read(),
		file_name="ogg.ogg",
		duration=100,
		caption="<b>Voice caption</b>",
		parse_mode=ParseMode.HTML,
		disable_notification=None
	)

	assert isinstance(result, Message) is True
	assert result.caption == "Voice caption"
	assert result.caption_entities is not None
	assert isinstance(result.caption_entities, list)
	assert isinstance(result.caption_entities[0], MessageEntity)
	assert result.caption_entities[0].type == "bold"
	assert result.caption_entities[0].offset == 0
	assert result.caption_entities[0].length == 13

	assert isinstance(result.voice, Voice) is True
	assert result.voice.file_id is not None

	# No caption
	result = _.send_voice(
		chat_id=TestValues.USER_CHAT_ID,
		voice=open("./tests/data/ogg.ogg", "rb").read(),
		file_name="ogg.ogg",
		duration=101
	)

	assert isinstance(result, Message) is True
	assert result.caption is None
	assert result.caption_entities == []

	assert isinstance(result.voice, Voice) is True
	assert result.voice.file_id is not None
	assert result.voice.duration == 101

	# Caption max length
	caption = "".join(str(i) for i in range(MAX_CAPTION_LENGTH + 10))
	result = _.send_voice(
		chat_id=TestValues.USER_CHAT_ID,
		voice=open("./tests/data/ogg.ogg", "rb").read(),
		file_name="ogg.ogg",
		duration=102,
		caption=caption,
		parse_mode=None,
		disable_notification=None
	)

	assert isinstance(result, Message) is True
	assert result.caption == caption[:MAX_CAPTION_LENGTH]
	assert result.caption_entities == []

	assert isinstance(result.voice, Voice) is True
	assert result.voice.file_id is not None
	assert result.voice.duration == 102

	# Just Audio
	result = _.send_voice(
		chat_id=TestValues.USER_CHAT_ID,
		voice=open("./tests/data/ogg.ogg", "rb").read(),
		file_name="ogg.ogg"
	)

	assert isinstance(result, Message) is True
	assert result.caption is None
	assert result.caption_entities == []

	assert isinstance(result.voice, Voice) is True
	assert result.voice.file_id is not None
	assert result.voice.file_id is not None
	assert result.voice.file_size == 1089524  # From meta
	assert result.voice.file_unique_id is not None
	assert result.voice.mime_type == "audio/ogg"


def test__bot__sendDocument():
	_ = Bot(token=TestValues.BOT_API_TOKEN)

	result = _.send_document(
		chat_id=TestValues.USER_CHAT_ID,
		document=open("./tests/data/pdf.pdf", "rb").read(),
		file_name="pdf.pdf",
		caption="<b>Document caption</b>",
		parse_mode=ParseMode.HTML,
		disable_notification=None,
		disable_content_type_detection=True
	)

	assert isinstance(result, Message) is True
	assert result.caption == "Document caption"
	assert result.caption_entities is not None
	assert isinstance(result.caption_entities, list)
	assert isinstance(result.caption_entities[0], MessageEntity)
	assert result.caption_entities[0].type == "bold"
	assert result.caption_entities[0].offset == 0
	assert result.caption_entities[0].length == 16

	assert isinstance(result.document, Document) is True
	assert result.document.file_id is not None
	assert result.document.file_unique_id is not None
	assert result.document.file_size == 100463  # From meta
	assert result.document.file_name == "pdf.pdf"

	# No caption
	result = _.send_document(
		chat_id=TestValues.USER_CHAT_ID,
		document=open("./tests/data/pdf.pdf", "rb").read(),
		file_name="pdf.pdf"
	)

	assert isinstance(result, Message) is True
	assert result.caption is None
	assert result.caption_entities == []

	assert isinstance(result.document, Document) is True
	assert result.document.file_id is not None

	# Caption max length
	caption = "".join(str(i) for i in range(MAX_CAPTION_LENGTH + 10))
	result = _.send_document(
		chat_id=TestValues.USER_CHAT_ID,
		document=open("./tests/data/pdf.pdf", "rb").read(),
		file_name="pdf.pdf",
		caption=caption,
		parse_mode=None,
		disable_notification=None
	)

	assert isinstance(result, Message) is True
	assert result.caption == caption[:MAX_CAPTION_LENGTH]
	assert result.caption_entities == []

	assert isinstance(result.document, Document) is True
	assert result.document.file_id is not None

	# Just Document
	result = _.send_document(
		chat_id=TestValues.USER_CHAT_ID,
		document=open("./tests/data/pdf.pdf", "rb").read(),
		file_name="pdf.pdf"
	)

	assert isinstance(result, Message) is True
	assert result.caption is None
	assert result.caption_entities == []

	assert isinstance(result.document, Document) is True
	assert result.document.file_id is not None
	assert result.document.file_id is not None
	assert result.document.file_name == "pdf.pdf"
	assert result.document.file_size == 100463  # From meta
	assert result.document.file_unique_id is not None
	assert result.document.mime_type == "application/pdf"


def test__bot__sendContact():
	_ = Bot(token=TestValues.BOT_API_TOKEN)

	result = _.send_contact(
		chat_id=TestValues.USER_CHAT_ID,
		phone_number="76665554433",
		first_name="Evgeniy",
		last_name="Privalov"
	)

	assert isinstance(result, Message) is True

	assert isinstance(result.contact, Contact) is True
	assert result.contact.user_id is None
	assert result.contact.phone_number == "76665554433"
	assert result.contact.first_name == "Evgeniy"
	assert result.contact.last_name == "Privalov"

	result = _.send_contact(
		chat_id=TestValues.USER_CHAT_ID,
		contact=Contact(
			# user_id=TestValues.USER_CHAT_ID,
			phone_number="76665554433",
			first_name="Evgeniy",
			last_name="Privalov"
		)
	)

	assert isinstance(result, Message) is True
	assert isinstance(result.contact, Contact) is True
	# assert result.contact.user_id == TestValues.USER_CHAT_ID
	assert result.contact.user_id is None
	assert result.contact.phone_number == "76665554433"
	assert result.contact.first_name == "Evgeniy"
	assert result.contact.last_name == "Privalov"


def test__bot__sendLocation():
	_ = Bot(token=TestValues.BOT_API_TOKEN)

	# As LAT - LNG
	result_1 = _.send_location(
		chat_id=TestValues.USER_CHAT_ID,
		latitude=62.098818,
		longitude=7.191824,
		reply_markup=ReplyKeyboardMarkup(
			keyboard=[
				[
					KeyboardButton(
						text="Button"
					)
				]
			],
			resize_keyboard=True
		),
		disable_notification=True,
		allow_sending_without_reply=True
	)

	assert isinstance(result_1, Message) is True

	assert isinstance(result_1.location, Location) is True
	assert result_1.location.latitude == 62.098818
	assert result_1.location.longitude == 7.191824
	assert result_1.location.horizontal_accuracy is None
	assert result_1.location.live_period is None
	assert result_1.location.heading is None
	assert result_1.location.proximity_alert_radius is None

	# AS Location Instance
	result_2 = _.send_location(
		chat_id=TestValues.USER_CHAT_ID,
		location=Location(
			latitude=62.098818,
			longitude=7.191824
		),
		allow_sending_without_reply=True,
		disable_notification=True,
		reply_markup=ReplyKeyboardMarkup(
			keyboard=[
				[
					KeyboardButton(
						text="Button"
					)
				]
			],
			resize_keyboard=True
		)
	)

	assert isinstance(result_2, Message) is True

	assert isinstance(result_2.location, Location) is True
	assert result_2.location.latitude == 62.098818
	assert result_2.location.longitude == 7.191824
	assert result_2.location.horizontal_accuracy is None
	assert result_2.location.live_period is None
	assert result_2.location.heading is None
	assert result_2.location.proximity_alert_radius is None

	# TODO: Live Locations
