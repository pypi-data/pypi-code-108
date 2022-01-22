#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/


from tgsdk.network import errors


def test__TelegramException():

	_ = errors.TelegramException(message="message")

	assert _.message == "message"

	assert str(_) == "message"


def test__SeeOther():

	_ = errors.SeeOther(message="SeeOther")

	assert _.message == "SeeOther"

	assert str(_) == "SeeOther"


def test__BadRequest():

	_ = errors.BadRequest(message="BadRequest")

	assert _.message == "BadRequest"

	assert str(_) == "BadRequest"


def test__Unauthorized():

	_ = errors.Unauthorized(message="Unauthorized")

	assert _.message == "Unauthorized"

	assert str(_) == "Unauthorized"


def test__Forbidden():

	_ = errors.TelegramException(message="Forbidden")

	assert _.message == "Forbidden"

	assert str(_) == "Forbidden"


def test__NotFound():

	_ = errors.TelegramException(message="NotFound")

	assert _.message == "NotFound"

	assert str(_) == "NotFound"


def test__NotAcceptable():

	_ = errors.TelegramException(message="NotAcceptable")

	assert _.message == "NotAcceptable"

	assert str(_) == "NotAcceptable"


def test__Flood():

	_ = errors.TelegramException(message="Flood")

	assert _.message == "Flood"

	assert str(_) == "Flood"


def test__Internal():

	_ = errors.Internal(message="Internal")

	assert _.message == "Internal"

	assert str(_) == "Internal"


def test__InvalidToken():

	_ = errors.InvalidToken()

	assert _.message == "Invalid token"

	assert str(_) == "Invalid token"


def test__RetryAfter():

	_ = errors.RetryAfter(retry_after_seconds=100)

	assert _.message == "Broadcasting limits exceeded. Please, retry in 100 seconds"

	assert str(_) == "Broadcasting limits exceeded. Please, retry in 100 seconds"


def test__ChatMigrated():

	_ = errors.ChatMigrated(chat_id=100)

	assert _.message == "Group migrated to supergroup. New chat id: 100"

	assert str(_) == "Group migrated to supergroup. New chat id: 100"


def test__NetworkError():

	_ = errors.NetworkError(message="NetworkError")

	assert _.message == "NetworkError"

	assert str(_) == "NetworkError"


def test__TimeOutError():

	_ = errors.TimeOutError()

	assert _.message == "Timed out"

	assert str(_) == "Timed out"
