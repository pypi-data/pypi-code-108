#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

import json
import unittest

from tgsdk import PhotoSize


def test__photosize__init():
	_ = PhotoSize(
		file_id="file_id",
		file_unique_id="file_unique_id",
		width=100,
		height=100
	)

	assert _.file_id == "file_id"
	assert _.file_unique_id == "file_unique_id"
	assert _.width == 100
	assert _.height == 100
	assert _.file_size is None
	assert _.bot is None


def test__photosize__to_dict():
	_ = PhotoSize(
		file_id="file_id",
		file_unique_id="file_unique_id",
		width=100,
		height=100
	)

	unittest.TestCase().assertDictEqual(
		_.to_dict(),
		{
			"file_id": "file_id",
			"file_unique_id": "file_unique_id",
			"width": 100,
			"height": 100
		}
	)


def test__photosize__to_json():
	_ = PhotoSize(
		file_id="file_id",
		file_unique_id="file_unique_id",
		width=100,
		height=100
	)

	unittest.TestCase().assertDictEqual(
		json.loads(_.to_json()),
		{
			"file_id": "file_id",
			"file_unique_id": "file_unique_id",
			"width": 100,
			"height": 100
		}
	)


def test__photosize__de_json():
	data = {
		"file_id": "file_id",
		"file_unique_id": "file_unique_id",
		"width": 100,
		"height": 100
	}

	_ = PhotoSize.de_json(data)

	assert isinstance(_, PhotoSize) is True
	assert _.file_id == "file_id"
	assert _.file_unique_id == "file_unique_id"
	assert _.width == 100
	assert _.height == 100
	assert _.file_size is None
	assert _.bot is None


def test__photosize__de_json__data_is_none():
	data = None

	_ = PhotoSize.de_json(data)

	assert _ is None
