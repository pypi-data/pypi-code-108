#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

from typing import (
	Optional,
	Dict,
	Union
)

from tgsdk import (
	OrderInfo,
	TelegramEntity
)


class SuccessfulPayment(TelegramEntity):
	"""
	https://core.telegram.org/bots/api#successfulpayment

	"""
	__slots__ = (
		"currency", "total_amount", "invoice_payload", "telegram_payment_charge_id",
		"provider_payment_charge_id", "shipping_option_id", "order_info"
	)

	def __init__(
		self,
		currency: str,
		total_amount: int,
		invoice_payload: str,
		telegram_payment_charge_id: str,
		provider_payment_charge_id: str,
		shipping_option_id: Optional[str] = None,
		order_info: Optional[OrderInfo] = None
	):
		self.currency = currency
		self.total_amount = total_amount
		self.invoice_payload = invoice_payload
		self.telegram_payment_charge_id = telegram_payment_charge_id
		self.provider_payment_charge_id = provider_payment_charge_id
		self.shipping_option_id = shipping_option_id
		self.order_info = order_info

	@classmethod
	def de_json(cls, data: Optional[Dict] = None) -> Union["SuccessfulPayment", None]:
		"""

		:param data:
		:return:
		"""
		if not data:
			return None

		data["order_info"] = OrderInfo.de_json(data.get("order_info"))

		return cls(**data)
