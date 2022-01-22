#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

from typing import (
	Optional,
	Dict,
	Union
)

from tgsdk import TelegramEntity
from .user import User


class ProximityAlertTriggered(TelegramEntity):
	"""
	https://core.telegram.org/bots/api#proximityalerttriggered

	"""

	__slots__ = ("traveler", "watcher", "distance")

	def __init__(
		self,
		traveler: User,
		watcher: User,
		distance: int
	):
		self.traveler = traveler
		self.watcher = watcher
		self.distance = distance

	@classmethod
	def de_json(cls, data: Optional[Dict] = None) -> Union["ProximityAlertTriggered", None]:
		"""

		:param data:
		:return:
		"""
		if not data:
			return None

		data["traveler"] = User.de_json(data.get("traveler"))
		data["watcher"] = User.de_json(data.get("watcher"))

		return cls(**data)
