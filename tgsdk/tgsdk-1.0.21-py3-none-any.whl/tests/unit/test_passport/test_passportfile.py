#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

import json
import unittest

from tgsdk import PassportFile


def test__passportfile__init():
	_ = PassportFile(
		file_id="file_id",
		file_unique_id="file_unique_id",
		file_size=1000,
		file_date=15672673427
	)

	assert _.file_id == "file_id"
	assert _.file_unique_id == "file_unique_id"
	assert _.file_size == 1000
	assert _.file_date == 15672673427


def test__passportfile__to_dict():
	_ = PassportFile(
		file_id="file_id",
		file_unique_id="file_unique_id",
		file_size=1000,
		file_date=15672673427
	)

	unittest.TestCase().assertDictEqual(
		_.to_dict(),
		{
			"file_id": "file_id",
			"file_unique_id": "file_unique_id",
			"file_size": 1000,
			"file_date": 15672673427
		}
	)


def test__passportfile__to_json():
	_ = PassportFile(
		file_id="file_id",
		file_unique_id="file_unique_id",
		file_size=1000,
		file_date=15672673427
	)

	unittest.TestCase().assertDictEqual(
		json.loads(_.to_json()),
		{
			"file_id": "file_id",
			"file_unique_id": "file_unique_id",
			"file_size": 1000,
			"file_date": 15672673427
		}
	)


def test__passportfile__de_json():
	data = {
		"file_id": "file_id",
		"file_unique_id": "file_unique_id",
		"file_size": 1000,
		"file_date": 15672673427
	}

	_ = PassportFile.de_json(data)

	assert isinstance(_, PassportFile) is True
	assert _.file_id == "file_id"
	assert _.file_unique_id == "file_unique_id"
	assert _.file_size == 1000
	assert _.file_date == 15672673427


def test__passportfile__de_json__data_is_none():
	data = None

	_ = PassportFile.de_json(data)

	assert _ is None
