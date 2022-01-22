#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

from tgsdk import ParseMode


def test__parsemode():
	assert ParseMode.MARKDOWN == "Markdown"
	assert ParseMode.MARKDOWN_V2 == "MarkdownV2"
	assert ParseMode.HTML == "HTML"
