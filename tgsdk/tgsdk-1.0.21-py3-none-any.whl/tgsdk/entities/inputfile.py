#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

import imghdr
import mimetypes
import os
from typing import (
	IO,
	Union,
	Tuple
)

from tgsdk import TelegramEntity


class InputFile(TelegramEntity):
	"""
	https://core.telegram.org/bots/api#inputfile

	"""

	__slots__ = ("file", "file_name", "as_attach", "input_file", "_mime_type")

	def __init__(
		self,
		file: Union[bytes, IO],
		file_name: str = None,
		as_attach: bool = None
	):
		self.as_attach = bool(as_attach)

		if file_name:
			self.file_name = file_name
		elif hasattr(file, "name"):
			self.file_name = os.path.basename(file.name)
		else:
			self.file_name = None

		if isinstance(file, bytes):
			self.input_file = file
		else:
			self.input_file = file.read()

		self._mime_type = self.set_mime_type()

	@property
	def tuple_mapping_values(self) -> Tuple[str, bytes, str]:
		"""

		:return:
		"""
		return self.file_name, self.input_file, self._mime_type

	@property
	def file_attach_name(self) -> Union[str, None]:
		"""

		:return:
		"""
		if not self.as_attach:
			return None

		file_name = self.file_name.replace(" ", "_")
		file_attach_name = "".join((i for i in file_name if i.isalnum() or i == "."))

		return "attach://%s" % file_attach_name

	def set_mime_type(self) -> str:
		"""

		:return:
		"""
		mime_type = "application/octet-stream"

		image_mime_type = self.is_image(self.input_file)
		if image_mime_type:
			mime_type = image_mime_type
		elif self.file_name:
			mime_type = mimetypes.guess_type(self.file_name)[0] or mime_type
		else:
			mime_type = mime_type

		return mime_type

	@staticmethod
	def is_image(stream: bytes) -> Union[str, None]:
		"""

		:param stream:
		:return:
		"""
		try:
			image_mime_type = imghdr.what(None, stream)
			if image_mime_type:
				return "image/%s" % image_mime_type
			return None
		except Exception:
			return None

	@staticmethod
	def is_file(file: object) -> bool:
		"""

		:param file:
		:return:
		"""
		return hasattr(file, "read")
