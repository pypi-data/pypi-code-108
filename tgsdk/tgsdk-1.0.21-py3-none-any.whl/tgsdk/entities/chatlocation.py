#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

from typing import (
	Optional,
	Dict,
	Union
)

from tgsdk import TelegramEntity
from tgsdk.entities.files.location import Location


class ChatLocation(TelegramEntity):
	"""
	https://core.telegram.org/bots/api#chatlocation

	"""
	__slots__ = ("location", "address")

	def __init__(
		self,
		location: Location,
		address: str
	):
		self.location = location
		self.address = address

	@classmethod
	def de_json(cls, data: Optional[Dict] = None) -> Union["ChatLocation", None]:
		if not data:
			return None

		data["location"] = Location.de_json(data.get("location"))

		return cls(**data)
