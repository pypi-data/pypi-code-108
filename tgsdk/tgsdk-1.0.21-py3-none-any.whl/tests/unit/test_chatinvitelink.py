#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

import json
import unittest

from tgsdk import (
	ChatInviteLink,
	User
)


def test__chatinvitelink__init():
	_ = ChatInviteLink(
		invite_link="invite_link",
		creator=User(
			id=1,
			first_name="first_name",
			is_bot=False
		),
		is_primary=True,
		is_revoked=False,
		expire_date=1203,
		member_limit=100
	)

	assert _.invite_link == "invite_link"

	assert _.creator.id == 1
	assert _.creator.first_name == "first_name"
	assert _.creator.is_bot is False

	assert _.is_primary is True
	assert _.is_revoked is False
	assert _.expire_date == 1203
	assert _.member_limit == 100


def test__chatinvitelink__to_dict():
	_ = ChatInviteLink(
		invite_link="invite_link",
		creator=User(
			id=1,
			first_name="first_name",
			is_bot=False
		),
		is_primary=True,
		is_revoked=False,
		expire_date=1203,
		member_limit=100
	)

	unittest.TestCase().assertDictEqual(
		_.to_dict(),
		{
			"invite_link": "invite_link",
			"creator": {
				"id": 1,
				"first_name": "first_name",
				"is_bot": False
			},
			"is_primary": True,
			"is_revoked": False,
			"expire_date": 1203,
			"member_limit": 100
		}
	)


def test__chatinvitelink__to_json():
	_ = ChatInviteLink(
		invite_link="invite_link",
		creator=User(
			id=1,
			first_name="first_name",
			is_bot=False
		),
		is_primary=True,
		is_revoked=False,
		expire_date=1203,
		member_limit=100
	)

	unittest.TestCase().assertDictEqual(
		json.loads(_.to_json()),
		{
			"invite_link": "invite_link",
			"creator": {
				"id": 1,
				"first_name": "first_name",
				"is_bot": False
			},
			"is_primary": True,
			"is_revoked": False,
			"expire_date": 1203,
			"member_limit": 100
		}
	)


def test__chatinvitelink__de_json():
	data = {
		"invite_link": "invite_link",
		"creator": {
			"id": 1,
			"first_name": "first_name",
			"is_bot": False
		},
		"is_primary": True,
		"is_revoked": False,
		"expire_date": 1203,
		"member_limit": 100
	}

	_ = ChatInviteLink.de_json(data)

	assert isinstance(_, ChatInviteLink) is True
	assert _.invite_link == "invite_link"

	assert _.creator.id == 1
	assert _.creator.first_name == "first_name"
	assert _.creator.is_bot is False

	assert _.is_primary is True
	assert _.is_revoked is False
	assert _.expire_date == 1203
	assert _.member_limit == 100


def test__chatinvitelink__de_json__data_is_none():
	data = None

	_ = ChatInviteLink.de_json(data)

	assert _ is None
