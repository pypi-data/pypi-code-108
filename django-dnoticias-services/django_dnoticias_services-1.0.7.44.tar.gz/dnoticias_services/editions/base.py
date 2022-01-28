from django.conf import settings
from dnoticias_services.base_service import BaseService


class BaseEditionsRequest(BaseService):
    def __init__(self):
        self.timeout = getattr(settings, "EDITIONS_SERVICE_REQUEST_TIMEOUT", 5)
        self.api_key = getattr(settings, "EDITIONS_SERVICE_ACCOUNT_API_KEY", None)
