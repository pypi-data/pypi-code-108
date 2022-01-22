#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

from tgsdk import TelegramEntity


class MessageId(TelegramEntity):
	"""
	https://core.telegram.org/bots/api#messageid

	"""

	__slots__ = ("message_id",)

	def __init__(
		self,
		message_id: int,
	):
		self.message_id = message_id
