#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

import json
import unittest

from tgsdk import Invoice


def test__invoice__init():
	_ = Invoice(
		title="title",
		description="description",
		start_parameter="start_parameter",
		currency="USD",
		total_amount=10
	)

	assert _.title == "title"
	assert _.description == "description"
	assert _.start_parameter == "start_parameter"
	assert _.currency == "USD"
	assert _.total_amount == 10


def test__invoice__to_dict():
	_ = Invoice(
		title="title",
		description="description",
		start_parameter="start_parameter",
		currency="USD",
		total_amount=10
	)

	unittest.TestCase().assertDictEqual(
		_.to_dict(),
		{
			"title": "title",
			"description": "description",
			"start_parameter": "start_parameter",
			"currency": "USD",
			"total_amount": 10
		}
	)


def test__invoice__to_json():
	_ = Invoice(
		title="title",
		description="description",
		start_parameter="start_parameter",
		currency="USD",
		total_amount=10
	)

	unittest.TestCase().assertDictEqual(
		json.loads(_.to_json()),
		{
			"title": "title",
			"description": "description",
			"start_parameter": "start_parameter",
			"currency": "USD",
			"total_amount": 10
		}
	)


def test__invoice__de_json():
	data = {
		"title": "title",
		"description": "description",
		"start_parameter": "start_parameter",
		"currency": "USD",
		"total_amount": 10
	}

	_ = Invoice.de_json(data)

	assert isinstance(_, Invoice) is True
	assert _.title == "title"
	assert _.description == "description"
	assert _.start_parameter == "start_parameter"
	assert _.currency == "USD"
	assert _.total_amount == 10


def test__invoice__de_json__data_is_none():
	data = None

	_ = Invoice.de_json(data)

	assert _ is None
