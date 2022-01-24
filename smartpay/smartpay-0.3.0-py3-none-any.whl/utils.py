import re
import jtd

from .payload import normalize_checkout_session_payload as from_loose_checkout_session_payload
from .schemas.checkout_session_payload import checkout_session_payload_schema

public_key_pattern = re.compile("^pk_(test|live)_[0-9a-zA-Z]+$")
secret_key_pattern = re.compile("^sk_(test|live)_[0-9a-zA-Z]+$")
checkout_id_pattern = re.compile("^checkout_(test|live)_[0-9a-zA-Z]+$")
order_id_pattern = re.compile("^order_(test|live)_[0-9a-zA-Z]+$")
payment_id_pattern = re.compile("^payment_(test|live)_[0-9a-zA-Z]+$")


def valid_public_api_key(apiKey):
    return bool(public_key_pattern.match(apiKey))


def valid_secret_api_key(apiKey):
    return bool(secret_key_pattern.match(apiKey))


def valid_checkout_id(checkoutId):
    return bool(checkout_id_pattern.match(checkoutId))


def valid_order_id(orderId):
    return bool(order_id_pattern.match(orderId))


def valid_payment_id(paymentId):
    return bool(payment_id_pattern.match(paymentId))


def validate_checkout_session_payload(payload):
    errors = jtd.validate(
        schema=checkout_session_payload_schema, instance=remove_none(payload))

    if len(payload['orderData']['lineItemData']) == 0:
        errors.append('payload.orderData.lineItemnData is required.')

    return errors


def get_currency(payload):
    order_data = payload.get('orderData')
    currency = order_data.get('currency', None)

    if not currency:
        lineItems = order_data.get('lineItemData', [])

        if len(lineItems) > 0:
            currency = lineItems[0]['priceData'].get('currency', None)

    return currency


def normalize_checkout_session_payload(input):
    payload = from_loose_checkout_session_payload(dict(input))
    order_data = payload.get('orderData')
    shipping_info = order_data.get('shippingInfo', {})
    currency = get_currency(payload)

    if not currency:
        raise Exception('Currency is not available.')

    if not order_data.get('currency', None):
        payload['orderData']['currency'] = currency

    if not shipping_info.get('feeCurrency'):
        shipping_info['feeCurrency'] = currency

    fee_currency = shipping_info.get('feeCurrency', None)
    fee_amount = shipping_info.get('feeAmount', None)
    shipping = fee_amount if fee_currency == currency and fee_amount else 0

    if not order_data.get('amount', None):
        def get_price(item):
            price_data = item.get('priceData')
            item_currency = price_data.get('currency', None)

            if not item_currency:
                price_data['currency'] = currency
                item_currency = currency

            if item_currency != currency:
                raise Exception('Currency of all items should be the same.')

            return price_data.get('amount', 0) * item.get('quantity', 0)

        payload['orderData']['amount'] = sum(
            list(map(get_price, order_data.get('lineItemData', [])))) + shipping

    return payload


def jtd_error_to_deta(errors=[], prefix=''):
    def transator(error):
        instancePath = error.get('instancePath', None)
        schemaPath = error.get('schemaPath', None)

        if instancePath and schemaPath:
            return '%s.%s is invalid (%s)' % (prefix, '.'.join(instancePath), schemaPath)

        return error

    return map(transator, errors)


def remove_none(obj):
    if isinstance(obj, (list, tuple, set)):
        return type(obj)(remove_none(x) for x in obj if x is not None)
    elif isinstance(obj, dict):
        return type(obj)((remove_none(k), remove_none(v))
                         for k, v in obj.items() if k is not None and v is not None)
    else:
        return obj
