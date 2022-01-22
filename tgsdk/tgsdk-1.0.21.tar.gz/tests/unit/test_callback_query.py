#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

import json
import unittest

from tgsdk import CallbackQuery, User, Message, Chat, InlineKeyboardMarkup

user = User(
	id=1234,
	first_name="Evgeniy",
	is_bot=False,
	username="evgeniyprivalov",
	last_name="Privalov",
	language_code="ru"
)

chat = Chat(
	id=1234,
	type=Chat.PRIVATE,
	username="evgeniyprivalov",
	first_name="Evgeniy",
	last_name="Privalov"
)

message = Message(
	message_id=1,
	from_user=user,
	sender_chat=chat,
	date=12368716231,
	chat=chat,
	text="Text"
)


def test__callback_query__init():

	_ = CallbackQuery(
		id="123",
		from_user=user,
		chat_instance="chat_instance",
		message=message,
		inline_message_id="inline_message_id",
		data="data"
	)

	assert _.id == "123"
	assert _.chat_instance == "chat_instance"
	assert _.inline_message_id == "inline_message_id"
	assert _.data == "data"

	assert isinstance(_.message.from_user, User) is True
	assert _.from_user.id == 1234
	assert _.from_user.first_name == "Evgeniy"
	assert _.from_user.is_bot is False
	assert _.from_user.username == "evgeniyprivalov"
	assert _.from_user.last_name == "Privalov"
	assert _.from_user.language_code == "ru"
	assert _.from_user.can_join_groups is None
	assert _.from_user.can_read_all_group_messages is None
	assert _.from_user.supports_inline_queries is None

	assert isinstance(_.message.sender_chat, Chat) is True

	assert isinstance(_.message.chat, Chat) is True
	assert _.message.message_id == 1
	assert _.message.date == 12368716231
	assert _.message.text == "Text"

	assert _.message.from_user.id == 1234
	assert _.message.from_user.first_name == "Evgeniy"
	assert _.message.from_user.is_bot is False
	assert _.message.from_user.username == "evgeniyprivalov"
	assert _.message.from_user.last_name == "Privalov"
	assert _.message.from_user.language_code == "ru"
	assert _.message.from_user.can_join_groups is None
	assert _.message.from_user.can_read_all_group_messages is None
	assert _.message.from_user.supports_inline_queries is None
	assert _.message.sender_chat.id == 1234
	assert _.message.sender_chat.type == "private"
	assert _.message.sender_chat.username == "evgeniyprivalov"
	assert _.message.sender_chat.first_name == "Evgeniy"
	assert _.message.sender_chat.last_name == "Privalov"

	assert _.message.forward_from is None
	assert _.message.forward_from_chat is None
	assert _.message.forward_from_message_id is None
	assert _.message.forward_signature is None
	assert _.message.forward_sender_name is None
	assert _.message.forward_date is None
	assert _.message.reply_to_message is None
	assert _.message.via_bot is None
	assert _.message.edit_date is None
	assert _.message.media_group_id is None
	assert _.message.author_signature is None
	assert _.message.entities is None
	assert _.message.animation is None
	assert _.message.audio is None
	assert _.message.document is None
	assert _.message.photo is None
	assert _.message.sticker is None
	assert _.message.video is None
	assert _.message.video_note is None
	assert _.message.voice is None
	assert _.message.caption is None
	assert _.message.caption_entities is None
	assert _.message.contact is None
	assert _.message.venue is None
	assert _.message.location is None
	assert _.message.new_chat_members is None
	assert _.message.left_chat_member is None
	assert _.message.new_chat_title is None
	assert _.message.new_chat_photo is None
	assert _.message.delete_chat_photo is None
	assert _.message.group_chat_created is None
	assert _.message.supergroup_chat_created is None
	assert _.message.channel_chat_created is None
	assert _.message.migrate_to_chat_id is None
	assert _.message.migrate_from_chat_id is None
	assert _.message.pinned_message is None
	assert _.message.invoice is None
	assert _.message.successful_payment is None
	assert _.message.connected_website is None
	assert _.message.passport_data is None
	assert _.message.proximity_alert_triggered is None
	assert _.message.reply_markup is None

	assert _.message.bot is None


def test__callbackquery__to_dict():
	_ = CallbackQuery(
		id="123",
		from_user=user,
		chat_instance="chat_instance",
		message=message,
		inline_message_id="inline_message_id",
		data="data"
	)

	unittest.TestCase().assertDictEqual(
		_.to_dict(),
		{
			"id": "123",
			"from": {
				"id": 1234,
				"first_name": "Evgeniy",
				"is_bot": False,
				"username": "evgeniyprivalov",
				"last_name": "Privalov",
				"language_code": "ru"
			},
			"chat_instance": "chat_instance",
			"message": {
				"message_id": 1,
				"from": {
					"id": 1234,
					"first_name": "Evgeniy",
					"is_bot": False,
					"username": "evgeniyprivalov",
					"last_name": "Privalov",
					"language_code": "ru"
				},
				"sender_chat": {
					"id": 1234,
					"type": "private",
					"username": "evgeniyprivalov",
					"first_name": "Evgeniy",
					"last_name": "Privalov"
				},
				"date": 12368716231,
				"chat": {
					"id": 1234,
					"type": "private",
					"username": "evgeniyprivalov",
					"first_name": "Evgeniy",
					"last_name": "Privalov"
				},
				"text": "Text"
			},
			"inline_message_id": "inline_message_id",
			"data": "data"
		}
	)


def test__callbackquery__de_json():
	data = {
		"id": "123",
		"inline_message_id": "inline_message_id",
		"data": "data",
		"chat_instance": "chat_instance",
		"from": {
			"id": 1234,
			"first_name": "Evgeniy",
			"is_bot": False,
			"username": "evgeniyprivalov",
			"last_name": "Privalov",
			"language_code": "ru"
		},
		"message": {
			"message_id": 1,
			"from": {
				"id": 1234,
				"first_name": "Evgeniy",
				"is_bot": False,
				"username": "evgeniyprivalov",
				"last_name": "Privalov",
				"language_code": "ru"
			},
			"sender_chat": {
				"id": 1234,
				"type": "private",
				"username": "evgeniyprivalov",
				"first_name": "Evgeniy",
				"last_name": "Privalov"
			},
			"date": 12368716231,
			"chat": {
				"id": 1234,
				"type": "private",
				"username": "evgeniyprivalov",
				"first_name": "Evgeniy",
				"last_name": "Privalov"
			},
			"text": "Text",
			"reply_markup": {
				"inline_keyboard": [
					[
						{
							"text": "inline",
							"callback_data": "data"
						}
					]
				]
			}
		}
	}

	_ = CallbackQuery.de_json(data)

	assert isinstance(_, CallbackQuery) is True

	assert _.id == "123"
	assert _.chat_instance == "chat_instance"
	assert _.inline_message_id == "inline_message_id"
	assert _.data == "data"

	assert isinstance(_.message.from_user, User) is True
	assert _.from_user.id == 1234
	assert _.from_user.first_name == "Evgeniy"
	assert _.from_user.is_bot is False
	assert _.from_user.username == "evgeniyprivalov"
	assert _.from_user.last_name == "Privalov"
	assert _.from_user.language_code == "ru"
	assert _.from_user.can_join_groups is None
	assert _.from_user.can_read_all_group_messages is None
	assert _.from_user.supports_inline_queries is None

	assert isinstance(_.message.sender_chat, Chat) is True

	assert isinstance(_.message.chat, Chat) is True
	assert _.message.message_id == 1
	assert _.message.date == 12368716231
	assert _.message.text == "Text"

	assert _.message.from_user.id == 1234
	assert _.message.from_user.first_name == "Evgeniy"
	assert _.message.from_user.is_bot is False
	assert _.message.from_user.username == "evgeniyprivalov"
	assert _.message.from_user.last_name == "Privalov"
	assert _.message.from_user.language_code == "ru"
	assert _.message.from_user.can_join_groups is None
	assert _.message.from_user.can_read_all_group_messages is None
	assert _.message.from_user.supports_inline_queries is None
	assert _.message.sender_chat.id == 1234
	assert _.message.sender_chat.type == "private"
	assert _.message.sender_chat.username == "evgeniyprivalov"
	assert _.message.sender_chat.first_name == "Evgeniy"
	assert _.message.sender_chat.last_name == "Privalov"

	assert _.message.forward_from is None
	assert _.message.forward_from_chat is None
	assert _.message.forward_from_message_id is None
	assert _.message.forward_signature is None
	assert _.message.forward_sender_name is None
	assert _.message.forward_date is None
	assert _.message.reply_to_message is None
	assert _.message.via_bot is None
	assert _.message.edit_date is None
	assert _.message.media_group_id is None
	assert _.message.author_signature is None
	assert _.message.entities == []
	assert _.message.animation is None
	assert _.message.audio is None
	assert _.message.document is None
	assert _.message.photo == []
	assert _.message.sticker is None
	assert _.message.video is None
	assert _.message.video_note is None
	assert _.message.voice is None
	assert _.message.caption is None
	assert _.message.caption_entities == []
	assert _.message.contact is None
	assert _.message.venue is None
	assert _.message.location is None
	assert _.message.new_chat_members == []
	assert _.message.left_chat_member is None
	assert _.message.new_chat_title is None
	assert _.message.new_chat_photo == []
	assert _.message.delete_chat_photo is None
	assert _.message.group_chat_created is None
	assert _.message.supergroup_chat_created is None
	assert _.message.channel_chat_created is None
	assert _.message.migrate_to_chat_id is None
	assert _.message.migrate_from_chat_id is None
	assert _.message.pinned_message is None
	assert _.message.invoice is None
	assert _.message.successful_payment is None
	assert _.message.connected_website is None
	assert _.message.passport_data is None
	assert _.message.proximity_alert_triggered is None

	assert isinstance(_.message.reply_markup, InlineKeyboardMarkup) is True
	assert _.message.reply_markup.inline_keyboard[0][0].text == "inline"
	assert _.message.reply_markup.inline_keyboard[0][0].callback_data == "data"

	assert _.message.bot is None


def test__callbackquery__de_json__data_is_none():
	data = None

	_ = CallbackQuery.de_json(data)

	assert _ is None
