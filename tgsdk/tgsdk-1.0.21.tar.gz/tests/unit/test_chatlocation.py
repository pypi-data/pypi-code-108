#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

import json
import unittest

from tgsdk import ChatLocation, Location


def test__chatlocation__init():
	_ = ChatLocation(
		location=Location(
			latitude=10,
			longitude=20
		),
		address="address"
	)

	assert _.location.latitude == 10
	assert _.location.longitude == 20
	assert _.address == "address"


def test__chatlocation__to_dict():
	_ = ChatLocation(
		location=Location(
			latitude=10,
			longitude=20
		),
		address="address"
	)

	unittest.TestCase().assertDictEqual(
		_.to_dict(),
		{
			"location": {
				"latitude": 10,
				"longitude": 20
			},
			"address": "address"
		}
	)


def test__chatlocation__to_json():
	_ = ChatLocation(
		location=Location(
			latitude=10,
			longitude=20
		),
		address="address"
	)

	unittest.TestCase().assertDictEqual(
		json.loads(_.to_json()),
		{
			"location": {
				"latitude": 10,
				"longitude": 20
			},
			"address": "address"
		}
	)


def test__chatlocation__de_json():
	data = {
		"location": {
			"latitude": 10,
			"longitude": 20
		},
		"address": "address"
	}

	_ = ChatLocation.de_json(data)

	assert isinstance(_, ChatLocation) is True
	assert _.location.latitude == 10
	assert _.location.longitude == 20
	assert _.address == "address"


def test__chatlocation__de_json__data_is_none():
	data = None

	_ = ChatLocation.de_json(data)

	assert _ is None
