#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

from typing import (
	Dict,
	TYPE_CHECKING
)

from tgsdk import TelegramEntity

if TYPE_CHECKING:
	from tgsdk import (
		Bot,
		File
	)


class Voice(TelegramEntity):
	"""
	https://core.telegram.org/bots/api#voice

	"""
	__slots__ = ("file_id", "file_unique_id", "duration", "mime_type", "file_size", "bot")

	def __init__(
		self,
		file_id: str,
		file_unique_id: str,
		duration: int,
		mime_type: str = None,
		file_size: int = None,

		bot: "Bot" = None
	):
		self.file_id = file_id
		self.file_unique_id = file_unique_id
		self.duration = duration
		self.mime_type = mime_type
		self.file_size = file_size

		self.bot = bot

	def get_file(self, timeout: float = None, kwargs: Dict = None) -> "File":
		"""

		:param timeout:
		:param kwargs:
		:return:
		"""
		return self.bot.get_file(file_id=self.file_id, timeout=timeout, kwargs=kwargs)
