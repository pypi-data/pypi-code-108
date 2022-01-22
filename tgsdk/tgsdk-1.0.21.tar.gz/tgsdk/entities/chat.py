#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

from typing import (
	TYPE_CHECKING,
	Any
)

from tgsdk import (
	ChatPhoto,
	TelegramEntity,
)
from tgsdk.utils import constants
from .chatlocation import ChatLocation
from .chatpermissions import ChatPermissions

if TYPE_CHECKING:
	from tgsdk import Message


class Chat(TelegramEntity):
	"""
	https://core.telegram.org/bots/api#chat

	"""
	__slots__ = (
		"id", "type", "title", "username", "first_name", "last_name", "photo", "bio", "description", "invite_link",
		"pinned_message", "permissions", "slow_mode_delay", "message_auto_delete_time", "sticker_set_name",
		"can_set_sticker_set", "linked_chat_id", "location", "all_members_are_administrators"
	)

	PRIVATE = constants.CHAT_PRIVATE  # type: str
	CHAT_CHANNEL = constants.CHAT_CHANNEL  # type: str
	CHAT_GROUP = constants.CHAT_GROUP  # type: str
	CHAT_SUPERGROUP = constants.CHAT_SUPERGROUP  # type: str

	def __init__(
		self,
		id: int,
		type: str,
		title: str = None,
		username: str = None,
		first_name: str = None,
		last_name: str = None,
		photo: ChatPhoto = None,
		bio: str = None,
		description: str = None,
		invite_link: str = None,
		pinned_message: "Message" = None,
		permissions: ChatPermissions = None,
		slow_mode_delay: int = None,
		message_auto_delete_time: int = None,
		sticker_set_name: str = None,
		can_set_sticker_set: bool = None,
		linked_chat_id: int = None,
		location: ChatLocation = None,
		**_kwargs: Any
	):
		self.id = id
		self.type = type
		self.title = title
		self.username = username
		self.first_name = first_name
		self.last_name = last_name
		self.photo = photo
		self.bio = bio
		self.description = description
		self.invite_link = invite_link
		self.pinned_message = pinned_message
		self.permissions = permissions
		self.slow_mode_delay = slow_mode_delay
		self.message_auto_delete_time = message_auto_delete_time
		self.sticker_set_name = sticker_set_name
		self.can_set_sticker_set = can_set_sticker_set
		self.linked_chat_id = linked_chat_id
		self.location = location

		# TODO:
		self.all_members_are_administrators = _kwargs.get("all_members_are_administrators")

	def is_private(self) -> bool:
		return self.type == self.PRIVATE

	def is_channel(self) -> bool:
		return self.type == self.CHAT_CHANNEL

	def is_group(self) -> bool:
		return self.type == self.CHAT_GROUP

	def is_supergroup(self) -> bool:
		return self.type == self.CHAT_SUPERGROUP
