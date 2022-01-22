#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

import json
import unittest

from tgsdk import (
	Chat,
	ChatMemberUpdated,
	ChatMember,
	ChatInviteLink,
	User
)


def test__chatmemberupdate__init():
	_ = ChatMemberUpdated(
		chat=Chat(
			id=1234567890,
			type=Chat.CHAT_GROUP,
			title="Chat Title"
		),
		invite_link=ChatInviteLink(
			invite_link="invite_link",
			creator=User(
				id=2,
				first_name="user2",
				is_bot=False
			),
			is_primary=True,
			is_revoked=False
		),
		from_user=User(
			id=3,
			first_name="user3",
			is_bot=False
		),
		date=1231231,
		old_chat_member=ChatMember(
			user=User(
				id=3,
				first_name="user3",
				is_bot=False
			),
			status=ChatMember.CHAT_MEMBER_MEMBER
		),
		new_chat_member=ChatMember(
			user=User(
				id=3,
				first_name="user3",
				is_bot=False
			),
			status=ChatMember.CHAT_MEMBER_KICKED
		)
	)

	assert _.chat.id == 1234567890
	assert _.chat.type == "group"
	assert _.chat.title == "Chat Title"

	assert _.invite_link.invite_link == "invite_link"
	assert _.invite_link.creator.id == 2
	assert _.invite_link.creator.first_name == "user2"
	assert _.invite_link.creator.is_bot is False

	assert _.from_user.id == 3
	assert _.from_user.first_name == "user3"
	assert _.from_user.is_bot is False

	assert _.date == 1231231

	assert _.old_chat_member.user.id == 3
	assert _.old_chat_member.user.first_name == "user3"
	assert _.old_chat_member.user.is_bot is False
	assert _.old_chat_member.status == "member"

	assert _.new_chat_member.user.id == 3
	assert _.new_chat_member.user.first_name == "user3"
	assert _.new_chat_member.user.is_bot is False
	assert _.new_chat_member.status == "kicked"


def test__chatmemberupdate__to_dict():
	_ = ChatMemberUpdated(
		chat=Chat(
			id=1234567890,
			type=Chat.CHAT_GROUP,
			title="Chat Title"
		),
		invite_link=ChatInviteLink(
			invite_link="invite_link",
			creator=User(
				id=2,
				first_name="user2",
				is_bot=False
			),
			is_primary=True,
			is_revoked=False
		),
		from_user=User(
			id=3,
			first_name="user3",
			is_bot=False
		),
		date=1231231,
		old_chat_member=ChatMember(
			user=User(
				id=3,
				first_name="user3",
				is_bot=False
			),
			status=ChatMember.CHAT_MEMBER_MEMBER
		),
		new_chat_member=ChatMember(
			user=User(
				id=3,
				first_name="user3",
				is_bot=False
			),
			status=ChatMember.CHAT_MEMBER_KICKED
		)
	)

	unittest.TestCase().assertDictEqual(
		_.to_dict(),
		{
			"chat": {
				"id": 1234567890,
				"type": "group",
				"title": "Chat Title"
			},
			"invite_link": {
				"invite_link": "invite_link",
				"creator": {
					"id": 2,
					"first_name": "user2",
					"is_bot": False
				},
				"is_primary": True,
				"is_revoked": False
			},
			"from": {
				"id": 3,
				"first_name": "user3",
				"is_bot": False
			},
			"date": 1231231,
			"old_chat_member": {
				"user": {
					"id": 3,
					"first_name": "user3",
					"is_bot": False
				},
				"status": "member"
			},
			"new_chat_member": {
				"user": {
					"id": 3,
					"first_name": "user3",
					"is_bot": False
				},
				"status": "kicked"
			}
		}
	)


def test__chatmemberupdate__to_json():
	_ = ChatMemberUpdated(
		chat=Chat(
			id=1234567890,
			type=Chat.CHAT_GROUP,
			title="Chat Title"
		),
		invite_link=ChatInviteLink(
			invite_link="invite_link",
			creator=User(
				id=2,
				first_name="user2",
				is_bot=False
			),
			is_primary=True,
			is_revoked=False
		),
		from_user=User(
			id=3,
			first_name="user3",
			is_bot=False
		),
		date=1231231,
		old_chat_member=ChatMember(
			user=User(
				id=3,
				first_name="user3",
				is_bot=False
			),
			status=ChatMember.CHAT_MEMBER_MEMBER
		),
		new_chat_member=ChatMember(
			user=User(
				id=3,
				first_name="user3",
				is_bot=False
			),
			status=ChatMember.CHAT_MEMBER_KICKED
		)
	)

	unittest.TestCase().assertDictEqual(
		json.loads(_.to_json()),
		{
			"chat": {
				"id": 1234567890,
				"type": "group",
				"title": "Chat Title"
			},
			"invite_link": {
				"invite_link": "invite_link",
				"creator": {
					"id": 2,
					"first_name": "user2",
					"is_bot": False
				},
				"is_primary": True,
				"is_revoked": False
			},
			"from": {
				"id": 3,
				"first_name": "user3",
				"is_bot": False
			},
			"date": 1231231,
			"old_chat_member": {
				"user": {
					"id": 3,
					"first_name": "user3",
					"is_bot": False
				},
				"status": "member"
			},
			"new_chat_member": {
				"user": {
					"id": 3,
					"first_name": "user3",
					"is_bot": False
				},
				"status": "kicked"
			}
		}
	)


def test__chatmemberupdate__de_json():
	data = {
		"chat": {
			"id": 1234567890,
			"type": "group",
			"title": "Chat Title"
		},
		"invite_link": {
			"invite_link": "invite_link",
			"creator": {
				"id": 2,
				"first_name": "user2",
				"is_bot": False
			},
			"is_primary": True,
			"is_revoked": False
		},
		"from": {
			"id": 3,
			"first_name": "user3",
			"is_bot": False
		},
		"date": 1231231,
		"old_chat_member": {
			"user": {
				"id": 3,
				"first_name": "user3",
				"is_bot": False
			},
			"status": "member"
		},
		"new_chat_member": {
			"user": {
				"id": 3,
				"first_name": "user3",
				"is_bot": False
			},
			"status": "kicked"
		}
	}

	_ = ChatMemberUpdated.de_json(data)

	assert isinstance(_, ChatMemberUpdated) is True

	assert _.chat.id == 1234567890
	assert _.chat.type == "group"
	assert _.chat.title == "Chat Title"

	assert _.invite_link.invite_link == "invite_link"
	assert _.invite_link.creator.id == 2
	assert _.invite_link.creator.first_name == "user2"
	assert _.invite_link.creator.is_bot is False

	assert _.from_user.id == 3
	assert _.from_user.first_name == "user3"
	assert _.from_user.is_bot is False

	assert _.date == 1231231

	assert _.old_chat_member.user.id == 3
	assert _.old_chat_member.user.first_name == "user3"
	assert _.old_chat_member.user.is_bot is False
	assert _.old_chat_member.status == "member"

	assert _.new_chat_member.user.id == 3
	assert _.new_chat_member.user.first_name == "user3"
	assert _.new_chat_member.user.is_bot is False
	assert _.new_chat_member.status == "kicked"


def test__chatmemberupdate__de_json__data_is_none():
	data = None

	_ = ChatMemberUpdated.de_json(data)

	assert _ is None
