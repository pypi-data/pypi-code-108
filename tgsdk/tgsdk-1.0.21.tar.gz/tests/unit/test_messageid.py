#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

import json
import unittest

from tgsdk import MessageId


def test__messageid__init():
	_ = MessageId(
		message_id=123
	)

	assert _.message_id == 123


def test__messageid__to_dict():
	_ = MessageId(
		message_id=123
	)

	unittest.TestCase().assertDictEqual(
		_.to_dict(),
		{
			"message_id": 123
		}
	)


def test__messageid__to_json():
	_ = MessageId(
		message_id=123
	)

	unittest.TestCase().assertDictEqual(
		json.loads(_.to_json()),
		{
			"message_id": 123
		}
	)


def test__messageid__de_json():
	data = {
		"message_id": 123
	}

	_ = MessageId.de_json(data)

	assert isinstance(_, MessageId) is True
	assert _.message_id == 123


def test__messageid__de_json__data_is_none():
	data = None

	_ = MessageId.de_json(data)

	assert _ is None
