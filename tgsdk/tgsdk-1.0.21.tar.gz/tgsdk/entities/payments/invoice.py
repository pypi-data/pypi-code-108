#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

from tgsdk import TelegramEntity


class Invoice(TelegramEntity):
	"""
	https://core.telegram.org/bots/api#invoice

	"""
	__slots__ = ("title", "description", "start_parameter", "currency", "total_amount")

	def __init__(
		self,
		title: str,
		description: str,
		start_parameter: str,
		currency: str,
		total_amount: int
	):
		self.title = title
		self.description = description
		self.start_parameter = start_parameter
		self.currency = currency
		self.total_amount = total_amount
