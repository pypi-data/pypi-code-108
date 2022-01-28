from django.conf import settings
from dnoticias_services.base_service import BaseService


class BaseSubscriptionRequest(BaseService):
    def __init__(self):
        self.api_key = getattr(settings, "SUBSCRIPTION_SERVICE_ACCOUNT_API_KEY", None)
        self.timeout = getattr(settings, "SUBSCRIPTION_SERVICE_REQUEST_TIMEOUT", 5)
