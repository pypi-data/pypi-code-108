#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import logging.config
from dataclasses import dataclass
from typing import List
import urllib.error
import urllib.parse
import urllib.request

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.propagate = True

@dataclass(eq=False)
class NgTelegramHandler(logging.Handler):
	token: str
	ids: List[int]
	disable_notification: bool = False
	disable_web_page_preview: bool = True
	timeout: float = 2.0
	level: str = logging.NOTSET

	def __post_init__(self):
		super().__init__(level=self.level)

	def emit(self, record: logging.LogRecord) -> None:
		try:
			url: str = f"https://api.telegram.org/bot{urllib.parse.quote(self.token, safe='')}/sendMessage"
			for chat_id in self.ids:
				payload = {
					'chat_id':                  chat_id,
					'text':                     self.format(record),
					'disable_web_page_preview': self.disable_web_page_preview,
					'disable_notification':     self.disable_notification,
					'parse_mode':               getattr(self.formatter, 'parse_mode', None),
				}
				req = urllib.request.Request(url, urllib.parse.urlencode(payload).encode())
				with urllib.request.urlopen(req, timeout=self.timeout):
					pass
				logger.debug(f'Sent logging-message to {chat_id} tg chat')
		# except urllib.error.URLError:
		except:
			self.handleError(record)
