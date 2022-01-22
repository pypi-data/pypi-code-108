#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

import json
import unittest

from tgsdk import Document


def test__document__init():
	_ = Document(
		file_id="file_id",
		file_unique_id="file_unique_id"
	)

	assert _.file_id == "file_id"
	assert _.file_unique_id == "file_unique_id"
	assert _.thumb is None
	assert _.file_name is None
	assert _.mime_type is None
	assert _.file_size is None
	assert _.bot is None


def test__document__to_dict():
	_ = Document(
		file_id="file_id",
		file_unique_id="file_unique_id"
	)

	unittest.TestCase().assertDictEqual(
		_.to_dict(),
		{
			"file_id": "file_id",
			"file_unique_id": "file_unique_id"
		}
	)


def test__document__to_json():
	_ = Document(
		file_id="file_id",
		file_unique_id="file_unique_id"
	)

	unittest.TestCase().assertDictEqual(
		json.loads(_.to_json()),
		{
			"file_id": "file_id",
			"file_unique_id": "file_unique_id"
		}
	)


def test__document__de_json():
	data = {
		"file_id": "file_id",
		"file_unique_id": "file_unique_id"
	}

	_ = Document.de_json(data)

	assert isinstance(_, Document) is True
	assert _.file_id == "file_id"
	assert _.file_unique_id == "file_unique_id"
	assert _.thumb is None
	assert _.file_name is None
	assert _.mime_type is None
	assert _.file_size is None
	assert _.bot is None


def test__document__de_json__data_is_none():
	data = None

	_ = Document.de_json(data)

	assert _ is None
