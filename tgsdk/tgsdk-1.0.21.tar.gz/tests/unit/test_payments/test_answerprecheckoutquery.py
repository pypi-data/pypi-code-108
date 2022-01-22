#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

import json
import unittest

from tgsdk import (
	AnswerPreCheckoutQuery,
	PreCheckoutQuery,
	OrderInfo,
	ShippingAddress,
	LabeledPrice,
	ShippingOption,
	User
)


def test__answerprecheckoutquery__init():
	_ = AnswerPreCheckoutQuery(
		pre_checkout_query_id="pre_checkout_query_id",
		ok=True,
		error_message="error_message"
	)

	assert _.pre_checkout_query_id == "pre_checkout_query_id"
	assert _.ok is True
	assert _.error_message == "error_message"


def test__answerprecheckoutquery__to_dict():
	_ = AnswerPreCheckoutQuery(
		pre_checkout_query_id="pre_checkout_query_id",
		ok=True,
		error_message="error_message"
	)

	unittest.TestCase().assertDictEqual(
		_.to_dict(),
		{
			"pre_checkout_query_id": "pre_checkout_query_id",
			"ok": True,
			"error_message": "error_message"
		}
	)


def test__answerprecheckoutquery__to_json():
	_ = AnswerPreCheckoutQuery(
		pre_checkout_query_id="pre_checkout_query_id",
		ok=True,
		error_message="error_message"
	)

	unittest.TestCase().assertDictEqual(
		json.loads(_.to_json()),
		{
			"pre_checkout_query_id": "pre_checkout_query_id",
			"ok": True,
			"error_message": "error_message"
		}
	)


def test__answerprecheckoutquery__de_json():
	data = {
		"pre_checkout_query_id": "pre_checkout_query_id",
		"ok": True,
		"error_message": "error_message"
	}

	_ = AnswerPreCheckoutQuery.de_json(data)

	assert isinstance(_, AnswerPreCheckoutQuery) is True
	assert _.pre_checkout_query_id == "pre_checkout_query_id"
	assert _.ok is True
	assert _.error_message == "error_message"


def test__answerprecheckoutquery__de_json__data_is_none():
	data = None

	_ = AnswerPreCheckoutQuery.de_json(data)

	assert _ is None
