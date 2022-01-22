#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

from typing import (
	Optional,
	Dict,
	List,
	Union
)

from .keyboardbutton import KeyboardButton
from .replymarkup import ReplyMarkup


class ReplyKeyboardMarkup(ReplyMarkup):
	"""
	https://core.telegram.org/bots/api#replykeyboardmarkup

	"""
	__slots__ = ("keyboard", "resize_keyboard", "one_time_keyboard", "input_field_placeholder", "selective")

	def __init__(
		self,
		keyboard: List[List[Union[str, KeyboardButton]]],
		resize_keyboard: Optional[bool] = False,
		one_time_keyboard: Optional[bool] = False,
		input_field_placeholder: Optional[str] = None,
		selective: Optional[bool] = False
	):
		self.keyboard = self.set_keyboard(keyboard)
		self.resize_keyboard = resize_keyboard
		self.one_time_keyboard = one_time_keyboard

		self.input_field_placeholder = input_field_placeholder
		if isinstance(input_field_placeholder, str):
			if len(self.input_field_placeholder) > 64:
				print("The placeholder to be shown in the input field when the keyboard is active; 1-64 characters")

		self.selective = selective

	@staticmethod
	def set_keyboard(keyboard: List[List[Union[str, KeyboardButton]]]) -> List[List[Union[str, KeyboardButton]]]:
		"""

		:param keyboard:
		:return:
		"""
		_keyboard = []

		for row in keyboard:
			button_row = []
			for button in row:
				if isinstance(button, KeyboardButton):
					button_row.append(button)
				else:
					button_row.append(KeyboardButton(button))

			_keyboard.append(button_row)

		return _keyboard

	def to_dict(self) -> Dict:
		"""

		:return:
		"""
		data = super().to_dict()
		data["keyboard"] = []

		for row in self.keyboard:
			row_buttons = []

			for col in row:
				if isinstance(col, KeyboardButton):
					row_buttons.append(col.to_dict())
				else:
					row_buttons.append(col)

			if row_buttons:
				data["keyboard"].append(row_buttons)

		return data
