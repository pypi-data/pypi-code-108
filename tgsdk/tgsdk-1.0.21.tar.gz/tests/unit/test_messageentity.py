#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

import json
import unittest

from tgsdk import MessageEntity


def test__messageentity__init():
	_ = MessageEntity(
		type="type",
		offset=10,
		length=10,
		url="url"
	)

	assert _.type == "type"
	assert _.offset == 10
	assert _.length == 10
	assert _.url == "url"
	assert _.user is None
	assert _.language is None


def test__messageentity__to_dict():
	_ = MessageEntity(
		type="type",
		offset=10,
		length=10,
		url="url"
	)

	unittest.TestCase().assertDictEqual(
		_.to_dict(),
		{
			"type": "type",
			"offset": 10,
			"length": 10,
			"url": "url"
		}
	)


def test__messageentity__to_json():
	_ = MessageEntity(
		type="type",
		offset=10,
		length=10,
		url="url"
	)

	unittest.TestCase().assertDictEqual(
		json.loads(_.to_json()),
		{
			"type": "type",
			"offset": 10,
			"length": 10,
			"url": "url"
		}
	)


def test__messageentity__de_json():
	data = {
		"type": "type",
		"offset": 10,
		"length": 10,
		"url": "url"
	}

	_ = MessageEntity.de_json(data)

	assert isinstance(_, MessageEntity) is True
	assert _.type == "type"
	assert _.offset == 10
	assert _.length == 10
	assert _.url == "url"
	assert _.user is None
	assert _.language is None


def test__messageentity__de_json__data_is_none():
	data = None

	_ = MessageEntity.de_json(data)

	assert _ is None
