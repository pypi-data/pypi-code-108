#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

import json
import unittest


from tgsdk import InputMediaAudio, Audio


# TODO: "media" as Bytes | IO AND "thumb"

def test__inputmediaaudio__init():
	_ = InputMediaAudio(
		media=Audio(
			file_id="file_id",
			file_unique_id="file_unique_id",
			duration=10
		)
	)

	assert _.type == "audio"
	assert _.caption_entities is None

	assert _.media == "file_id"

	assert _.duration == 10
	assert _.thumb is None
	assert _.caption is None
	assert _.parse_mode is None
	assert _.caption_entities is None
	assert _.performer is None
	assert _.title is None
	assert _.file_name is None


def test__inputmediaaudio__to_dict():
	_ = InputMediaAudio(
		media=Audio(
			file_id="file_id",
			file_unique_id="file_unique_id",
			duration=10
		)
	)

	unittest.TestCase().assertDictEqual(
		_.to_dict(),
		{
			"type": "audio",
			"media": "file_id",
			"duration": 10
		}
	)


def test__inputmediaaudio__to_json():
	_ = InputMediaAudio(
		media=Audio(
			file_id="file_id",
			file_unique_id="file_unique_id",
			duration=10
		)
	)

	unittest.TestCase().assertDictEqual(
		json.loads(_.to_json()),
		{
			"type": "audio",
			"media": "file_id",
			"duration": 10
		}
	)


def test__inputmediaaudio__de_json():
	data = {
		"type": "audio",
		"media": "file_id",
		"duration": 10
	}

	_ = InputMediaAudio.de_json(data)

	assert isinstance(_, InputMediaAudio) is True
	assert _.type == "audio"
	assert _.caption_entities is None

	assert _.media == "file_id"

	assert _.duration == 10
	assert _.thumb is None
	assert _.caption is None
	assert _.parse_mode is None
	assert _.caption_entities is None
	assert _.performer is None
	assert _.title is None
	assert _.file_name is None


def test__inputmediaaudio__de_json__data_is_none():
	data = None

	_ = InputMediaAudio.de_json(data)

	assert _ is None
