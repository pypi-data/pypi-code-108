#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

from typing import (
	Optional,
	List,
	Dict,
	Union
)

from tgsdk import (
	EncryptedCredentials,
	EncryptedPassportElement,
	TelegramEntity
)


class PassportData(TelegramEntity):
	"""
	https://core.telegram.org/bots/api#passportdata

	"""

	__slots__ = ("data", "credentials")

	def __init__(
		self,
		data: List[EncryptedPassportElement],
		credentials: EncryptedCredentials
	):
		self.data = data
		self.credentials = credentials

	def to_dict(self) -> Dict:
		"""

		:return:
		"""
		data = super().to_dict()

		data["data"] = []
		for _ in self.data:
			if isinstance(_, EncryptedPassportElement):
				data["data"].append(_.to_dict())

		return data

	@classmethod
	def de_json(cls, data: Optional[Dict] = None) -> Union["PassportData", None]:
		"""

		:param data:
		:return:
		"""
		if not data:
			return None

		data["data"] = EncryptedPassportElement.de_list(data.get("data"))
		data["credentials"] = EncryptedCredentials.de_json(data.get("credentials"))

		return cls(**data)
