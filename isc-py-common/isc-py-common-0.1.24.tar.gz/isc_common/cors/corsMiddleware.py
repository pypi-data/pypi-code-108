import logging

from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class CorsMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        setattr(response, "Access-Control-Allow-Origin", "*")
        return response
