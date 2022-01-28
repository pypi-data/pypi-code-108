import requests
import json
from urllib.parse import urlencode

from django.conf import settings

from dnoticias_services.utils.request import get_headers
from .base import BasePaymentRequest


class GetPaymentProviders(BasePaymentRequest):
    """
    Gets all the active payment providers from dnoticias-payments.
    """
    def __call__(self, item_uuid, request, api_key=None, timeout=None):
        self.set_api_url(settings.PAYMENT_PROVIDERS_SELECT2VIEW_API_URL, (item_uuid, ))
        return self.get(dict(request.query_params), api_key, timeout)


get_payment_providers = GetPaymentProviders()

__all__ = ("get_payment_providers", )
