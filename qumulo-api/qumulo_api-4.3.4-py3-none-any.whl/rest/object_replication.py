# Copyright (c) 2021 Qumulo, Inc.
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

"""
Object replication v3 API beta for evaluation
"""

from typing import Dict, Optional, Union

import qumulo.lib.request as request

from qumulo.lib.auth import Credentials


@request.request
def create_object_relationship(
    conninfo: request.Connection,
    credentials: Optional[Credentials],
    direction: str,
    object_store_address: str,
    bucket: str,
    object_folder: str,
    region: str,
    access_key_id: str,
    secret_access_key: str,
    local_directory_id: Optional[str] = None,
    local_directory_path: Optional[str] = None,
    port: Optional[int] = None,
    ca_certificate: Optional[str] = None,
    bucket_style: Optional[str] = None,
) -> request.RestResponse:
    """
    @p direction  One of "COPY_TO_OBJECT", "COPY_FROM_OBJECT"
    @p bucket_style  One of "BUCKET_STYLE_PATH", "BUCKET_STYLE_VIRTUAL_HOSTED"
    """

    method = 'POST'
    uri = '/v3/replication/object-relationships/'

    body: Dict[str, Union[str, int]] = {
        'direction': direction,
        'object_store_address': object_store_address,
        'bucket': bucket,
        'object_folder': object_folder,
        'region': region,
        'access_key_id': access_key_id,
        'secret_access_key': secret_access_key,
    }

    if local_directory_id is not None:
        body['local_directory_id'] = local_directory_id

    if local_directory_path is not None:
        body['local_directory_path'] = local_directory_path

    if port is not None:
        body['port'] = port

    if ca_certificate is not None:
        body['ca_certificate'] = ca_certificate

    if bucket_style is not None:
        body['bucket_style'] = bucket_style

    return request.rest_request(conninfo, credentials, method, uri, body=body)


@request.request
def get_object_relationship(
    conninfo: request.Connection, credentials: Optional[Credentials], relationship_id: str
) -> request.RestResponse:
    method = 'GET'
    uri = '/v3/replication/object-relationships/{}'

    return request.rest_request(conninfo, credentials, method, uri.format(relationship_id))


@request.request
def list_object_relationships(
    conninfo: request.Connection, credentials: Optional[Credentials]
) -> request.RestResponse:
    method = 'GET'
    uri = '/v3/replication/object-relationships/'

    return request.rest_request(conninfo, credentials, method, uri)


@request.request
def get_object_relationship_status(
    conninfo: request.Connection, credentials: Optional[Credentials], relationship_id: str
) -> request.RestResponse:
    method = 'GET'
    uri = '/v3/replication/object-relationships/{}/status'

    return request.rest_request(conninfo, credentials, method, uri.format(relationship_id))


@request.request
def list_object_relationship_statuses(
    conninfo: request.Connection, credentials: Optional[Credentials]
) -> request.RestResponse:
    method = 'GET'
    uri = '/v3/replication/object-relationships/status/'

    return request.rest_request(conninfo, credentials, method, uri)


@request.request
def abort_object_replication(
    conninfo: request.Connection, credentials: Optional[Credentials], relationship_id: str
) -> request.RestResponse:
    method = 'POST'
    uri = f'/v3/replication/object-relationships/{relationship_id}/abort-replication'

    return request.rest_request(conninfo, credentials, method, uri)


@request.request
def delete_object_relationship(
    conninfo: request.Connection,
    credentials: Optional[Credentials],
    relationship_id: str,
    if_match: Optional[str] = None,
) -> request.RestResponse:
    method = 'DELETE'
    uri = f'/v3/replication/object-relationships/{relationship_id}'

    return request.rest_request(conninfo, credentials, method, uri, if_match=if_match)


@request.request
def replicate_object_relationship(
    conninfo: request.Connection, credentials: Optional[Credentials], relationship_id: str
) -> request.RestResponse:
    method = 'POST'
    uri = f'/v3/replication/object-relationships/{relationship_id}/replicate'

    return request.rest_request(conninfo, credentials, method, uri)
