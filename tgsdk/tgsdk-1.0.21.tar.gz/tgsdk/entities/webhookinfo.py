#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

from typing import List

from tgsdk import TelegramEntity


class WebhookInfo(TelegramEntity):
	"""
	https://core.telegram.org/bots/api#webhookinfo

	"""

	__slots__ = (
		"url", "has_custom_certificate", "pending_update_count", "ip_address",
		"last_error_date", "last_error_message", "max_connections", "allowed_updates"
	)

	def __init__(
		self,
		url: str,
		has_custom_certificate: bool,
		pending_update_count: int,
		ip_address: str = None,
		last_error_date: int = None,
		last_error_message: str = None,
		max_connections: int = None,
		allowed_updates: List[str] = None,
	):
		self.url = url
		self.has_custom_certificate = has_custom_certificate
		self.pending_update_count = pending_update_count

		self.ip_address = ip_address
		self.last_error_date = last_error_date
		self.last_error_message = last_error_message
		self.max_connections = max_connections
		self.allowed_updates = allowed_updates

	def is_url_equal(self, url: str) -> bool:
		return self.url == url

	def is_domain_equal(self, domain: str) -> bool:
		return domain in self.url
