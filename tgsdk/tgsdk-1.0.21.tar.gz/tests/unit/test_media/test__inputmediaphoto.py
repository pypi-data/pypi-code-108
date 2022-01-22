#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

import json
import unittest


from tgsdk import InputMediaPhoto, PhotoSize


# TODO: "media" as Bytes | IO AND "thumb"

def test__inputmediaphoto__init():
	_ = InputMediaPhoto(
		media=PhotoSize(
			file_id="file_id",
			file_unique_id="file_unique_id",
			width=100,
			height=100
		)
	)

	assert _.type == "photo"
	assert _.caption_entities is None

	assert _.media == "file_id"

	assert _.caption is None
	assert _.parse_mode is None
	assert _.caption_entities is None
	assert _.file_name is None


def test__inputmediaphoto__to_dict():
	_ = InputMediaPhoto(
		media=PhotoSize(
			file_id="file_id",
			file_unique_id="file_unique_id",
			width=100,
			height=100
		)
	)

	unittest.TestCase().assertDictEqual(
		_.to_dict(),
		{
			"type": "photo",
			"media": "file_id",
		}
	)


def test__inputmediaphoto__to_json():
	_ = InputMediaPhoto(
		media=PhotoSize(
			file_id="file_id",
			file_unique_id="file_unique_id",
			width=100,
			height=100
		)
	)

	unittest.TestCase().assertDictEqual(
		json.loads(_.to_json()),
		{
			"type": "photo",
			"media": "file_id",
		}
	)


def test__inputmediaphoto__de_json():
	data = {
		"type": "photo",
		"media": "file_id",
	}

	_ = InputMediaPhoto.de_json(data)

	assert isinstance(_, InputMediaPhoto) is True
	assert _.type == "photo"
	assert _.caption_entities is None

	assert _.media == "file_id"

	assert _.caption is None
	assert _.parse_mode is None
	assert _.caption_entities is None
	assert _.file_name is None


def test__inputmediaphoto__de_json__data_is_none():
	data = None

	_ = InputMediaPhoto.de_json(data)

	assert _ is None
