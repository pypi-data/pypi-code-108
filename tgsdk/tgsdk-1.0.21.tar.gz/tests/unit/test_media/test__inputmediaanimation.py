#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

import json
import unittest


from tgsdk import InputMediaAnimation, Animation


# TODO: "media" as Bytes | IO AND "thumb"

def test__inputmediaanimation__init():
	_ = InputMediaAnimation(
		media=Animation(
			file_id="file_id",
			file_unique_id="file_unique_id",
			width=100,
			height=100,
			duration=10
		)
	)

	assert _.type == "animation"
	assert _.caption_entities is None

	assert _.media == "file_id"

	assert _.width == 100
	assert _.height == 100
	assert _.duration == 10
	assert _.thumb is None
	assert _.caption is None
	assert _.parse_mode is None
	assert _.caption_entities is None
	assert _.file_name is None


def test__inputmediaanimation__to_dict():
	_ = InputMediaAnimation(
		media=Animation(
			file_id="file_id",
			file_unique_id="file_unique_id",
			width=100,
			height=100,
			duration=10
		),
		width=100,
		height=100,
		duration=10
	)

	unittest.TestCase().assertDictEqual(
		_.to_dict(),
		{
			"type": "animation",
			"media": "file_id",
			"width": 100,
			"height": 100,
			"duration": 10
		}
	)


def test__inputmediaanimation__to_json():
	_ = InputMediaAnimation(
		media=Animation(
			file_id="file_id",
			file_unique_id="file_unique_id",
			width=100,
			height=100,
			duration=10
		),
		width=100,
		height=100,
		duration=10
	)

	unittest.TestCase().assertDictEqual(
		json.loads(_.to_json()),
		{
			"type": "animation",
			"media": "file_id",
			"width": 100,
			"height": 100,
			"duration": 10
		}
	)


def test__inputmediaanimation__de_json():
	data = {
		"type": "animation",
		"media": "file_id",
		"width": 100,
		"height": 100,
		"duration": 10
	}

	_ = InputMediaAnimation.de_json(data)

	assert isinstance(_, InputMediaAnimation) is True
	assert _.type == "animation"
	assert _.caption_entities is None

	assert _.media == "file_id"

	assert _.width == 100
	assert _.height == 100
	assert _.duration == 10
	assert _.thumb is None
	assert _.caption is None
	assert _.parse_mode is None
	assert _.caption_entities is None
	assert _.file_name is None


def test__inputmediaanimation__de_json__data_is_none():
	data = None

	_ = InputMediaAnimation.de_json(data)

	assert _ is None
