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
		File,
		Bot
	)


class PhotoSize(TelegramEntity):
	"""
	https://core.telegram.org/bots/api#photosize

	"""
	__slots__ = ("file_id", "file_unique_id", "width", "height", "file_size", "bot")

	def __init__(
		self,
		file_id: str,
		file_unique_id: str,
		width: int,
		height: int,
		file_size: int = None,

		bot: "Bot" = None
	):
		self.file_id = file_id
		self.file_unique_id = file_unique_id
		self.width = width
		self.height = height
		self.file_size = file_size

		self.bot = bot

	def get_file(self, timeout: float = None, kwargs: Dict = None) -> "File":
		"""

		:param timeout:
		:param kwargs:
		:return:
		"""
		return self.bot.get_file(file_id=self.file_id, timeout=timeout, kwargs=kwargs)
