#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

from tgsdk import (
	InlineKeyboardButton,
	LoginUrl
)


def test_init_button():
	button = InlineKeyboardButton(
		text="Button",
		callback_data="callback_data",
		url="https://linkedin.com/in/evgeniyprivalov/",
		switch_inline_query="switch_inline_query",
		switch_inline_query_current_chat="switch_inline_query_current_chat",
		pay=True,
		login_url=LoginUrl(
			url="https://linkedin.com/in/evgeniyprivalov/",
			forward_text=True,
			bot_username="bot_username",
			request_write_access=True
		)
	)

	assert button.text == "Button"
	assert button.callback_data == "callback_data"
	assert button.url == "https://linkedin.com/in/evgeniyprivalov/"
	assert button.switch_inline_query is "switch_inline_query"
	assert button.switch_inline_query_current_chat is "switch_inline_query_current_chat"
	assert button.pay is True

	assert isinstance(button.login_url, LoginUrl) is True
	assert button.login_url.url == "https://linkedin.com/in/evgeniyprivalov/"
	assert button.login_url.forward_text is True
	assert button.login_url.bot_username == "bot_username"
	assert button.login_url.request_write_access is True


def test__inline_keyboard_button__de_json():
	data = {
		"text": "Button",
		"callback_data": "callback_data"
	}

	inline_button = InlineKeyboardButton.de_json(data)  # type: InlineKeyboardButton

	assert inline_button.text == "Button"
	assert inline_button.callback_data == "callback_data"


def test__inline_keyboard_button__de_json__data_is_none():
	data = None

	inline_button = InlineKeyboardButton.de_json(data)  # type: InlineKeyboardButton

	assert inline_button is None
