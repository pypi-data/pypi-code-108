import os
import re

from abc import ABC, abstractmethod
from logging import getLogger, DEBUG
from typing import Dict, List, Optional, Union

from opentelemetry import trace
from opentelemetry.baggage import get_baggage, set_baggage
from opentelemetry.context import Context, attach
from opentelemetry.propagate import extract
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.sdk.trace import (
    ReadableSpan, Span, SpanProcessor, TracerProvider)
from opentelemetry.sdk.trace.export import SpanExporter
from helios.base.tracing.export.hooked_batch_span_processor import (
    HookedBatchSpanProcessor, HookedBatchSpanProcessorConfig)
from helios.base.tracing.export.conditional_span_processor import (
    ConditionalSpanProcessor, ConditionalSpanProcessorConfig)

_LOG = getLogger(__name__)


class HeliosTags(object):
    ACCESS_TOKEN = 'hs-access-token'
    TEST_TRIGGERED_TRACE = 'hs-triggered-test'


class HeliosBase(ABC):
    HS_DISABLED_ENV_VAR = 'HS_DISABLED'
    HS_COLLECTOR_ENDPOINT_ENV_VAR = 'HS_COLLECTOR_ENDPOINT'
    HS_TEST_COLLECTOR_ENDPOINT_ENV_VAR = 'HS_TEST_COLLECTOR_ENDPOINT'
    HS_DEFAULT_COLLECTOR = 'https://collector.heliosphere.io/traces'
    HS_DEFAULT_TEST_COLLECTOR = 'https://collector.heliosphere.io/tests'

    def __init__(self,
                 api_token: str,
                 service_name: str,
                 enabled: bool = False,
                 collector_endpoint: Optional[str] = None,
                 test_collector_endpoint: Optional[str] = None,
                 sampling_ratio: Optional[Union[float, int, str]] = 1.0,
                 environment: Optional[str] = None,
                 commit_hash: Optional[str] = None,
                 resource_tags: Optional[Dict[str, Union[bool, float, int, str]]] = None,
                 debug: Optional[bool] = False,
                 **kwargs):

        if debug:
            _LOG.setLevel(DEBUG)

        self.enabled = enabled
        if self._is_sdk_disabled():
            _LOG.warning("object wasn't initialized since sdk is disabled")
            return

        self.api_token = api_token
        self.collector_endpoint = collector_endpoint
        self.test_collector_endpoint = test_collector_endpoint
        self.environment = environment
        self.commit_hash = commit_hash
        self.resource_tags = resource_tags

        self.service_name = service_name.strip()
        self._validate_service_name()
        self.sampling_ratio = self._validate_sampling_ratio_and_convert_to_float(sampling_ratio)

        self.id_generator = kwargs.get('id_generator', None)
        self.custom_sampler = kwargs.get('sampler', None)

        # Enable overwriting the default span exporter through kwargs (mainly for testing purposes).
        span_exporter = kwargs.get('span_exporter', None)
        test_span_exporter = kwargs.get('test_span_exporter', None)

        _LOG.debug('Extracting trace provider')
        self.tracer_provider: TracerProvider = self.init_tracer_provider()
        _LOG.debug('Extracting span exporter')
        self.span_exporter: SpanExporter = self.init_span_exporter(span_exporter)
        _LOG.debug('Extracting test span exporter')
        self.test_span_exporter: SpanExporter = self.init_test_span_exporter(test_span_exporter)
        _LOG.debug('Extracting span processor')
        self.span_processor: SpanProcessor = self.init_span_processor()
        _LOG.debug('Extracting test span processor')
        self.test_span_processor: SpanProcessor = self.init_test_span_processor()
        self.tracer_provider.add_span_processor(self.span_processor)
        self.tracer_provider.add_span_processor(self.test_span_processor)
        self.instrumentations = self.get_instrumentations()

        _LOG.debug('Registering instrumentations')
        for instrumentor in self.instrumentations:
            instrumentor.instrument(tracer_provider=self.tracer_provider)

        trace.set_tracer_provider(self.tracer_provider)

        _LOG.info('Helios tracing initialized.')

        if self.is_running_in_databricks():
            self.extract_context_from_databricks()

        if debug:
            self.send_debug_span()

    def uninstrument(self) -> None:
        for instrumentor in self.instrumentations:
            instrumentor.uninstrument()

    @abstractmethod
    def init_tracer_provider(self) -> TracerProvider:
        """Get Trace Provider"""

    @abstractmethod
    def get_instrumentations(self) -> List[BaseInstrumentor]:
        """Get Instrumentor list"""

    def init_span_exporter(self, span_exporter) -> SpanExporter:
        if span_exporter:
            return span_exporter

        collector_endpoint = (self.collector_endpoint
                              or os.environ.get(
                                  self.HS_COLLECTOR_ENDPOINT_ENV_VAR)
                              or self.HS_DEFAULT_COLLECTOR)

        if not collector_endpoint:
            error_message = 'Missing Helios collector endpoint.'
            _LOG.error(error_message)
            raise ValueError(error_message)

        return OTLPSpanExporter(
            endpoint=collector_endpoint,
            headers={'Authorization': self.api_token})

    def init_test_span_exporter(self, span_exporter) -> SpanExporter:
        if span_exporter:
            return span_exporter

        test_collector_endpoint = (self.test_collector_endpoint
                                   or os.environ.get(self.HS_TEST_COLLECTOR_ENDPOINT_ENV_VAR)
                                   or self.HS_DEFAULT_TEST_COLLECTOR)
        return OTLPSpanExporter(
            endpoint=test_collector_endpoint,
            headers={'Authorization': self.api_token})

    def init_span_processor(self) -> SpanProcessor:
        if not self.span_exporter:
            error_message = 'Missing Span Exporter.'
            _LOG.error(error_message)
            raise ValueError(error_message)

        return HookedBatchSpanProcessor(
            self.span_exporter,
            HookedBatchSpanProcessorConfig(
                on_start_hook=HeliosBase.on_start_hook
            )
        )

    def init_test_span_processor(self) -> SpanProcessor:
        if not self.test_span_exporter:
            error_message = 'Missing Test Span Exporter.'
            _LOG.error(error_message)
            raise ValueError(error_message)

        return ConditionalSpanProcessor(
            self.test_span_exporter,
            ConditionalSpanProcessorConfig(
                on_start_hook=HeliosBase.on_start_hook,
                on_end_condition=HeliosBase.is_span_triggered_by_helios_test
            )
        )

    def get_tracer_provider(self):
        return self.tracer_provider

    def flush(self, timeout_millis: int = 30000) -> bool:
        """
        Args:
            timeout_millis: The maximum amount of time to wait for spans to be
                processed.

        Returns:
            False if the timeout is exceeded, True otherwise.
        """
        return self.tracer_provider.force_flush(timeout_millis)

    def send_debug_span(self):
        tracer = self.tracer_provider.get_tracer('helios')
        debug_span = tracer.start_span('debug span')
        debug_span.set_attribute('hs-debug-span', 'true')
        debug_span.end()
        self.flush()

    def is_running_in_databricks(self) -> bool:
        env_keys = os.environ.keys()
        if any('DATABRICKS' in key for key in env_keys):
            _LOG.info("Databricks environment detected")
            return True
        return False

    def extract_context_from_databricks(self):
        try:
            from pyspark.dbutils import DBUtils
            from pyspark.sql import SparkSession
            spark = SparkSession.getActiveSession()
            dbutils = DBUtils(spark)
            traceparent = dbutils.widgets.get("traceparent")
            extracted_context = extract({"traceparent": traceparent})
            span = self.tracer_provider.get_tracer(__name__).start_span('databricks_job', context=extracted_context, kind=trace.SpanKind.SERVER)
            new_context = trace.set_span_in_context(span)
            span.end()
            attach(new_context)
        except Exception as err:
            _LOG.warning("Failed to extract context", err)
            None

    @staticmethod
    def on_start_hook(span: Span, parent_context: Optional[Context]) -> None:
        if HeliosBase.is_context_of_helios_test(parent_context):
            HeliosBase.set_span_as_triggered_by_helios_test(span)
        HeliosBase.push_operation_name_attribute(span)
        HeliosBase.push_jaeger_attributes(span)

    @staticmethod
    def is_context_of_helios_test(parent_context: Optional[Context]) -> bool:
        baggage_value = \
            get_baggage(HeliosTags.TEST_TRIGGERED_TRACE, parent_context)
        return baggage_value == HeliosTags.TEST_TRIGGERED_TRACE

    @staticmethod
    def is_span_triggered_by_helios_test(span: ReadableSpan) -> bool:
        test_triggered_trace = HeliosTags.TEST_TRIGGERED_TRACE
        return span.attributes \
            and span.attributes.get(
                test_triggered_trace) == test_triggered_trace

    @staticmethod
    def set_span_as_triggered_by_helios_test(span: Span) -> None:
        test_triggered_trace = HeliosTags.TEST_TRIGGERED_TRACE
        span.set_attribute(test_triggered_trace, test_triggered_trace)

    @staticmethod
    def set_test_triggered_baggage(context: Optional[Context] = None) -> Context:
        test_triggered_trace = HeliosTags.TEST_TRIGGERED_TRACE
        return set_baggage(test_triggered_trace, test_triggered_trace, context)

    @staticmethod
    def push_jaeger_attributes(span: Span) -> None:
        if span.kind:
            span.set_attribute('span.kind', span.kind.name.lower())

        if span.instrumentation_info:
            name = span.instrumentation_info.name
            span.set_attribute('otel.library.name', name) if name else None
            version = span.instrumentation_info.version
            span.set_attribute('otel.library.version', version) if version else None

    @staticmethod
    def push_operation_name_attribute(span: Span) -> None:
        span.set_attribute('span.operation', span.name)

    def _is_sdk_disabled(self) -> bool:
        if os.environ.get(self.HS_DISABLED_ENV_VAR):
            _LOG.info(f'Helios instrumentation disabled by \
                 {self.HS_DISABLED_ENV_VAR} env var')
            return True

        return not self.enabled

    def _validate_service_name(self) -> None:
        if not self.service_name:
            raise ValueError('Service name cannot be empty')

        service_name_regex = '^[a-zA-Z0-9][a-zA-Z0-9-_]{1,62}[a-zA-Z0-9]$'
        compiled_regex = re.compile(service_name_regex)
        if not compiled_regex.match(self.service_name):
            raise ValueError(f'Service name must contain letters, digits,\
                               hyphens and underscores only. It may range\
                               between 3 to 64 characters. got {self.service_name}')

    def _validate_sampling_ratio_and_convert_to_float(
            self, sampling_ratio: Optional[Union[float, int, str]]) -> Optional[float]:
        if sampling_ratio is None or sampling_ratio == "":
            sampling_ratio = 1.0

        try:
            sampling_ratio = float(sampling_ratio)

        except ValueError as err:
            _LOG.error(err)
            raise ValueError(f'Invalid sampling ratio: {sampling_ratio}')

        if sampling_ratio < 0 or sampling_ratio > 1:
            raise ValueError(f'Sampling ratio must range between 0 to 1.\
                               got {sampling_ratio}')
        return sampling_ratio
