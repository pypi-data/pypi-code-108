#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

import json
import unittest

from tgsdk import Venue, Location


def test__venue__init():
	_ = Venue(
		location=Location(
			latitude=10,
			longitude=20
		),
		title="title",
		address="address"
	)

	assert _.location.latitude == 10
	assert _.location.longitude == 20
	assert _.title == "title"
	assert _.address == "address"
	assert _.foursquare_id is None
	assert _.foursquare_type is None
	assert _.google_place_id is None
	assert _.google_place_type is None


def test__venue__to_dict():
	_ = Venue(
		location=Location(
			latitude=10,
			longitude=20
		),
		title="title",
		address="address"
	)

	unittest.TestCase().assertDictEqual(
		_.to_dict(),
		{
			"location": {
				"latitude": 10,
				"longitude": 20
			},
			"title": "title",
			"address": "address"
		}
	)


def test__venue__to_json():
	_ = Venue(
		location=Location(
			latitude=10,
			longitude=20
		),
		title="title",
		address="address"
	)

	unittest.TestCase().assertDictEqual(
		json.loads(_.to_json()),
		{
			"location": {
				"latitude": 10,
				"longitude": 20
			},
			"title": "title",
			"address": "address"
		}
	)


def test__venue__de_json():
	data = {
		"location": {
			"latitude": 10,
			"longitude": 20
		},
		"title": "title",
		"address": "address"
	}

	_ = Venue.de_json(data)

	assert isinstance(_, Venue) is True
	assert _.location.latitude == 10
	assert _.location.longitude == 20
	assert _.title == "title"
	assert _.address == "address"
	assert _.foursquare_id is None
	assert _.foursquare_type is None
	assert _.google_place_id is None
	assert _.google_place_type is None


def test__venue__de_json__data_is_none():
	data = None

	_ = Venue.de_json(data)

	assert _ is None
