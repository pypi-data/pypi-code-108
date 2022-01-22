#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

import json
import unittest

from tgsdk import (
	ShippingQuery,
	ShippingAddress,
	User
)


def test__shippingquery__init():
	_ = ShippingQuery(
		id="1",
		from_user=User(
			id=1,
			username="username1",
			first_name="user1",
			is_bot=False,
		),
		invoice_payload="invoice_payload",
		shipping_address=ShippingAddress(
			country_code="ru",
			state="Saint-Petersburg",
			city="Saint-Petersburg",
			street_line1="street_line1",
			street_line2="street_line2",
			post_code="190000"
		)
	)

	assert _.id == "1"

	assert _.from_user.id == 1
	assert _.from_user.username == "username1"
	assert _.from_user.first_name == "user1"
	assert _.from_user.is_bot is False

	assert _.invoice_payload == "invoice_payload"

	assert _.shipping_address.country_code == "ru"
	assert _.shipping_address.state == "Saint-Petersburg"
	assert _.shipping_address.city == "Saint-Petersburg"
	assert _.shipping_address.street_line1 == "street_line1"
	assert _.shipping_address.street_line2 == "street_line2"
	assert _.shipping_address.post_code == "190000"


def test__shippingquery__to_dict():
	_ = ShippingQuery(
		id="1",
		from_user=User(
			id=1,
			username="username1",
			first_name="user1",
			is_bot=False,
		),
		invoice_payload="invoice_payload",
		shipping_address=ShippingAddress(
			country_code="ru",
			state="Saint-Petersburg",
			city="Saint-Petersburg",
			street_line1="street_line1",
			street_line2="street_line2",
			post_code="190000"
		)
	)

	unittest.TestCase().assertDictEqual(
		_.to_dict(),
		{
			"id": "1",
			"from": {
				"id": 1,
				"username": "username1",
				"first_name": "user1",
				"is_bot": False
			},
			"invoice_payload": "invoice_payload",
			"shipping_address": {
				"country_code": "ru",
				"state": "Saint-Petersburg",
				"city": "Saint-Petersburg",
				"street_line1": "street_line1",
				"street_line2": "street_line2",
				"post_code": "190000"
			}
		}
	)


def test__shippingquery__to_json():
	_ = ShippingQuery(
		id="1",
		from_user=User(
			id=1,
			username="username1",
			first_name="user1",
			is_bot=False,
		),
		invoice_payload="invoice_payload",
		shipping_address=ShippingAddress(
			country_code="ru",
			state="Saint-Petersburg",
			city="Saint-Petersburg",
			street_line1="street_line1",
			street_line2="street_line2",
			post_code="190000"
		)
	)

	unittest.TestCase().assertDictEqual(
		json.loads(_.to_json()),
		{
			"id": "1",
			"from": {
				"id": 1,
				"username": "username1",
				"first_name": "user1",
				"is_bot": False
			},
			"invoice_payload": "invoice_payload",
			"shipping_address": {
				"country_code": "ru",
				"state": "Saint-Petersburg",
				"city": "Saint-Petersburg",
				"street_line1": "street_line1",
				"street_line2": "street_line2",
				"post_code": "190000"
			}
		}
	)


def test__shippingquery__de_json():
	data = {
		"id": "1",
		"from": {
			"id": 1,
			"username": "username1",
			"first_name": "user1",
			"is_bot": False
		},
		"invoice_payload": "invoice_payload",
		"shipping_address": {
			"country_code": "ru",
			"state": "Saint-Petersburg",
			"city": "Saint-Petersburg",
			"street_line1": "street_line1",
			"street_line2": "street_line2",
			"post_code": "190000"
		}
	}

	_ = ShippingQuery.de_json(data)

	assert isinstance(_, ShippingQuery) is True
	assert _.id == "1"

	assert _.from_user.id == 1
	assert _.from_user.username == "username1"
	assert _.from_user.first_name == "user1"
	assert _.from_user.is_bot is False

	assert _.invoice_payload == "invoice_payload"

	assert _.shipping_address.country_code == "ru"
	assert _.shipping_address.state == "Saint-Petersburg"
	assert _.shipping_address.city == "Saint-Petersburg"
	assert _.shipping_address.street_line1 == "street_line1"
	assert _.shipping_address.street_line2 == "street_line2"
	assert _.shipping_address.post_code == "190000"


def test__shippingquery__de_json__data_is_none():
	data = None

	_ = ShippingQuery.de_json(data)

	assert _ is None
