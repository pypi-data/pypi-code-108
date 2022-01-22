#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

import json
import unittest

from tgsdk import Sticker


def test__sticker__init():
	_ = Sticker(
		file_id="file_id",
		file_unique_id="file_unique_id",
		width=100,
		height=100,
		is_animated=True
	)

	assert _.file_id == "file_id"
	assert _.file_unique_id == "file_unique_id"
	assert _.width == 100
	assert _.height == 100
	assert _.is_animated is True
	assert _.thumb is None
	assert _.emoji is None
	assert _.set_name is None
	assert _.mask_position is None
	assert _.file_size is None


def test__sticker__to_dict():
	_ = Sticker(
		file_id="file_id",
		file_unique_id="file_unique_id",
		width=100,
		height=100,
		is_animated=True
	)

	unittest.TestCase().assertDictEqual(
		_.to_dict(),
		{
			"file_id": "file_id",
			"file_unique_id": "file_unique_id",
			"width": 100,
			"height": 100,
			"is_animated": True
		}
	)


def test__sticker__to_json():
	_ = Sticker(
		file_id="file_id",
		file_unique_id="file_unique_id",
		width=100,
		height=100,
		is_animated=True
	)

	unittest.TestCase().assertDictEqual(
		json.loads(_.to_json()),
		{
			"file_id": "file_id",
			"file_unique_id": "file_unique_id",
			"width": 100,
			"height": 100,
			"is_animated": True
		}
	)


def test__document__de_json():
	data = {
		"file_id": "file_id",
		"file_unique_id": "file_unique_id",
		"width": 100,
		"height": 100,
		"is_animated": True
	}

	_ = Sticker.de_json(data)

	assert isinstance(_, Sticker) is True
	assert _.file_id == "file_id"
	assert _.file_unique_id == "file_unique_id"
	assert _.width == 100
	assert _.height == 100
	assert _.is_animated is True
	assert _.thumb is None
	assert _.emoji is None
	assert _.set_name is None
	assert _.mask_position is None
	assert _.file_size is None


def test__document__de_json__data_is_none():
	data = None

	_ = Sticker.de_json(data)

	assert _ is None
