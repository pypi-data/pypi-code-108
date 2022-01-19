# Copyright 2015 VMware, Inc.
# All Rights Reserved
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#

import abc
import contextlib
import copy
import datetime
import inspect
import itertools
import logging
import re
import time
from urllib import parse as urlparse

import urllib3

import eventlet
from eventlet import greenpool
from eventlet import pools
import OpenSSL
from oslo_log import log
from oslo_service import loopingcall
import requests
from requests import adapters

from vmware_nsxlib._i18n import _
from vmware_nsxlib.v3 import client as nsx_client
from vmware_nsxlib.v3 import constants
from vmware_nsxlib.v3 import exceptions
from vmware_nsxlib.v3 import utils


LOG = log.getLogger(__name__)

# disable warning message for each HTTP retry
logging.getLogger(
    "urllib3.connectionpool").setLevel(logging.ERROR)

# Hide the InsecureRequestWarning from urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class AbstractHTTPProvider(object, metaclass=abc.ABCMeta):
    """Interface for providers of HTTP connections.

    which are responsible for creating and validating connections
    for their underlying HTTP support.
    """
    @property
    def default_scheme(self):
        return 'https'

    @abc.abstractproperty
    def provider_id(self):
        """A unique string name for this provider."""
        pass

    @abc.abstractmethod
    def new_connection(self, cluster_api, provider):
        """Create a new http connection.

        Create a new http connection for the said cluster and
        cluster provider. The actual connection should duck type
        requests.Session http methods (get(), put(), etc.).
        """
        pass


class TimeoutSession(requests.Session):
    """Extends requests.Session to support timeout at the session level."""

    def __init__(self, timeout, read_timeout):
        self.timeout = timeout
        self.read_timeout = read_timeout
        self.cert_provider = None
        self._silent = False
        super(TimeoutSession, self).__init__()

    @property
    def cert_provider(self):
        return self._cert_provider

    @cert_provider.setter
    def cert_provider(self, value):
        self._cert_provider = value

    def set_silent(self, silent_mode):
        self._silent = silent_mode

    # wrapper timeouts at the session level
    # see: https://goo.gl/xNk7aM
    def request(self, *args, **kwargs):
        def request_with_retry_on_ssl_error(*args, **kwargs):
            try:
                return super(TimeoutSession, self).request(*args, **kwargs)
            except (IOError, OpenSSL.SSL.Error):
                # This can happen when connection tries to access certificate
                # file it was opened with (renegotiation?)
                # Proper way to solve this would be to pass in-memory cert
                # to ssl C code.
                # Retrying here works around the problem
                return super(TimeoutSession, self).request(*args, **kwargs)

        def get_cert_provider():
            if inspect.isclass(self._cert_provider):
                # If client provided certificate provider as a class,
                # we spawn an instance here
                return self._cert_provider()
            return self._cert_provider

        if 'timeout' not in kwargs:
            kwargs['timeout'] = (self.timeout, self.read_timeout)
        if not self.cert_provider:
            # No client certificate needed
            return super(TimeoutSession, self).request(*args, **kwargs)

        if self.cert is not None:
            # Recursive call - shouldn't happen
            return request_with_retry_on_ssl_error(*args, **kwargs)

        # The following with statement allows for preparing certificate and
        # private key file and dispose it at the end of request
        # (since PK is sensitive information, immediate disposal is
        # important).
        # It would be optimal to populate certificate once per connection,
        # per request. Unfortunately requests library verifies cert file
        # existence regardless of whether certificate is going to be used
        # for this request.
        # Optimal solution for this would be to expose certificate as variable
        # and not as a file to the SSL library
        with get_cert_provider() as provider:
            self.cert = provider.filename()
            try:
                ret = request_with_retry_on_ssl_error(*args, **kwargs)
            except Exception as e:
                self.cert = None
                raise e

            self.cert = None

        return ret


class NSXRequestsHTTPProvider(AbstractHTTPProvider):
    """Concrete implementation of AbstractHTTPProvider.

    using requests.Session() as the underlying connection.
    """

    SESSION_CREATE_URL = '/api/session/create'
    COOKIE_FIELD = 'Cookie'
    SET_COOKIE_FIELD = 'Set-Cookie'
    XSRF_TOKEN = 'X-XSRF-TOKEN'
    JSESSIONID = 'JSESSIONID'

    @property
    def provider_id(self):
        return "%s-%s" % (requests.__title__, requests.__version__)

    def validate_connection(self, cluster_api, endpoint, conn):
        # Retry during validation can cause retry storm, thus limit
        # max_attempts to 1
        # on connection level, validation will be retried according to
        # nsxlib 'retries' and 'http_timeout' parameters.
        client = nsx_client.NSX3Client(
            conn, url_prefix=endpoint.provider.url,
            url_path_base=nsx_client.NSX3Client.NSX_V1_API_PREFIX,
            default_headers=conn.default_headers,
            max_attempts=1)

        # Try to get the status silently and with no retries
        status = client.get('reverse-proxy/node/health',
                            silent=True, with_retries=False)
        if not status or not status.get('healthy', False):
            msg = _("NSX Node is not healthy, reported status: %s") % status
            LOG.warning(msg)
            raise exceptions.ResourceNotFound(
                manager=endpoint.provider.url, operation=msg)

    def new_connection(self, cluster_api, provider):
        config = cluster_api.nsxlib_config
        session = TimeoutSession(config.http_timeout,
                                 config.http_read_timeout)
        if config.client_cert_provider:
            session.cert_provider = config.client_cert_provider
        # Set the headers with Auth info when token provider is set,
        # otherwise set the username and password
        elif not config.token_provider:
            session.auth = (provider.username, provider.password)

        # NSX v3 doesn't use redirects
        session.max_redirects = 0

        if config.insecure:
            # no verification on server certificate
            session.verify = False
            thumbprint = None
        elif provider.ca_file:
            # verify using the said ca bundle path
            session.verify = provider.ca_file
            thumbprint = None
        elif provider.thumbprint:
            # verify using the thumbprint
            session.verify = None
            thumbprint = provider.thumbprint
        else:
            # verify using the default system root CAs
            session.verify = True
            thumbprint = None

        # we are pooling with eventlet in the cluster class
        adapter = NSXHTTPAdapter(
            pool_connections=1, pool_maxsize=1,
            max_retries=config.retries,
            pool_block=False, thumbprint=thumbprint)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        self.get_default_headers(session, provider,
                                 config.allow_overwrite_header,
                                 config.token_provider)
        return session

    def get_default_headers(self, session, provider, allow_overwrite_header,
                            token_provider=None):
        """Get the default headers that should be added to future requests"""
        session.default_headers = {}

        # Add allow-overwrite if configured
        if allow_overwrite_header:
            session.default_headers['X-Allow-Overwrite'] = 'true'

        if session.cert_provider:
            # Session create will fail with cert provider
            LOG.debug("Skipping session create with client certificate auth")
            return

        # Perform the initial session create and get the relevant jsessionid &
        # X-XSRF-TOKEN for future requests
        req_data = ''
        req_headers = {'Accept': 'application/json',
                       'Content-Type': 'application/x-www-form-urlencoded'}
        # Insert the JWT in Auth header if using tokens for auth
        if token_provider:
            try:
                token_value = token_provider.get_token()
                bearer_token = token_provider.get_header_value(token_value)
                token_header = {"Authorization": bearer_token}
                session.default_headers.update(token_header)
                # Don't call /api/session/create when using
                # JWT Token Based Principal Identity auth scheme
                LOG.debug("Skipping session create with JWT based auth")
                return
            except exceptions.BadJSONWebTokenProviderRequest as e:
                LOG.error("Session create failed for endpoint %s due to "
                          "error in retrieving JSON Web Token: %s",
                          provider.url, e)
        else:
            # With client certificate authentication, username and password
            # may not be provided.
            # If provided, backend treats these credentials as authentication
            # and ignores client cert as principal identity indication.
            req_data = 'j_username=%s&j_password=%s' % (provider.username,
                                                        provider.password)
        # Cannot use the certificate at this stage, because it is used for
        # the certificate generation
        try:
            resp = session.request(
                'post', provider.url + self.SESSION_CREATE_URL,
                data=req_data, headers=req_headers)
        except Exception as e:
            # Error 403 might be because the backend does not support this for
            # all versions.
            LOG.warning("Session create failed for endpoint %s with error %s",
                        provider.url, e)
        else:
            if resp.status_code != 200 and resp.status_code != 201:
                LOG.warning("Session create failed for endpoint %s with "
                            "response %s, error message: %s, "
                            "local NSX time: %s",
                            provider.url, resp.status_code,
                            resp.json().get('error_message'),
                            resp.headers['Date'])
                # this may will later cause the endpoint to be Down
            else:
                for header_name in resp.headers:
                    if self.SET_COOKIE_FIELD.lower() == header_name.lower():
                        m = re.match(r'%s=.*?\;' % self.JSESSIONID,  # noqa
                                     resp.headers[header_name])
                        if m:
                            session.default_headers[self.COOKIE_FIELD] = (
                                m.group())
                    if self.XSRF_TOKEN.lower() == header_name.lower():
                        session.default_headers[self.XSRF_TOKEN] = (
                            resp.headers[header_name])
                LOG.info("Session create succeeded for endpoint %(url)s with "
                         "headers %(hdr)s",
                         {'url': provider.url,
                          'hdr':
                          utils.censor_headers(session.default_headers)})


class NSXHTTPAdapter(adapters.HTTPAdapter):
    def __init__(self, *args, **kwargs):
        self.thumbprint = kwargs.pop("thumbprint", None)
        super(NSXHTTPAdapter, self).__init__(*args, **kwargs)

    def init_poolmanager(self, *args, **kwargs):
        if self.thumbprint:
            kwargs["assert_fingerprint"] = self.thumbprint
        super(NSXHTTPAdapter, self).init_poolmanager(*args, **kwargs)


class ClusterHealth(object):
    """Indicator of overall cluster health.

    with respect to the connectivity of the clusters managed endpoints.
    """
    # all endpoints are UP
    GREEN = 'GREEN'
    # at least 1 endpoint is UP, but 1 or more are DOWN
    ORANGE = 'ORANGE'
    # all endpoints are DOWN
    RED = 'RED'


class EndpointState(object):
    """Tracks the connectivity state for a said endpoint."""
    # no UP or DOWN state recorded yet
    INITIALIZED = 'INITIALIZED'
    # endpoint has been validate and is good
    UP = 'UP'
    # endpoint can't be reached or validated
    DOWN = 'DOWN'


class Provider(object):
    """Data holder for a provider

    Which has a unique id a connection URL, and the credential details.
    """

    def __init__(self, provider_id, provider_url, username, password, ca_file,
                 thumbprint=None):
        self.id = provider_id
        self.url = provider_url
        self.username = username
        self.password = password
        self.ca_file = ca_file
        self.thumbprint = thumbprint

    def __str__(self):
        return str(self.url)


class Endpoint(object):
    """A single NSX manager endpoint (host).

    A single NSX manager endpoint (host) which includes
    related information such as the endpoint's provider,
    state, etc.. A pool is used to hold connections to the
    endpoint which are doled out when proxying HTTP methods
    to the underlying connections.
    """

    def __init__(self, provider, pool, api_rate_limit=None,
                 api_rate_mode=None, api_call_collector=None):
        self.provider = provider
        self.pool = pool
        self._state = EndpointState.INITIALIZED
        self._last_updated = datetime.datetime.now()
        if api_rate_mode == constants.API_RATE_MODE_AIMD:
            self.rate_limiter = utils.APIRateLimiterAIMD(
                max_calls=api_rate_limit)
        else:
            self.rate_limiter = utils.APIRateLimiter(max_calls=api_rate_limit)
        self.api_call_collector = api_call_collector

    def regenerate_pool(self):
        self.pool = pools.Pool(min_size=self.pool.min_size,
                               max_size=self.pool.max_size,
                               order_as_stack=True,
                               create=self.pool.create)

    @property
    def last_updated(self):
        return self._last_updated

    @property
    def state(self):
        return self._state

    def set_state(self, state):
        if self.state != state:
            LOG.info("Endpoint '%(ep)s' changing from state"
                     " '%(old)s' to '%(new)s'",
                     {'ep': self.provider,
                      'old': self.state,
                      'new': state})
        old_state = self._state
        self._state = state

        self._last_updated = datetime.datetime.now()

        return old_state

    def add_api_record(self, record):
        if self.api_call_collector:
            self.api_call_collector.add_record(record)

    def pop_all_api_records(self):
        if self.api_call_collector:
            return self.api_call_collector.pop_all_records()
        return []

    def __str__(self):
        return "[%s] %s" % (self.state, self.provider)


class EndpointConnection(object):
    """Simple data holder

    Which contains an endpoint and a connection for that endpoint.
    """

    def __init__(self, endpoint, connection, conn_wait, rate_wait):
        self.endpoint = endpoint
        self.connection = connection
        self.conn_wait = conn_wait
        self.rate_wait = rate_wait


class ClusteredAPI(object):
    """Duck types the major HTTP based methods of a requests.Session

    Such as get(), put(), post(), etc.
    and transparently proxies those calls to one of
    its managed NSX manager endpoints.
    """
    _HTTP_VERBS = ['get', 'delete', 'head', 'put', 'post', 'patch', 'create']

    def __init__(self, providers,
                 http_provider,
                 min_conns_per_pool=0,
                 max_conns_per_pool=20,
                 keepalive_interval=33,
                 api_rate_limit=None,
                 api_rate_mode=None,
                 api_log_mode=None,
                 enable_health_check=True):

        self._http_provider = http_provider
        self._keepalive_interval = keepalive_interval
        self._print_keepalive = 0
        self._silent = False
        self._api_call_collectors = []
        self._enable_health_check = enable_health_check

        def _init_cluster(*args, **kwargs):
            self._init_endpoints(providers, min_conns_per_pool,
                                 max_conns_per_pool, api_rate_limit,
                                 api_rate_mode, api_log_mode,
                                 enable_health_check)

        _init_cluster()

        # keep this internal method for reinitialize upon fork
        # for api workers to ensure each process has its own keepalive
        # loops + state
        self._reinit_cluster = _init_cluster

    def set_silent(self, silent_mode):
        self._silent = silent_mode

    def _init_endpoints(self, providers, min_conns_per_pool,
                        max_conns_per_pool, api_rate_limit, api_rate_mode,
                        api_log_mode, enable_health_check=True):
        LOG.debug("Initializing API endpoints")

        def _create_conn(p):
            def _conn():
                return self._http_provider.new_connection(self, p)

            return _conn

        self._api_call_collectors = []
        api_call_collector = None
        if api_log_mode == constants.API_CALL_LOG_PER_CLUSTER:
            # Init one instance of collector for the entire cluster
            api_call_collector = utils.APICallCollector(
                ",".join([provider.id for provider in providers]))
            self._api_call_collectors.append(api_call_collector)

        self._endpoints = {}
        for provider in providers:
            pool = pools.Pool(
                min_size=min_conns_per_pool,
                max_size=max_conns_per_pool,
                order_as_stack=True,
                create=_create_conn(provider))

            if api_log_mode == constants.API_CALL_LOG_PER_ENDPOINT:
                # Init one instance of collector for each endpoint
                api_call_collector = utils.APICallCollector(provider.id)
                self._api_call_collectors.append(api_call_collector)

            endpoint = Endpoint(provider, pool, api_rate_limit, api_rate_mode,
                                api_call_collector)
            self._endpoints[provider.id] = endpoint

        # service requests using round robin
        self._endpoint_schedule = itertools.cycle(self._endpoints.values())

        # duck type to proxy http invocations
        for method in ClusteredAPI._HTTP_VERBS:
            setattr(self, method, self._proxy_stub(method))
        # If health check is disabled, skip endpoint accessiblity check
        # and health check loop. Set api health to GREEN.
        if enable_health_check:
            conns = greenpool.GreenPool()
            for endpoint in self._endpoints.values():
                conns.spawn(self._validate, endpoint)
            eventlet.sleep(0)
            while conns.running():
                if (self.health == ClusterHealth.GREEN or
                    self.health == ClusterHealth.ORANGE):
                    # only wait for 1 or more endpoints to reduce init time
                    break
                eventlet.sleep(0.5)

            if len(self._endpoints) > 1:
                # We don't monitor connectivity when one endpoint is available,
                # since there is no alternative to querying this single backend
                # If endpoint was down, we can tolerate extra roundtrip to
                # validate connectivity
                for endpoint in self._endpoints.values():
                    # dynamic loop for each endpoint to ensure connectivity
                    loop = loopingcall.DynamicLoopingCall(
                        self._endpoint_keepalive, endpoint)
                    loop.start(initial_delay=self._keepalive_interval,
                               periodic_interval_max=self._keepalive_interval,
                               stop_on_exception=False)
        else:
            for endpoint in self._endpoints.values():
                endpoint.set_state(EndpointState.UP)

        LOG.debug("Done initializing API endpoint(s). "
                  "API cluster health: %s", self.health)

    def _endpoint_keepalive(self, endpoint):
        delta = datetime.datetime.now() - endpoint.last_updated
        if delta.seconds >= self._keepalive_interval:
            # TODO(boden): backoff on validation failure
            if self._print_keepalive % 10 == 0:
                # Print keepalive debug message once every 10 probes
                LOG.debug("Running keepalive probe for cluster endpoint "
                          "'%(ep)s' ",
                          {'ep': endpoint})
            self._print_keepalive += 1

            self._validate(endpoint)
            return self._keepalive_interval
        return self._keepalive_interval - delta.seconds

    @property
    def providers(self):
        return [ep.provider for ep in self._endpoints.values()]

    @property
    def endpoints(self):
        return copy.copy(self._endpoints)

    @property
    def http_provider(self):
        return self._http_provider

    @property
    def api_call_collectors(self):
        return self._api_call_collectors

    @property
    def health(self):
        down = 0
        up = 0
        for endpoint in self._endpoints.values():
            if endpoint.state != EndpointState.UP:
                down += 1
            else:
                up += 1

        if down == len(self._endpoints):
            return ClusterHealth.RED
        return (ClusterHealth.GREEN
                if up == len(self._endpoints)
                else ClusterHealth.ORANGE)

    def _validate(self, endpoint):
        try:
            with endpoint.pool.item() as conn:
                # with some configurations, validation will be skipped
                self._http_provider.validate_connection(self,
                                                        endpoint,
                                                        conn)
                endpoint.set_state(EndpointState.UP)
        except Exception as e:
            if self.nsxlib_config.exception_config.should_regenerate(e):
                LOG.warning("Failed to validate API cluster endpoint "
                            "'%(ep)s' due to an exception that calls for "
                            "regeneration. Re-generating pool.",
                            {'ep': endpoint})
                if bool(self.nsxlib_config.token_provider):
                    # get new jwt token for authentication
                    self.nsxlib_config.token_provider.get_token(
                        refresh_token=True)
                # refresh endpoint with new headers that have updated token
                endpoint.regenerate_pool()
                return
            elif self.nsxlib_config.exception_config.should_retry(e):
                LOG.info("Exception is retriable, endpoint stays UP")
                endpoint.set_state(EndpointState.UP)
            else:
                endpoint.set_state(EndpointState.DOWN)

            LOG.warning("Failed to validate API cluster endpoint "
                        "'%(ep)s' due to: %(err)s",
                        {'ep': endpoint, 'err': e})

    def _select_endpoint(self):
        """Return an endpoint in UP state.

        Go over all endpoint and return the next one which is UP
        If all endpoints are currently DOWN, depending on the configuration
        retry it until one is UP (or max retries exceeded)
        """
        def _select_endpoint_internal(refresh=False):
            # check for UP state until exhausting all endpoints
            seen, total = 0, len(self._endpoints.values())
            while seen < total:
                endpoint = next(self._endpoint_schedule)
                if refresh:
                    self._validate(endpoint)
                if endpoint.state == EndpointState.UP:
                    return endpoint
                seen += 1

        # First attempt to get an UP endpoint
        endpoint = _select_endpoint_internal()
        if endpoint or not self.nsxlib_config.cluster_unavailable_retry:
            return endpoint

        # Retry the selection while refreshing the endpoints state
        return _select_endpoint_internal(refresh=True)

    def endpoint_for_connection(self, conn):
        # check all endpoint pools
        for endpoint in self._endpoints.values():
            if (conn in endpoint.pool.channel.queue or
                    conn in endpoint.pool.free_items):
                return endpoint

    @property
    def cluster_id(self):
        return ','.join([str(ep.provider.url)
                         for ep in self._endpoints.values()])

    @contextlib.contextmanager
    def connection(self):
        with self.endpoint_connection() as conn_data:
            yield conn_data.connection

    @contextlib.contextmanager
    def endpoint_connection(self):
        endpoint = self._select_endpoint()
        if not endpoint:
            LOG.debug("All endpoints down for: %s" %
                      [str(ep) for ep in self._endpoints.values()])
            # all endpoints are DOWN and will have their next
            # state updated as per _endpoint_keepalive()
            raise exceptions.ServiceClusterUnavailable(
                cluster_id=self.cluster_id)

        if endpoint.pool.free() == 0:
            LOG.info("API endpoint %(ep)s at connection "
                     "capacity %(max)s and has %(waiting)s waiting",
                     {'ep': endpoint,
                      'max': endpoint.pool.max_size,
                      'waiting': endpoint.pool.waiting()})
            conn_wait_start = time.time()
        else:
            conn_wait_start = None
        # pool.item() will wait if pool has 0 free
        with endpoint.pool.item() as conn:
            if conn_wait_start:
                conn_wait = time.time() - conn_wait_start
            else:
                conn_wait = 0
            with endpoint.rate_limiter as rate_wait:
                # Connection validation calls are not currently rate-limited
                # by this context manager.
                # This should be fine as validation api calls are sent in a
                # slow rate at once per 33 seconds by default.
                yield EndpointConnection(endpoint, conn, conn_wait, rate_wait)

    def _raise_http_exception_if_needed(self, response, endpoint):
        # We need to inspect http codes to understand whether
        # this error is relevant for endpoint-level decisions, such
        # as ground endpoint or retry with next endpoint
        exc = nsx_client.init_http_exception_from_response(response)
        if not exc:
            # This exception is irrelevant for endpoint decisions
            return

        if self.nsxlib_config.exception_config.should_regenerate(exc):
            if bool(self.nsxlib_config.token_provider):
                # get new jwt token for authentication
                self.nsxlib_config.token_provider.get_token(
                    refresh_token=True)
            # refresh endpoint so that it gets new header with updated token
            endpoint.regenerate_pool()
            raise exc

        exc_config = self.nsxlib_config.exception_config
        if (exc_config.should_ground_endpoint(exc) or
            exc_config.should_retry(exc)):
            raise exc

    def _proxy_stub(self, proxy_for):
        def _call_proxy(url, *args, **kwargs):
            try:
                return self._proxy(proxy_for, url, *args, **kwargs)
            except Exception as ex:
                # If this was exception that grounded the cluster,
                # we want to translate this exception to
                # ServiceClusterUnavailable. This is in order to
                # provide unified "cluster down" experience for
                # the client
                exc_config = self.nsxlib_config.exception_config
                if exc_config.should_ground_endpoint(ex):
                    raise exceptions.ServiceClusterUnavailable(
                        cluster_id=self.cluster_id)

                raise ex

        return _call_proxy

    def _proxy(self, proxy_for, uri, *args, **kwargs):

        @utils.retry_random_upon_exception_result(
            max_attempts=self.nsxlib_config.max_attempts)
        def _proxy_internal(proxy_for, uri, *args, **kwargs):
            # proxy http request call to an avail endpoint
            with self.endpoint_connection() as conn_data:
                conn = conn_data.connection
                endpoint = conn_data.endpoint

                # http conn must support requests style interface
                do_request = getattr(conn, proxy_for)

                if not uri.startswith('/'):
                    uri = "/%s" % uri
                url = "%s%s" % (endpoint.provider.url, uri)
                try:
                    # Add the connection default headers
                    if conn.default_headers:
                        kwargs['headers'] = kwargs.get('headers', {})
                        kwargs['headers'].update(conn.default_headers)
                    if not self._silent:
                        # To censor sensitive headers before logging
                        kwargs_copy = copy.copy(kwargs)
                        kwargs_copy['headers'] = utils.censor_headers(
                            kwargs_copy['headers'])
                        LOG.debug("[%x] API cluster proxy %s %s to %s "
                                  "with %s. Waited conn: %2.4f, rate: %2.4f",
                                  id(conn), proxy_for.upper(), uri, url,
                                  kwargs_copy, conn_data.conn_wait,
                                  conn_data.rate_wait)

                    # call the actual connection method to do the
                    # http request/response over the wire
                    response = do_request(url, *args, **kwargs)
                    endpoint.set_state(EndpointState.UP)

                    # add api call log
                    api_record = utils.APICallRecord(
                        verb=proxy_for, uri=uri, status=response.status_code,
                        provider=endpoint.provider.id)
                    endpoint.add_api_record(api_record)

                    # Adjust API Rate Limit before raising HTTP exception
                    endpoint.rate_limiter.adjust_rate(
                        wait_time=conn_data.rate_wait,
                        status_code=response.status_code)

                    # for some status codes, we need to bring the cluster
                    # down or retry API call
                    self._raise_http_exception_if_needed(response, endpoint)

                    return response
                except Exception as e:
                    LOG.warning("[%x] Request failed due to: %s", id(conn), e)
                    exc_config = self.nsxlib_config.exception_config
                    if exc_config.should_ground_endpoint(e):
                        # consider endpoint inaccessible and move to next
                        # endpoint
                        endpoint.set_state(EndpointState.DOWN)

                    elif not exc_config.should_retry(e):
                        LOG.info("Exception %s is configured as not retriable",
                                 e)
                        raise e

                    # Returning the exception instead of raising it will cause
                    # decorator to retry. If retry attempts is exceeded, this
                    # same exception will be raised due to overriden reraise
                    # method of RetryAttemptsExceeded
                    return e

        return _proxy_internal(proxy_for, uri, *args, **kwargs)


class NSXClusteredAPI(ClusteredAPI):
    """Extends ClusteredAPI to get conf values and setup the NSXv3 cluster."""

    def __init__(self, nsxlib_config):
        self.nsxlib_config = nsxlib_config

        self._http_provider = (nsxlib_config.http_provider or
                               NSXRequestsHTTPProvider())

        super(NSXClusteredAPI, self).__init__(
            self._build_conf_providers(),
            self._http_provider,
            max_conns_per_pool=self.nsxlib_config.concurrent_connections,
            keepalive_interval=self.nsxlib_config.conn_idle_timeout,
            api_rate_limit=self.nsxlib_config.api_rate_limit_per_endpoint,
            api_rate_mode=self.nsxlib_config.api_rate_mode,
            api_log_mode=self.nsxlib_config.api_log_mode,
            enable_health_check=self.nsxlib_config.enable_health_check)

        LOG.debug("Created NSX clustered API with '%s' "
                  "provider", self._http_provider.provider_id)

    def _build_conf_providers(self):

        def _schemed_url(uri):
            uri = uri.strip('/')
            return urlparse.urlparse(
                uri if uri.startswith('http') else
                "%s://%s" % (self._http_provider.default_scheme, uri))

        conf_urls = self.nsxlib_config.nsx_api_managers[:]
        urls = []
        providers = []
        provider_index = -1
        for conf_url in conf_urls:
            provider_index += 1
            conf_url = _schemed_url(conf_url)
            if conf_url in urls:
                LOG.warning("'%s' already defined in configuration file. "
                            "Skipping.", urlparse.urlunparse(conf_url))
                continue
            urls.append(conf_url)
            providers.append(
                Provider(
                    conf_url.netloc,
                    urlparse.urlunparse(conf_url),
                    self.nsxlib_config.username(provider_index),
                    self.nsxlib_config.password(provider_index),
                    self.nsxlib_config.ca_file(provider_index),
                    self.nsxlib_config.thumbprint(provider_index)))
        return providers
