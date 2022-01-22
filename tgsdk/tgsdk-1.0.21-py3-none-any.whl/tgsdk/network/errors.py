#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

from tgsdk.utils.types import ID


class TelegramException(Exception):
	"""
	Base Telegram Exception Handler class

	"""

	def __init__(self, message: str):
		super().__init__()

		self.message = message

	def __str__(self) -> str:
		return str(self.message)


class SeeOther(TelegramException):
	"""
	https://core.telegram.org/api/errors#303-see-other

	"""
	pass


class BadRequest(TelegramException):
	"""
	https://core.telegram.org/api/errors#400-bad-request

	"""
	pass


class Unauthorized(TelegramException):
	"""
	https://core.telegram.org/api/errors#401-unauthorized

	"""
	pass


class Forbidden(TelegramException):
	"""
	https://core.telegram.org/api/errors#403-forbidden

	"""
	pass


class NotFound(TelegramException):
	"""
	https://core.telegram.org/api/errors#404-not-found

	"""
	pass


class NotAcceptable(TelegramException):
	"""
	https://core.telegram.org/api/errors#406-not-acceptable

	"""
	pass


class Flood(TelegramException):
	"""
	https://core.telegram.org/api/errors#420-flood

	"""
	pass


class Internal(TelegramException):
	"""
	https://core.telegram.org/api/errors#500-internal

	"""
	pass


# Validation Exceptions
class InvalidToken(TelegramException):

	def __init__(self):
		super().__init__(message="Invalid token")


# Network Exceptions
class RetryAfter(TelegramException):
	"""
	https://core.telegram.org/bots/faq#broadcasting-to-users

	"""

	def __init__(self, retry_after_seconds: int):
		"""

		:param retry_after_seconds:
		"""
		self.retry_after_seconds = float(retry_after_seconds)

		super().__init__(message="Broadcasting limits exceeded. Please, retry in %s seconds" % retry_after_seconds)


class ChatMigrated(TelegramException):
	"""
	https://core.telegram.org/bots/api#responseparameters

	"""

	def __init__(self, chat_id: ID):
		self.chat_id = chat_id

		super().__init__("Group migrated to supergroup. New chat id: %s" % chat_id)


class NetworkError(TelegramException):
	"""
	Base Network exception

	"""
	pass


class TimeOutError(TelegramException):
	"""
	Raised when a socket timeout error occurs

	"""

	def __init__(self):
		super().__init__(message="Timed out")
