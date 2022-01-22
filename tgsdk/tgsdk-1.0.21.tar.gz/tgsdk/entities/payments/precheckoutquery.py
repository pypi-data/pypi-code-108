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
	OrderInfo,
	TelegramEntity
)


class PreCheckoutQuery(TelegramEntity):
	"""
	https://core.telegram.org/bots/api/#precheckoutquery

	"""

	__slots__ = ("id", "from_user", "currency", "total_amount", "invoice_payload", "shipping_option_id", "order_info")

	def __init__(
		self,
		id: str,
		from_user: User,
		currency: str,
		total_amount: int,
		invoice_payload: str,
		shipping_option_id: Optional[str] = None,
		order_info: Optional[OrderInfo] = None,
		**_kwargs: Any
	):
		self.id = id
		self.from_user = from_user
		self.currency = currency
		self.total_amount = total_amount
		self.invoice_payload = invoice_payload
		self.shipping_option_id = shipping_option_id
		self.order_info = order_info

	@classmethod
	def de_json(cls, data: Optional[Dict] = None) -> Union["PreCheckoutQuery", None]:
		"""

		:param data:
		:return:
		"""
		if not data:
			return None

		data["from_user"] = User.de_json(data.get("from"))
		data["order_info"] = OrderInfo.de_json(data.get("order_info"))

		return cls(**data)
