#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

from typing import (
	Optional,
	Dict,
	List
)

from .inlinekeyboardbutton import InlineKeyboardButton
from .replymarkup import ReplyMarkup


class InlineKeyboardMarkup(ReplyMarkup):
	"""
	https://core.telegram.org/bots/api#inlinekeyboardmarkup

	"""
	__slots__ = ("inline_keyboard",)

	def __init__(
		self,
		inline_keyboard: List[List[InlineKeyboardButton]],
	):
		self.inline_keyboard = inline_keyboard

	def to_dict(self) -> Dict:
		"""

		:return:
		"""
		data = super().to_dict()

		data["inline_keyboard"] = []
		for row in self.inline_keyboard:

			row_inline_buttons = []  # type: List[List[InlineKeyboardButton]]
			for col in row:
				row_inline_buttons.append(col.to_dict())

			data["inline_keyboard"].append(row_inline_buttons)

		return data

	@classmethod
	def de_json(cls, data: Optional[Dict] = None) -> Optional["InlineKeyboardMarkup"]:
		"""

		:param data:
		:return:
		"""
		if not data:
			return None

		keyboard = []
		for row in data["inline_keyboard"]:
			row_inline_buttons = []
			for col in row:
				inline_keyboard_button = InlineKeyboardButton.de_json(col)
				if inline_keyboard_button:
					row_inline_buttons.append(inline_keyboard_button)

			if row_inline_buttons:
				keyboard.append(row_inline_buttons)

		return cls(keyboard)
