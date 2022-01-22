#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

import json
import unittest

from tgsdk import OrderInfo


def test__orderinfo__init():
	_ = OrderInfo(
		name="name",
		phone_number="76665554433",
		email="evgeniyprivalov94@gmail.com"
	)

	assert _.name == "name"
	assert _.phone_number == "76665554433"
	assert _.email == "evgeniyprivalov94@gmail.com"
	assert _.shipping_address is None


def test__orderinfo__to_dict():
	_ = OrderInfo(
		name="name",
		phone_number="76665554433",
		email="evgeniyprivalov94@gmail.com"
	)

	unittest.TestCase().assertDictEqual(
		_.to_dict(),
		{
			"name": "name",
			"phone_number": "76665554433",
			"email": "evgeniyprivalov94@gmail.com"
		}
	)


def test__orderinfo__to_json():
	_ = OrderInfo(
		name="name",
		phone_number="76665554433",
		email="evgeniyprivalov94@gmail.com"
	)

	unittest.TestCase().assertDictEqual(
		json.loads(_.to_json()),
		{
			"name": "name",
			"phone_number": "76665554433",
			"email": "evgeniyprivalov94@gmail.com"
		}
	)


def test__orderinfo__de_json():
	data = {
		"name": "name",
		"phone_number": "76665554433",
		"email": "evgeniyprivalov94@gmail.com"
	}

	_ = OrderInfo.de_json(data)

	assert isinstance(_, OrderInfo) is True
	assert _.name == "name"
	assert _.phone_number == "76665554433"
	assert _.email == "evgeniyprivalov94@gmail.com"
	assert _.shipping_address is None


def test__orderinfo__de_json__data_is_none():
	data = None

	_ = OrderInfo.de_json(data)

	assert _ is None
