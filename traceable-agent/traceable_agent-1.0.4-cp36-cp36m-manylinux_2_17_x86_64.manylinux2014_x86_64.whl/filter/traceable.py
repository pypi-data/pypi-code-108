import os
import traceback
import logging

import hypertrace.agent.filter
from hypertrace.agent.filter.registry import TYPE_HTTP, TYPE_RPC
from opentelemetry.trace import Span
from traceableai.config.config import Config

logger = logging.getLogger(__name__)

_BLOCKING_AVAILABLE = False
_NOT_BODY = False
_IS_BODY = True

try:
    import traceableai.filter._blocking as _blocking # pylint: disable=E0611,E0401,bad-option-value
    _BLOCKING_AVAILABLE = True
except Exception as error:  # pylint: disable=broad-except
    _BLOCKING_AVAILABLE = False
    traceback.print_tb(error.__traceback__)
    logger.warning(error)
    logger.warning("error loading traceable extension - blocking filter disabled")


_HEADER_PREFIXES = {
    TYPE_HTTP: 'http.request.header',
    TYPE_RPC: 'rpc.request.metadata'
}

_BODY_PREFIXES = {
    TYPE_HTTP: 'http.request.body',
    TYPE_RPC: 'rpc.request.body'
}


class Traceable(hypertrace.agent.filter.Filter):

    def __init__(self):
        if _BLOCKING_AVAILABLE:
            self.blocking_config = _create_blocking_config()
            p_blocking_engine = _blocking.ffi.new("traceable_blocking_engine*")
            result_code = _blocking.lib.traceable_new_blocking_engine(self.blocking_config[0], p_blocking_engine)
            self.blocking_available = (result_code == _blocking.lib.TRACEABLE_SUCCESS)
            if self.blocking_available:
                logger.debug("blocking available")
                self.blocking_engine = p_blocking_engine[0]
                result = _blocking.lib.traceable_start_blocking_engine(self.blocking_engine)
                if result != _blocking.lib.TRACEABLE_SUCCESS:
                    logger.debug("Failed to start blocking engine")
                    self.blocking_available = False
        else:
            self.blocking_available = False

    def evaluate_url_and_headers(self, span: Span, url: str, headers: dict, request_type) -> bool:
        if not self.blocking_available:
            return False

        pairs = _add_header_and_span_attributes(span, headers, request_type)

        # add url as part of header processing
        pairs.append((_blocking.ffi.new("char[]", b"http.url"),
                      _blocking.ffi.new("char[]", f"{url}".encode('ascii'))))

        num_headers = len(pairs)
        attributes = _blocking.ffi.new("traceable_attributes*")
        attribute_array = _blocking.ffi.new("traceable_attribute[]", num_headers)
        attributes.count = num_headers

        for index, pair in enumerate(pairs, start=0):
            attribute_array[index].key = pair[0]
            attribute_array[index].value = pair[1]
        attributes.attribute_array = attribute_array

        return self._evaluate_attributes(span, attributes, _NOT_BODY)

    def evaluate_body(self, span: Span, body, headers: dict, request_type) -> bool:
        if not self.blocking_available:
            return False

        if not body or len(str(body)) == 0:
            return False

        pairs = _add_header_and_span_attributes(span, headers, request_type)
        prefix = _BODY_PREFIXES[request_type]
        pairs.append((_blocking.ffi.new("char[]", prefix.encode('ascii')),
                      _blocking.ffi.new("char[]", f"{body}".encode('ascii'))))

        num_attrs = len(pairs)
        attributes = _blocking.ffi.new("traceable_attributes*")
        attribute_array = _blocking.ffi.new("traceable_attribute[]", num_attrs)
        attributes.count = num_attrs

        for index, pair in enumerate(pairs, start=0):
            attribute_array[index].key = pair[0]
            attribute_array[index].value = pair[1]
        attributes.attribute_array = attribute_array


        return self._evaluate_attributes(span, attributes, _IS_BODY)

    def _evaluate_attributes(self, span, attributes, is_body) -> bool:
        blocking_result = _blocking.ffi.new("traceable_block_result*")
        result_code = _blocking.lib.TRACEABLE_SUCCESS
        if is_body:
            result_code = _blocking.lib.traceable_block_request_body(self.blocking_engine, attributes[0], blocking_result) # pylint:disable=C0301
        else:
            result_code = _blocking.lib.traceable_block_request(self.blocking_engine, attributes[0], blocking_result)

        if result_code != _blocking.lib.TRACEABLE_SUCCESS:
            logger.debug ("traceable_block_request fail!")
            return False

        _add_span_attributes(span, blocking_result)

        _result_code = _blocking.lib.traceable_delete_block_result_data(blocking_result[0])
        if blocking_result.block:
            return True
        return False


def _add_span_attributes(span: Span, blocking_result):
    attr_count = blocking_result.attributes.count
    for i in range(attr_count):
        key_attr = blocking_result.attributes.attribute_array[i].key
        value_attr = blocking_result.attributes.attribute_array[i].value
        if key_attr == _blocking.ffi.NULL or value_attr == _blocking.ffi.NULL:
            continue

        key = _blocking.ffi.string(key_attr)
        value = _blocking.ffi.string(value_attr)

        span.set_attribute(key.decode('utf-8', 'backslashescape'), value.decode('utf-8', 'backslashescape'))

def _add_header_and_span_attributes(span: Span, headers: dict, request_type) -> []:
    pairs = []
    ip_address = span._readable_span().attributes.get('net.peer.ip')  # pylint:disable=W0212
    if ip_address:
        pairs.append((_blocking.ffi.new("char[]", b"net.peer.ip"),
                      _blocking.ffi.new("char[]", f"{ip_address}".encode('ascii'))))

    header_prefix = _HEADER_PREFIXES[request_type]
    for header_key, header_value in headers.items():
        pairs.append((_blocking.ffi.new("char[]", f"{header_prefix}.{header_key}".lower().encode('ascii')),
                      _blocking.ffi.new("char[]", f"{header_value}".encode('ascii'))))

    return pairs


def _create_blocking_config():
    traceable_config = Config().config
    should_debug = 0
    if os.environ.get("TA_LOG_LEVEL", "").upper() == "DEBUG":
        should_debug = 1
    if traceable_config.blocking_config.debug_log.value is True:
        should_debug = 1

    blocking_config = _blocking.ffi.new("traceable_blocking_config*")

    blocking_config.log_config.mode = should_debug

    traceable_opa = traceable_config.opa
    opa_server_url = _blocking.ffi.new("char[]", f"{traceable_opa.endpoint.value}".encode('ascii'))

    blocking_config.opa_config.opa_server_url = opa_server_url
    blocking_config.opa_config.log_to_console = 1
    blocking_config.opa_config.skip_verify = 0
    blocking_config.opa_config.debug_log = should_debug
    blocking_config.opa_config.min_delay = traceable_opa.poll_period_seconds.value
    blocking_config.opa_config.max_delay = traceable_opa.poll_period_seconds.value
    blocking_config.opa_config.logging_dir = _blocking.ffi.new("char[]", "".encode('ascii'))
    blocking_config.opa_config.logging_file_prefix = _blocking.ffi.new("char[]", "".encode('ascii'))
    blocking_config.opa_config.cert_file = _blocking.ffi.new("char[]", "".encode('ascii'))

    modsecurity_enabled = 1 if traceable_config.blocking_config.modsecurity.enabled.value is True else 0
    blocking_config.modsecurity_config.enabled = modsecurity_enabled

    rb_enabled = 1 if traceable_config.blocking_config.region_blocking.enabled else 0
    blocking_config.rb_config.enabled = rb_enabled

    remote_config_enabled = 1 if traceable_config.blocking_config.remote_config.enabled.value is True else 0
    blocking_config.remote_config.enabled = remote_config_enabled

    cert_file = _blocking.ffi.new("char[]", "".encode('ascii'))
    blocking_config.remote_config.cert_file = cert_file

    remote_config_endpoint = traceable_config.blocking_config.remote_config.endpoint.value
    remote_url = _blocking.ffi.new("char[]", f"{remote_config_endpoint}".encode('ascii'))
    blocking_config.remote_config.remote_endpoint = remote_url

    remote_poll_period_seconds = traceable_config.blocking_config.remote_config.poll_period_seconds.value
    blocking_config.remote_config.poll_period_sec = remote_poll_period_seconds

    blocking_config.evaluate_body = 1 if traceable_config.blocking_config.evaluate_body.value is True else 0
    blocking_config.skip_internal_request = 1 if traceable_config.blocking_config.skip_internal_request.value is True else 0 # pylint:disable=C0301
    return blocking_config
