#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

import json
import unittest

from tgsdk import Voice


def test__voice__init():
	_ = Voice(
		file_id="file_id",
		file_unique_id="file_unique_id",
		duration=10
	)

	assert _.file_id == "file_id"
	assert _.file_unique_id == "file_unique_id"
	assert _.duration == 10
	assert _.mime_type is None
	assert _.file_size is None
	assert _.bot is None


def test__voice__to_dict():
	_ = Voice(
		file_id="file_id",
		file_unique_id="file_unique_id",
		duration=10
	)

	unittest.TestCase().assertDictEqual(
		_.to_dict(),
		{
			"file_id": "file_id",
			"file_unique_id": "file_unique_id",
			"duration": 10
		}
	)


def test__voice__to_json():
	_ = Voice(
		file_id="file_id",
		file_unique_id="file_unique_id",
		duration=10
	)

	unittest.TestCase().assertDictEqual(
		json.loads(_.to_json()),
		{
			"file_id": "file_id",
			"file_unique_id": "file_unique_id",
			"duration": 10
		}
	)


def test__voice__de_json():
	data = {
		"file_id": "file_id",
		"file_unique_id": "file_unique_id",
		"duration": 10
	}

	_ = Voice.de_json(data)

	assert isinstance(_, Voice) is True
	assert _.file_id == "file_id"
	assert _.file_unique_id == "file_unique_id"
	assert _.duration == 10
	assert _.mime_type is None
	assert _.file_size is None
	assert _.bot is None


def test__voice__de_json__data_is_none():
	data = None

	_ = Voice.de_json(data)

	assert _ is None
