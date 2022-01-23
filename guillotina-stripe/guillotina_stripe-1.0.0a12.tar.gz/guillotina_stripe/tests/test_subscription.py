import os
import os
import pytest
import json
from guillotina_stripe.tests.payloads import PAYLOAD, PAYLOAD_CANCEL_SUBSCRIPTION
from guillotina.tests.utils import ContainerRequesterAsyncContextManager

TRAILING_DEFAULT_SETTINGS = {
    "stripe": {
        "subscriptions": {
            "CustomSubscriptionType": [{"trial": 10000, "price": "price_1HNb9XGeGvgK89lRkF3KPEgs"}]
        },
        "products": {
            "CustomProductType": ["price_1I0UIuGeGvgK89lReW6fQzYM", "price_1I0UJWGeGvgK89lRf4C1Qt7z"]
        }
    }
}


class InitSubscription(ContainerRequesterAsyncContextManager):
    async def __aenter__(self):
        requester = await super().__aenter__()

        _, status_code = await requester(
            "POST",
            "/db/guillotina/",
            data=json.dumps(
                {"@type": "CustomSubscriptionType", "id": "subscription"}),
        )

        assert status_code == 201

        resp, status_code = await requester(
            "GET",
            "/db/guillotina/subscription/@subscriptions",
        )

        assert resp['error'] == 'No customer'

        resp, status_code = await requester(
            "GET",
            "/db/guillotina/subscription/@cards",
        )

        assert status_code == 200
        assert len(resp['data']) == 0

        resp, status_code = await requester(
            "POST",
            "/db/guillotina/subscription/@register-card",
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

        return requester


@pytest.fixture(scope='function')
async def init_subscription(guillotina):
    return InitSubscription(guillotina)


@pytest.mark.asyncio
async def test_pay_subscription_us(init_subscription):
    async with init_subscription as requester:
        resp, status_code = await requester(
            "GET",
            "/db/guillotina/subscription/@cards",
        )

        assert status_code == 200
        assert len(resp['data']) == 1
        pmid = resp['data'][0]['id']

        resp, status_code = await requester(
            "POST",
            "/db/guillotina/subscription/@subscribe",
            data=json.dumps({
                'pmid': pmid
            })
        )

        assert resp['status'] == 'active'
        assert resp["discount"] is None

        resp, status_code = await requester(
            "GET",
            "/db/guillotina/subscription"
        )

        assert resp['subscribed'] is True

        resp, status_code = await requester(
            "GET",
            "/db/guillotina/subscription/@subscriptions",
        )
        assert status_code == 200
        assert len(resp['data']) == 1


@pytest.mark.asyncio
async def test_pay_subscription_us_with_coupon(init_subscription):
    async with init_subscription as requester:
        resp, status_code = await requester(
            "GET",
            "/db/guillotina/subscription/@cards",
        )

        assert status_code == 200
        assert len(resp['data']) == 1
        pmid = resp['data'][0]['id']

        resp, status_code = await requester(
            "POST",
            "/db/guillotina/subscription/@subscribe",
            data=json.dumps({
                'pmid': pmid,
                'coupon': "foo-coupon-25"
            })
        )

        assert resp['status'] == 'active'
        assert isinstance(resp["discount"], dict)


@pytest.mark.asyncio
async def test_pay_subscription_us_error_double_subscription(init_subscription):
    async with init_subscription as requester:
        resp, status_code = await requester(
            "GET",
            "/db/guillotina/subscription/@cards",
        )

        assert status_code == 200
        assert len(resp['data']) == 1
        pmid = resp['data'][0]['id']

        resp, status_code = await requester(
            "POST",
            "/db/guillotina/subscription/@subscribe",
            data=json.dumps({
                'pmid': pmid,
            })
        )
        assert status_code == 200
        assert resp['status'] == 'active'

        resp, status_code = await requester(
            "POST",
            "/db/guillotina/subscription/@subscribe",
            data=json.dumps({
                'pmid': pmid,
            })
        )
        assert status_code == 412
        assert resp['reason'] == "Subscription already exist"


@pytest.mark.asyncio
async def test_pay_subscription_eu(container_requester):
    async with container_requester as requester:
        resp, status_code = await requester(
            "POST",
            "/db/guillotina/",
            data=json.dumps(
                {"@type": "CustomSubscriptionType", "id": "subscription"}),
        )

        assert status_code == 201

        resp, status_code = await requester(
            "POST",
            "/db/guillotina/subscription/@register-card",
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
            "/db/guillotina/subscription/@cards",
        )

        assert status_code == 200
        assert len(resp['data']) == 1

        resp, status_code = await requester(
            "POST",
            "/db/guillotina/subscription/@subscribe",
            data=json.dumps({
                'pmid': pmid
            })
        )

        assert resp['status'] == 'incomplete'
        action = resp['latest_invoice']['payment_intent']['next_action']
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
            "/db/guillotina/subscription",
        )

        assert resp['subscribed'] == True


@pytest.mark.asyncio
async def test_pay_subscription_updated(init_subscription):
    async with init_subscription as requester:
        resp, status_code = await requester(
            "GET",
            "/db/guillotina/subscription/@cards",
        )

        assert status_code == 200
        assert len(resp['data']) == 1
        pmid = resp['data'][0]['id']

        resp, status_code = await requester(
            "POST",
            "/db/guillotina/subscription/@subscribe",
            data=json.dumps({
                'pmid': pmid
            })
        )

        assert resp['status'] == 'active'

        resp, status_code = await requester(
            "PATCH",
            "/db/guillotina/subscription/@subscribe",
            data=json.dumps({
                'cancel_at_period_end': True
            })
        )
        assert resp['cancel_at_period_end'] == True


@pytest.mark.asyncio
@pytest.mark.app_settings(TRAILING_DEFAULT_SETTINGS)
async def test_pay_subscription_trailing_canceled_and_reactivate(init_subscription):
    async with init_subscription as requester:
        resp, status_code = await requester(
            "GET",
            "/db/guillotina/subscription/@cards",
        )

        assert status_code == 200
        assert len(resp['data']) == 1
        pmid = resp['data'][0]['id']

        resp, status_code = await requester(
            "POST",
            "/db/guillotina/subscription/@subscribe",
            data=json.dumps({
                'pmid': pmid
            })
        )

        assert resp['status'] == 'trialing'

        resp, status_code = await requester(
            "DELETE",
            "/db/guillotina/subscription/@subscribe",
        )

        assert status_code == 200

        resp, status_code = await requester(
            "POST",
            "/db/guillotina/subscription/@subscribe",
            data=json.dumps({
                'pmid': pmid
            })
        )

        assert resp['status'] == 'active'


@pytest.mark.asyncio
async def test_pay_subscription_delete_it_and_keep_cards(init_subscription):
    async with init_subscription as requester:
        resp, status_code = await requester(
            "GET",
            "/db/guillotina/subscription/@cards",
        )

        assert status_code == 200
        assert len(resp['data']) == 1
        pmid = resp['data'][0]['id']

        resp, status_code = await requester(
            "POST",
            "/db/guillotina/subscription/@subscribe",
            data=json.dumps({
                'pmid': pmid
            })
        )

        assert resp['status'] == 'active'

        resp, status_code = await requester(
            "POST",
            "/@stripe",
            data=json.dumps(PAYLOAD)
        )

        assert resp['status'] == 'success'

        resp, status_code = await requester(
            "GET",
            "/db/guillotina/subscription",
        )
        assert resp['subscribed'] == True

        resp, status_code = await requester(
            "DELETE",
            "/db/guillotina/subscription/@subscribe",
        )

        assert status_code == 200

        resp, status_code = await requester(
            "POST",
            "/@stripe",
            data=json.dumps(PAYLOAD_CANCEL_SUBSCRIPTION)
        )

        assert resp['status'] == 'success'

        resp, status_code = await requester(
            "GET",
            "/db/guillotina/subscription",
        )
        assert resp['subscribed'] == False

        resp, status_code = await requester(
            "GET",
            "/db/guillotina/subscription/@cards",
        )

        assert status_code == 200
        assert len(resp['data']) == 1
