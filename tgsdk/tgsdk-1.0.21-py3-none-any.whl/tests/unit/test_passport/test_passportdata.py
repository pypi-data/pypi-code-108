#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

import json
import unittest

from tgsdk import (
	PassportData,
	EncryptedPassportElement,
	EncryptedCredentials
)


def test__passportdata__init():
	_ = PassportData(
		data=[
			EncryptedPassportElement(
				type="type",
				data="data",
				phone_number="76665554433",
				email="evgeniyprivalov94@gmail.com"
			)
		],
		credentials=EncryptedCredentials(
			data="data",
			hash="hash",
			secret="secret"
		)
	)

	assert _.data[0].type == "type"
	assert _.data[0].data == "data"
	assert _.data[0].phone_number == "76665554433"
	assert _.data[0].email == "evgeniyprivalov94@gmail.com"
	assert _.data[0].files is None
	assert _.data[0].front_side is None
	assert _.data[0].reverse_side is None
	assert _.data[0].selfie is None
	assert _.data[0].translation is None
	assert _.data[0].hash is None

	assert _.credentials.data == "data"
	assert _.credentials.hash == "hash"
	assert _.credentials.secret == "secret"


def test__passportdata__to_dict():
	_ = PassportData(
		data=[
			EncryptedPassportElement(
				type="type",
				data="data",
				phone_number="76665554433",
				email="evgeniyprivalov94@gmail.com"
			)
		],
		credentials=EncryptedCredentials(
			data="data",
			hash="hash",
			secret="secret"
		)
	)

	unittest.TestCase().assertDictEqual(
		_.to_dict(),
		{
			"data": [
				{
					"type": "type",
					"data": "data",
					"phone_number": "76665554433",
					"email": "evgeniyprivalov94@gmail.com"
				}
			],
			"credentials": {
				"data": "data",
				"hash": "hash",
				"secret": "secret"
			}
		}
	)


def test__passportdata__to_dict__with_empty_value():
	_ = PassportData(
		data=[
			EncryptedPassportElement(
				type="type",
				data="data",
				phone_number="76665554433",
				email="evgeniyprivalov94@gmail.com"
			),
			None
		],
		credentials=EncryptedCredentials(
			data="data",
			hash="hash",
			secret="secret"
		)
	)

	unittest.TestCase().assertDictEqual(
		_.to_dict(),
		{
			"data": [
				{
					"type": "type",
					"data": "data",
					"phone_number": "76665554433",
					"email": "evgeniyprivalov94@gmail.com"
				}
			],
			"credentials": {
				"data": "data",
				"hash": "hash",
				"secret": "secret"
			}
		}
	)


def test__passportdata__to_json():
	_ = PassportData(
		data=[
			EncryptedPassportElement(
				type="type",
				data="data",
				phone_number="76665554433",
				email="evgeniyprivalov94@gmail.com"
			)
		],
		credentials=EncryptedCredentials(
			data="data",
			hash="hash",
			secret="secret"
		)
	)

	unittest.TestCase().assertDictEqual(
		json.loads(_.to_json()),
		{
			"data": [
				{
					"type": "type",
					"data": "data",
					"phone_number": "76665554433",
					"email": "evgeniyprivalov94@gmail.com"
				}
			],
			"credentials": {
				"data": "data",
				"hash": "hash",
				"secret": "secret"
			}
		}
	)


def test__passportdata__de_json():
	data = {
		"data": [
			{
				"type": "type",
				"data": "data",
				"phone_number": "76665554433",
				"email": "evgeniyprivalov94@gmail.com"
			}
		],
		"credentials": {
			"data": "data",
			"hash": "hash",
			"secret": "secret"
		}
	}

	_ = PassportData.de_json(data)

	assert isinstance(_, PassportData) is True
	assert _.data[0].type == "type"
	assert _.data[0].data == "data"
	assert _.data[0].phone_number == "76665554433"
	assert _.data[0].email == "evgeniyprivalov94@gmail.com"
	assert _.data[0].files == []
	assert _.data[0].front_side is None
	assert _.data[0].reverse_side is None
	assert _.data[0].selfie is None
	assert _.data[0].translation == []
	assert _.data[0].hash is None

	assert _.credentials.data == "data"
	assert _.credentials.hash == "hash"
	assert _.credentials.secret == "secret"


def test__passportdata__de_json__data_is_none():
	data = None

	_ = PassportData.de_json(data)

	assert _ is None
