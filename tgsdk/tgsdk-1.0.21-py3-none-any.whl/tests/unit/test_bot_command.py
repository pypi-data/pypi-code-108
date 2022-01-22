#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

import json
import unittest

from tgsdk import BotCommand


def test__bot_command__init():
	_ = BotCommand(
		command="command",
		description="description"
	)

	assert _.command == "command"
	assert _.description == "description"


def test__bot_command__de_json():
	data = {
		"command": "Command",
		"description": "Description"
	}

	_ = BotCommand.de_json(data)

	assert isinstance(_, BotCommand) is True
	assert _.command == "Command"
	assert _.description == "Description"


def test__bot_command__de_json__data_is_none():
	data = None

	_ = BotCommand.de_json(data)

	assert _ is None


def test__bot_command__to_dict():
	_ = BotCommand(
		command="new_command",
		description="new description"
	)

	unittest.TestCase().assertDictEqual(
		_.to_dict(),
		{
			"command": "new_command",
			"description": "new description"
		}
	)


def test__bot_command__to_json():
	_ = BotCommand(
		command="new_command",
		description="new description"
	)

	unittest.TestCase().assertDictEqual(
		json.loads(_.to_json()),
		{
			"command": "new_command",
			"description": "new description"
		}
	)
