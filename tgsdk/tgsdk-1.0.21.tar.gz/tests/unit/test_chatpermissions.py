#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

import json
import unittest

from tgsdk import ChatPermissions


def test__chatpermissions__init():
	_ = ChatPermissions()

	assert _.can_send_messages is None
	assert _.can_send_media_messages is None
	assert _.can_send_polls is None
	assert _.can_send_other_messages is None
	assert _.can_add_web_page_previews is None
	assert _.can_change_info is None
	assert _.can_invite_users is None
	assert _.can_pin_messages is None


def test__chatpermissions__to_dict():
	_ = ChatPermissions()

	unittest.TestCase().assertDictEqual(
		_.to_dict(),
		{}
	)


def test__chatpermissions__to_json():
	_ = ChatPermissions()

	unittest.TestCase().assertDictEqual(
		json.loads(_.to_json()),
		{}
	)


def test__chatpermissions__de_json():
	data = {
	}

	_ = ChatPermissions.de_json(data)

	assert _ is None


def test__chatpermissions__de_json__with_data():
	data = {
		"can_send_messages": True
	}

	_ = ChatPermissions.de_json(data)

	assert isinstance(_, ChatPermissions) is True
	assert _.can_send_messages is True
	assert _.can_send_media_messages is None
	assert _.can_send_polls is None
	assert _.can_send_other_messages is None
	assert _.can_add_web_page_previews is None
	assert _.can_change_info is None
	assert _.can_invite_users is None
	assert _.can_pin_messages is None


def test__chatpermissions__de_json__data_is_none():
	data = None

	_ = ChatPermissions.de_json(data)

	assert _ is None
