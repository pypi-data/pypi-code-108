#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

import json
import unittest

from tgsdk import (
	AnswerShippingQuery,
	PreCheckoutQuery,
	OrderInfo,
	ShippingAddress,
	LabeledPrice,
	ShippingOption,
	User
)


def test__answershippingquery__init():
	_ = AnswerShippingQuery(
		shipping_query_id="shipping_query_id",
		ok=True,
		shipping_options=[
			ShippingOption(
				id="1",
				title="title",
				prices=[
					LabeledPrice(
						label="label",
						amount=1
					)
				]
			)
		],
		error_message="error_message"
	)

	assert _.shipping_query_id == "shipping_query_id"
	assert _.ok is True

	assert len(_.shipping_options) == 1
	assert isinstance(_.shipping_options[0], ShippingOption) is True
	assert _.shipping_options[0].id == "1"
	assert _.shipping_options[0].title == "title"
	assert len(_.shipping_options[0].prices) == 1
	assert isinstance(_.shipping_options[0].prices[0], LabeledPrice) is True
	assert _.shipping_options[0].prices[0].label == "label"
	assert _.shipping_options[0].prices[0].amount == 1
	assert _.error_message == "error_message"


def test__answershippingquery__to_dict():
	_ = AnswerShippingQuery(
		shipping_query_id="shipping_query_id",
		ok=True,
		shipping_options=[
			ShippingOption(
				id="1",
				title="title",
				prices=[
					LabeledPrice(
						label="label",
						amount=1
					)
				]
			)
		],
		error_message="error_message"
	)

	unittest.TestCase().assertDictEqual(
		_.to_dict(),
		{
			"shipping_query_id": "shipping_query_id",
			"ok": True,
			"shipping_options": [
				{
					"id": "1",
					"title": "title",
					"prices": [
						{
							"label": "label",
							"amount": 1
						}
					]
				}
			],
			"error_message": "error_message"
		}
	)


def test__answershippingquery__to_json():
	_ = AnswerShippingQuery(
		shipping_query_id="shipping_query_id",
		ok=True,
		shipping_options=[
			ShippingOption(
				id="1",
				title="title",
				prices=[
					LabeledPrice(
						label="label",
						amount=1
					)
				]
			)
		],
		error_message="error_message"
	)

	unittest.TestCase().assertDictEqual(
		json.loads(_.to_json()),
		{
			"shipping_query_id": "shipping_query_id",
			"ok": True,
			"shipping_options": [
				{
					"id": "1",
					"title": "title",
					"prices": [
						{
							"label": "label",
							"amount": 1
						}
					]
				}
			],
			"error_message": "error_message"
		}
	)


def test__answershippingquery__de_json():
	data = {
		"shipping_query_id": "shipping_query_id",
		"ok": True,
		"shipping_options": [
			{
				"id": "1",
				"title": "title",
				"prices": [
					{
						"label": "label",
						"amount": 1
					}
				]
			}
		],
		"error_message": "error_message"
	}

	_ = AnswerShippingQuery.de_json(data)

	assert isinstance(_, AnswerShippingQuery) is True
	assert _.shipping_query_id == "shipping_query_id"
	assert _.ok is True

	assert len(_.shipping_options) == 1
	assert isinstance(_.shipping_options[0], ShippingOption) is True
	assert _.shipping_options[0].id == "1"
	assert _.shipping_options[0].title == "title"
	assert len(_.shipping_options[0].prices) == 1
	assert isinstance(_.shipping_options[0].prices[0], LabeledPrice) is True
	assert _.shipping_options[0].prices[0].label == "label"
	assert _.shipping_options[0].prices[0].amount == 1
	assert _.error_message == "error_message"


def test__answershippingquery__de_json__data_is_none():
	data = None

	_ = AnswerShippingQuery.de_json(data)

	assert _ is None
