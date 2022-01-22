#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

import json
import unittest

from tgsdk import Animation


def test__animation__init():
	_ = Animation(
		file_id="123",
		file_unique_id="1234",
		width=100,
		height=100,
		duration=10
	)

	assert _.file_id == "123"
	assert _.file_unique_id == "1234"
	assert _.width == 100
	assert _.height == 100
	assert _.duration == 10
	assert _.file_name is None
	assert _.bot is None
	assert _.thumb is None
	assert _.mime_type is None
	assert _.file_size is None


def test__animation__to_dict():
	_ = Animation(
		file_id="123",
		file_unique_id="1234",
		width=100,
		height=100,
		duration=10
	)

	unittest.TestCase().assertDictEqual(
		_.to_dict(),
		{
			"file_id": "123",
			"file_unique_id": "1234",
			"width": 100,
			"height": 100,
			"duration": 10
		}
	)


def test__animation__to_json():
	_ = Animation(
		file_id="123",
		file_unique_id="1234",
		width=100,
		height=100,
		duration=10
	)

	unittest.TestCase().assertDictEqual(
		json.loads(_.to_json()),
		{
			"file_id": "123",
			"file_unique_id": "1234",
			"width": 100,
			"height": 100,
			"duration": 10
		}
	)


def test__animation__de_json():
	data = {
		"file_id": "123",
		"file_unique_id": "1234",
		"width": 100,
		"height": 100,
		"duration": 10
	}

	_ = Animation.de_json(data)

	assert isinstance(_, Animation) is True
	assert _.file_id == "123"
	assert _.file_unique_id == "1234"
	assert _.width == 100
	assert _.height == 100
	assert _.duration == 10
	assert _.file_name is None
	assert _.bot is None
	assert _.thumb is None
	assert _.mime_type is None
	assert _.file_size is None


def test__animation__de_json__data_is_none():
	data = None

	_ = Animation.de_json(data)

	assert _ is None
