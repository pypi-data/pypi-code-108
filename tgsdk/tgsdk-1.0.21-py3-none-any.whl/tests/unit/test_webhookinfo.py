#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

import json
import unittest

from tgsdk import WebhookInfo


def test__webhookinfo__init():
	_ = WebhookInfo(
		url="url",
		has_custom_certificate=False,
		pending_update_count=0
	)

	assert _.url == "url"
	assert _.has_custom_certificate is False
	assert _.pending_update_count == 0
	assert _.ip_address is None
	assert _.last_error_date is None
	assert _.last_error_message is None
	assert _.max_connections is None
	assert _.allowed_updates is None


def test__webhookinfo__to_dict():
	_ = WebhookInfo(
		url="url",
		has_custom_certificate=False,
		pending_update_count=0
	)

	unittest.TestCase().assertDictEqual(
		_.to_dict(),
		{
			"url": "url",
			"has_custom_certificate": False,
			"pending_update_count": 0
		}
	)


def test__webhookinfo__to_json():
	_ = WebhookInfo(
		url="url",
		has_custom_certificate=False,
		pending_update_count=0
	)

	unittest.TestCase().assertDictEqual(
		json.loads(_.to_json()),
		{
			"url": "url",
			"has_custom_certificate": False,
			"pending_update_count": 0
		}
	)


def test__webhookinfo__de_json():
	data = {
		"url": "url",
		"has_custom_certificate": False,
		"pending_update_count": 0
	}

	_ = WebhookInfo.de_json(data)

	assert isinstance(_, WebhookInfo) is True
	assert _.url == "url"
	assert _.has_custom_certificate is False
	assert _.pending_update_count == 0
	assert _.ip_address is None
	assert _.last_error_date is None
	assert _.last_error_message is None
	assert _.max_connections is None
	assert _.allowed_updates is None


def test__webhookinfo__de_json__data_is_none():
	data = None

	_ = WebhookInfo.de_json(data)

	assert _ is None


def test__webhookinfo__methods():
	_ = WebhookInfo(
		url="https://domain.com",
		has_custom_certificate=False,
		pending_update_count=0
	)

	assert _.is_url_equal("https://domain.com") is True
	assert _.is_domain_equal("domain.com") is True

	assert _.is_url_equal("https://domain.com/random") is False
	assert _.is_domain_equal("example.com") is False
