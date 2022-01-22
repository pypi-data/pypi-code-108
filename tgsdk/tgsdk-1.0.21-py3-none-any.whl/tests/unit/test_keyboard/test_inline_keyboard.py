#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

import json
import unittest

from tgsdk import (
	InlineKeyboardMarkup,
	InlineKeyboardButton
)


def test_inline_keyboard_all_button_types__to_dict():
	inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[
		[
			InlineKeyboardButton(
				text="Button 1",
				callback_data="button_1"
			),
			InlineKeyboardButton(
				text="Button 2",
				callback_data="button_2"
			)
		],
		[
			InlineKeyboardButton(
				text="Button 3",
				callback_data="button_3"
			)
		],
		[
			InlineKeyboardButton(
				text="Button 4",
				url="https://linkedin.com/in/evgeniyprivalov/"
			)
		],
		[
			InlineKeyboardButton(
				text="Button 5",
				switch_inline_query="Hello, World!"
			)
		],
		[
			InlineKeyboardButton(
				text="Button 6",
				switch_inline_query_current_chat="Hello, Chat!"
			)
		]
	])

	unittest.TestCase().assertDictEqual(
		inline_keyboard.to_dict(),
		{
			"inline_keyboard": [
				[
					{
						"callback_data": "button_1",
						"text": "Button 1"
					},
					{
						"callback_data": "button_2",
						"text": "Button 2"
					}
				],
				[
					{
						"callback_data": "button_3",
						"text": "Button 3"
					}
				],
				[
					{
						"url": "https://linkedin.com/in/evgeniyprivalov/",
						"text": "Button 4"
					}
				],
				[
					{
						"switch_inline_query": "Hello, World!",
						"text": "Button 5"
					}
				],
				[
					{
						"switch_inline_query_current_chat": "Hello, Chat!",
						"text": "Button 6"
					}
				]
			]
		}

	)


def test_inline_keyboard_all_button_types__to_json():
	inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[
		[
			InlineKeyboardButton(
				text="Button 1",
				callback_data="button_1"
			),
			InlineKeyboardButton(
				text="Button 2",
				callback_data="button_2"
			)
		],
		[
			InlineKeyboardButton(
				text="Button 3",
				callback_data="button_3"
			)
		],
		[
			InlineKeyboardButton(
				text="Button 4",
				url="https://linkedin.com/in/evgeniyprivalov/"
			)
		],
		[
			InlineKeyboardButton(
				text="Button 5",
				switch_inline_query="Hello, World!"
			)
		],
		[
			InlineKeyboardButton(
				text="Button 6",
				switch_inline_query_current_chat="Hello, Chat!"
			)
		]
	])

	unittest.TestCase().assertDictEqual(
		json.loads(inline_keyboard.to_json()),
		{
			"inline_keyboard": [
				[
					{
						"callback_data": "button_1",
						"text": "Button 1"
					},
					{
						"callback_data": "button_2",
						"text": "Button 2"
					}
				],
				[
					{
						"callback_data": "button_3",
						"text": "Button 3"
					}
				],
				[
					{
						"url": "https://linkedin.com/in/evgeniyprivalov/",
						"text": "Button 4"
					}
				],
				[
					{
						"switch_inline_query": "Hello, World!",
						"text": "Button 5"
					}
				],
				[
					{
						"switch_inline_query_current_chat": "Hello, Chat!",
						"text": "Button 6"
					}
				]
			]
		}
	)


def test__inline_keyboard__de_json():
	data = {
		"inline_keyboard": [
			[
				{
					"callback_data": "button_1",
					"text": "Button 1"
				},
				{
					"callback_data": "button_2",
					"text": "Button 2"
				}
			],
			[
				{
					"callback_data": "button_3",
					"text": "Button 3"
				}
			],
			[
				{
					"url": "https://linkedin.com/in/evgeniyprivalov/",
					"text": "Button 4"
				}
			],
			[
				{
					"switch_inline_query": "Hello, World!",
					"text": "Button 5"
				}
			],
			[
				{
					"switch_inline_query_current_chat": "Hello, Chat!",
					"text": "Button 6"
				}
			]
		]
	}

	inline_keyboard = InlineKeyboardMarkup.de_json(data)

	assert isinstance(inline_keyboard, InlineKeyboardMarkup) is True

	unittest.TestCase().assertDictEqual(
		inline_keyboard.to_dict(),
		{
			"inline_keyboard": [
				[
					{
						"callback_data": "button_1",
						"text": "Button 1"
					},
					{
						"callback_data": "button_2",
						"text": "Button 2"
					}
				],
				[
					{
						"callback_data": "button_3",
						"text": "Button 3"
					}
				],
				[
					{
						"url": "https://linkedin.com/in/evgeniyprivalov/",
						"text": "Button 4"
					}
				],
				[
					{
						"switch_inline_query": "Hello, World!",
						"text": "Button 5"
					}
				],
				[
					{
						"switch_inline_query_current_chat": "Hello, Chat!",
						"text": "Button 6"
					}
				]
			]
		}
	)


def test__inline_keyboard__de_json__with_wrong_object():
	data = {
		"inline_keyboard": [
			[
				{
					"callback_data": "button_1",
					"text": "Button 1"
				},
				{
					"callback_data": "button_2",
					"text": "Button 2"
				}
			],
			[
				{
					"callback_data": "button_3",
					"text": "Button 3"
				}
			],
			[
				{
					"url": "https://linkedin.com/in/evgeniyprivalov/",
					"text": "Button 4"
				}
			],
			[
				{
					"switch_inline_query": "Hello, World!",
					"text": "Button 5"
				}
			],
			[
				{
					"switch_inline_query_current_chat": "Hello, Chat!",
					"text": "Button 6"
				}
			],
			[
				None
			]
		]
	}

	inline_keyboard = InlineKeyboardMarkup.de_json(data)

	assert isinstance(inline_keyboard, InlineKeyboardMarkup) is True

	t = unittest.TestCase()
	t.maxDiff = None

	t.assertDictEqual(
		inline_keyboard.to_dict(),
		{
			"inline_keyboard": [
				[
					{
						"callback_data": "button_1",
						"text": "Button 1"
					},
					{
						"callback_data": "button_2",
						"text": "Button 2"
					}
				],
				[
					{
						"callback_data": "button_3",
						"text": "Button 3"
					}
				],
				[
					{
						"url": "https://linkedin.com/in/evgeniyprivalov/",
						"text": "Button 4"
					}
				],
				[
					{
						"switch_inline_query": "Hello, World!",
						"text": "Button 5"
					}
				],
				[
					{
						"switch_inline_query_current_chat": "Hello, Chat!",
						"text": "Button 6"
					}
				]
			]
		}
	)


def test__inline_keyboard__de_json__no_data():
	inline_keyboard = InlineKeyboardMarkup.de_json(None)

	assert inline_keyboard is None
