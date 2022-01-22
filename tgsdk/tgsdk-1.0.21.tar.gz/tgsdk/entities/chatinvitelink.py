#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

from typing import (
	Optional,
	Dict
)

from tgsdk import TelegramEntity
from tgsdk import User


class ChatInviteLink(TelegramEntity):
	"""
	https://core.telegram.org/bots/api#chatmember

	"""

	__slots__ = ("invite_link", "creator", "is_primary", "is_revoked", "expire_date", "member_limit")

	def __init__(
		self,
		invite_link: str,
		creator: User,
		is_primary: bool,
		is_revoked: bool,
		expire_date: Optional[int] = None,
		member_limit: Optional[int] = None
	):
		self.invite_link = invite_link
		self.creator = creator
		self.is_primary = is_primary
		self.is_revoked = is_revoked
		self.expire_date = expire_date
		self.member_limit = member_limit

	@classmethod
	def de_json(cls, data: Optional[Dict] = None):
		if not data:
			return None

		data["creator"] = User.de_json(data.get("creator"))

		return cls(**data)
