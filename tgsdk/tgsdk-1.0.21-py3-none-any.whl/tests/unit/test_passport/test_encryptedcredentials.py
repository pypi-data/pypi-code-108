#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

import json
import unittest

from tgsdk import EncryptedCredentials


def test__passportfile__init():
	_ = EncryptedCredentials(
		data="data",
		hash="hash",
		secret="secret"
	)

	assert _.data == "data"
	assert _.hash == "hash"
	assert _.secret == "secret"


def test__passportfile__to_dict():
	_ = EncryptedCredentials(
		data="data",
		hash="hash",
		secret="secret"
	)

	unittest.TestCase().assertDictEqual(
		_.to_dict(),
		{
			"data": "data",
			"hash": "hash",
			"secret": "secret"
		}
	)


def test__passportfile__to_json():
	_ = EncryptedCredentials(
		data="data",
		hash="hash",
		secret="secret"
	)

	unittest.TestCase().assertDictEqual(
		json.loads(_.to_json()),
		{
			"data": "data",
			"hash": "hash",
			"secret": "secret"
		}
	)


def test__passportfile__de_json():
	data = {
		"data": "data",
		"hash": "hash",
		"secret": "secret"
	}

	_ = EncryptedCredentials.de_json(data)

	assert isinstance(_, EncryptedCredentials) is True
	assert _.data == "data"
	assert _.hash == "hash"
	assert _.secret == "secret"


def test__passportfile__de_json__data_is_none():
	data = None

	_ = EncryptedCredentials.de_json(data)

	assert _ is None
