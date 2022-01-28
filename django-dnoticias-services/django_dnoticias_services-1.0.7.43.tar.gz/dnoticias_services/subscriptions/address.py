from urllib.parse import urljoin

import requests
from django.conf import settings
from dnoticias_services.utils.request import get_headers

from .base import BaseSubscriptionRequest


class BaseAddressRequest(BaseSubscriptionRequest):
    def get_url(self):
        return settings.ADDRESS_API_URL

class CreateAddress(BaseAddressRequest):
    def __call__(self, email, country, district, city, postal_address, postal_address_number, post_code, postal_address_extra_info=None, api_key=None, timeout=None):
        _api_key = api_key or self.api_key
        _timeout = timeout or self.timeout
        context = {
            "email" : email,
            "country" : country,
            "district" : district,
            "city" : city,
            "postal_address" : postal_address,
            "postal_address_number" : postal_address_number,
            "postal_address_extra_info" : postal_address_extra_info,
            "post_code" : post_code
        }
        response = requests.post(
            self.get_url(),
            headers=get_headers(_api_key),
            json=context,
            timeout=_timeout
        )
        response.raise_for_status()
        return response

class ResolveAddressRequest(BaseAddressRequest):
    def get_url(self, uuid):
        return urljoin(settings.ADDRESS_API_URL, str(uuid) + "/")

class UpdateAddress(ResolveAddressRequest):
    def __call__(self, uuid, country=None, district=None, city=None, postal_address=None, postal_address_number=None, post_code=None, postal_address_extra_info=None, api_key=None, timeout=None):
        _api_key = api_key or self.api_key
        _timeout = timeout or self.timeout
        context = {
            "country" : country,
            "district" : district,
            "city" : city,
            "postal_address" : postal_address,
            "postal_address_number" : postal_address_number,
            "postal_address_extra_info" : postal_address_extra_info,
            "post_code" : post_code
        }
        response = requests.patch(
            self.get_url(uuid),
            headers=get_headers(_api_key),
            json=context,
            timeout=_timeout
        )
        response.raise_for_status()
        return response

create_address = CreateAddress()
update_address = UpdateAddress()
