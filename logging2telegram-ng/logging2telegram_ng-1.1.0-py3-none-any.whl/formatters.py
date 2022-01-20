# -*- coding: utf-8 -*-
import logging
import html
from typing import Optional


class HtmlFormatter(logging.Formatter):
	fmt: str = '📢<b>%(levelname)s</b> > <code>%(filename)s:%(name)s:%(funcName)s</code> (line:%(lineno)s)' \
	           '<pre>%(message)s</pre><code>%(exc_text)s</code>\n_________________________\n🕐<i>%(asctime)s</i>'
	style: str = '%'
	parse_mode: str = 'HTML'

	def __init__(self, fmt: Optional[str] = None, *args, **kwargs):
		super().__init__(fmt or self.fmt, *args, **kwargs)

	def format(self, record: logging.LogRecord) -> str:
		record.funcName: str = html.escape(record.funcName)
		record.name: str = html.escape(record.name)
		record.msg: str = html.escape(str(record.msg))
		record.message = record.getMessage()
		if self.usesTime():
			record.asctime = self.formatTime(record, self.datefmt)
		record.exc_text = str()
		if record.exc_info:
			record.exc_text = self.formatException(record.exc_info)

		return self.formatMessage(record)

# emoji unicode obtained from https://emojiterra.com/
class NgHtmlFormatter(logging.Formatter):
	fmt: str = '%(levelnameHTML)s > <code>%(filenameHTML)s:%(nameHTML)s:%(funcNameHTML)s</code> (line:%(lineno)s)' \
	           '\n<code>%(messageHTML)s</code><code>%(exc_text)s</code>\n_________________________\n\u23F1<i>%(asctime)s</i>'
	style: str = '%'
	parse_mode: str = 'HTML'
	BASE_EMOJI_MAP = {
		logging.DEBUG: "\u26aa",
		logging.INFO: "\U0001f535",
		logging.WARNING: "\U0001F7E0",
		logging.ERROR: "\U0001F534",
		logging.CRITICAL: "\U0001f525",
	}
	EMOJI_MAP = {
		logging.DEBUG: "\U0001f41b",
		logging.INFO: "\U0001f4e2",
		logging.WARNING: "\U0001F7E0",
		logging.ERROR: "\U0001f6a8",
		logging.CRITICAL: "\U0001f525",
	}
	DEFAULT_EMOJI = "\U0001f4a1"

	def __init__(self,
		fmt: Optional[str] = None,
		datefmt: Optional[str] = None,
		use_emoji: bool = True,
		emoji_map: Optional[dict] = None,
		*args,
		**kwargs
	):
		super().__init__(fmt or self.fmt, datefmt, *args, **kwargs)
		
		print(f'Paco {args} {kwargs} {fmt} {use_emoji} {datefmt} {emoji_map}')
		self.use_emoji = use_emoji
		self.emoji_map = self.EMOJI_MAP.copy()
		if isinstance(emoji_map, dict):
			self.emoji_map.update(emoji_map)

	def format(self, record: logging.LogRecord) -> str:
		record.filenameHTML: str = html.escape(record.filename)
		record.funcNameHTML: str = html.escape(record.funcName)
		record.nameHTML: str = html.escape(record.name)
		record.msgHTML: str = html.escape(str(record.msg))
		record.message: str = record.getMessage()
		record.messageHTML: str = html.escape(record.message)
		if self.use_emoji:
			record.levelnameHTML = self.emoji_map.get(record.levelno, self.DEFAULT_EMOJI) + ' '
		else:
			record.levelnameHTML = ''
			
		record.levelnameHTML += '<b>' + record.levelname + '</b>'
		if self.usesTime():
			record.asctime = self.formatTime(record, self.datefmt)
		record.exc_text = str()
		if record.exc_info:
			record.exc_text = self.formatException(record.exc_info)

		return self.formatMessage(record)
