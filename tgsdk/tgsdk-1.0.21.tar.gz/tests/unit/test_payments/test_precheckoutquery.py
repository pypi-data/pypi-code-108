#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

import json
import unittest

from tgsdk import (
	PreCheckoutQuery,
	OrderInfo,
	ShippingAddress,
	LabeledPrice,
	ShippingOption,
	User
)


def test__precheckoutquery__init():
	_ = PreCheckoutQuery(
		id="1",
		from_user=User(
			id=1,
			username="username1",
			first_name="user1",
			is_bot=False
		),
		currency="RUB",
		total_amount=1,
		invoice_payload="invoice_payload",
		shipping_option_id="shipping_option_id",
		order_info=OrderInfo(
			name="Evgeniy Privalov",
			phone_number="76665554433",
			email="example@example.com",
			shipping_address=ShippingAddress(
				country_code="ru",
				state="Saint-Petersburg",
				city="Saint-Petersburg",
				street_line1="street_line1",
				street_line2="street_line2",
				post_code="190000"
			)
		)
	)

	assert _.id == "1"

	assert _.from_user.id == 1
	assert _.from_user.username == "username1"
	assert _.from_user.first_name == "user1"
	assert _.from_user.is_bot is False

	assert _.currency == "RUB"
	assert _.total_amount == 1
	assert _.invoice_payload == "invoice_payload"
	assert _.shipping_option_id == "shipping_option_id"

	assert _.order_info.name == "Evgeniy Privalov"
	assert _.order_info.phone_number == "76665554433"
	assert _.order_info.email == "example@example.com"
	assert _.order_info.shipping_address.country_code == "ru"
	assert _.order_info.shipping_address.state == "Saint-Petersburg"
	assert _.order_info.shipping_address.city == "Saint-Petersburg"
	assert _.order_info.shipping_address.street_line1 == "street_line1"
	assert _.order_info.shipping_address.street_line2 == "street_line2"
	assert _.order_info.shipping_address.post_code == "190000"


def test__precheckoutquery__to_dict():
	_ = PreCheckoutQuery(
		id="1",
		from_user=User(
			id=1,
			username="username1",
			first_name="user1",
			is_bot=False
		),
		currency="RUB",
		total_amount=1,
		invoice_payload="invoice_payload",
		shipping_option_id="shipping_option_id",
		order_info=OrderInfo(
			name="Evgeniy Privalov",
			phone_number="76665554433",
			email="example@example.com",
			shipping_address=ShippingAddress(
				country_code="ru",
				state="Saint-Petersburg",
				city="Saint-Petersburg",
				street_line1="street_line1",
				street_line2="street_line2",
				post_code="190000"
			)
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
			"currency": "RUB",
			"total_amount": 1,
			"invoice_payload": "invoice_payload",
			"shipping_option_id": "shipping_option_id",
			"order_info": {
				"name": "Evgeniy Privalov",
				"phone_number": "76665554433",
				"email": "example@example.com",
				"shipping_address": {
					"country_code": "ru",
					"state": "Saint-Petersburg",
					"city": "Saint-Petersburg",
					"street_line1": "street_line1",
					"street_line2": "street_line2",
					"post_code": "190000"
				}
			}
		}
	)


def test__precheckoutquery__to_json():
	_ = PreCheckoutQuery(
		id="1",
		from_user=User(
			id=1,
			username="username1",
			first_name="user1",
			is_bot=False
		),
		currency="RUB",
		total_amount=1,
		invoice_payload="invoice_payload",
		shipping_option_id="shipping_option_id",
		order_info=OrderInfo(
			name="Evgeniy Privalov",
			phone_number="76665554433",
			email="example@example.com",
			shipping_address=ShippingAddress(
				country_code="ru",
				state="Saint-Petersburg",
				city="Saint-Petersburg",
				street_line1="street_line1",
				street_line2="street_line2",
				post_code="190000"
			)
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
			"currency": "RUB",
			"total_amount": 1,
			"invoice_payload": "invoice_payload",
			"shipping_option_id": "shipping_option_id",
			"order_info": {
				"name": "Evgeniy Privalov",
				"phone_number": "76665554433",
				"email": "example@example.com",
				"shipping_address": {
					"country_code": "ru",
					"state": "Saint-Petersburg",
					"city": "Saint-Petersburg",
					"street_line1": "street_line1",
					"street_line2": "street_line2",
					"post_code": "190000"
				}
			}
		}
	)


def test__precheckoutquery__de_json():
	data = {
		"id": "1",
		"from": {
			"id": 1,
			"username": "username1",
			"first_name": "user1",
			"is_bot": False
		},
		"currency": "RUB",
		"total_amount": 1,
		"invoice_payload": "invoice_payload",
		"shipping_option_id": "shipping_option_id",
		"order_info": {
			"name": "Evgeniy Privalov",
			"phone_number": "76665554433",
			"email": "example@example.com",
			"shipping_address": {
				"country_code": "ru",
				"state": "Saint-Petersburg",
				"city": "Saint-Petersburg",
				"street_line1": "street_line1",
				"street_line2": "street_line2",
				"post_code": "190000"
			}
		}
	}

	_ = PreCheckoutQuery.de_json(data)

	assert isinstance(_, PreCheckoutQuery) is True
	assert _.id == "1"

	assert _.from_user.id == 1
	assert _.from_user.username == "username1"
	assert _.from_user.first_name == "user1"
	assert _.from_user.is_bot is False

	assert _.currency == "RUB"
	assert _.total_amount == 1
	assert _.invoice_payload == "invoice_payload"
	assert _.shipping_option_id == "shipping_option_id"

	assert _.order_info.name == "Evgeniy Privalov"
	assert _.order_info.phone_number == "76665554433"
	assert _.order_info.email == "example@example.com"
	assert _.order_info.shipping_address.country_code == "ru"
	assert _.order_info.shipping_address.state == "Saint-Petersburg"
	assert _.order_info.shipping_address.city == "Saint-Petersburg"
	assert _.order_info.shipping_address.street_line1 == "street_line1"
	assert _.order_info.shipping_address.street_line2 == "street_line2"
	assert _.order_info.shipping_address.post_code == "190000"


def test__precheckoutquery__de_json__data_is_none():
	data = None

	_ = PreCheckoutQuery.de_json(data)

	assert _ is None
