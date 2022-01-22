#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

from typing import (
	Any,
	Optional,
	Dict,
	Union
)

from tgsdk import (
	User,
	ShippingAddress,
	TelegramEntity
)


class ShippingQuery(TelegramEntity):
	"""
	https://core.telegram.org/bots/api/#shippingquery

	"""
	__slots__ = ("id", "from_user", "invoice_payload", "shipping_address")

	def __init__(
		self,
		id: str,
		from_user: User,
		invoice_payload: str,
		shipping_address: ShippingAddress,
		**_kwargs: Any
	):
		self.id = id
		self.from_user = from_user
		self.invoice_payload = invoice_payload
		self.shipping_address = shipping_address

	@classmethod
	def de_json(cls, data: Optional[Dict] = None) -> Union["ShippingQuery", None]:
		"""

		:param data:
		:return:
		"""
		if not data:
			return None

		data["from_user"] = User.de_json(data.get("from"))
		data["shipping_address"] = ShippingAddress.de_json(data.get("shipping_address"))

		return cls(**data)
