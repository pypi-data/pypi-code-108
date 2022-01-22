#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

import json
import unittest

from tgsdk import Video


def test__video__init():
	_ = Video(
		file_id="file_id",
		file_unique_id="file_unique_id",
		width=100,
		height=100,
		duration=10
	)

	assert _.file_id == "file_id"
	assert _.file_unique_id == "file_unique_id"
	assert _.width == 100
	assert _.height == 100
	assert _.duration == 10
	assert _.thumb is None
	assert _.file_name is None
	assert _.mime_type is None
	assert _.file_size is None
	assert _.bot is None


def test__video__to_dict():
	_ = Video(
		file_id="file_id",
		file_unique_id="file_unique_id",
		width=100,
		height=100,
		duration=10
	)

	unittest.TestCase().assertDictEqual(
		_.to_dict(),
		{
			"file_id": "file_id",
			"file_unique_id": "file_unique_id",
			"width": 100,
			"height": 100,
			"duration": 10
		}
	)


def test__video__to_json():
	_ = Video(
		file_id="file_id",
		file_unique_id="file_unique_id",
		width=100,
		height=100,
		duration=10
	)

	unittest.TestCase().assertDictEqual(
		json.loads(_.to_json()),
		{
			"file_id": "file_id",
			"file_unique_id": "file_unique_id",
			"width": 100,
			"height": 100,
			"duration": 10
		}
	)


def test__video__de_json():
	data = {
		"file_id": "file_id",
		"file_unique_id": "file_unique_id",
		"width": 100,
		"height": 100,
		"duration": 10
	}

	_ = Video.de_json(data)

	assert isinstance(_, Video) is True
	assert _.file_id == "file_id"
	assert _.file_unique_id == "file_unique_id"
	assert _.width == 100
	assert _.height == 100
	assert _.duration == 10
	assert _.thumb is None
	assert _.file_name is None
	assert _.mime_type is None
	assert _.file_size is None
	assert _.bot is None


def test__video__de_json__data_is_none():
	data = None

	_ = Video.de_json(data)

	assert _ is None
