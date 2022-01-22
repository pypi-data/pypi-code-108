#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

import json
import unittest

from tgsdk import EncryptedPassportElement


def test__encryptedpassportelement__init():
	_ = EncryptedPassportElement(
		type="type",
		data="data",
		phone_number="76665554433",
		email="evgeniyprivalov94@gmail.com",
	)

	assert _.type == "type"
	assert _.data == "data"
	assert _.phone_number == "76665554433"
	assert _.email == "evgeniyprivalov94@gmail.com"
	assert _.files is None
	assert _.front_side is None
	assert _.reverse_side is None
	assert _.selfie is None
	assert _.translation is None
	assert _.hash is None


def test__encryptedpassportelement__to_dict():
	_ = EncryptedPassportElement(
		type="type",
		data="data",
		phone_number="76665554433",
		email="evgeniyprivalov94@gmail.com",
	)

	unittest.TestCase().assertDictEqual(
		_.to_dict(),
		{
			"type": "type",
			"data": "data",
			"phone_number": "76665554433",
			"email": "evgeniyprivalov94@gmail.com"
		}
	)


def test__encryptedpassportelement__to_json():
	_ = EncryptedPassportElement(
		type="type",
		data="data",
		phone_number="76665554433",
		email="evgeniyprivalov94@gmail.com",
	)

	unittest.TestCase().assertDictEqual(
		json.loads(_.to_json()),
		{
			"type": "type",
			"data": "data",
			"phone_number": "76665554433",
			"email": "evgeniyprivalov94@gmail.com"
		}
	)


def test__encryptedpassportelement__de_json():
	data = {
		"type": "type",
		"data": "data",
		"phone_number": "76665554433",
		"email": "evgeniyprivalov94@gmail.com"
	}

	_ = EncryptedPassportElement.de_json(data)

	assert isinstance(_, EncryptedPassportElement) is True
	assert _.type == "type"
	assert _.data == "data"
	assert _.phone_number == "76665554433"
	assert _.email == "evgeniyprivalov94@gmail.com"
	assert _.files == []
	assert _.front_side is None
	assert _.reverse_side is None
	assert _.selfie is None
	assert _.translation == []
	assert _.hash is None


def test__encryptedpassportelement__de_json__data_is_none():
	data = None

	_ = EncryptedPassportElement.de_json(data)

	assert _ is None
