#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

from tgsdk.utils import constants


class ParseMode:
	MARKDOWN = constants.PARSE_MODE_MARKDOWN  # type: str
	MARKDOWN_V2 = constants.PARSE_MODE_MARKDOWN_V2  # type: str
	HTML = constants.PARSE_MODE_HTML  # type: str
