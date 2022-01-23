import pytest
import json
import asyncio

from guillotina.component import get_utility
from guillotina_stripe.interfaces import IStripePayUtility


PAYLOAD = {
    "id": "evt_1I0WtnGeGvgK89lRmPnLKO1J",
    "object": "event",
    "api_version": "2020-08-27",
    "created": 1608489895,
    "data": {
        "object": {
            "id": "pi_1I0WtdGeGvgK89lRyA62my6H",
            "object": "payment_intent",
            "amount": 1000,
            "amount_capturable": 0,
            "amount_received": 1000,
            "application": None,
            "application_fee_amount": None,
            "canceled_at": None,
            "cancellation_reason": None,
            "capture_method": "automatic",
            "charges": {
                "object": "list",
                "data": [
                    {
                        "id": "ch_1I0WtmGeGvgK89lRJfe4Fh5W",
                        "object": "charge",
                        "amount": 1000,
                        "amount_captured": 1000,
                        "amount_refunded": 0,
                        "application": None,
                        "application_fee": None,
                        "application_fee_amount": None,
                        "balance_transaction": "txn_1I0WtnGeGvgK89lRWjGNJi3g",
                        "billing_details": {
                            "address": {
                                "city": "Barcelona",
                                "country": "ES",
                                "line1": "C\\\\ Carrer 99",
                                "line2": "None",
                                "postal_code": "08000",
                                "state": "Barcelona"
                            },
                            "email": "test@test.com",
                            "name": "Test user",
                            "phone": "000000000"
                        },
                        "calculated_statement_descriptor": "BLA BLA",
                        "captured": True,
                        "created": 1608489894,
                        "currency": "eur",
                        "customer": "cus_IbkOMDM7izMHr0",
                        "description": "CustomProductType product 20",
                        "destination": None,
                        "dispute": None,
                        "disputed": False,
                        "failure_code": None,
                        "failure_message": None,
                        "fraud_details": {},
                        "invoice": None,
                        "livemode": False,
                        "metadata": {
                            "path": "/guillotina/product",
                            "db": "db"
                        },
                        "on_behalf_of": None,
                        "order": None,
                        "outcome": {
                            "network_status": "approved_by_network",
                            "reason": None,
                            "risk_level": "normal",
                            "risk_score": 13,
                            "seller_message": "Payment complete.",
                            "type": "authorized"
                        },
                        "paid": True,
                        "payment_intent": "pi_1I0WtdGeGvgK89lRyA62my6H",
                        "payment_method": "pm_1I0WtbGeGvgK89lRwQ7VAJhL",
                        "payment_method_details": {
                            "card": {
                                "brand": "visa",
                                "checks": {
                                    "address_line1_check": "pass",
                                    "address_postal_code_check": "pass",
                                    "cvc_check": "pass"
                                },
                                "country": "DE",
                                "exp_month": 12,
                                "exp_year": 2030,
                                "fingerprint": "KoC87hPDrVmLnkym",
                                "funding": "credit",
                                "installments": None,
                                "last4": "3184",
                                "network": "visa",
                                "three_d_secure": {
                                    "authentication_flow": "challenge",
                                    "result": "authenticated",
                                    "result_reason": None,
                                    "version": "1.0.2"
                                },
                                "wallet": None
                            },
                            "type": "card"
                        },
                        "receipt_email": None,
                        "receipt_number": None,
                        "receipt_url": "https://pay.stripe.com/receipts/acct_1ALBplGeGvgK89lR/ch_1I0WtmGeGvgK89lRJfe4Fh5W/rcpt_IbkOvIZTDI1gmk2P2i1u2vBdBynLSDQ",
                        "refunded": False,
                        "refunds": {
                            "object": "list",
                            "data": [],
                            "has_more": False,
                            "total_count": 0,
                            "url": "/v1/charges/ch_1I0WtmGeGvgK89lRJfe4Fh5W/refunds"
                        },
                        "review": None,
                        "shipping": None,
                        "source": None,
                        "source_transfer": None,
                        "statement_descriptor": None,
                        "statement_descriptor_suffix": None,
                        "status": "succeeded",
                        "transfer_data": None,
                        "transfer_group": None
                    }
                ],
                "has_more": False,
                "total_count": 1,
                "url": "/v1/charges?payment_intent=pi_1I0WtdGeGvgK89lRyA62my6H"
            },
            "client_secret": "pi_1I0WtdGeGvgK89lRyA62my6H_secret_WExOZeeEy7alLKJTjXHIFJ3bs",
            "confirmation_method": "automatic",
            "created": 1608489885,
            "currency": "eur",
            "customer": "cus_IbkOMDM7izMHr0",
            "description": "CustomProductType product 20",
            "invoice": None,
            "last_payment_error": None,
            "livemode": False,
            "metadata": {
                "path": "/guillotina/product",
                "db": "db"
            },
            "next_action": None,
            "on_behalf_of": None,
            "payment_method": "pm_1I0WtbGeGvgK89lRwQ7VAJhL",
            "payment_method_options": {
                "card": {
                    "installments": None,
                    "network": None,
                    "request_three_d_secure": "automatic"
                }
            },
            "payment_method_types": [
                "card"
            ],
            "receipt_email": None,
            "review": None,
            "setup_future_usage": None,
            "shipping": None,
            "source": None,
            "statement_descriptor": None,
            "statement_descriptor_suffix": None,
            "status": "succeeded",
            "transfer_data": None,
            "transfer_group": None
        }
    },
    "livemode": False,
    "pending_webhooks": 2,
    "request": {
        "id": None,
        "idempotency_key": "pi_1I0WtdGeGvgK89lRyA62my6H-src_1I0WtdGeGvgK89lRMoVXUX1W"
    },
    "type": "payment_intent.succeeded"
}

@pytest.mark.asyncio
async def test_pay_product_us(container_requester):
    async with container_requester as requester:
        resp, status_code = await requester(
            "POST",
            "/db/guillotina/@addons",
            data=json.dumps({
                "id": "stripe"
            })
        )
        assert status_code == 200


        resp, status_code = await requester(
            "PATCH",
            "/db/guillotina/@registry/guillotina_stripe.interfaces.IStripeConfiguration.product_prices",
            data=json.dumps({
                "value": {
                    "CustomProductType": [{
                        "price": "price_1I0UIuGeGvgK89lReW6fQzYM",
                        "id": "value1"
                    }, {
                        "price": "price_1I0UJWGeGvgK89lRf4C1Qt7z",
                        "id": "value2"
                    }]
                }
            })
        )
        assert status_code == 204


        resp, status_code = await requester(
            "POST",
            "/db/guillotina/",
            data=json.dumps({
                "@type": "CustomProductType",
                "id": "product"
            })
        )
        assert status_code == 201

        resp, status_code = await requester(
            "GET",
            "/db/guillotina/product/@cards",
        )

        assert status_code == 200
        assert len(resp['data']) == 0

        resp, status_code = await requester(
            "POST",
            "/db/guillotina/product/@register-card",
            data=json.dumps({
                "email": "test@test.com",
                "number": "4242424242424242",
                "expMonth": "12",
                "expYear": "2030",
                "cvc": "123",
                "cardholderName": "Test user",
                "address": "C\ Carrer 99",
                "state": "Barcelona",
                "city": "Barcelona",
                "cp": "08000",
                "country": "ES",
                "phone": "000000000"
            })
        )

        pmid = resp['id']

        resp, status_code = await requester(
            "GET",
            "/db/guillotina/product/@cards",
        )

        assert status_code == 200
        assert len(resp['data']) == 1


        resp, status_code = await requester(
            "GET",
            "/db/guillotina/product/@prices"
        )
        assert len(resp['prices']) == 2

        resp, status_code = await requester(
            "POST",
            "/db/guillotina/product/@pay",
            data=json.dumps({
                'pmid': pmid,
                'price': 'price_1I0UJWGeGvgK89lRf4C1Qt7z',
                'quantity': 20
            })
        )
        assert resp['status'] == 'succeeded'
        total_amount = resp["amount_received"]
        await asyncio.sleep(1)
        resp, status_code = await requester(
            "GET",
            "/db/guillotina/product"
        )
        assert resp['ispaid'] is True

        resp, status_code = await requester(
            "POST",
            "/db/guillotina/product/@pay",
            data=json.dumps({
                'pmid': pmid,
                'price': 'price_1I0UJWGeGvgK89lRf4C1Qt7z',
                'quantity': 20,
                'coupon': "foo-coupon-25"
            })
        )
        assert resp['status'] == 'succeeded'
        assert resp["amount_received"] == int(total_amount - (total_amount * 0.25))

        resp, status_code = await requester(
            "POST",
            "/db/guillotina/product/@pay",
            data=json.dumps({
                'pmid': pmid,
                'price': 'price_1I0UJWGeGvgK89lRf4C1Qt7z',
                'quantity': 20,
                'coupon': "coupon-2-euros"
            })
        )
        assert resp['status'] == 'succeeded'
        # Diescout 2 euros: 200
        assert resp["amount_received"] == total_amount - 200

@pytest.mark.asyncio
async def test_pay_product_eu(container_requester):
    async with container_requester as requester:
        resp, status_code = await requester(
            "POST",
            "/db/guillotina/",
            data=json.dumps({
                "@type": "CustomProductType",
                "id": "product"
            })
        )
        assert status_code == 201

        resp, status_code = await requester(
            "GET",
            "/db/guillotina/product/@cards",
        )

        assert status_code == 200
        assert len(resp['data']) == 0

        resp, status_code = await requester(
            "POST",
            "/db/guillotina/product/@register-card",
            data=json.dumps({
                "email": "test@test.com",
                "number": "4000002760003184",
                "expMonth": "12",
                "expYear": "2030",
                "cvc": "123",
                "cardholderName": "Test user",
                "address": "C\ Carrer 99",
                "state": "Barcelona",
                "city": "Barcelona",
                "cp": "08000",
                "country": "ES",
                "phone": "000000000"
            })
        )

        pmid = resp['id']

        resp, status_code = await requester(
            "GET",
            "/db/guillotina/product/@cards",
        )

        assert status_code == 200
        assert len(resp['data']) == 1

        resp, status_code = await requester(
            "POST",
            "/db/guillotina/product/@pay",
            data=json.dumps({
                'pmid': pmid,
                'price': 'price_1I0UJWGeGvgK89lRf4C1Qt7z',
                'quantity': 20
            })
        )
        assert resp['status'] == 'requires_action'
        action = resp['next_action']
        assert action['type'] == 'use_stripe_sdk'
        assert action['use_stripe_sdk']['type'] == 'three_d_secure_redirect'

        resp, status_code = await requester(
            "POST",
            "/@stripe",
            data=json.dumps(PAYLOAD)
        )

        assert resp['status'] == 'success'

        resp, status_code = await requester(
            "GET",
            "/db/guillotina/product"
        )

        assert resp['ispaid'] is True


@pytest.mark.asyncio
async def test_coupon_utility(container_requester):
    async with container_requester:
        utility = get_utility(IStripePayUtility)
        # Applying 25% coupon
        amount = await utility.get_total_amount_applying_coupon(coupon="foo-coupon-25", amount=1000)
        assert amount == 750

        # Coupon does not exists
        amount = await utility.get_total_amount_applying_coupon(coupon="invalid-coupon-404", amount=1000)
        assert amount == 1000

        # Coupon of 2 euros
        amount = await utility.get_total_amount_applying_coupon(coupon="coupon-2-euros", amount=1000)
        assert amount == 800

        # Coupon of 2 euros
        # Stripe does not admit payment below 50 (0.5 euros). In that case, pay 50
        amount = await utility.get_total_amount_applying_coupon(coupon="coupon-2-euros", amount=200)
        assert amount == 50
