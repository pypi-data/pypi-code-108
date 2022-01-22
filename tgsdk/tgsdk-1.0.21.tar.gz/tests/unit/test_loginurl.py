#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

import json
import unittest

from tgsdk import LoginUrl


def test__loginurl__init():
	_ = LoginUrl(
		url="url",
		bot_username="eprivalovbot"
	)

	assert _.url == "url"
	assert _.bot_username == "eprivalovbot"
	assert _.forward_text is None
	assert _.request_write_access is None


def test__loginurl__to_dict():
	_ = LoginUrl(
		url="url",
		bot_username="eprivalovbot"
	)

	unittest.TestCase().assertDictEqual(
		_.to_dict(),
		{
			"url": "url",
			"bot_username": "eprivalovbot"
		}
	)


def test__loginurl__to_json():
	_ = LoginUrl(
		url="url",
		bot_username="eprivalovbot"
	)

	unittest.TestCase().assertDictEqual(
		json.loads(_.to_json()),
		{
			"url": "url",
			"bot_username": "eprivalovbot"
		}
	)


def test__loginurl__de_json():
	data = {
		"url": "url",
		"bot_username": "eprivalovbot"
	}

	_ = LoginUrl.de_json(data)

	assert isinstance(_, LoginUrl) is True
	assert _.url == "url"
	assert _.bot_username == "eprivalovbot"
	assert _.forward_text is None
	assert _.request_write_access is None


def test__loginurl__de_json__data_is_none():
	data = None

	_ = LoginUrl.de_json(data)

	assert _ is None
