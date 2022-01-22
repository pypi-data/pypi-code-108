#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

import json
import unittest

from tgsdk import Location


def test__location__init():
	_ = Location(
		latitude=10,
		longitude=20
	)

	assert _.latitude == 10
	assert _.longitude == 20
	assert _.horizontal_accuracy is None
	assert _.live_period is None
	assert _.heading is None
	assert _.proximity_alert_radius is None


def test__location__to_dict():
	_ = Location(
		latitude=10,
		longitude=20
	)

	unittest.TestCase().assertDictEqual(
		_.to_dict(),
		{
			"latitude": 10,
			"longitude": 20
		}
	)


def test__location__to_json():
	_ = Location(
		latitude=10,
		longitude=20
	)

	unittest.TestCase().assertDictEqual(
		json.loads(_.to_json()),
		{
			"latitude": 10,
			"longitude": 20
		}
	)


def test__location__de_json():
	data = {
		"latitude": 10,
		"longitude": 20
	}

	_ = Location.de_json(data)

	assert isinstance(_, Location) is True
	assert _.latitude == 10
	assert _.longitude == 20
	assert _.proximity_alert_radius is None
	assert _.heading is None
	assert _.live_period is None
	assert _.horizontal_accuracy is None


def test__location__de_json__data_is_none():
	data = None

	_ = Location.de_json(data)

	assert _ is None
