# Copyright (c) 2013 Qumulo, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

from typing import Mapping, Optional

import qumulo.lib.request as request

from qumulo.lib.auth import Credentials
from qumulo.lib.request import Connection, RestResponse


@request.request
def get_config(conninfo: Connection, credentials: Optional[Credentials]) -> RestResponse:
    method = 'GET'
    uri = '/v1/support/settings'

    return request.rest_request(conninfo, credentials, method, uri)


# pylint: disable=unused-argument
@request.request
def set_config(
    conninfo: Connection,
    credentials: Optional[Credentials],
    enabled: Optional[bool] = None,
    mq_host: Optional[str] = None,
    mq_port: Optional[int] = None,
    mq_proxy_host: Optional[str] = None,
    mq_proxy_port: Optional[int] = None,
    s3_proxy_host: Optional[str] = None,
    s3_proxy_port: Optional[int] = None,
    s3_proxy_disable_https: Optional[bool] = None,
    period: Optional[int] = None,
    vpn_host: Optional[str] = None,
    vpn_enabled: Optional[bool] = None,
) -> RestResponse:
    method = 'PATCH'
    uri = '/v1/support/settings'

    config = {}
    for field in [
        'enabled',
        'mq_host',
        'mq_port',
        'mq_proxy_host',
        'mq_proxy_port',
        's3_proxy_host',
        's3_proxy_port',
        's3_proxy_disable_https',
        'period',
        'vpn_host',
        'vpn_enabled',
    ]:
        if locals().get(field) is not None:
            config[field] = locals().get(field)

    return request.rest_request(conninfo, credentials, method, uri, body=config)


@request.request
def get_monitoring_status(conninfo: Connection, credentials: Optional[Credentials]) -> RestResponse:
    method = 'GET'
    uri = '/v1/support/status/'

    return request.rest_request(conninfo, credentials, method, uri)


@request.request
def put_local_monitoring_status(
    conninfo: Connection, credentials: Optional[Credentials], status: Mapping[str, str]
) -> RestResponse:
    method = 'PUT'
    uri = '/v1/support/status/local'

    return request.rest_request(conninfo, credentials, method, uri, body=status)


@request.request
def get_vpn_keys(conninfo: Connection, credentials: Optional[Credentials]) -> RestResponse:
    method = 'GET'
    uri = '/v1/support/vpn-keys'

    return request.rest_request(conninfo, credentials, method, uri)


@request.request
def install_vpn_keys(
    conninfo: Connection, credentials: Optional[Credentials], vpn_keys: Mapping[str, str]
) -> RestResponse:
    method = 'PUT'
    uri = '/v1/support/vpn-keys'

    return request.rest_request(conninfo, credentials, method, uri, body=vpn_keys)
