#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

import unittest

from tgsdk import ReplyKeyboardRemove


def test__reply_keyboard_remove__init():
	_ = ReplyKeyboardRemove(
		selective=True
	)

	assert _.selective is True
	assert _.remove_keyboard is True


def test__reply_keyboard_remove__to_dict():
	_ = ReplyKeyboardRemove(
		selective=True
	).to_dict()

	unittest.TestCase().assertDictEqual(
		_,
		{
			"selective": True,
			"remove_keyboard": True
		}
	)


def test__reply_keyboard_remove__de_json():
	data = {
		"selective": True
	}

	_ = ReplyKeyboardRemove.de_json(data)  # type: ReplyKeyboardRemove

	assert _.selective is True
	assert _.remove_keyboard is True


def test__reply_keyboard_remove__de_json__data_is_none():
	data = None

	_ = ReplyKeyboardRemove.de_json(data)

	assert _ is None

