#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

import json
import unittest

from tgsdk import ChatPhoto


def test__chatphoto__init():
	_ = ChatPhoto(
		small_file_id="small_file_id",
		small_file_unique_id="small_file_unique_id",
		big_file_id="big_file_id",
		big_file_unique_id="big_file_unique_id"
	)

	assert _.small_file_id == "small_file_id"
	assert _.small_file_unique_id == "small_file_unique_id"
	assert _.big_file_id == "big_file_id"
	assert _.big_file_unique_id == "big_file_unique_id"
	assert _.bot is None


def test__chatphoto__to_dict():
	_ = ChatPhoto(
		small_file_id="small_file_id",
		small_file_unique_id="small_file_unique_id",
		big_file_id="big_file_id",
		big_file_unique_id="big_file_unique_id"
	)

	unittest.TestCase().assertDictEqual(
		_.to_dict(),
		{
			"small_file_id": "small_file_id",
			"small_file_unique_id": "small_file_unique_id",
			"big_file_id": "big_file_id",
			"big_file_unique_id": "big_file_unique_id"
		}
	)


def test__chatphoto__to_json():
	_ = ChatPhoto(
		small_file_id="small_file_id",
		small_file_unique_id="small_file_unique_id",
		big_file_id="big_file_id",
		big_file_unique_id="big_file_unique_id"
	)

	unittest.TestCase().assertDictEqual(
		json.loads(_.to_json()),
		{
			"small_file_id": "small_file_id",
			"small_file_unique_id": "small_file_unique_id",
			"big_file_id": "big_file_id",
			"big_file_unique_id": "big_file_unique_id"
		}
	)


def test__chatphoto__de_json():
	data = {
		"small_file_id": "small_file_id",
		"small_file_unique_id": "small_file_unique_id",
		"big_file_id": "big_file_id",
		"big_file_unique_id": "big_file_unique_id"
	}

	_ = ChatPhoto.de_json(data)

	assert isinstance(_, ChatPhoto) is True
	assert _.small_file_id == "small_file_id"
	assert _.small_file_unique_id == "small_file_unique_id"
	assert _.big_file_id == "big_file_id"
	assert _.big_file_unique_id == "big_file_unique_id"
	assert _.bot is None


def test__chatphoto__de_json__data_is_none():
	data = None

	_ = ChatPhoto.de_json(data)

	assert _ is None
