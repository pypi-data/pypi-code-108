#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

from typing import (
	List,
	Optional,
	Dict,
	Union
)

from tgsdk import LabeledPrice
from tgsdk import TelegramEntity


class ShippingOption(TelegramEntity):
	"""
	https://core.telegram.org/bots/api/#shippingoption

	"""

	__slots__ = ("id", "title", "prices")

	def __init__(
		self,
		id: str,
		title: str,
		prices: List[LabeledPrice]
	):
		self.id = id
		self.title = title
		self.prices = prices

	def to_dict(self) -> Dict:
		"""

		:return:
		"""
		data = super().to_dict()

		data["prices"] = []
		for price in self.prices:
			data["prices"].append(price.to_dict())

		return data

	@classmethod
	def de_json(cls, data: Optional[Dict] = None) -> Union["ShippingOption", None]:
		"""

		"""
		if not data:
			return None

		data["prices"] = LabeledPrice.de_list(data.get("prices"))

		return cls(**data)
