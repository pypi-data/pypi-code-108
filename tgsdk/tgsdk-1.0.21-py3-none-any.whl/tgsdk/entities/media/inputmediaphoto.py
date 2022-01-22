#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

from typing import (
	Any,
	Union,
	List
)

from tgsdk import (
	PhotoSize,
	InputMedia,
	MessageEntity
)
from tgsdk.utils.get_input_file import get_input_file
from tgsdk.utils.types import FileInput


class InputMediaPhoto(InputMedia):
	__slots__ = ("media", "caption", "parse_mode", "caption_entities", "file_name")

	def __init__(
		self,
		media: Union[FileInput, PhotoSize],
		caption: str = None,
		parse_mode: str = None,
		caption_entities: List[MessageEntity] = None,
		file_name: str = None,
		**_kwargs: Any
	):
		super().__init__(
			type="photo",
			caption_entities=caption_entities
		)

		self.media = media
		self.caption = caption
		self.parse_mode = parse_mode
		self.file_name = file_name

		self.media = get_input_file(media, PhotoSize, as_attach=True, file_name=self.file_name)
