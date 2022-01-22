#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

from typing import (
	TYPE_CHECKING,
	Optional,
	Dict,
	Union
)

from tgsdk import PhotoSize
from tgsdk import TelegramEntity

if TYPE_CHECKING:
	from tgsdk import (
		Bot,
		File
	)


class Document(TelegramEntity):
	"""
	https://core.telegram.org/bots/api#document

	"""
	__slots__ = ("file_id", "file_unique_id", "thumb", "file_name", "mime_type", "file_size", "bot")

	def __init__(
		self,
		file_id: str,
		file_unique_id: str,
		thumb: PhotoSize = None,
		file_name: str = None,
		mime_type: str = None,
		file_size: int = None,

		bot: "Bot" = None
	):
		self.file_id = file_id
		self.file_unique_id = file_unique_id
		self.thumb = thumb
		self.file_name = file_name
		self.mime_type = mime_type
		self.file_size = file_size

		self.bot = bot

	@classmethod
	def de_json(cls, data: Optional[Dict] = None) -> Union["Document", None]:
		"""

		:param data:
		:return:
		"""
		if not data:
			return None

		data["thumb"] = PhotoSize.de_json(data.get("thumb"))

		return cls(**data)

	def get_file(self, timeout: float = None, kwargs: Dict = None) -> "File":
		"""

		:param timeout:
		:param kwargs:
		:return:
		"""
		return self.bot.get_file(file_id=self.file_id, timeout=timeout, kwargs=kwargs)
