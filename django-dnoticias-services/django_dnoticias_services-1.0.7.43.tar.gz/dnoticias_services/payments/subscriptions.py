from django.conf import settings
from .base import BasePaymentRequest


class GetStripeSubscription(BasePaymentRequest):
    def __call__(self, remote_subscription_id, api_key=None, timeout=None):
        self.set_api_url(
            settings.PAYMENTS_GET_STRIPE_SUBSCRIPTION_API_URL,
            (remote_subscription_id, )
        )
        return self.get({}, api_key, timeout)


class GetSubscription(BasePaymentRequest):
    def __call__(self, email, status, api_key=None, timeout=None):
        self.set_api_url(settings.PAYMENTS_GET_SUBSCRIPTION_API_URL)
        return self.get({'email': email, 'status': status}, api_key, timeout)


get_stripe_subscription = GetStripeSubscription()
get_subscription = GetSubscription()

__all__ = ('get_stripe_subscription', 'get_subscription', )
