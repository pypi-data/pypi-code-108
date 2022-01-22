#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

from tgsdk import TelegramEntity


class LoginUrl(TelegramEntity):
	"""
	https://core.telegram.org/bots/api#loginurl

	"""
	__slots__ = ("url", "forward_text", "bot_username", "request_write_access")

	def __init__(
		self,
		url: str,
		forward_text: bool = None,
		bot_username: str = None,
		request_write_access: bool = None
	):
		self.url = url
		self.forward_text = forward_text
		self.bot_username = bot_username
		self.request_write_access = request_write_access
