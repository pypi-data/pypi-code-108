import json
from typing import Dict, Optional
from urllib.parse import urlparse

from opentelemetry.semconv.trace import SpanAttributes
from opentelemetry.trace import Span

from helios.instrumentation.base import HeliosBaseInstrumentor


class HeliosBaseHttpInstrumentor(HeliosBaseInstrumentor):

    HTTP_REQUEST_BODY_ATTRIBUTE_NAME = 'http.request.body'
    HTTP_REQUEST_HEADERS_ATTRIBUTE_NAME = 'http.request.headers'
    HTTP_RESPONSE_BODY_ATTRIBUTE_NAME = 'http.response.body'
    HTTP_RESPONSE_HEADERS_ATTRIBUTE_NAME = 'http.response.headers'
    DEFAULT_IGNORED_HOSTNAMES = ['newrelic.com', 'listener.logz.io', 'ingest.sentry.io']

    def __init__(self, module_name: str, class_name: str, ignored_hostnames: [str] = None):
        super().__init__(module_name, class_name)
        self.ignored_hostnames = ignored_hostnames or self.DEFAULT_IGNORED_HOSTNAMES

    @staticmethod
    def base_hook(span: Span, headers_attribute_name: str, payload_attribute_name: str,
                  headers: Dict, payload: Optional[str]) -> None:
        custom_http_attributes = dict()

        custom_http_attributes[headers_attribute_name] = json.dumps(dict(headers), default=str)
        if payload and len(payload) <= HeliosBaseHttpInstrumentor.MAX_PAYLOAD_SIZE:
            custom_http_attributes[payload_attribute_name] = payload

        span.set_attributes(custom_http_attributes)

    @staticmethod
    def base_response_hook(span: Span, response_headers: Dict, response_payload: Optional[str]) -> None:
        HeliosBaseHttpInstrumentor.base_hook(span,
                                             HeliosBaseHttpInstrumentor.HTTP_RESPONSE_HEADERS_ATTRIBUTE_NAME,
                                             HeliosBaseHttpInstrumentor.HTTP_RESPONSE_BODY_ATTRIBUTE_NAME,
                                             response_headers, response_payload)

    @staticmethod
    def base_request_hook(span: Span, request_headers: Dict, request_payload: Optional[str]) -> None:
        url = span.attributes.get(SpanAttributes.HTTP_URL)
        target = span.attributes.get(SpanAttributes.HTTP_TARGET)

        if target is None and url is not None:
            try:
                parsed_url = urlparse(url)
                target = parsed_url.path
            except ValueError:
                pass

            span.set_attribute(SpanAttributes.HTTP_TARGET, target) if target is not None else None

        HeliosBaseHttpInstrumentor.base_hook(span,
                                             HeliosBaseHttpInstrumentor.HTTP_REQUEST_HEADERS_ATTRIBUTE_NAME,
                                             HeliosBaseHttpInstrumentor.HTTP_REQUEST_BODY_ATTRIBUTE_NAME,
                                             request_headers, request_payload)
