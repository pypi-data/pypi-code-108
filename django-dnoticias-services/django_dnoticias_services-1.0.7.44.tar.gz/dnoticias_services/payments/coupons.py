import requests
from urllib.parse import urlencode

from django.conf import settings
from dnoticias_services.utils.request import get_headers

from .base import BasePaymentRequest


class GetSuitableCoupons(BasePaymentRequest):
    def __call__(self, item_remote_uuid, request, api_key=None, timeout=None):
        params = dict(request.query_params)
        params.update({'remote_id': item_remote_uuid})
        self.set_api_url(settings.PAYMENTS_GET_COUPONS_API_URL)
        return self.get(params, api_key, timeout)


class GetCoupon(BasePaymentRequest):
    def __call__(self, coupon_remote_id, item_remote_id, api_key=None, timeout=None):
        params = {'item_uuid': item_remote_id}
        self.set_api_url(settings.PAYMENTS_GET_SINGLE_COUPON_API_URL, (coupon_remote_id, ))
        return self.get(params, api_key, timeout)


get_coupon = GetCoupon()
get_suitable_coupons = GetSuitableCoupons()

__all__ = ("get_coupon", "get_suitable_coupons", )