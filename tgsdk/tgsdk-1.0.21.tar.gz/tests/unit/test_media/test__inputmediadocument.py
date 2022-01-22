#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

import json
import unittest


from tgsdk import InputMediaDocument, Document


# TODO: "media" as Bytes | IO AND "thumb"

def test__inputmediadocument__init():
	_ = InputMediaDocument(
		media=Document(
			file_id="file_id",
			file_unique_id="file_unique_id"
		)
	)

	assert _.type == "document"
	assert _.caption_entities is None

	assert _.media == "file_id"

	assert _.thumb is None
	assert _.caption is None
	assert _.parse_mode is None
	assert _.caption_entities is None
	assert _.disable_content_type_detection is None
	assert _.file_name is None


def test__inputmediadocument__to_dict():
	_ = InputMediaDocument(
		media=Document(
			file_id="file_id",
			file_unique_id="file_unique_id"
		)
	)

	unittest.TestCase().assertDictEqual(
		_.to_dict(),
		{
			"type": "document",
			"media": "file_id"
		}
	)


def test__inputmediadocument__to_json():
	_ = InputMediaDocument(
		media=Document(
			file_id="file_id",
			file_unique_id="file_unique_id"
		)
	)

	unittest.TestCase().assertDictEqual(
		json.loads(_.to_json()),
		{
			"type": "document",
			"media": "file_id"
		}
	)


def test__inputmediadocument__de_json():
	data = {
		"type": "document",
		"media": "file_id"
	}

	_ = InputMediaDocument.de_json(data)

	assert isinstance(_, InputMediaDocument) is True
	assert _.type == "document"
	assert _.caption_entities is None

	assert _.media == "file_id"

	assert _.thumb is None
	assert _.caption is None
	assert _.parse_mode is None
	assert _.caption_entities is None
	assert _.disable_content_type_detection is None
	assert _.file_name is None


def test__inputmediadocument__de_json__data_is_none():
	data = None

	_ = InputMediaDocument.de_json(data)

	assert _ is None
