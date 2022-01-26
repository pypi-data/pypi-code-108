# Copyright The OpenTelemetry Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Usage
-----

Instrumenting all clients
*************************

When using the instrumentor, all clients will automatically trace requests.

.. code-block:: python

     import httpx
     from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

     url = "https://httpbin.org/get"
     HTTPXClientInstrumentor().instrument()

     with httpx.Client() as client:
          response = client.get(url)

     async with httpx.AsyncClient() as client:
          response = await client.get(url)

Instrumenting single clients
****************************

If you only want to instrument requests for specific client instances, you can
use the `instrument_client` method.


.. code-block:: python

    import httpx
    from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

    url = "https://httpbin.org/get"

    with httpx.Client(transport=telemetry_transport) as client:
        HTTPXClientInstrumentor.instrument_client(client)
        response = client.get(url)

    async with httpx.AsyncClient(transport=telemetry_transport) as client:
        HTTPXClientInstrumentor.instrument_client(client)
        response = await client.get(url)


Uninstrument
************

If you need to uninstrument clients, there are two options available.

.. code-block:: python

     import httpx
     from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

     HTTPXClientInstrumentor().instrument()
     client = httpx.Client()

     # Uninstrument a specific client
     HTTPXClientInstrumentor.uninstrument_client(client)

     # Uninstrument all clients
     HTTPXClientInstrumentor().uninstrument()


Using transports directly
*************************

If you don't want to use the instrumentor class, you can use the transport classes directly.


.. code-block:: python

    import httpx
    from opentelemetry.instrumentation.httpx import (
        AsyncOpenTelemetryTransport,
        SyncOpenTelemetryTransport,
    )

    url = "https://httpbin.org/get"
    transport = httpx.HTTPTransport()
    telemetry_transport = SyncOpenTelemetryTransport(transport)

    with httpx.Client(transport=telemetry_transport) as client:
        response = client.get(url)

    transport = httpx.AsyncHTTPTransport()
    telemetry_transport = AsyncOpenTelemetryTransport(transport)

    async with httpx.AsyncClient(transport=telemetry_transport) as client:
        response = await client.get(url)


Request and response hooks
***************************

The instrumentation supports specifying request and response hooks. These are functions that get called back by the instrumentation right after a span is created for a request
and right before the span is finished while processing a response.

.. note::

    The request hook receives the raw arguments provided to the transport layer. The response hook receives the raw return values from the transport layer.

The hooks can be configured as follows:


.. code-block:: python

    from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

    def request_hook(span, request):
        # method, url, headers, stream, extensions = request
        pass

    def response_hook(span, request, response):
        # method, url, headers, stream, extensions = request
        # status_code, headers, stream, extensions = response
        pass

    HTTPXClientInstrumentor().instrument(request_hook=request_hook, response_hook=response_hook)


Or if you are using the transport classes directly:


.. code-block:: python

    from opentelemetry.instrumentation.httpx import SyncOpenTelemetryTransport

    def request_hook(span, request):
        # method, url, headers, stream, extensions = request
        pass

    def response_hook(span, request, response):
        # method, url, headers, stream, extensions = request
        # status_code, headers, stream, extensions = response
        pass

    transport = httpx.HTTPTransport()
    telemetry_transport = SyncOpenTelemetryTransport(
        transport,
        request_hook=request_hook,
        response_hook=response_hook
    )

API
---
"""
import logging
import typing

import httpx
import wrapt

from opentelemetry import context
from helios.httpx_instrumentation.src.httpx.package import _instruments
from helios.httpx_instrumentation.src.httpx.version import __version__
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.instrumentation.utils import http_status_to_status_code, unwrap
from opentelemetry.propagate import inject
from opentelemetry.semconv.trace import SpanAttributes
from opentelemetry.trace import SpanKind, get_tracer
from opentelemetry.trace.span import Span
from opentelemetry.trace.status import Status

_logger = logging.getLogger(__name__)

URL = typing.Tuple[bytes, bytes, typing.Optional[int], bytes]
Headers = typing.List[typing.Tuple[bytes, bytes]]
RequestHook = typing.Callable[[Span, "RequestInfo"], None]
ResponseHook = typing.Callable[[Span, "RequestInfo", "ResponseInfo"], None]
AsyncRequestHook = typing.Callable[
    [Span, "RequestInfo"], typing.Awaitable[typing.Any]
]
AsyncResponseHook = typing.Callable[
    [Span, "RequestInfo", "ResponseInfo"], typing.Awaitable[typing.Any]
]


class RequestInfo(typing.NamedTuple):
    method: bytes
    url: URL
    headers: typing.Optional[Headers]
    stream: typing.Optional[
        typing.Union[httpx.SyncByteStream, httpx.AsyncByteStream]
    ]
    extensions: typing.Optional[dict]


class ResponseInfo(typing.NamedTuple):
    status_code: int
    headers: typing.Optional[Headers]
    stream: typing.Iterable[bytes]
    extensions: typing.Optional[dict]


def _get_default_span_name(method: str) -> str:
    return f"HTTP {method.strip()}"


def _apply_status_code(span: Span, status_code: int) -> None:
    if not span.is_recording():
        return

    span.set_attribute(SpanAttributes.HTTP_STATUS_CODE, status_code)
    span.set_status(Status(http_status_to_status_code(status_code)))


def _prepare_attributes(method: bytes, url: URL) -> typing.Dict[str, str]:
    _method = method.decode().upper()
    _url = str(httpx.URL(url))
    span_attributes = {
        SpanAttributes.HTTP_METHOD: _method,
        SpanAttributes.HTTP_URL: _url,
    }
    return span_attributes


def _prepare_headers(headers: typing.Optional[Headers]) -> httpx.Headers:
    return httpx.Headers(headers)


def extract_parameters(orig_args, orig_kwargs):
    if type(orig_args[0]) == httpx.Request:
        request: httpx.Request = orig_args[0]
        method = request.method.encode()
        url = request.url
        headers = request.headers
        stream = request.stream
        extensions = request.extensions
    else:
        method = orig_args[0]
        url = orig_args[1]
        headers = orig_kwargs.get('headers', orig_args[2] if len(orig_args) > 2 else None)
        stream = orig_kwargs.get('stream', orig_args[3] if len(orig_args) > 3 else None)
        extensions = orig_kwargs.get('extensions', orig_args[4] if len(orig_args) > 4 else None)

    return method, url, headers, stream, extensions


def inject_propagation_headers(headers, orig_args, orig_kwargs):
    _headers = _prepare_headers(headers)
    inject(_headers)
    if type(orig_args[0]) == httpx.Request:
        request: httpx.Request = orig_args[0]
        request.headers = _headers
    else:
        orig_kwargs['headers'] = _headers.raw


async def wrapped_async_handle_request(orig_wrapped, orig_args, orig_kwargs, tracer, request_hook, response_hook):
    if context.get_value("suppress_instrumentation"):
        return await orig_wrapped(*orig_args, **orig_kwargs)

    method, url, headers, stream, extensions = extract_parameters(orig_args, orig_kwargs)
    span_attributes = _prepare_attributes(method, url)
    request_info = RequestInfo(method, url, headers, stream, extensions)
    span_name = _get_default_span_name(span_attributes[SpanAttributes.HTTP_METHOD])

    with tracer.start_as_current_span(
            span_name, kind=SpanKind.CLIENT, attributes=span_attributes
    ) as span:
        if request_hook is not None:
            request_hook(span, request_info)

        inject_propagation_headers(headers, orig_args, orig_kwargs)
        response = await orig_wrapped(*orig_args, **orig_kwargs)
        if type(response) == httpx.Response:
            response: httpx.Response = response
            status_code = response.status_code
            headers = response.headers
            stream = response.stream
            extensions = response.extensions
        else:
            (status_code, headers, stream, extensions) = response

        _apply_status_code(span, status_code)

        if response_hook is not None:
            response_hook(
                span,
                request_info,
                ResponseInfo(status_code, headers, stream, extensions),
            )

    return response


def wrapped_sync_handle_request(orig_wrapped, orig_args, orig_kwargs, tracer, request_hook, response_hook):
    if context.get_value("suppress_instrumentation"):
        return orig_wrapped(*orig_args, **orig_kwargs)

    method, url, headers, stream, extensions = extract_parameters(orig_args, orig_kwargs)
    span_attributes = _prepare_attributes(method, url)

    request_info = RequestInfo(method, url, headers, stream, extensions)
    span_name = _get_default_span_name(span_attributes[SpanAttributes.HTTP_METHOD])

    with tracer.start_as_current_span(
            span_name, kind=SpanKind.CLIENT, attributes=span_attributes
    ) as span:
        if request_hook is not None:
            request_hook(span, request_info)

        inject_propagation_headers(headers, orig_args, orig_kwargs)
        response = orig_wrapped(*orig_args, **orig_kwargs)
        if type(response) == httpx.Response:
            response: httpx.Response = response
            status_code = response.status_code
            headers = response.headers
            stream = response.stream
            extensions = response.extensions
        else:
            (status_code, headers, stream, extensions) = response

        _apply_status_code(span, status_code)

        if response_hook is not None:
            response_hook(
                span,
                request_info,
                ResponseInfo(status_code, headers, stream, extensions),
            )

    return response


class HTTPXClientInstrumentor(BaseInstrumentor):
    # pylint: disable=protected-access,attribute-defined-outside-init
    """An instrumentor for httpx Client and AsyncClient

    See `BaseInstrumentor`
    """

    def instrumentation_dependencies(self) -> typing.Collection[str]:
        return _instruments

    def _instrument(self, **kwargs):
        """Instruments httpx Client and AsyncClient

        Args:
            **kwargs: Optional arguments
                ``tracer_provider``: a TracerProvider, defaults to global
                ``request_hook``: A hook that receives the span and request that is called
                    right after the span is created
                ``response_hook``: A hook that receives the span, request, and response
                    that is called right before the span ends
        """

        request_hook = kwargs.get("request_hook")
        response_hook = kwargs.get("response_hook")
        tracer_provider = kwargs.get("tracer_provider")
        tracer = get_tracer(
            "opentelemetry.instrumentation.httpx",
            instrumenting_library_version=__version__,
            tracer_provider=tracer_provider,
        )

        def sync_wrapper(wrapped, _instance, args, kwargs):
            return wrapped_sync_handle_request(wrapped, args, kwargs, tracer, request_hook, response_hook)

        wrapt.wrap_function_wrapper("httpx", "HTTPTransport.handle_request", sync_wrapper)

        def async_wrapper(wrapped, _instance, args, kwargs):
            return wrapped_async_handle_request(wrapped, args, kwargs, tracer, request_hook, response_hook)

        wrapt.wrap_function_wrapper("httpx", "AsyncHTTPTransport.handle_async_request", async_wrapper)

    def _uninstrument(self, **kwargs):
        unwrap('httpx', 'HTTPTransport.handle_request')
        unwrap('httpx', 'AsyncHTTPTransport.handle_async_request')
