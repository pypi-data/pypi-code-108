#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

import json
import unittest

from tgsdk import Contact


def test__contact__init():
	_ = Contact(
		phone_number="76665554433",
		first_name="Evgeniy",
		last_name="Privalov",
		user_id="12345"
	)

	assert _.phone_number == "76665554433"
	assert _.first_name == "Evgeniy"
	assert _.last_name == "Privalov"
	assert _.user_id == "12345"
	assert _.vcard is None


def test__contact__to_dict():
	_ = Contact(
		phone_number="76665554433",
		first_name="Evgeniy",
		last_name="Privalov",
		user_id="12345"
	)

	unittest.TestCase().assertDictEqual(
		_.to_dict(),
		{
			"phone_number": "76665554433",
			"first_name": "Evgeniy",
			"last_name": "Privalov",
			"user_id": "12345"
		}
	)


def test__contact__to_json():
	_ = Contact(
		phone_number="76665554433",
		first_name="Evgeniy",
		last_name="Privalov",
		user_id="12345"
	)

	unittest.TestCase().assertDictEqual(
		json.loads(_.to_json()),
		{
			"phone_number": "76665554433",
			"first_name": "Evgeniy",
			"last_name": "Privalov",
			"user_id": "12345"
		}
	)


def test__contact__de_json():
	data = {
		"phone_number": "76665554433",
		"first_name": "Evgeniy",
		"last_name": "Privalov",
		"user_id": "12345"
	}

	_ = Contact.de_json(data)

	assert isinstance(_, Contact) is True
	assert _.phone_number == "76665554433"
	assert _.first_name == "Evgeniy"
	assert _.last_name == "Privalov"
	assert _.user_id == "12345"
	assert _.vcard is None


def test__contact__de_json__data_is_none():
	data = None

	_ = Contact.de_json(data)

	assert _ is None
