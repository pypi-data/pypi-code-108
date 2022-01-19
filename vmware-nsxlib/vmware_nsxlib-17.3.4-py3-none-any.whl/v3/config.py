# Copyright 2016  VMware, Inc.
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

from oslo_log import log

from requests import exceptions as requests_exceptions

from vmware_nsxlib.v3 import exceptions as v3_exceptions

LOG = log.getLogger(__name__)


class ExceptionConfig(object):

    def __init__(self):
        # When hit during API call, these exceptions will mark
        # endpoint as DOWN immediately
        # This setting has no effect on keepalive validation
        self.ground_triggers = [requests_exceptions.ConnectionError,
                                requests_exceptions.Timeout]

        # When hit during API call, these exceptions will be
        # retried with next available endpoint
        # When hit during validation, these exception will not
        # mark endpoint as DOWN
        self.retriables = [v3_exceptions.APITransactionAborted,
                           v3_exceptions.CannotConnectToServer,
                           v3_exceptions.ServerBusy]

        # When hit during API call, these exceptions will be retried
        # after the endpoints are regenerated with up-to-date auth
        # credentials / tokens
        self.regenerate_triggers = [v3_exceptions.InvalidCredentials,
                                    v3_exceptions.ClientCertificateNotTrusted,
                                    v3_exceptions.BadXSRFToken]

    def should_ground_endpoint(self, ex):
        for exception in self.ground_triggers:
            if isinstance(ex, exception):
                return True

        return False

    def should_retry(self, ex):
        for exception in self.retriables:
            if isinstance(ex, exception):
                return True

        return False

    def should_regenerate(self, ex):
        for exception in self.regenerate_triggers:
            if isinstance(ex, exception):
                return True

        return False


class NsxLibConfig(object):
    """Class holding all the configuration parameters used by the nsxlib code.

    :param nsx_api_managers: List of IP addresses of the NSX managers.
                             Each IP address should be of the form:
                             [<scheme>://]<ip_address>[:<port>]
                             If scheme is not provided https is used.
                             If port is not provided port 80 is used for http
                             and port 443 for https.
    :param username: User name for the NSX manager
    :param password: Password for the NSX manager
    :param client_cert_provider: None, or ClientCertProvider object.
                             If specified, nsxlib will use client cert auth
                             instead of basic authentication.
    :param insecure: If true, the NSX Manager server certificate is not
                     verified. If false the CA bundle specified via "ca_file"
                     will be used or if unset the "thumbprint" will be used.
                     If "thumbprint" is unset, the default system root CAs
                     will be used.
    :param ca_file: Specify a CA bundle file to use in verifying the NSX
                    Manager server certificate. This option is ignored if
                    "insecure" is set to True. If "insecure" is set to False
                    and "ca_file" is unset, the "thumbprint" will be used.
                    If "thumbprint" is unset, the system root CAs will be
                    used to verify the server certificate.
    :param thumbprint: Specify a thumbprint string to use in verifying the
                       NSX Manager server certificate. This option is ignored
                       if "insecure" is set to True or "ca_file" is defined.
    :param token_provider: None, or instance of implemented AbstractJWTProvider
                           which will return the JSON Web Token used in the
                           requests in NSX for authorization.

    :param concurrent_connections: Maximum concurrent connections to each NSX
                                   manager.
    :param retries: Maximum number of times to retry a HTTP connection.
    :param http_timeout: The time in seconds before aborting a HTTP connection
                         to a NSX manager.
    :param http_read_timeout: The time in seconds before aborting a HTTP read
                              response from a NSX manager.
    :param conn_idle_timeout: The amount of time in seconds to wait before
                              ensuring connectivity to the NSX manager if no
                              manager connection has been used.
    :param http_provider: HTTPProvider object, or None.

    :param max_attempts: Maximum number of times to retry API requests upon
                         stale revision errors.

    :param plugin_scope: The default scope for the v3 api-version tag
    :param plugin_tag: The value for the v3 api-version tag
    :param plugin_ver: The version of the plugin used as the 'os-api-version'
                       tag value in the v3 api-version tag
    :param dns_nameservers: List of nameservers to configure for the DHCP
                            binding entries. These will be used if there are
                            no nameservers defined on the subnet.
    :param dns_domain: Domain to use for building the hostnames.
    :param allow_overwrite_header: If True, a default header of
                                   X-Allow-Overwrite:true will be added to all
                                   the requests, to allow admin user to update/
                                   delete all entries.
    :param rate_limit_retry: If True, the client will retry requests failed on
           "Too many requests" error.
    :param cluster_unavailable_retry: If True, skip fatal errors when no
                                      endpoint in the NSX management cluster is
                                      available to serve a request, and retry
                                      the request instead. This setting can
                                      not be False if single endpoint is
                                      configured in the cluster, since there
                                      will be no keepalive probes in this
                                      case.
    :param api_rate_limit_per_endpoint: If set to positive integer, API calls
                                        sent to each endpoint will be limited
                                        to a max rate of this value per second.
                                        The rate limit is not enforced on
                                        connection validations. This option
                                        defaults to None, which disables rate
                                        limit.
    :param api_rate_mode: Algorithm used to adaptively adjust max API rate
                          limit. If not set, the max rate will not be
                          automatically changed. If set to 'AIMD', max API
                          rate will be increase by 1 after successful calls
                          that was blocked before sent, and will be decreased
                          by half after 429/503 error for each period.
                          The rate has hard max limit of min(100/s, param
                          api_rate_limit_per_endpoint).
    :param api_log_mode: Option to collect API call logs within nsxlib.
                         When set to API_LOG_PER_CLUSTER, API calls sent to all
                         endpoints will be collected at one place.
                         When set to API_LOG_PER_ENDPOINT, API calls sent to
                         each endpoint will be collected individually.
                         By default, this option is disabled as set to None.
    :param enable_health_check: Options to enable or disable health check for
                                all endpoints when initializing cluster API.
                                The checking including endpoint connection
                                validation and health check loop.
                                For some condition, eg election process. It
                                does not need to check the endpoint's
                                accessibility.
                                By default, this option is set to True.

    -- Additional parameters which are relevant only for the Policy manager:
    :param allow_passthrough: If True, use nsx manager api for cases which are
                              not supported by the policy manager api.
    :param realization_max_attempts: Maximum number of times to retry while
                                     waiting for a resource to be realized.
    :param realization_wait_sec: Number of seconds to wait between attempts
                                 for a resource to be realized.
    """

    def __init__(self,
                 nsx_api_managers=None,
                 username=None,
                 password=None,
                 client_cert_provider=None,
                 insecure=True,
                 ca_file=None,
                 thumbprint=None,
                 token_provider=None,
                 concurrent_connections=10,
                 retries=3,
                 http_timeout=10,
                 http_read_timeout=180,
                 conn_idle_timeout=10,
                 http_provider=None,
                 max_attempts=10,
                 plugin_scope=None,
                 plugin_tag=None,
                 plugin_ver=None,
                 dns_nameservers=None,
                 dns_domain='openstacklocal',
                 allow_overwrite_header=False,
                 rate_limit_retry=True,
                 cluster_unavailable_retry=False,
                 allow_passthrough=False,
                 realization_max_attempts=50,
                 realization_wait_sec=1.0,
                 api_rate_limit_per_endpoint=None,
                 api_rate_mode=None,
                 exception_config=None,
                 api_log_mode=None,
                 enable_health_check=True):

        self.nsx_api_managers = nsx_api_managers
        self._username = username
        self._password = password
        self._ca_file = ca_file
        self._thumbprint = thumbprint
        self.insecure = insecure
        self.concurrent_connections = concurrent_connections
        self.retries = retries
        self.http_timeout = http_timeout
        self.http_read_timeout = http_read_timeout
        self.conn_idle_timeout = conn_idle_timeout
        self.http_provider = http_provider
        self.client_cert_provider = client_cert_provider
        self.token_provider = token_provider
        self.max_attempts = max_attempts
        self.plugin_scope = plugin_scope
        self.plugin_tag = plugin_tag
        self.plugin_ver = plugin_ver
        self.dns_nameservers = dns_nameservers or []
        self.dns_domain = dns_domain
        self.allow_overwrite_header = allow_overwrite_header
        self.rate_limit_retry = rate_limit_retry
        self.cluster_unavailable_retry = cluster_unavailable_retry
        self.allow_passthrough = allow_passthrough
        self.realization_max_attempts = realization_max_attempts
        self.realization_wait_sec = realization_wait_sec
        self.api_rate_limit_per_endpoint = api_rate_limit_per_endpoint
        self.api_rate_mode = api_rate_mode
        self.exception_config = exception_config or ExceptionConfig()
        self.api_log_mode = api_log_mode
        self.enable_health_check = enable_health_check

        if len(nsx_api_managers) == 1 and not self.cluster_unavailable_retry:
            LOG.warning("When only one endpoint is provided, keepalive probes"
                        " are disabled. For the system to be able to recover"
                        " from DOWN state, cluster_unavailable_retry is set"
                        " to True, overriding provided configuration")
            self.cluster_unavailable_retry = True

        if len(nsx_api_managers) > self.max_attempts:
            LOG.warning("max_attempts setting (%d) is lower than amount of"
                        " endpoints (%d), which means that not all endpoints"
                        " will be probed in case of retriable error",
                        self.max_attempts, len(nsx_api_managers))

    def extend(self, keepalive_section, validate_connection_method=None,
               url_base=None):
        if keepalive_section or validate_connection_method:
            LOG.warning("keepalive_section and validate_connection_method are"
                        " no longer used to conduct keepalive probes. For"
                        " most efficient keepalive roundtrip, proxy health"
                        " API is always used.")
        self.url_base = url_base

    def _attribute_by_index(self, scalar_or_list, index):
        if isinstance(scalar_or_list, list):
            if not len(scalar_or_list):
                return None
            if len(scalar_or_list) > index:
                return scalar_or_list[index]
            # if not long enough - use the first one as default
            return scalar_or_list[0]
        # this is a scalar
        return scalar_or_list

    def username(self, index):
        return self._attribute_by_index(self._username, index)

    def password(self, index):
        return self._attribute_by_index(self._password, index)

    def ca_file(self, index):
        return self._attribute_by_index(self._ca_file, index)

    def thumbprint(self, index):
        return self._attribute_by_index(self._thumbprint, index)
