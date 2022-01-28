from urllib.parse import urljoin

import requests
from django.conf import settings
from dnoticias_services.utils.request import get_headers

from .base import BaseSubscriptionRequest


class BaseBillingRequest(BaseSubscriptionRequest):
    def get_url(self):
        return settings.BILLING_API_URL

class CreateBilling(BaseBillingRequest):
    def __call__(self, email, vat, name, contact_id=None, address_id=None, api_key=None, timeout=None):
        _api_key = api_key or self.api_key
        _timeout = timeout or self.timeout
        context = {
            "email" : email,
            "vat" : vat,
            "name" : name,
            "contact_id" : contact_id,
            "address_id" : address_id
        }
        response = requests.post(
            self.get_url(),
            headers=get_headers(_api_key),
            json=context,
            timeout=_timeout
        )
        response.raise_for_status()
        return response

class ResolveBillingRequest(BaseBillingRequest):
    def get_url(self, uuid):
        return urljoin(settings.BILLING_API_URL, str(uuid) + "/")

class UpdateBilling(BaseBillingRequest):
    def __call__(self, uuid, vat=None, name=None, contact_id=None, address_id=None, api_key=None, timeout=None):
        _api_key = api_key or self.api_key
        _timeout = timeout or self.timeout
        context = {
            "email" : email,
            "vat" : vat,
            "name" : name,
            "contact_id" : contact_id,
            "address_id" : address_id
        }
        response = requests.patch(
            self.get_url(uuid),
            headers=get_headers(_api_key),
            json=context,
            timeout=_timeout
        )
        response.raise_for_status()
        return response

create_billing = CreateBilling()
update_billing = UpdateBilling()
