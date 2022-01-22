#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

from tgsdk import BotCommand


def test__base__str():
	_ = BotCommand(
		command="command",
		description="description"
	)

	assert _.__str__() == "<BotCommand: {'command': 'command', 'description': 'description'}>" or _.__str__() == "<BotCommand: {'description': 'description', 'command': 'command'}>"


def test__base__get_item():
	_ = BotCommand(
		command="command_text",
		description="description"
	)

	assert _["command"] == "command_text"
