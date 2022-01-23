from guillotina_stripe.models import BillingDetails, Card, Subscription
import aiohttp
import logging
import hmac
import json
import time
from hashlib import sha256
from guillotina_stripe.util import secure_compare
from collections import OrderedDict
from typing import Optional

logger = logging.getLogger("guillotina_stripe")

BASE_URL = "https://api.stripe.com"


class Webhook:
    DEFAULT_TOLERANCE = 300

    EXPECTED_SCHEME = "v1"

    @staticmethod
    def _compute_signature(payload, secret):
        mac = hmac.new(
            secret.encode("utf-8"), msg=payload.encode("utf-8"), digestmod=sha256,
        )
        return mac.hexdigest()

    @staticmethod
    def _get_timestamp_and_signatures(header, scheme):
        list_items = [i.split("=", 2) for i in header.split(",")]
        timestamp = int([i[1] for i in list_items if i[0] == "t"][0])
        signatures = [i[1] for i in list_items if i[0] == scheme]
        return timestamp, signatures

    @classmethod
    def verify_header(cls, payload, header, secret, tolerance=None):

        try:
            timestamp, signatures = cls._get_timestamp_and_signatures(
                header, cls.EXPECTED_SCHEME
            )
        except Exception:
            raise Exception(
                "Unable to extract timestamp and signatures from header")

        if not signatures:
            raise Exception("No signatures found with expected scheme")

        signed_payload = "%d.%s" % (timestamp, payload)
        expected_sig = cls._compute_signature(signed_payload, secret)

        if not any(secure_compare(expected_sig, s) for s in signatures):
            raise Exception(
                "No signatures found matching the expected signature for")

        if tolerance and timestamp < time.time() - tolerance:
            raise Exception(
                "Timestamp outside the tolerance zone (%d)" % timestamp)

        return True

    @staticmethod
    def construct_event(payload, sig_header, secret, tolerance=DEFAULT_TOLERANCE):
        if hasattr(payload, "decode"):
            payload = payload.decode("utf-8")

        return Webhook.verify_header(payload, sig_header, secret, tolerance)


class StripePayUtility(object):
    def __init__(self, settings={}, loop=None):
        self.loop = loop
        self.api = settings.get("api", BASE_URL)
        self.secret = settings.get("secret", None)
        self.auth = aiohttp.BasicAuth(self.secret)
        self.signing_secret = settings.get("signing", None)
        self.testing = settings.get("testing", False)

        self.prices = settings.get("prices", [])
        self.plan = settings.get("plan", None)

    async def initialize(self, app):
        self.session = aiohttp.ClientSession(auth=self.auth)

    async def finalize(self):
        await self.session.close()

    # CUSTOMER
    async def get_customer(self, customer: str):
        url = f"/v1/customers/{customer}"
        async with self.session.get(self.api + url) as resp:
            body = await resp.json()

        return body

    async def set_customer(self, email: str, id_=None):
        url = "/v1/customers"
        if id_ is not None:
            url += f"/{id_}"
        async with self.session.post(self.api + url, data={"email": email}) as resp:
            body = await resp.json()

        return body

    async def set_tax(self, customer: str, tax: str):
        url = f"/v1/customers/{customer}/tax_ids/"
        async with self.session.post(self.api + url, data={"type": 'eu_vat', "value": tax}) as resp:
            body = await resp.json()

        return body

    async def modify_customer(self, payment_method: str, customer: str):
        url = f"/v1/customers/{customer}"
        async with self.session.post(
            self.api + url,
            data={"invoice_settings[default_payment_method]": payment_method},
        ) as resp:
            body = await resp.json()

        return body

    async def detach_payment_method(self, pmid: str):
        url = f"/v1/payment_methods/{pmid}/detach"

        async with self.session.post(BASE_URL + url) as resp:
            body = await resp.json()

        return body

    async def attach_payment_method(self, pmid: str, customer: str):
        url = f"/v1/payment_methods/{pmid}/attach"

        async with self.session.post(
            BASE_URL + url, data={"customer": customer}
        ) as resp:
            body = await resp.json()

        return body

    async def get_payment_methods(self, customer: str, type: str):
        url = f"/v1/payment_methods"

        async with self.session.get(
            BASE_URL + url, data={"customer": customer, "type": type}
        ) as resp:
            body = await resp.json()

        return body

    async def create_paymentmethod(
        self, type, billing_details: BillingDetails = None, card: Card = None
    ):
        url = "/v1/payment_methods"

        data = {
            "type": type,
        }

        if billing_details is not None:
            data["billing_details[address][city]"] = (billing_details.city,)
            data["billing_details[address][country]"] = (
                billing_details.country,)
            data["billing_details[address][postal_code]"] = (
                billing_details.postal_code,
            )
            data["billing_details[address][line1]"] = billing_details.line1
            data["billing_details[address][line2]"] = billing_details.line2
            data["billing_details[address][state]"] = billing_details.state
            data["billing_details[email]"] = billing_details.email
            data["billing_details[name]"] = billing_details.name
            data["billing_details[phone]"] = billing_details.phone

        if card is not None:
            if card.token is not None:
                data["card[token]"] = card.token
            else:
                data["card[exp_month]"] = card.exp_month
                data["card[exp_year]"] = card.exp_year
                data["card[number]"] = card.number
                data["card[cvc]"] = card.cvc

        async with self.session.post(self.api + url, data=data) as resp:
            body = await resp.json()

        return body

    async def get_price(self, price):
        url = f"/v1/prices/{price}"
        async with self.session.get(self.api + url) as resp:
            body = await resp.json()

        return body

    async def get_total_amount_applying_coupon(self, coupon: str, amount: int):
        # https://support.stripe.com/questions/support-for-coupons-using-payment-intents-api
        # Payment intent does not support coupons
        # https://stripe.com/docs/api/coupons/retrieve
        url_coupon = f"v1/coupons/{coupon}"
        try:
            valid_amount = amount
            async with self.session.get(f"{BASE_URL}/{url_coupon}") as resp:
                body = await resp.json()
                if body.get("amount_off"):
                    amount -= body.get("amount_off")
                elif body.get("percent_off"):
                    amount -= (amount * (body["percent_off"] / 100))
                if amount < 50:
                    amount = 50
        except Exception:
            amount = valid_amount
        return int(amount)

    async def create_paymentintent(
            self, payment_method, currency, amount, description, customer, shipping, path, db, coupon: Optional[str] = None
    ):
        url = "/v1/payment_intents"

        if coupon is not None:
            amount = await self.get_total_amount_applying_coupon(coupon, amount)

        data = {
            "amount": amount,
            "currency": currency,
            "description": description,
            "confirm": True,
            "payment_method": payment_method,
            "customer": customer,
            "metadata[path]": path,
            "metadata[db]": db,
        }
        if shipping is not None:
            data["shipping"] = shipping

        async with self.session.post(self.api + url, data=data) as resp:
            body = await resp.json()

        return body

    async def update_subscription(self, subscription, data):
        url = f"/v1/subscriptions/{subscription}"

        async with self.session.post(
            self.api + url,
            data=data,
        ) as resp:
            body = await resp.json()

        return body

    async def create_subscription(self, customer: str, price: str, payment_method: str, path: str, db: str, trial: int, coupon: Optional[str] = None):
        url = f"/v1/subscriptions"

        subsdata = {
            "customer": customer,
            "metadata[path]": path,
            "metadata[db]": db,
            "items[0][price]": price,
            "expand[]": "latest_invoice",
            "expand[]": "latest_invoice.payment_intent",
            "default_payment_method": payment_method
        }
        if coupon is not None:
            subsdata["coupon"] = coupon
        if trial > 0:
            trial_end = time.time() + trial
            subsdata["trial_end"] = round(trial_end)

        async with self.session.post(
            self.api + url,
            data=subsdata,
        ) as resp:
            body = await resp.json()

        return body

    async def cancel_subscription(self, subscription):
        url = f"/v1/subscriptions/{subscription}"

        async with self.session.delete(self.api + url) as resp:
            body = await resp.json()

        return body

    async def get_subscriptions(self, customer):
        url = f"/v1/subscriptions"

        async with self.session.get(
            BASE_URL + url,
            params={"customer": customer},
        ) as resp:
            body = await resp.json()

        result = []
        for subs in body.get("data", []):
            result.append(Subscription(**subs))

        return result

    async def get_subscription(self, subscription):
        url = f"/v1/subscriptions/{subscription}"

        async with self.session.get(
            BASE_URL + url
        ) as resp:
            body = await resp.json()

        return body

    async def get_event(self, payload, signature):
        if self.testing:
            data = json.loads(payload, object_pairs_hook=OrderedDict)
            return data

        if Webhook.construct_event(payload, signature, self.signing_secret):
            data = json.loads(payload, object_pairs_hook=OrderedDict)
            return data
            # event_id = data['id']
            # url = f'/v1/events/{event_id}'
            # async with self.session.get(BASE_URL + url) as resp:
            #     body = await resp.json()
            # return body
        else:
            return None
