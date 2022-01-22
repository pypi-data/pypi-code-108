#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

from tgsdk import TelegramEntity


class ChatPermissions(TelegramEntity):
	"""
	https://core.telegram.org/bots/api#chatpermissions

	"""

	__slots__ = (
		"can_send_messages", "can_send_media_messages", "can_send_polls", "can_send_other_messages",
		"can_add_web_page_previews", "can_change_info", "can_invite_users", "can_pin_messages"
	)

	def __init__(
		self,
		can_send_messages: bool = None,
		can_send_media_messages: bool = None,
		can_send_polls: bool = None,
		can_send_other_messages: bool = None,
		can_add_web_page_previews: bool = None,
		can_change_info: bool = None,
		can_invite_users: bool = None,
		can_pin_messages: bool = None
	):
		self.can_send_messages = can_send_messages
		self.can_send_media_messages = can_send_media_messages
		self.can_send_polls = can_send_polls
		self.can_send_other_messages = can_send_other_messages
		self.can_add_web_page_previews = can_add_web_page_previews
		self.can_change_info = can_change_info
		self.can_invite_users = can_invite_users
		self.can_pin_messages = can_pin_messages
