#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

from .replymarkup import ReplyMarkup


class ReplyKeyboardRemove(ReplyMarkup):
	__slots__ = ("remove_keyboard", "selective")

	def __init__(
		self,
		selective: bool = False
	):
		self.remove_keyboard = True

		self.selective = selective
