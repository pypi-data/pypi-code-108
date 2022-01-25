# Copyright (c) 2012 Qumulo, Inc.
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

from typing import Optional, Sequence, Union

import qumulo.lib.request as request

from qumulo.lib.auth import Credentials
from qumulo.lib.request import Connection, RestResponse


@request.request
def list_nodes(conninfo: Connection, credentials: Optional[Credentials]) -> RestResponse:
    method = 'GET'
    uri = '/v1/cluster/nodes/'

    return request.rest_request(conninfo, credentials, method, uri)


@request.request
def list_node(conninfo: Connection, credentials: Optional[Credentials], node: int) -> RestResponse:
    method = 'GET'
    uri = f'/v1/cluster/nodes/{node}'

    return request.rest_request(conninfo, credentials, method, uri)


@request.request
def get_cluster_conf(conninfo: Connection, credentials: Optional[Credentials]) -> RestResponse:
    method = 'GET'
    uri = '/v1/cluster/settings'

    return request.rest_request(conninfo, credentials, method, uri)


@request.request
def put_cluster_conf(
    conninfo: Connection, credentials: Optional[Credentials], cluster_name: str
) -> RestResponse:
    method = 'PUT'
    uri = '/v1/cluster/settings'

    config = {'cluster_name': str(cluster_name)}

    return request.rest_request(conninfo, credentials, method, uri, body=config)


@request.request
def set_ssl_certificate(
    conninfo: Connection, credentials: Optional[Credentials], certificate: str, private_key: str
) -> RestResponse:
    method = 'PUT'
    uri = '/v2/cluster/settings/ssl/certificate'

    config = {'certificate': str(certificate), 'private_key': str(private_key)}

    return request.rest_request(conninfo, credentials, method, uri, body=config)


@request.request
def set_ssl_ca_certificate(
    conninfo: Connection, credentials: Optional[Credentials], ca_cert: str
) -> RestResponse:
    method = 'PUT'
    uri = '/v2/cluster/settings/ssl/ca-certificate'
    body = {'ca_certificate': str(ca_cert)}
    return request.rest_request(conninfo, credentials, method, uri, body=body)


@request.request
def get_ssl_ca_certificate(
    conninfo: Connection, credentials: Optional[Credentials]
) -> RestResponse:
    method = 'GET'
    uri = '/v2/cluster/settings/ssl/ca-certificate'

    return request.rest_request(conninfo, credentials, method, uri)


@request.request
def delete_ssl_ca_certificate(
    conninfo: Connection, credentials: Optional[Credentials]
) -> RestResponse:
    method = 'DELETE'
    uri = '/v2/cluster/settings/ssl/ca-certificate'

    return request.rest_request(conninfo, credentials, method, uri)


@request.request
def get_cluster_slots_status(
    conninfo: Connection, credentials: Optional[Credentials]
) -> RestResponse:
    method = 'GET'
    uri = '/v1/cluster/slots/'

    return request.rest_request(conninfo, credentials, method, uri)


@request.request
def get_cluster_slot_status(
    conninfo: Connection, credentials: Optional[Credentials], slot: str
) -> RestResponse:
    method = 'GET'
    uri = f'/v1/cluster/slots/{slot}'

    return request.rest_request(conninfo, credentials, method, uri)


@request.request
def set_cluster_slot_config(
    conninfo: Connection, credentials: Optional[Credentials], slot: str, pattern: str
) -> RestResponse:
    method = 'PATCH'
    uri = f'/v1/cluster/slots/{slot}'

    body = {'led_pattern': pattern}

    return request.rest_request(conninfo, credentials, method, uri, body=body)


@request.request
def get_restriper_status(conninfo: Connection, credentials: Optional[Credentials]) -> RestResponse:
    method = 'GET'
    uri = '/v1/cluster/restriper/status'

    return request.rest_request(conninfo, credentials, method, uri)


@request.request
def get_protection_status(conninfo: Connection, credentials: Optional[Credentials]) -> RestResponse:
    method = 'GET'
    uri = '/v1/cluster/protection/status'

    return request.rest_request(conninfo, credentials, method, uri)


@request.request
def set_node_identify_light(
    conninfo: Connection, credentials: Optional[Credentials], node: int, light_visible: bool
) -> RestResponse:
    method = 'POST'
    uri = f'/v1/cluster/nodes/{node}/identify'

    body = {'light_visible': light_visible}

    return request.rest_request(conninfo, credentials, method, uri, body=body)


@request.request
def get_node_chassis_status(
    conninfo: Connection, credentials: Optional[Credentials], node: Optional[int] = None
) -> RestResponse:
    method = 'GET'

    if node is not None:
        uri = f'/v1/cluster/nodes/{node}/chassis'
    else:
        uri = '/v1/cluster/nodes/chassis/'

    return request.rest_request(conninfo, credentials, method, uri)


# This should match the max_drive_failures enumeration in /v1/cluster/create
PROTECTION_LEVEL_MAP = {'RECOMMENDED': -1, 'TWO_DRIVES': 2, 'THREE_DRIVES': 3}


def sanitize_max_drive_failures(param: Optional[Union[str, int]]) -> Optional[int]:
    """
    In order to avoid revving the bindings, we need to continue to support the
    old-style drive failures params, which are strings that must be either
    RECOMMENDED, TWO_DRIVES or THREE_DRIVES.  These can easily be translated
    into an optional int, matching the v2 REST endpoint.
    """
    if param is None:
        return param
    if isinstance(param, int):
        return param

    if param not in PROTECTION_LEVEL_MAP:
        raise ValueError(f"invalid max drive failures count: '{param}'")

    value = PROTECTION_LEVEL_MAP[param]
    return value if value > 0 else None


@request.request
def create_cluster(
    conninfo: Connection,
    credentials: Optional[Credentials],
    cluster_name: str,
    admin_password: str,
    node_uuids: Optional[Sequence[str]] = None,
    node_ips: Optional[Sequence[str]] = None,
    eula_accepted: bool = True,
    host_instance_id: Optional[str] = None,
    blocks_per_stripe: Optional[int] = None,
    max_drive_failures: Optional[Union[str, int]] = None,
    max_node_failures: Optional[int] = None,
) -> RestResponse:
    method = 'POST'
    uri = '/v2/cluster/create'

    cluster_create_request = {
        'eula_accepted': eula_accepted,
        'cluster_name': str(cluster_name),
        'node_uuids': list() if node_uuids is None else list(node_uuids),
        'node_ips': list() if node_ips is None else list(node_ips),
        'admin_password': str(admin_password),
    }

    if host_instance_id is not None:
        cluster_create_request['host_instance_id'] = host_instance_id

    if blocks_per_stripe is not None:
        cluster_create_request['blocks_per_stripe'] = blocks_per_stripe

    sanitized_max_drive_failures = sanitize_max_drive_failures(max_drive_failures)
    if sanitized_max_drive_failures is not None:
        cluster_create_request['max_drive_failures'] = sanitized_max_drive_failures

    if max_node_failures is not None:
        cluster_create_request['max_node_failures'] = max_node_failures

    return request.rest_request(conninfo, credentials, method, uri, body=cluster_create_request)


@request.request
def add_node(
    conninfo: Connection,
    credentials: Optional[Credentials],
    node_uuids: Optional[Sequence[str]] = None,
    node_ips: Optional[Sequence[str]] = None,
    blobs: Optional[Sequence[object]] = None,
) -> RestResponse:
    method = 'POST'
    uri = '/v1/cluster/nodes/'

    req = {
        'node_uuids': list() if node_uuids is None else list(node_uuids),
        'node_ips': list() if node_ips is None else list(node_ips),
        'blobs': list() if blobs is None else list(blobs),
    }

    return request.rest_request(conninfo, credentials, method, uri, body=req)


@request.request
def calculate_node_add_capacity(
    conninfo: Connection,
    credentials: Optional[Credentials],
    node_uuids: Optional[Sequence[str]] = None,
    node_ips: Optional[Sequence[str]] = None,
) -> RestResponse:
    method = 'POST'
    uri = '/v1/cluster/calculate-node-add-capacity'

    req = {
        'node_uuids': list() if node_uuids is None else list(node_uuids),
        'node_ips': list() if node_ips is None else list(node_ips),
    }

    return request.rest_request(conninfo, credentials, method, uri, body=req)
