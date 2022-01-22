#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

from typing import (
	Optional,
	List,
	Dict,
	Union
)

from tgsdk import TelegramEntity
from tgsdk.entities.files.photosize import PhotoSize


class UserProfilePhotos(TelegramEntity):
	"""
	https://core.telegram.org/bots/api#userprofilephotos

	"""

	__slots__ = ("total_count", "photos")

	def __init__(
		self,
		total_count: int,
		photos: List[List[PhotoSize]]
	):
		self.total_count = total_count
		self.photos = photos

	@classmethod
	def de_json(cls, data: Optional[Dict] = None) -> Union["UserProfilePhotos", None]:
		"""

		:param data:
		:return:
		"""
		if not data:
			return None

		data["photos"] = [PhotoSize.de_list(photo) for photo in data["photos"]]

		return cls(**data)

	def to_dict(self) -> Dict:
		"""

		:return:
		"""
		data = super().to_dict()

		data["photos"] = []
		for photo in self.photos:
			row_photos = []

			for _photo in photo:
				if isinstance(_photo, PhotoSize):
					row_photos.append(_photo.to_dict())

			if row_photos:
				data["photos"].append(row_photos)

		return data
