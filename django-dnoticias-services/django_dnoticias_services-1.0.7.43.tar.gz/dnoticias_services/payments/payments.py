import requests

from django.conf import settings

from dnoticias_services.utils.request import get_headers
from .base import BasePaymentRequest

class SetupPaymentIntent(BasePaymentRequest):
    """
        Need to call this API when we intent to ask the payment details
        path: "{domain}/api/setup/payment-intent/"
        returns : {
            "client_secret" : "*******************",
            "public_key" : "xxxxxxxxxxxxxxxx",
        }
        More info: https://stripe.com/docs/payments/save-and-reuse?platform=web
    """
    def __call__(self, email=None, subscription_id=None, api_key=None):
        _api_key = api_key or self.api_key
        
        params = {}
        if email:
            params["email"] = email
        if subscription_id:
            params["subscription_id"] = subscription_id

        response = requests.get(
            settings.SETUP_PAYMENT_INTENT_API_URL,
            headers=get_headers(_api_key),
            params=params
        )
        response.raise_for_status()
        return response

class ChangeSubscriptionPaymentMethod(BasePaymentRequest):
    """
        path: "{domain}/api/change/subscription/payment-method/{id}/"
    """
    def __call__(self, subscription_id, payment_method, api_key=None):
        _api_key = api_key or self.api_key
        response = requests.post(
            settings.CHANGE_SUBSCRIPTION_PAYMENT_METHOD_API_URL.format(subscription_id),
            headers=get_headers(_api_key),
            json={
                "payment_method" : payment_method
            }
        )
        response.raise_for_status()
        return response

class GeneratePaymentDetails(BasePaymentRequest):
    """
        Depending the payment provider returns a different response
    """
    def __call__(self, email, payment_provider_id, items_id=None, amount=None, api_key=None):
        _api_key = api_key or self.api_key
        response = requests.post(
            settings.GENERATE_PAYMENT_DETAILS_API_URL,
            headers=get_headers(_api_key),
            json={
                "email" : email,
                "payment_provider_id" : payment_provider_id,
                "items_id" : items_id,
                "amount" : amount,
            }
        )
        response.raise_for_status()
        return response


class RequestPaymentInvoice(BasePaymentRequest):
    def __call__(self, order_id, api_key=None, timeout=None):
        self.set_api_url(settings.PAYMENTS_REQUEST_INVOICE_API_URL, (order_id, ))
        return self.get({}, api_key, timeout)


setup_payment_intent = SetupPaymentIntent()
change_subscription_payment_method = ChangeSubscriptionPaymentMethod()
generate_payment_details = GeneratePaymentDetails()
request_payment_invoice = RequestPaymentInvoice()

__all__ = (
    "setup_payment_intent",
    "change_subscription_payment_method",
    "generate_payment_details",
    "request_payment_invoice",
)
