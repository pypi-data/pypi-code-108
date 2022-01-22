#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

import json
import unittest

from tgsdk import (
	LabeledPrice,
	ShippingOption,
	User
)


def test__shippingoption__init():
	_ = ShippingOption(
		id="1",
		title="title",
		prices=[
			LabeledPrice(
				label="label",
				amount=1
			)
		]
	)

	assert _.id == "1"
	assert _.title == "title"

	assert len(_.prices) == 1
	assert isinstance(_.prices[0], LabeledPrice)
	assert _.prices[0].label == "label"
	assert _.prices[0].amount == 1


def test__shippingoption__to_dict():
	_ = ShippingOption(
		id="1",
		title="title",
		prices=[
			LabeledPrice(
				label="label",
				amount=1
			)
		]
	)

	unittest.TestCase().assertDictEqual(
		_.to_dict(),
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
	)


def test__shippingoption__to_json():
	_ = ShippingOption(
		id="1",
		title="title",
		prices=[
			LabeledPrice(
				label="label",
				amount=1
			)
		]
	)

	unittest.TestCase().assertDictEqual(
		json.loads(_.to_json()),
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
	)


def test__shippingoption__de_json():
	data = {
		"id": "1",
		"title": "title",
		"prices": [
			{
				"label": "label",
				"amount": 1
			}
		]
	}

	_ = ShippingOption.de_json(data)

	assert isinstance(_, ShippingOption) is True
	assert _.id == "1"
	assert _.title == "title"

	assert len(_.prices) == 1
	assert isinstance(_.prices[0], LabeledPrice)
	assert _.prices[0].label == "label"
	assert _.prices[0].amount == 1


def test__shippingoption__de_json__data_is_none():
	data = None

	_ = ShippingOption.de_json(data)

	assert _ is None
