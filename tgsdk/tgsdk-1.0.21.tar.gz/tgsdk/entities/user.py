#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

from typing import Any

from tgsdk import TelegramEntity


class User(TelegramEntity):
	"""
	https://core.telegram.org/bots/api#user

	"""

	__slots__ = (
		"id", "first_name", "is_bot", "username", "last_name", "language_code",
		"can_join_groups", "can_read_all_group_messages", "supports_inline_queries"
	)

	def __init__(
		self,
		id: int,
		first_name: str,
		is_bot: bool,
		username: str = None,
		last_name: str = None,
		language_code: str = None,
		can_join_groups: bool = None,
		can_read_all_group_messages: bool = None,
		supports_inline_queries: bool = None,
		**_kwargs: Any
	):
		self.id = int(id)
		self.first_name = first_name
		self.is_bot = is_bot
		self.username = username
		self.last_name = last_name
		self.language_code = language_code
		self.can_join_groups = can_join_groups
		self.can_read_all_group_messages = can_read_all_group_messages
		self.supports_inline_queries = supports_inline_queries
