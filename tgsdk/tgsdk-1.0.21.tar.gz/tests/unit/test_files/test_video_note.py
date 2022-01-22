#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

import json
import unittest

from tgsdk import VideoNote


def test__videonote__init():
	_ = VideoNote(
		file_id="file_id",
		file_unique_id="file_unique_id",
		length=20,
		duration=10
	)

	assert _.file_id == "file_id"
	assert _.file_unique_id == "file_unique_id"
	assert _.length == 20
	assert _.duration == 10
	assert _.thumb is None
	assert _.file_size is None
	assert _.bot is None


def test__videonote__to_dict():
	_ = VideoNote(
		file_id="file_id",
		file_unique_id="file_unique_id",
		length=20,
		duration=10
	)

	unittest.TestCase().assertDictEqual(
		_.to_dict(),
		{
			"file_id": "file_id",
			"file_unique_id": "file_unique_id",
			"length": 20,
			"duration": 10
		}
	)


def test__videonote__to_json():
	_ = VideoNote(
		file_id="file_id",
		file_unique_id="file_unique_id",
		length=20,
		duration=10
	)

	unittest.TestCase().assertDictEqual(
		json.loads(_.to_json()),
		{
			"file_id": "file_id",
			"file_unique_id": "file_unique_id",
			"length": 20,
			"duration": 10
		}
	)


def test__videonote__de_json():
	data = {
		"file_id": "file_id",
		"file_unique_id": "file_unique_id",
		"length": 20,
		"duration": 10
	}

	_ = VideoNote.de_json(data)

	assert isinstance(_, VideoNote) is True
	assert _.file_id == "file_id"
	assert _.file_unique_id == "file_unique_id"
	assert _.length == 20
	assert _.duration == 10
	assert _.thumb is None
	assert _.file_size is None
	assert _.bot is None


def test__videonote__de_json__data_is_none():
	data = None

	_ = VideoNote.de_json(data)

	assert _ is None
