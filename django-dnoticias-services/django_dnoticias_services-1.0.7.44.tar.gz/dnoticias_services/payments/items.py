from urllib.parse import urljoin

import requests
from django.conf import settings
from dnoticias_services.utils.request import get_headers

from .base import BasePaymentRequest


class BaseItemRequest(BasePaymentRequest):
    def get_url(self):
        return settings.ITEM_API_URL

class CreateItem(BaseItemRequest):
    def __call__(self, name, slug, price, active=True, extra_attrs=dict(), description="", images=dict(), shippable=False, interval=None, interval_count=None, trial_interval=None, trial_interval_count=None, offers=[], category=None, accounting_id=None, can_be_recurring=False, api_key=None, timeout=None):
        url = self.get_url()
        _api_key = api_key or self.api_key
        _timeout = timeout or self.timeout
        
        response = requests.post(
            url,
            headers=get_headers(_api_key),
            json={
                "name" : name,
                "slug" : slug,
                "extra_attrs" : extra_attrs,
                "description" : description,
                "price" : price,
                "active" : active,
                "images" : images,
                "shippable" : shippable,
                "accounting_id": accounting_id,
                "interval" : interval,
                "interval_count" : interval_count,
                "trial_interval" : trial_interval,
                "trial_interval_count" : trial_interval_count,
                "offers" : offers,
                "category" : category,
                "can_be_recurring": can_be_recurring,
            },
            timeout=_timeout
        )
        response.raise_for_status()
        return response

class ResolveItem(BaseItemRequest):
    def get_url(self, uuid):
        return urljoin(settings.ITEM_API_URL, str(uuid) + "/")

class UpdateItem(ResolveItem):
    def __call__(self, uuid, name=None, slug=None, price=None, active=None, extra_attrs=None, description=None, images=None, shippable=None, interval=None, interval_count=None, trial_interval=None, trial_interval_count=None, offers=None, category=None, accounting_id=None, can_be_recurring=False, api_key=None, timeout=None):
        assert uuid

        url = self.get_url(uuid)
        _api_key = api_key or self.api_key
        _timeout = timeout or self.timeout

        context = {
            "name" : name,
            "slug" : slug,
            "extra_attrs" : extra_attrs,
            "description" : description,
            "price" : price,
            "active" : active,
            "images" : images,
            "shippable" : shippable,
            "interval" : interval,
            "interval_count" : interval_count,
            "trial_interval" : trial_interval,
            "trial_interval_count" : trial_interval_count,
            "offers" : offers,
            "category" : category,
            "accounting_id": accounting_id,
            "can_be_recurring": can_be_recurring,
        }
        
        response = requests.patch(
            url,
            headers=get_headers(_api_key),
            json={key: context[key] for key in context.keys()},
            timeout=_timeout
        )
        response.raise_for_status()
        return response


class DeleteItem(ResolveItem):
    def __call__(self, uuid, api_key=None, timeout=None):
        _api_key = api_key or self.api_key
        _timeout = timeout or self.timeout
        response = requests.delete(
            self.get_url(uuid),
            headers=get_headers(_api_key),
            timeout=_timeout
        )
        response.raise_for_status()
        return response


class GetItem(BasePaymentRequest):
    def __call__(self, slug=None, accounting_id=None, api_key=None, timeout=None):
        params = {'slug': slug} if slug else {'accounting_id': accounting_id}
        self.set_api_url(settings.PAYMENTS_GET_ITEM_API_URL)
        return self.get(params, api_key, timeout)


create_item = CreateItem()
update_item = UpdateItem()
delete_item = DeleteItem()
get_item = GetItem()
