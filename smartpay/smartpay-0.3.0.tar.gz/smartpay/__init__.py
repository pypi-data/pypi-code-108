import os
import requests
from urllib.parse import urlencode

from .utils import valid_public_api_key, valid_secret_api_key
from .utils import valid_order_id, valid_payment_id
from .utils import validate_checkout_session_payload, normalize_checkout_session_payload

from .version import __version__

API_PREFIX = 'https://api.smartpay.co/v1'
CHECKOUT_URL = 'https://checkout.smartpay.co'

POST = 'POST'
PUT = 'PUT'
DELETE = 'DELETE'

STATUS_SUCCEEDED = 'succeeded'
STATUS_REJECTED = 'rejected'
STATUS_FAILED = 'failed'
STATUS_REQUIRES_AUTHORIZATION = 'requires_authorization'

api_prefix_candidate = os.environ.get('SMARTPAY_API_PREFIX', None)

SMARTPAY_API_PREFIX = api_prefix_candidate if api_prefix_candidate and 'api.smartpay' in api_prefix_candidate else None
SMARTPAY_CHECKOUT_URL = os.environ.get('SMARTPAY_CHECKOUT_URL', None)


class Smartpay:
    def __init__(self, secret_key, public_key=None, api_prefix=None, checkout_url=None):
        if not secret_key:
            raise Exception('Secret Key is required.')

        if not valid_secret_api_key(secret_key):
            raise Exception('Secret Key is invalid.')

        if public_key and not valid_public_api_key(public_key):
            raise Exception('Public Key is invalid.')

        self._secret_key = secret_key
        self._public_key = public_key
        self._api_prefix = api_prefix or SMARTPAY_API_PREFIX or API_PREFIX
        self._checkout_url = checkout_url or SMARTPAY_CHECKOUT_URL or CHECKOUT_URL

    def request(self, endpoint, method='GET', params=None, payload=None):
        r = requests.request(method, '%s%s' % (self._api_prefix, endpoint), headers={
            'Authorization': 'Basic %s' % (self._secret_key,),
        }, params=params, json=payload)

        if r.status_code < 200 or r.status_code > 299:
            raise Exception('%s: %s' % (r.status_code, r.text))

        return r.json()

    def normalize_checkout_session_payload(self, payload):
        normalize_payload = normalize_checkout_session_payload(payload)
        errors = validate_checkout_session_payload(normalize_payload)

        if len(errors) > 0:
            raise Exception(errors)

        return normalize_payload

    def create_checkout_session(self, payload):
        normalized_payload = self.normalize_checkout_session_payload(payload)

        params = {
            'dev-lang': 'python',
            'sdk-version': __version__,
        }

        session = self.request(
            '/checkout-sessions', POST, params, payload=normalized_payload)

        try:
            session['checkoutURL'] = self.get_session_url(session, {
                'promotionCode': payload.get('promotionCode', None)
            })
        except Exception:
            pass

        return session

    def set_public_key(self, public_key):
        if not public_key:
            raise Exception('Public API Key is required.')

        if not valid_public_api_key(public_key):
            raise Exception('Public API Key is invalid.')

        self._public_key = public_key

    def get_session_url(self, session, options={}):
        if not session:
            raise Exception('Checkout Session is required.')

        if not self._public_key:
            raise Exception('Public API Key is required.')

        checkoutURL = options.get('checkoutURL', self._checkout_url)
        promotionCode = options.get('promotionCode', None)

        params = {
            'session-id': session.get('id'),
            'public-key': self._public_key,
            'promotion-code': promotionCode,
        }

        return '%s/login?%s' % (checkoutURL, urlencode(params))
