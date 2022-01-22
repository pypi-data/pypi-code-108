#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

from typing import (
	List,
	Optional,
	Dict,
	Union
)

from tgsdk import ShippingOption
from tgsdk import TelegramEntity


class AnswerShippingQuery(TelegramEntity):
	"""
	https://core.telegram.org/bots/api/#answershippingquery

	"""
	__slots__ = ("shipping_query_id", "ok", "shipping_options", "error_message")

	def __init__(
		self,
		shipping_query_id: str,
		ok: bool,
		shipping_options: List[ShippingOption],
		error_message: str
	):
		self.shipping_query_id = shipping_query_id
		self.ok = ok
		self.shipping_options = shipping_options
		self.error_message = error_message

	def to_dict(self) -> Dict:
		"""

		:return:
		"""
		data = super().to_dict()

		data["shipping_options"] = []
		for shipping_option in self.shipping_options:
			data["shipping_options"].append(shipping_option.to_dict())

		return data

	@classmethod
	def de_json(cls, data: Optional[Dict] = None) -> Union["AnswerShippingQuery", None]:
		"""

		"""
		if not data:
			return None

		data["shipping_options"] = ShippingOption.de_list(data.get("shipping_options"))

		return cls(**data)
