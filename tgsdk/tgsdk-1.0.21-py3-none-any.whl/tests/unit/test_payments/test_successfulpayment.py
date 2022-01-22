#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

import json
import unittest

from tgsdk import SuccessfulPayment


def test__successfulpayment__init():
	_ = SuccessfulPayment(
		currency="USD",
		total_amount=10,
		invoice_payload="invoice_payload",
		telegram_payment_charge_id="telegram_payment_charge_id",
		provider_payment_charge_id="provider_payment_charge_id"
	)

	assert _.currency == "USD"
	assert _.total_amount == 10
	assert _.invoice_payload == "invoice_payload"
	assert _.telegram_payment_charge_id == "telegram_payment_charge_id"
	assert _.provider_payment_charge_id == "provider_payment_charge_id"
	assert _.shipping_option_id is None
	assert _.order_info is None


def test__successfulpayment__to_dict():
	_ = SuccessfulPayment(
		currency="USD",
		total_amount=10,
		invoice_payload="invoice_payload",
		telegram_payment_charge_id="telegram_payment_charge_id",
		provider_payment_charge_id="provider_payment_charge_id"
	)

	unittest.TestCase().assertDictEqual(
		_.to_dict(),
		{
			"currency": "USD",
			"total_amount": 10,
			"invoice_payload": "invoice_payload",
			"telegram_payment_charge_id": "telegram_payment_charge_id",
			"provider_payment_charge_id": "provider_payment_charge_id"
		}
	)


def test__successfulpayment__to_json():
	_ = SuccessfulPayment(
		currency="USD",
		total_amount=10,
		invoice_payload="invoice_payload",
		telegram_payment_charge_id="telegram_payment_charge_id",
		provider_payment_charge_id="provider_payment_charge_id"
	)

	unittest.TestCase().assertDictEqual(
		json.loads(_.to_json()),
		{
			"currency": "USD",
			"total_amount": 10,
			"invoice_payload": "invoice_payload",
			"telegram_payment_charge_id": "telegram_payment_charge_id",
			"provider_payment_charge_id": "provider_payment_charge_id"
		}
	)


def test__successfulpayment__de_json():
	data = {
		"currency": "USD",
		"total_amount": 10,
		"invoice_payload": "invoice_payload",
		"telegram_payment_charge_id": "telegram_payment_charge_id",
		"provider_payment_charge_id": "provider_payment_charge_id"
	}

	_ = SuccessfulPayment.de_json(data)

	assert isinstance(_, SuccessfulPayment) is True
	assert _.currency == "USD"
	assert _.total_amount == 10
	assert _.invoice_payload == "invoice_payload"
	assert _.telegram_payment_charge_id == "telegram_payment_charge_id"
	assert _.provider_payment_charge_id == "provider_payment_charge_id"
	assert _.shipping_option_id is None
	assert _.order_info is None


def test__successfulpayment__de_json__data_is_none():
	data = None

	_ = SuccessfulPayment.de_json(data)

	assert _ is None
