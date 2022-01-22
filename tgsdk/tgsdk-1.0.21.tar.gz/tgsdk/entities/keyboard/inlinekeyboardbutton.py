#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

from typing import TYPE_CHECKING

from tgsdk import TelegramEntity

if TYPE_CHECKING:
	from tgsdk import LoginUrl


class InlineKeyboardButton(TelegramEntity):
	"""
	https://core.telegram.org/bots/api#inlinekeyboardbutton

	"""
	__slots__ = ("text", "callback_data", "url", "switch_inline_query", "switch_inline_query_current_chat", "pay", "login_url")

	def __init__(
		self,
		text: str,
		callback_data: str = None,
		url: str = None,
		switch_inline_query: str = None,
		switch_inline_query_current_chat: str = None,
		pay: bool = None,
		login_url: "LoginUrl" = None,
	):
		self.text = text
		self.callback_data = callback_data
		self.url = url
		self.switch_inline_query = switch_inline_query
		self.switch_inline_query_current_chat = switch_inline_query_current_chat
		self.pay = pay
		self.login_url = login_url
