import json

from .utils import generate_hmac


class SmoothCodeAuth:
    def __init__(self, request_hmac: str, client_secret: str):
        self.hmac = request_hmac
        self.client_secret = client_secret

    def is_dashboard_request(self, shop: str):
        return generate_hmac(self.client_secret, shop) == self.hmac

    def is_webhook_request(self, webhook_data: dict):
        webhook_id = webhook_data.get('id')
        return generate_hmac(self.client_secret, str(webhook_id)) == self.hmac
