from urllib.parse import urlencode
import requests
import json

from django.conf import settings
from requests import api

from dnoticias_services.utils.request import get_headers
from .base import BasePaymentRequest

class GetUserOrderDatatable(BasePaymentRequest):
    def __call__(self, request, user_email, api_key=None):
        _api_key = api_key or self.api_key
        request = json.dumps(request.POST)

        response = requests.post(
            settings.ORDER_USER_DATATABLE_LIST_API_URL.format(user_email),
            headers=get_headers(_api_key),
            json=request,
        )

        response.raise_for_status()

        return response

get_user_order_datatable = GetUserOrderDatatable()


class GetUserOrders(BasePaymentRequest):
    def __call__(self, user_email, page=1, last=False, status=None, api_key=None):
        _api_key = api_key or self.api_key
        params = {}

        query_params = ''

        if page:
            params['page'] = page

        if last:
            params['last'] = True

        if status is not None:
            params['status'] = status

        if params:
            query_params = "?{}".format(urlencode(params))

        response = requests.get(
            settings.ORDER_USER_LIST_API_URL.format(user_email) + query_params,
            headers=get_headers(_api_key),
        )

        response.raise_for_status()

        return response

get_user_orders = GetUserOrders()


class GetOrderDetail(BasePaymentRequest):
    def __call__(self, order_id, api_key=None):
        _api_key = api_key or self.api_key

        response = requests.get(
            settings.ORDER_DETAIL_API_URL.format(order_id),
            headers=get_headers(_api_key),
        )

        response.raise_for_status()

        return response

get_order_detail = GetOrderDetail()


class GetOrderBilling(BasePaymentRequest):
    def __call__(self, order_id, api_key=None, timeout=None):
        self.set_api_url(settings.ORDER_GET_BILLING_API_URL, (order_id, ))
        return self.get({}, api_key, timeout)

get_order_billing = GetOrderBilling()


class RequestOrderInvoice(BasePaymentRequest):
    def __call__(self, order_id, api_key=None, timeout=None):
        self.set_api_url(settings.ORDER_REQUEST_INVOICE_API_URL, (order_id, ))
        return self.post({}, {}, api_key, timeout)

request_order_invoice = RequestOrderInvoice()


class CreateOrder(BasePaymentRequest):
    def __call__(self, context, api_key=None):
        _api_key = api_key or self.api_key

        response = requests.post(
            settings.ORDER_CREATE_API_URL,
            headers=get_headers(_api_key),
            json=context,
        )

        response.raise_for_status()

        return response

create_order = CreateOrder()


__all__ = (
    "get_user_order_datatable",
    "get_user_orders",
    "get_order_detail",
    "setup_payment_intent",
    "change_subscription_payment_method",
    "create_order",
    "get_order_billing",
    "request_order_invoice",
)
