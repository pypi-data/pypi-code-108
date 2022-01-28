import requests

from django.conf import settings
from dnoticias_services.utils.request import get_headers

from .base import BaseSubscriptionRequest


class DeleteSubscriptionCoupon(BaseSubscriptionRequest):
    def __call__(self, remote_id, api_key=None):
        _api_key = api_key or self.api_key

        response = requests.post(
            settings.SUBSCRIPTION_DELETE_COUPON_API_URL,
            headers=get_headers(_api_key),
            json={
                'remote_id': remote_id
            },
        )
        response.raise_for_status()
        return response


delete_subscription_coupon = DeleteSubscriptionCoupon()

__all__ = ("delete_subscription_coupon", )