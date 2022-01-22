#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

import json
import unittest

from tgsdk import UserProfilePhotos, PhotoSize


def test__userprofilephotos__init():
	_ = UserProfilePhotos(
		total_count=0,
		photos=[
			[
				PhotoSize(
					file_id="file_id",
					file_unique_id="file_unique_id",
					width=100,
					height=100,
					file_size=1000
				)
			]
		]
	)

	assert _.total_count == 0
	assert _.photos[0][0].file_id == "file_id"
	assert _.photos[0][0].file_unique_id == "file_unique_id"
	assert _.photos[0][0].width == 100
	assert _.photos[0][0].height == 100
	assert _.photos[0][0].file_size == 1000


def test__userprofilephotos__to_dict():
	_ = UserProfilePhotos(
		total_count=0,
		photos=[
			[
				PhotoSize(
					file_id="file_id",
					file_unique_id="file_unique_id",
					width=100,
					height=100,
					file_size=1000
				)
			]
		]
	)

	unittest.TestCase().assertDictEqual(
		_.to_dict(),
		{
			"total_count": 0,
			"photos": [
				[
					{
						"file_id": "file_id",
						"file_unique_id": "file_unique_id",
						"width": 100,
						"height": 100,
						"file_size": 1000
					}
				]
			]
		}
	)


def test__userprofilephotos__to_dict__with_empty_row():
	_ = UserProfilePhotos(
		total_count=0,
		photos=[
			[
				PhotoSize(
					file_id="file_id",
					file_unique_id="file_unique_id",
					width=100,
					height=100,
					file_size=1000
				)
			],
			[
				None
			]
		]
	)

	unittest.TestCase().assertDictEqual(
		_.to_dict(),
		{
			"total_count": 0,
			"photos": [
				[
					{
						"file_id": "file_id",
						"file_unique_id": "file_unique_id",
						"width": 100,
						"height": 100,
						"file_size": 1000
					}
				]
			]
		}
	)


def test__userprofilephotos__to_json():
	_ = UserProfilePhotos(
		total_count=0,
		photos=[
			[
				PhotoSize(
					file_id="file_id",
					file_unique_id="file_unique_id",
					width=100,
					height=100,
					file_size=1000
				)
			]
		]
	)

	unittest.TestCase().assertDictEqual(
		json.loads(_.to_json()),
		{
			"total_count": 0,
			"photos": [
				[
					{
						"file_id": "file_id",
						"file_unique_id": "file_unique_id",
						"width": 100,
						"height": 100,
						"file_size": 1000
					}
				]
			]
		}
	)


def test__userprofilephotos__de_json():
	data = {
		"total_count": 0,
		"photos": [
			[
				{
					"file_id": "file_id",
					"file_unique_id": "file_unique_id",
					"width": 100,
					"height": 100,
					"file_size": 1000
				}
			]
		]
	}

	_ = UserProfilePhotos.de_json(data)

	assert isinstance(_, UserProfilePhotos) is True
	assert _.total_count == 0
	assert _.photos[0][0].file_id == "file_id"
	assert _.photos[0][0].file_unique_id == "file_unique_id"
	assert _.photos[0][0].width == 100
	assert _.photos[0][0].height == 100
	assert _.photos[0][0].file_size == 1000


def test__userprofilephotos__de_json__data_is_none():
	data = None

	_ = UserProfilePhotos.de_json(data)

	assert _ is None
