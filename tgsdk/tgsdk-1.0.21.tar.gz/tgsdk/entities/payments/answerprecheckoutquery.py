#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

from tgsdk import TelegramEntity


class AnswerPreCheckoutQuery(TelegramEntity):
	"""
	https://core.telegram.org/bots/api/#answerprecheckoutquery

	"""

	__slots__ = ("pre_checkout_query_id", "ok", "error_message")

	def __init__(
		self,
		pre_checkout_query_id: str,
		ok: bool,
		error_message: str
	):
		self.pre_checkout_query_id = pre_checkout_query_id
		self.ok = ok
		self.error_message = error_message
