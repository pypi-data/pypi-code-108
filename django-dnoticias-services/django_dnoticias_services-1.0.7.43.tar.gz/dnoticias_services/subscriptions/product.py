from urllib.parse import urljoin

from dnoticias_services.utils.request import get_headers
from django.conf import settings

import requests

from .base import BaseSubscriptionRequest


class BaseProductRequest(BaseSubscriptionRequest):
    def get_url(self):
        return settings.PRODUCT_API_URL


class CreateProduct(BaseProductRequest):
    def __call__(self, name: str, slug: str, price: int, active: bool=True, extra_attrs: dict=dict(), remote_id: str="", description="", shippable: bool=False, category=None, accounting_code: str=None, api_key: str=None, timeout: int=None):
        url = self.get_url()
        _api_key = api_key or self.api_key
        _timeout = timeout or self.timeout
        print(get_headers(_api_key))
        response = requests.post(
            url,
            headers=get_headers(_api_key),
            json={
                "name": name,
                "slug": slug,
                "extra_attrs": extra_attrs,
                "description": description,
                "price": price,
                "active": active,
                "shippable": shippable,
                "accounting_code": accounting_code,
                "category": category,
                "remote_id": remote_id,
            },
            timeout=_timeout
        )
        response.raise_for_status()
        return response


class ResolveProduct(BaseProductRequest):
    def get_url(self, uuid):
        return urljoin(settings.PRODUCT_API_URL, str(uuid) + "/")


class UpdateProduct(ResolveProduct):
    def __call__(self, uuid, name=None, slug=None, price=None, active=None, extra_attrs=None, description=None, shippable=None, category=None, accounting_code=None, api_key=None, timeout=None):
        assert uuid

        url = self.get_url(uuid)
        _api_key = api_key or self.api_key
        _timeout = timeout or self.timeout
        print(get_headers(_api_key))
        context = {
            "name": name,
            "slug": slug,
            "extra_attrs": extra_attrs,
            "description": description,
            "price": price,
            "active": active,
            "shippable": shippable,
            "accounting_code": accounting_code,
            "category": category,
        }

        response = requests.patch(
            url,
            headers=get_headers(_api_key),
            json={key: context[key] for key in context.keys()},
            timeout=_timeout
        )

        response.raise_for_status()
        return response


class DeleteProduct(ResolveProduct):
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


class GetProduct(BaseSubscriptionRequest):
    def __call__(self, slug=None, accounting_code=None, api_key=None, timeout=None):
        params = {'slug': slug} if slug else {'accounting_code': accounting_code}
        self.set_api_url(settings.PAYMENTS_GET_ITEM_API_URL)
        return self.get(params, api_key, timeout)


create_product = CreateProduct()
update_product = UpdateProduct()
delete_product = DeleteProduct()
get_product = GetProduct()
