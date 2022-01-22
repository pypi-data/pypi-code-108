#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

import json
import unittest

from tgsdk import ChatMember, User


def test__chatmember__init():
	_ = ChatMember(
		user=User(
			id=123,
			is_bot=False,
			username="evgeniyprivalov",
			first_name="Evgeniy",
			last_name="Privalov"
		),
		status=ChatMember.CHAT_MEMBER_MEMBER
	)

	assert _.status == "member"
	assert _.custom_title is None
	assert _.is_anonymous is None
	assert _.can_be_edited is None
	assert _.can_post_messages is None
	assert _.can_edit_messages is None
	assert _.can_delete_messages is None
	assert _.can_restrict_members is None
	assert _.can_promote_members is None
	assert _.can_change_info is None
	assert _.can_invite_users is None
	assert _.can_pin_messages is None
	assert _.is_member is None
	assert _.can_send_messages is None
	assert _.can_send_media_messages is None
	assert _.can_send_polls is None
	assert _.can_send_other_messages is None
	assert _.can_add_web_page_previews is None
	assert _.until_date is None

	assert _.user.id == 123
	assert _.user.is_bot is False
	assert _.user.username == "evgeniyprivalov"
	assert _.user.first_name == "Evgeniy"
	assert _.user.last_name == "Privalov"


def test__chatmember__to_dict():
	_ = ChatMember(
		user=User(
			id=123,
			is_bot=False,
			username="evgeniyprivalov",
			first_name="Evgeniy",
			last_name="Privalov"
		),
		status=ChatMember.CHAT_MEMBER_MEMBER
	)

	unittest.TestCase().assertDictEqual(
		_.to_dict(),
		{
			"user": {
				"id": 123,
				"is_bot": False,
				"username": "evgeniyprivalov",
				"first_name": "Evgeniy",
				"last_name": "Privalov"
			},
			"status": "member"
		}
	)


def test__chatmember__to_json():
	_ = ChatMember(
		user=User(
			id=123,
			is_bot=False,
			username="evgeniyprivalov",
			first_name="Evgeniy",
			last_name="Privalov"
		),
		status=ChatMember.CHAT_MEMBER_MEMBER
	)

	unittest.TestCase().assertDictEqual(
		json.loads(_.to_json()),
		{
			"user": {
				"id": 123,
				"is_bot": False,
				"username": "evgeniyprivalov",
				"first_name": "Evgeniy",
				"last_name": "Privalov"
			},
			"status": "member"
		}
	)


def test__chatmember__de_json():
	data = {
		"user": {
			"id": 123,
			"is_bot": False,
			"username": "evgeniyprivalov",
			"first_name": "Evgeniy",
			"last_name": "Privalov"
		},
		"status": "member"
	}

	_ = ChatMember.de_json(data)

	assert isinstance(_, ChatMember) is True
	assert _.status == "member"
	assert _.custom_title is None
	assert _.is_anonymous is None
	assert _.can_be_edited is None
	assert _.can_post_messages is None
	assert _.can_edit_messages is None
	assert _.can_delete_messages is None
	assert _.can_restrict_members is None
	assert _.can_promote_members is None
	assert _.can_change_info is None
	assert _.can_invite_users is None
	assert _.can_pin_messages is None
	assert _.is_member is None
	assert _.can_send_messages is None
	assert _.can_send_media_messages is None
	assert _.can_send_polls is None
	assert _.can_send_other_messages is None
	assert _.can_add_web_page_previews is None
	assert _.until_date is None

	assert _.user.id == 123
	assert _.user.is_bot is False
	assert _.user.username == "evgeniyprivalov"
	assert _.user.first_name == "Evgeniy"
	assert _.user.last_name == "Privalov"


def test__chatmember__de_json__data_is_none():
	data = None

	_ = ChatMember.de_json(data)

	assert _ is None
