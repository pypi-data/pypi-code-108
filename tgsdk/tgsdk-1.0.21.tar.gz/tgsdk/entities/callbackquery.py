#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

from typing import (
	Optional,
	Union,
	Dict
)

from tgsdk import (
	User,
	Message
)
from .base import TelegramEntity


class CallbackQuery(TelegramEntity):
	"""
	https://core.telegram.org/bots/api#callbackquery

	"""

	__slots__ = ("id", "from_user", "chat_instance", "message", "inline_message_id", "data")

	def __init__(
		self,
		id: str,
		from_user: User,
		chat_instance: str,
		message: Message = None,
		inline_message_id: str = None,
		data: str = None,
		# game_short_name: str = None
	):
		self.id = id
		self.from_user = from_user
		self.message = message
		self.inline_message_id = inline_message_id
		self.chat_instance = chat_instance
		self.data = data

	# self.game_short_name = game_short_name

	@classmethod
	def de_json(cls, data: Optional[Dict] = None) -> Union["CallbackQuery", None]:
		"""

		:param data:
		:return:
		"""
		if not data:
			return None

		data["from_user"] = User.de_json(data.get("from"))
		data["message"] = Message.de_json(data.get("message"))

		del data["from"]  # TODO:

		return cls(**data)
