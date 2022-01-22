#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

from tgsdk import TelegramEntity


class ShippingAddress(TelegramEntity):
	"""
	https://core.telegram.org/bots/api#shippingaddress

	"""
	__slots__ = ("country_code", "state", "city", "street_line1", "street_line2", "post_code")

	def __init__(
		self,
		country_code: str,
		state: str,
		city: str,
		street_line1: str,
		street_line2: str,
		post_code: str
	):
		self.country_code = country_code
		self.state = state
		self.city = city
		self.street_line1 = street_line1
		self.street_line2 = street_line2
		self.post_code = post_code
