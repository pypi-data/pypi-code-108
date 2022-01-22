#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

from typing import (
	Optional,
	Dict,
	Union
)

from tgsdk import (
	ShippingAddress,
	TelegramEntity
)


class OrderInfo(TelegramEntity):
	"""
	https://core.telegram.org/bots/api#orderinfo

	"""

	__slots__ = ("name", "phone_number", "email", "shipping_address")

	def __init__(
		self,
		name: str = None,
		phone_number: str = None,
		email: str = None,
		shipping_address: ShippingAddress = None
	):
		self.name = name
		self.phone_number = phone_number
		self.email = email
		self.shipping_address = shipping_address

	@classmethod
	def de_json(cls, data: Optional[Dict] = None) -> Union["OrderInfo", None]:
		"""

		:param data:
		:return:
		"""
		if not data:
			return None

		data["shipping_address"] = ShippingAddress.de_json(data.get("shipping_address"))

		return cls(**data)
