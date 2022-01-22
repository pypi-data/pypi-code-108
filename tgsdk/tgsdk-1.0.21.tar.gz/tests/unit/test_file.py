#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

import json
import unittest

from tgsdk import File


def test__file__init():
	_ = File(
		file_id="file_id",
		file_unique_id="file_unique_id",
		file_size=1000,
		file_path="file_path"
	)

	assert _.file_id == "file_id"
	assert _.file_unique_id == "file_unique_id"
	assert _.file_size == 1000
	assert _.file_path == "file_path"


def test__file__to_dict():
	_ = File(
		file_id="file_id",
		file_unique_id="file_unique_id",
		file_size=1000,
		file_path="file_path"
	)

	unittest.TestCase().assertDictEqual(
		_.to_dict(),
		{
			"file_id": "file_id",
			"file_unique_id": "file_unique_id",
			"file_size": 1000,
			"file_path": "file_path"
		}
	)


def test__file__to_json():
	_ = File(
		file_id="file_id",
		file_unique_id="file_unique_id",
		file_size=1000,
		file_path="file_path"
	)

	unittest.TestCase().assertDictEqual(
		json.loads(_.to_json()),
		{
			"file_id": "file_id",
			"file_unique_id": "file_unique_id",
			"file_size": 1000,
			"file_path": "file_path"
		}
	)


def test__file__de_json():
	data = {
		"file_id": "file_id",
		"file_unique_id": "file_unique_id",
		"file_size": 1000,
		"file_path": "file_path"
	}

	_ = File.de_json(data)

	assert isinstance(_, File) is True
	assert _.file_id == "file_id"
	assert _.file_unique_id == "file_unique_id"
	assert _.file_size == 1000
	assert _.file_path == "file_path"


def test__file__de_json__data_is_none():
	data = None

	_ = File.de_json(data)

	assert _ is None
