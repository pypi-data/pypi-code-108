#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

from typing import (
	Any,
	Union,
	List
)

from tgsdk import (
	InputFile,
	InputMedia,
	MessageEntity,
	Video
)
from tgsdk.utils.get_input_file import get_input_file


class InputMediaVideo(InputMedia):
	__slots__ = ("media", "thumb", "caption", "parse_mode", "caption_entities", "width", "height", "duration", "supports_streaming", "file_name")

	def __init__(
		self,
		media: Union[InputFile, Video],
		thumb: InputFile = None,
		caption: str = None,
		parse_mode: str = None,
		caption_entities: List[MessageEntity] = None,
		width: int = None,
		height: int = None,
		duration: int = None,
		supports_streaming: bool = None,
		file_name: str = None,
		**_kwargs: Any
	):
		super().__init__(
			type="video",
			caption_entities=caption_entities
		)

		self.media = media
		self.thumb = thumb
		self.caption = caption
		self.parse_mode = parse_mode
		self.file_name = file_name
		self.supports_streaming = supports_streaming

		if isinstance(media, Video):
			self.media = media.file_id  # type: str

			self.width = media.width
			self.height = media.height
			self.duration = media.duration
		else:
			self.media = get_input_file(media, as_attach=True, file_name=self.file_name)

			self.width = width
			self.height = height
			self.duration = duration

		if thumb:
			self.thumb = get_input_file(thumb, as_attach=True)
