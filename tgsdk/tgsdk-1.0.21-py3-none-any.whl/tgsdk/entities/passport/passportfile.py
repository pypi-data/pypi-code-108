#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

from tgsdk import TelegramEntity


class PassportFile(TelegramEntity):
	"""
	https://core.telegram.org/bots/api#passportfile

	"""

	__slots__ = ("file_id", "file_unique_id", "file_size", "file_date")

	def __init__(
		self,
		file_id: str,
		file_unique_id: str,
		file_size: int,
		file_date: int
	):
		self.file_id = file_id
		self.file_unique_id = file_unique_id
		self.file_size = file_size
		self.file_date = file_date
