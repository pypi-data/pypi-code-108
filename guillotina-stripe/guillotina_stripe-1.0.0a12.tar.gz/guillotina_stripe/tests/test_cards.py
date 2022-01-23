import pytest
import json


@pytest.mark.asyncio
async def test_cards(container_requester):
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
            data=json.dumps(
                {"@type": "CustomCardsType", "id": "cards"}),
        )

        assert status_code == 201

        resp, status_code = await requester(
            "GET",
            "/db/guillotina/cards/@cards",
        )

        assert status_code == 200
        assert len(resp['data']) == 0

        resp, status_code = await requester(
            "POST",
            "/db/guillotina/cards/@register-card",
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
        assert status_code == 200
        pmid = resp['id']
        customer = resp['customer']

        resp, status_code = await requester(
            "GET",
            "/db/guillotina/cards/@cards",
        )

        assert status_code == 200
        assert len(resp['data']) == 1

        resp, status_code = await requester(
            "POST",
            "/db/guillotina/",
            data=json.dumps(
                {"@type": "CustomSubscriptionType", "id": "subscription"}),
        )

        assert status_code == 201

        resp, status_code = await requester(
            "POST",
            "/db/guillotina/subscription/@subscribe",
            data=json.dumps({
                'pmid': pmid,
                'customer': customer
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
            "POST",
            "/db/guillotina/",
            data=json.dumps({
                "@type": "CustomProductType",
                "id": "product"
            })
        )
        assert status_code == 201

        resp, status_code = await requester(
            "POST",
            "/db/guillotina/product/@pay",
            data=json.dumps({
                'pmid': pmid,
                'price': 'price_1I0UJWGeGvgK89lRf4C1Qt7z',
                'quantity': 20,
                'customer': customer
            })
        )
        assert resp['status'] == 'succeeded'

        resp, status_code = await requester(
            "POST",
            "/db/guillotina/cards/@register-card",
            data=json.dumps({
                "email": "test@test.com",
                "number": "5555555555554444",
                "expMonth": "12",
                "expYear": "2030",
                "cvc": "123",
                "cardholderName": "Test user",
                "address": "C\ Carrer 99",
                "state": "Barcelona",
                "city": "Barcelona",
                "cp": "08000",
                "country": "ES",
                "phone": "000000000",
                "customer_id": customer
            })
        )
        assert status_code == 200
        pmid = resp['id']

        resp, status_code = await requester(
            "GET",
            "/db/guillotina/cards/@cards",
        )

        assert status_code == 200
        assert len(resp['data']) == 2

        resp, status_code = await requester(
            "POST",
            "/db/guillotina/",
            data=json.dumps(
                {"@type": "CustomSubscriptionType", "id": "second_subscription"}),
        )

        assert status_code == 201

        resp, status_code = await requester(
            "POST",
            "/db/guillotina/second_subscription/@subscribe",
            data=json.dumps({
                'pmid': pmid,
                'customer': customer
            })
        )
        assert resp['status'] == 'active'
        assert resp["discount"] is None

        resp, status_code = await requester(
            "GET",
            "/db/guillotina/second_subscription"
        )
        assert status_code == 200
        assert resp['subscribed'] is True

        resp, status_code = await requester(
            "GET",
            "/db/guillotina/second_subscription/@subscriptions",
        )

        assert status_code == 200
        assert len(resp['data']) == 2

        resp, status_code = await requester(
            "DELETE",
            "/db/guillotina/second_subscription/@subscribe",
        )
        assert status_code == 200

        resp, status_code = await requester(
            "GET",
            "/db/guillotina/second_subscription/@subscriptions",
        )

        assert status_code == 200
        assert len(resp['data']) == 1
