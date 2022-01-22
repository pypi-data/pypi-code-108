#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

from typing import (
	Union,
	Dict,
	List
)

from tgsdk import (
	MessageEntity,
	TelegramEntity
)


class InputMedia(TelegramEntity):
	__slots__ = ("type", "caption_entities", "media")

	def __init__(
		self,
		type: str,
		caption_entities: Union[List[MessageEntity], None]
	):
		self.type = type
		self.caption_entities = caption_entities

		self.media = None  # Rewrite in children

	def to_dict(self) -> Dict:
		"""

		:return:
		"""
		data = super().to_dict()

		if self.caption_entities:
			data["caption_entities"] = [caption_entity.to_dict() for caption_entity in self.caption_entities]

		return data
