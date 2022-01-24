

import os
import base64

from functools import partial
from six.moves.urllib.parse import urlparse
from twisted.web.client import Agent
from twisted.web.client import ProxyAgent
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.internet.defer import DeferredSemaphore
from treq.client import HTTPClient

from .basemixin import BaseMixin
from .common import HTTPError
from .log import NodeLoggingMixin
from .busy import NodeBusyMixin

from twisted.internet.protocol import Protocol
from twisted.web.client import ResponseDone
from twisted.web.http import PotentialDataLoss
from twisted.internet.defer import Deferred, succeed

from twisted.internet.error import TimeoutError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import ConnectError
from twisted.internet.error import NoRouteError
from twisted.web.client import ResponseNeverReceived
from twisted.web.client import ResponseFailed
from twisted.web.error import SchemeNotSupported

from .shell.network import NetworkInfoMixin

_http_errors = (HTTPError, DNSLookupError, NoRouteError,
                TimeoutError, ConnectError, ResponseNeverReceived)


def swallow_http_error(failure):
    failure.trap(*_http_errors)
    print("Swallowing HTTP Error")


class NoResumeResponseError(Exception):
    def __init__(self, code):
        self.code = code


class DefaultHeadersHttpClient(HTTPClient):
    def __init__(self, *args, **kwargs):
        self._default_headers = kwargs.pop('headers', {})
        super(DefaultHeadersHttpClient, self).__init__(*args, **kwargs)

    def get(self, url, **kwargs):
        simple_headers = kwargs.pop('headers', {})
        simple_headers.update(self._default_headers)
        kwargs['headers'] = simple_headers
        return super(DefaultHeadersHttpClient, self).get(url, **kwargs)

    def post(self, url, **kwargs):
        simple_headers = kwargs.pop('headers', {})
        simple_headers.update(self._default_headers)
        kwargs['headers'] = simple_headers
        return super(DefaultHeadersHttpClient, self).post(url, **kwargs)


class WatchfulBodyCollector(Protocol):
    def __init__(self, finished, collector, chunktimeout, reactor):
        # TODO Reimplement with twisted.protocols.policies.TimeoutMixin
        self.latest_tick = 0
        self.chunktimeout = chunktimeout
        self.reactor = reactor
        self.finished = finished
        self.collector = collector

    def dataReceived(self, data):
        self.collector(data)
        if self.chunktimeout is not None:
            self.latest_tick += 1
            self.reactor.callLater(self.chunktimeout, self.checkTimeout,
                                   self.latest_tick)

    def checkTimeout(self, tick):
        if tick == self.latest_tick:
            # We've really timed out.
            self.transport.loseConnection()

    def connectionLost(self, reason):
        self.latest_tick = 0
        if reason.check(ResponseDone):
            self.finished.callback(None)
        elif reason.check(PotentialDataLoss):
            # http://twistedmatrix.com/trac/ticket/4840
            self.finished.callback(None)
        else:
            self.finished.errback(reason)


def watchful_collect(response, collector, chunktimeout=None, reactor=None):
    if response.length == 0:
        return succeed(None)

    d = Deferred()
    response.deliverBody(
        WatchfulBodyCollector(d, collector, chunktimeout, reactor)
    )
    return d


class HttpClientMixin(NetworkInfoMixin, NodeBusyMixin,
                      NodeLoggingMixin, BaseMixin):
    def __init__(self, *args, **kwargs):
        self._http_headers = {}
        self._http_client = None
        self._http_semaphore = None
        self._http_semaphore_background = None
        self._http_semaphore_download = None
        super(HttpClientMixin, self).__init__(*args, **kwargs)

    def http_get(self, url, **kwargs):
        self.log.debug("Executing HTTP GET Request\n"
                       " to URL {url}\n"
                       " with kwargs {kwargs}", 
                       url=url, kwargs=kwargs)
        deferred_response = self.http_semaphore.run(
            self.http_client.get, url, **kwargs
        )
        deferred_response.addCallbacks(
            self._http_check_response,
            self._deferred_error_passthrough
        )
        deferred_response.addErrback(
            partial(self._http_error_handler, url=url)
        )
        return deferred_response

    def http_post(self, url, **kwargs):
        self.log.debug("Executing HTTP Post Request\n"
                       " to URL {url}\n"
                       " with kwargs {kwargs}",
                       url=url, kwargs=kwargs)
        deferred_response = self.http_semaphore.run(
            self.http_client.post, url, **kwargs
        )

        deferred_response.addCallbacks(
            self._http_check_response,
            self._deferred_error_passthrough
        )

        def _parse_json_response(response):
            self.log.debug("Attempting to extract JSON from response {r}", r=response)
            return response.json()
        deferred_response.addCallbacks(
            _parse_json_response,
            partial(self._http_error_handler, url=url)
        )

        return deferred_response

    def http_download(self, url, dst, semaphore=None, **kwargs):
        if not semaphore:
            semaphore = self.http_semaphore
        deferred_response = semaphore.run(
            self._http_download, url, dst, **kwargs
        )
        return deferred_response

    def _http_download(self, url, dst, **kwargs):
        dst = os.path.abspath(dst)
        # self.log.debug("Starting download {url} to {destination}",
        #                url=url, destination=dst)
        if os.path.isdir(dst):
            fname = os.path.basename(urlparse(url).path)
            dst = os.path.join(dst, fname)

        if not os.path.exists(os.path.split(dst)[0]):
            os.makedirs(os.path.split(dst)[0])

        self.busy_set()

        _clear_partial_file = None
        if os.path.exists(dst + '.partial'):
            csize = os.path.getsize(dst + '.partial')
            deferred_response = self.http_client.get(
                url, headers={'Range': 'bytes={0}-'.format(csize)}, **kwargs
            )
            _clear_partial_file = dst + '.partial'
        else:
            deferred_response = self.http_client.get(url, **kwargs)

        deferred_response.addCallback(self._http_check_response)
        deferred_response.addErrback(self._deferred_error_passthrough)

        deferred_response.addCallback(
            self._http_download_response, destination_path=dst
        )
        deferred_response.addErrback(
            partial(self._http_error_handler, url=url)
        )

        if _clear_partial_file:
            # If a range request resulted in an error, get rid of the partial
            # file so it'll work the next time
            def _eb_clear_partial_file(failure):
                os.remove(_clear_partial_file)
                return failure
            deferred_response.addErrback(_eb_clear_partial_file)

        def _busy_clear(maybe_failure):
            self.busy_clear()
            return maybe_failure
        deferred_response.addBoth(_busy_clear)

        return deferred_response

    def _http_download_response(self, response, destination_path):
        if response.code == 206:
            # TODO Check that the range is actually correct?
            # self.log.debug("Got partial content response for {dst}",
            #                dst=destination_path)
            append = True
        else:
            # self.log.debug("Got full content response for {dst}",
            #                dst=destination_path)
            append = False
        temp_path = destination_path + '.partial'
        if not append:
            destination = open(temp_path, 'wb')
        else:
            destination = open(temp_path, 'ab')
        collectmethod = partial(watchful_collect, chunktimeout=10, reactor=self.reactor)
        d = collectmethod(response, destination.write)

        def _close_download_file(maybe_failure):
            destination.close()
            return maybe_failure
        d.addBoth(_close_download_file)

        def _finalize_successful_download(_):
            os.rename(temp_path, destination_path)
        d.addCallback(_finalize_successful_download)

        return d

    def _http_error_handler(self, failure, url=None):
        self.log.failure("HTTP Connection Failure to {url} : ", failure=failure, url=url)
        failure.trap(HTTPError, DNSLookupError, ResponseNeverReceived, SchemeNotSupported)
        if isinstance(failure.value, HTTPError):
            self.log.warn(
                "Encountered error {e} while trying to {method} {url}",
                e=failure.value.response.code, url=url,
                method=failure.value.response.request.method
            )
        if isinstance(failure.value, DNSLookupError):
            self.log.warn(
                "Got a DNS lookup error for {url}. Check your URL and "
                "internet connection.", url=url
            )
        if isinstance(failure.value, ResponseNeverReceived):
            self.log.warn(
                "Response never received for {url}. Underlying error is {e}",
                url=url, e=failure.value.reasons
            )
        elif isinstance(failure.value, ResponseFailed):
            self.log.warn(
                "Response Failed for {url}. Underlying error is {e}",
                url=url, e=failure.value.reasons
            )
        if isinstance(failure.value, SchemeNotSupported):
            self.log.warn(
                "Got an unsupported scheme for {url}. Check your URL and "
                "try again.", url=url
            )
        return failure

    def _http_check_response(self, response):
        if 400 < response.code < 600:
            self.log.info("Got a HTTP Error\n"
                          "with Response Code : {code}\n"
                          "and Response Headers : {headers}\n",
                          code=response.code, headers=response.headers)

            d = response.content()

            def _log_error_content(r):
                self.log.info("  Got Response Content : {msg}", msg=r)
            d.addCallback(_log_error_content)

            raise HTTPError(response=response)
        return response

    @property
    def http_semaphore(self):
        if self._http_semaphore is None:
            n = self.config.http_max_concurrent_requests
            self._http_semaphore = DeferredSemaphore(n)
            _ = self.http_client
        return self._http_semaphore

    @property
    def http_semaphore_background(self):
        if self._http_semaphore_background is None:
            n = self.config.http_max_background_downloads
            self._http_semaphore_background = DeferredSemaphore(n)
        return self._http_semaphore_background

    @property
    def http_semaphore_download(self):
        if self._http_semaphore_download is None:
            n = self.config.http_max_concurrent_downloads
            self._http_semaphore_download = DeferredSemaphore(n)
        return self._http_semaphore_download

    @property
    def http_client(self):
        if not self._http_client:
            self.log.info("Creating treq HTTPClient")
            # Silence the twisted.web.client._HTTP11ClientFactory
            from twisted.web.client import _HTTP11ClientFactory
            _HTTP11ClientFactory.noisy = False
            if self.config.http_proxy_enabled:
                proxy_endpoint = TCP4ClientEndpoint(self.reactor,
                                                    self.config.http_proxy_host,
                                                    self.config.http_proxy_port)
                agent = ProxyAgent(proxy_endpoint)
                if self.config.http_proxy_user:
                    auth = base64.b64encode(self.config.http_proxy_auth)
                    self._http_headers['Proxy-Authorization'] = ["Basic {0}".format(auth.strip())]
            else:
                agent = Agent(reactor=self.reactor)
            self._http_client = DefaultHeadersHttpClient(agent=agent, headers=self._http_headers)
        return self._http_client

    def stop(self):
        self.log.debug("Closing HTTP client session")
        super(HttpClientMixin, self).stop()
