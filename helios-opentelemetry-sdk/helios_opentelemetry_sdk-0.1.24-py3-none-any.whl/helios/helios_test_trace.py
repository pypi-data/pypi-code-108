import os
import requests
import time

from contextlib import contextmanager
from opentelemetry import context, trace
from opentelemetry.semconv.resource import ResourceAttributes
from opentelemetry.instrumentation.utils import _SUPPRESS_INSTRUMENTATION_KEY
from requests.adapters import HTTPAdapter, RetryError
from requests.packages.urllib3.util.retry import Retry

from helios.defaults import DEFAULT_HS_API_ENDPOINT
from helios.utils import encode_id_as_hex_string

HS_ACCESS_TOKEN_ENV_VAR = 'HS_ACCESS_TOKEN'


class SpanResult():

    def __init__(self, span_id, operation, service, parent_span_id, attributes):
        self.span_id = span_id
        self.operation = operation
        self.service = service
        self.parent_span_id = parent_span_id
        self.attributes = attributes


class HeliosTestTrace():

    def __init__(self, api_token=None, helios_host=None):
        self.api_token = api_token or os.environ.get(HS_ACCESS_TOKEN_ENV_VAR)
        self.helios_host = os.environ.get('HS_API_ENDPOINT', helios_host) or DEFAULT_HS_API_ENDPOINT
        self.trace_id = encode_id_as_hex_string(trace.get_current_span().get_span_context().trace_id)
        self.spans = []

    def fetch_trace(self):
        with HeliosTestTrace.suppress_instrumentation():

            session = requests.Session()
            retries = Retry(total=3, backoff_factor=1, status_forcelist=[404, 502, 503, 504])
            session.mount('https://', HTTPAdapter(max_retries=retries))

            try:
                response = session.get(
                    f"{self.helios_host}/trace-api/test-acceptance/{self.trace_id}",
                    headers={'Authorization': f'Bearer {self.api_token}'})

                if response.status_code == 200:
                    return response.json()

            except RetryError:
                return None

    @contextmanager
    def suppress_instrumentation():
        try:
            context_token = context.attach(context.set_value(_SUPPRESS_INSTRUMENTATION_KEY, True))
            yield
        finally:
            if context_token:
                context.detach(context_token)

    def fetch_spans(self):
        trace = self.fetch_trace()
        self.spans = HeliosTestTrace.extract_spans(trace) if trace else []

    @staticmethod
    def extract_spans(trace):
        spans = []
        for span in trace.get('spans'):
            spans.append(
                SpanResult(
                    span_id=span.get('spanId'),
                    parent_span_id=span.get('parentSpanId'),
                    operation=span.get('name'),
                    service=HeliosTestTrace.extract_attribute(
                        span.get('resource').get('attributes'), ResourceAttributes.SERVICE_NAME),
                    attributes=HeliosTestTrace.convert_attributes(span.get('attributes'))))

        return spans

    @staticmethod
    def convert_attributes(attributes):
        return {a.get('key'): HeliosTestTrace.extract_attribute_value(a.get('value')) for a in attributes}

    @staticmethod
    def extract_attribute(attributes, key):
        value = list(filter(lambda attr: attr.get('key') == key, attributes))[0].get('value')
        attr = HeliosTestTrace.extract_attribute_value(value)
        return attr

    @staticmethod
    def extract_attribute_value(attribute_value_dict):
        value_type, raw_value = list(attribute_value_dict.items())[0]
        try:
            if value_type == 'kvlistValue':
                return HeliosTestTrace.convert_attributes(raw_value.get('values'))
            elif value_type == 'arrayValue':
                return [HeliosTestTrace.extract_attribute_value(v) for v in raw_value.get('values')]
            elif value_type == 'intValue':
                return int(raw_value)
            elif value_type == 'doubleValue':
                return float(raw_value)
            elif value_type == 'boolValue':
                return bool(raw_value)
            else:
                return raw_value
        except ValueError:
            return raw_value

    def get_spans_matching(self, service, operation, span_selectors=[]):
        selectors = span_selectors if isinstance(span_selectors, list) else [span_selectors]
        return list(filter(
            lambda span: (
                span.service == service and
                span.operation == operation and
                all([span.attributes[s.get('key')] == s.get('value') for s in selectors])
            ), self.spans
        ))

    def find_spans(self, service, operation, span_selectors=[], expected_number_of_spans=1, max_attempts=6):
        spans = self.get_spans_matching(service, operation, span_selectors)
        if len(spans) >= expected_number_of_spans:
            return spans

        # wait for spans
        for i in range(max_attempts):
            time.sleep(1 + i)
            self.fetch_spans()
            spans = self.get_spans_matching(service, operation, span_selectors)
            if len(spans) >= expected_number_of_spans:
                return spans

        return spans or []
