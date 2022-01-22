#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

import json
import unittest

from tgsdk import ProximityAlertTriggered, User


def test__proximityalerttriggered__init():
	_ = ProximityAlertTriggered(
		traveler=User(
			id=1,
			is_bot=False,
			username="evgeniyprivalov",
			first_name="Evgeniy",
			last_name="Privalov"
		),
		watcher=User(
			id=2,
			is_bot=False,
			username="user2",
			first_name="User"
		),
		distance=1
	)

	assert _.distance == 1

	assert _.traveler.id == 1
	assert _.traveler.is_bot is False
	assert _.traveler.username == "evgeniyprivalov"
	assert _.traveler.first_name == "Evgeniy"
	assert _.traveler.last_name == "Privalov"
	assert _.traveler.language_code is None
	assert _.traveler.can_join_groups is None
	assert _.traveler.can_read_all_group_messages is None
	assert _.traveler.supports_inline_queries is None

	assert _.watcher.id == 2
	assert _.watcher.is_bot is False
	assert _.watcher.username == "user2"
	assert _.watcher.first_name == "User"
	assert _.watcher.last_name is None
	assert _.watcher.language_code is None
	assert _.watcher.can_join_groups is None
	assert _.watcher.can_read_all_group_messages is None
	assert _.watcher.supports_inline_queries is None


def test__proximityalerttriggered__to_dict():
	_ = ProximityAlertTriggered(
		traveler=User(
			id=1,
			is_bot=False,
			username="evgeniyprivalov",
			first_name="Evgeniy",
			last_name="Privalov"
		),
		watcher=User(
			id=2,
			is_bot=False,
			username="user2",
			first_name="User"
		),
		distance=1
	)

	unittest.TestCase().assertDictEqual(
		_.to_dict(),
		{
			"traveler": {
				"id": 1,
				"is_bot": False,
				"username": "evgeniyprivalov",
				"first_name": "Evgeniy",
				"last_name": "Privalov"
			},
			"watcher": {
				"id": 2,
				"is_bot": False,
				"username": "user2",
				"first_name": "User"
			},
			"distance": 1
		}
	)


def test__proximityalerttriggered__to_json():
	_ = ProximityAlertTriggered(
		traveler=User(
			id=1,
			is_bot=False,
			username="evgeniyprivalov",
			first_name="Evgeniy",
			last_name="Privalov"
		),
		watcher=User(
			id=2,
			is_bot=False,
			username="user2",
			first_name="User"
		),
		distance=1
	)

	unittest.TestCase().assertDictEqual(
		json.loads(_.to_json()),
		{
			"traveler": {
				"id": 1,
				"is_bot": False,
				"username": "evgeniyprivalov",
				"first_name": "Evgeniy",
				"last_name": "Privalov"
			},
			"watcher": {
				"id": 2,
				"is_bot": False,
				"username": "user2",
				"first_name": "User"
			},
			"distance": 1
		}
	)


def test__proximityalerttriggered__de_json():
	data = {
		"traveler": {
			"id": 1,
			"is_bot": False,
			"username": "evgeniyprivalov",
			"first_name": "Evgeniy",
			"last_name": "Privalov"
		},
		"watcher": {
			"id": 2,
			"is_bot": False,
			"username": "user2",
			"first_name": "User"
		},
		"distance": 1
	}

	_ = ProximityAlertTriggered.de_json(data)

	assert isinstance(_, ProximityAlertTriggered) is True
	assert _.distance == 1

	assert _.traveler.id == 1
	assert _.traveler.is_bot is False
	assert _.traveler.username == "evgeniyprivalov"
	assert _.traveler.first_name == "Evgeniy"
	assert _.traveler.last_name == "Privalov"
	assert _.traveler.language_code is None
	assert _.traveler.can_join_groups is None
	assert _.traveler.can_read_all_group_messages is None
	assert _.traveler.supports_inline_queries is None

	assert _.watcher.id == 2
	assert _.watcher.is_bot is False
	assert _.watcher.username == "user2"
	assert _.watcher.first_name == "User"
	assert _.watcher.last_name is None
	assert _.watcher.language_code is None
	assert _.watcher.can_join_groups is None
	assert _.watcher.can_read_all_group_messages is None
	assert _.watcher.supports_inline_queries is None


def test__proximityalerttriggered__de_json__data_is_none():
	data = None

	_ = ProximityAlertTriggered.de_json(data)

	assert _ is None
