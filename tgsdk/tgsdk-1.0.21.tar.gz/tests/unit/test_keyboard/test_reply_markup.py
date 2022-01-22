#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

import unittest

from tgsdk import (
	ReplyKeyboardMarkup,
	KeyboardButton
)


def test__reply_keyboard_markup__to_dict():
	_ = ReplyKeyboardMarkup(
		keyboard=[["Button"]],
		resize_keyboard=True,
		input_field_placeholder="INPUT FIELD PLACEHOLDER"
	)

	unittest.TestCase().assertDictEqual(
		_.to_dict(),
		{
			"keyboard": [
				[
					{
						"text": "Button"
					}
				]
			],
			"one_time_keyboard": False,
			"resize_keyboard": True,
			"input_field_placeholder": "INPUT FIELD PLACEHOLDER",
			"selective": False
		}
	)


def test__reply_keyboard_markup__to_dict__no_buttons():
	_ = ReplyKeyboardMarkup(
		keyboard=[[]],
		resize_keyboard=True,
		input_field_placeholder="INPUT FIELD PLACEHOLDER"
	)

	unittest.TestCase().assertDictEqual(
		_.to_dict(),
		{
			"keyboard": [],
			"one_time_keyboard": False,
			"resize_keyboard": True,
			"input_field_placeholder": "INPUT FIELD PLACEHOLDER",
			"selective": False
		}
	)


def test__reply_keyboard_markup__to_dict__button_is_instance():
	_ = ReplyKeyboardMarkup(
		keyboard=[
			[
				KeyboardButton(
					text="Button"
				)
			]
		],
		resize_keyboard=True
	)

	unittest.TestCase().assertDictEqual(
		_.to_dict(),
		{
			"keyboard": [
				[
					{
						"text": "Button"
					}
				]
			],
			"one_time_keyboard": False,
			"resize_keyboard": True,
			"selective": False
		}
	)


def test__as_instances__no_addition_properties():
	keyboard = ReplyKeyboardMarkup(
		keyboard=[
			[
				KeyboardButton(
					text="Button 1"
				)
			],
			[
				KeyboardButton(
					text="Request Contact",
					request_contact=True
				)
			],
			[
				KeyboardButton(
					text="Request Location",
					request_location=True
				)
			]
		]
	)

	unittest.TestCase().assertDictEqual(
		keyboard.to_dict(),
		{
			"keyboard": [
				[
					{
						"text": "Button 1"
					}
				],
				[
					{
						"request_contact": True,
						"text": "Request Contact"
					}
				],
				[
					{
						"request_location": True,
						"text": "Request Location"
					}
				]
			],
			"one_time_keyboard": False,
			"resize_keyboard": False,
			"selective": False
		}
	)


def test_as_instances__with_one_time_keyboard_property():
	keyboard = ReplyKeyboardMarkup(
		keyboard=[
			[
				KeyboardButton(
					text="Button 1"
				)
			],
			[
				KeyboardButton(
					text="Request Contact",
					request_contact=True
				)
			],
			[
				KeyboardButton(
					text="Request Location",
					request_location=True
				)
			]
		],
		one_time_keyboard=True
	)

	unittest.TestCase().assertDictEqual(
		keyboard.to_dict(),
		{
			"keyboard": [
				[
					{
						"text": "Button 1"
					}
				],
				[
					{
						"request_contact": True,
						"text": "Request Contact"
					}
				],
				[
					{
						"request_location": True,
						"text": "Request Location"
					}
				]
			],
			"one_time_keyboard": True,
			"resize_keyboard": False,
			"selective": False
		}
	)


def test_as_instances__with_resize_property():
	keyboard = ReplyKeyboardMarkup(
		keyboard=[
			[
				KeyboardButton(
					text="Button 1"
				)
			],
			[
				KeyboardButton(
					text="Request Contact",
					request_contact=True
				)
			],
			[
				KeyboardButton(
					text="Request Location",
					request_location=True
				)
			]
		],
		resize_keyboard=True
	)

	unittest.TestCase().assertDictEqual(
		keyboard.to_dict(),
		{
			"keyboard": [
				[
					{
						"text": "Button 1"
					}
				],
				[
					{
						"request_contact": True,
						"text": "Request Contact"
					}
				],
				[
					{
						"request_location": True,
						"text": "Request Location"
					}
				]
			],
			"one_time_keyboard": False,
			"resize_keyboard": True,
			"selective": False
		}
	)


def test_as_instances__with_selective_property():
	keyboard = ReplyKeyboardMarkup(
		keyboard=[
			[
				KeyboardButton(
					text="Button 1"
				)
			],
			[
				KeyboardButton(
					text="Request Contact",
					request_contact=True
				)
			],
			[
				KeyboardButton(
					text="Request Location",
					request_location=True
				)
			]
		],
		selective=True
	)

	unittest.TestCase().assertDictEqual(
		keyboard.to_dict(),
		{
			"keyboard": [
				[
					{
						"text": "Button 1"
					}
				],
				[
					{
						"request_contact": True,
						"text": "Request Contact"
					}
				],
				[
					{
						"request_location": True,
						"text": "Request Location"
					}
				]
			],
			"one_time_keyboard": False,
			"resize_keyboard": False,
			"selective": True
		}
	)

def test_as_instances__with_input_field_placeholder_property():
	keyboard = ReplyKeyboardMarkup(
		keyboard=[
			[
				KeyboardButton(
					text="Button 1"
				)
			],
			[
				KeyboardButton(
					text="Request Contact",
					request_contact=True
				)
			],
			[
				KeyboardButton(
					text="Request Location",
					request_location=True
				)
			]
		],
		input_field_placeholder="INPUT FIELD PLACEHOLDER"
	)

	unittest.TestCase().assertDictEqual(
		keyboard.to_dict(),
		{
			"keyboard": [
				[
					{
						"text": "Button 1"
					}
				],
				[
					{
						"request_contact": True,
						"text": "Request Contact"
					}
				],
				[
					{
						"request_location": True,
						"text": "Request Location"
					}
				]
			],
			"one_time_keyboard": False,
			"resize_keyboard": False,
			"input_field_placeholder": "INPUT FIELD PLACEHOLDER",
			"selective": False
		}
	)
