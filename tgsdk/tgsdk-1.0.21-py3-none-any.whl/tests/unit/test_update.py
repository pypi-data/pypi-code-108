#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

import json
import unittest

from tgsdk import (
	CallbackQuery,
	Message,
	Update,
	Chat,
	User
)

_chat = Chat(
	id=1,
	first_name="user1",
	username="user1",
	type=Chat.PRIVATE
)

_user = User(
	id=1,
	username="user1",
	first_name="user1",
	is_bot=False
)


def test__update__init():
	_ = Update(
		update_id=1234567890,
		message=Message(
			message_id=123,
			from_user=_user,
			date=12345,
			chat=_chat,
			text="Message"
		)
	)

	assert _.update_id == 1234567890

	assert _.message.message_id == 123

	assert _.message.from_user.id == 1
	assert _.message.from_user.username == "user1"
	assert _.message.from_user.first_name == "user1"
	assert _.message.from_user.is_bot is False

	assert _.message.date == 12345

	assert _.message.chat.id == 1
	assert _.message.chat.username == "user1"
	assert _.message.chat.first_name == "user1"
	assert _.message.chat.type == "private"

	assert _.message.text == "Message"


def test__update__to_dict():
	_ = Update(
		update_id=1234567890,
		message=Message(
			message_id=123,
			from_user=_user,
			date=12345,
			chat=_chat,
			text="Message"
		)
	)

	unittest.TestCase().assertDictEqual(
		_.to_dict(),
		{
			"update_id": 1234567890,
			"message": {
				"message_id": 123,
				"from": {
					"id": 1,
					"username": "user1",
					"first_name": "user1",
					"is_bot": False
				},
				"date": 12345,
				"chat": {
					"id": 1,
					"type": "private",
					"username": "user1",
					"first_name": "user1"
				},
				"text": "Message"
			}
		}
	)


def test__update__to_json():
	_ = Update(
		update_id=1234567890,
		message=Message(
			message_id=123,
			from_user=_user,
			date=12345,
			chat=_chat,
			text="Message"
		)
	)

	unittest.TestCase().assertDictEqual(
		json.loads(_.to_json()),
		{
			"update_id": 1234567890,
			"message": {
				"message_id": 123,
				"from": {
					"id": 1,
					"username": "user1",
					"first_name": "user1",
					"is_bot": False
				},
				"date": 12345,
				"chat": {
					"id": 1,
					"type": "private",
					"username": "user1",
					"first_name": "user1"
				},
				"text": "Message"
			}
		}
	)


def test__update__de_json():
	data = {
		"update_id": 1234567890,
		"message": {
			"message_id": 123,
			"from": {
				"id": 1,
				"username": "user1",
				"first_name": "user1",
				"is_bot": False
			},
			"date": 12345,
			"chat": {
				"id": 1,
				"type": "private",
				"username": "user1",
				"first_name": "user1"
			},
			"text": "Message"
		}
	}

	_ = Update.de_json(data)

	assert isinstance(_, Update) is True
	assert _.update_id == 1234567890

	assert _.message.message_id == 123

	assert _.message.from_user.id == 1
	assert _.message.from_user.username == "user1"
	assert _.message.from_user.first_name == "user1"
	assert _.message.from_user.is_bot is False

	assert _.message.date == 12345

	assert _.message.chat.id == 1
	assert _.message.chat.username == "user1"
	assert _.message.chat.first_name == "user1"
	assert _.message.chat.type == "private"

	assert _.message.text == "Message"


def test__update__de_json__data_is_none():
	data = None

	_ = Update.de_json(data)

	assert _ is None
