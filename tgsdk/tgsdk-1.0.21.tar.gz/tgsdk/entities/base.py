#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

try:
	import ujson as json
except ImportError:
	import json

from typing import (
	TypeVar,
	List,
	Type,
	Optional,
	Dict,
	Any
)

TelegramEntityType = TypeVar("TelegramEntityType", bound="TelegramEntity", covariant=True)


class TelegramEntity(object):
	__slots__ = ()

	def __str__(self) -> str:
		"""

		:return:
		"""
		return str("<%s: %s>" % (self.__class__.__name__, self.to_dict()))

	def __getitem__(self, item: str) -> Any:
		"""

		:param item:
		:return:
		"""
		return getattr(self, item)

	def to_dict(self) -> Dict:
		"""

		:return:
		"""
		data = dict()

		# Default MRO: (<class '__main__.B'>, <class '__main__.A'>, <class 'object'>)
		# we get just our objects: (<class '__main__.B'>, <class '__main__.A'>, ) without base python class "object"
		mro = self.__class__.__mro__[:-1]

		fields = []
		for _ in mro:
			for field in _.__slots__:
				fields.append(field)

		for key in fields:
			if key == "bot" or key.startswith("_"):
				continue

			value = getattr(self, key, None)
			if value is not None:
				if hasattr(value, "to_dict"):
					data[key] = value.to_dict()
				else:
					data[key] = value

			if data.get("from_user"):
				data["from"] = data.pop("from_user", None)

		return data

	@classmethod
	def de_list(cls, data: Dict) -> List[Optional[TelegramEntityType]]:
		"""

		:param data:
		:return:
		"""
		if not data:
			return []

		return [cls.de_json(_) for _ in data]

	@classmethod
	def de_json(cls: Type[TelegramEntityType], data: Optional[Dict] = None):
		"""

		:param data:
		:return:
		"""
		if not data:
			return None

		if cls == TelegramEntity:
			return cls()

		return cls(**data)

	def to_json(self) -> str:
		"""

		:return:
		"""
		return json.dumps(self.to_dict())
