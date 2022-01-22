#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

from typing import (
	Optional,
	Dict,
	Union
)

from tgsdk import TelegramEntity
from tgsdk import User


class MessageEntity(TelegramEntity):
	"""
	https://core.telegram.org/bots/api#messageentity

	"""

	__slots__ = ("type", "offset", "length", "url", "user", "language")

	def __init__(
		self,
		type: str,
		offset: int,
		length: int,
		url: str = None,
		user: User = None,
		language: str = None
	):
		self.type = type
		self.offset = offset
		self.length = length
		self.url = url
		self.user = user
		self.language = language

	@classmethod
	def de_json(cls, data: Optional[Dict] = None) -> Union["MessageEntity", None]:
		"""

		:param data:
		:return:
		"""
		if not data:
			return None

		data["user"] = User.de_json(data.get("user"))

		return cls(**data)
