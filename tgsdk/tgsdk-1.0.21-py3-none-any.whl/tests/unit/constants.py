#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

import os
from tgsdk.utils.types import ID


class TestValues:
	USER_CHAT_ID = int(os.environ["USER_CHAT_ID"])  # type: ID # Paste user tg id

	BOT_ID = int(os.environ["BOT_ID"])
	BOT_USERNAME = os.environ["BOT_USERNAME"]
	BOT_FIRST_NAME = os.environ["BOT_FIRST_NAME"]
	BOT_API_TOKEN = os.environ["BOT_API_TOKEN"]

	CHAT_ID = os.getenv("CHAT_ID", None)  # type: ID  # Paste Your chat id
	CHAT_USERNAME = os.getenv("CHAT_USERNAME", None)  # type: str  # Paste your chat username if need
