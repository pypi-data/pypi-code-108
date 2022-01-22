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


class ChatPhoto(TelegramEntity):
	__slots__ = ("small_file_id", "small_file_unique_id", "big_file_id", "big_file_unique_id", "bot")

	def __init__(
		self,
		small_file_id: str,
		small_file_unique_id: str,
		big_file_id: str,
		big_file_unique_id: str,

		bot: "Bot" = None
	):
		self.small_file_id = small_file_id
		self.small_file_unique_id = small_file_unique_id
		self.big_file_id = big_file_id
		self.big_file_unique_id = big_file_unique_id

		self.bot = bot

	def get_small_file(self, timeout: float = None, kwargs: Dict = None) -> "File":
		"""

		:param timeout:
		:param kwargs:
		:return:
		"""
		return self.bot.get_file(file_id=self.small_file_id, timeout=timeout, kwargs=kwargs)

	def get_big_file(self, timeout: float = None, kwargs: Dict = None) -> "File":
		"""

		:param timeout:
		:param kwargs:
		:return:
		"""
		return self.bot.get_file(file_id=self.big_file_id, timeout=timeout, kwargs=kwargs)
