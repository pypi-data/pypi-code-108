#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

import json
import unittest

from tgsdk import ShippingAddress


def test__shippingaddress__init():
	_ = ShippingAddress(
		country_code="ru",
		state="moscow",
		city="Moscow",
		street_line1="street_line1",
		street_line2="street_line2",
		post_code="post_code"
	)

	assert _.country_code == "ru"
	assert _.state == "moscow"
	assert _.city == "Moscow"
	assert _.street_line1 == "street_line1"
	assert _.street_line2 == "street_line2"
	assert _.post_code == "post_code"


def test__shippingaddress__to_dict():
	_ = ShippingAddress(
		country_code="ru",
		state="moscow",
		city="Moscow",
		street_line1="street_line1",
		street_line2="street_line2",
		post_code="post_code"
	)

	unittest.TestCase().assertDictEqual(
		_.to_dict(),
		{
			"country_code": "ru",
			"state": "moscow",
			"city": "Moscow",
			"street_line1": "street_line1",
			"street_line2": "street_line2",
			"post_code": "post_code"
		}
	)


def test__shippingaddress__to_json():
	_ = ShippingAddress(
		country_code="ru",
		state="moscow",
		city="Moscow",
		street_line1="street_line1",
		street_line2="street_line2",
		post_code="post_code"
	)

	unittest.TestCase().assertDictEqual(
		json.loads(_.to_json()),
		{
			"country_code": "ru",
			"state": "moscow",
			"city": "Moscow",
			"street_line1": "street_line1",
			"street_line2": "street_line2",
			"post_code": "post_code"
		}
	)


def test__shippingaddress__de_json():
	data = {
		"country_code": "ru",
		"state": "moscow",
		"city": "Moscow",
		"street_line1": "street_line1",
		"street_line2": "street_line2",
		"post_code": "post_code"
	}

	_ = ShippingAddress.de_json(data)

	assert isinstance(_, ShippingAddress) is True
	assert _.country_code == "ru"
	assert _.state == "moscow"
	assert _.city == "Moscow"
	assert _.street_line1 == "street_line1"
	assert _.street_line2 == "street_line2"
	assert _.post_code == "post_code"


def test__shippingaddress__de_json__data_is_none():
	data = None

	_ = ShippingAddress.de_json(data)

	assert _ is None
