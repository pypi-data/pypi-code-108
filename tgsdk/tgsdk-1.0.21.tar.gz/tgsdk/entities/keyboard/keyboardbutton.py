#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

from tgsdk import TelegramEntity


class KeyboardButton(TelegramEntity):
	"""
	https://core.telegram.org/bots/api#keyboardbutton

	"""
	__slots__ = ("text", "request_contact", "request_location")

	def __init__(
		self,
		text: str,
		request_contact: bool = None,
		request_location: bool = None
	):
		self.text = text
		self.request_contact = request_contact
		self.request_location = request_location
