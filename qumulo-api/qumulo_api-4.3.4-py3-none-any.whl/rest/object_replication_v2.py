# Copyright (c) 2016 Qumulo, Inc.
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

# XXX: Please add types to the functions in this file. Static type checking in
# Python prevents bugs!
# mypy: ignore-errors


import qumulo.lib.request as request


@request.request
def create_object_relationship(
    conninfo,
    credentials,
    object_store_address,
    bucket,
    object_folder,
    region,
    access_key_id,
    secret_access_key,
    source_directory_id=None,
    source_directory_path=None,
    port=None,
    ca_certificate=None,
    bucket_style=None,
):

    method = 'POST'
    uri = '/v2/replication/object-relationships/'

    body = {
        'object_store_address': object_store_address,
        'bucket': bucket,
        'object_folder': object_folder,
        'region': region,
        'access_key_id': access_key_id,
        'secret_access_key': secret_access_key,
    }

    if source_directory_id is not None:
        body['source_directory_id'] = source_directory_id

    if source_directory_path is not None:
        body['source_directory_path'] = source_directory_path

    if port is not None:
        body['port'] = port

    if ca_certificate is not None:
        body['ca_certificate'] = ca_certificate

    if bucket_style is not None:
        body['bucket_style'] = bucket_style

    return request.rest_request(conninfo, credentials, method, uri, body=body)


@request.request
def list_object_relationships(conninfo, credentials):
    method = 'GET'
    uri = '/v2/replication/object-relationships/'

    return request.rest_request(conninfo, credentials, method, uri)


@request.request
def get_object_relationship(conninfo, credentials, relationship_id):
    method = 'GET'
    uri = f'/v2/replication/object-relationships/{relationship_id}'

    return request.rest_request(conninfo, credentials, method, uri)


@request.request
def delete_object_relationship(conninfo, credentials, relationship_id, if_match=None):
    method = 'DELETE'
    uri = f'/v2/replication/object-relationships/{relationship_id}'

    return request.rest_request(conninfo, credentials, method, uri, if_match=if_match)


@request.request
def abort_object_replication(conninfo, credentials, relationship_id):
    method = 'POST'
    uri = f'/v2/replication/object-relationships/{relationship_id}/abort-replication'

    return request.rest_request(conninfo, credentials, method, uri)


@request.request
def list_object_relationship_statuses(conninfo, credentials):
    method = 'GET'
    uri = '/v2/replication/object-relationships/status/'

    return request.rest_request(conninfo, credentials, method, uri)


@request.request
def get_object_relationship_status(conninfo, credentials, relationship_id):
    method = 'GET'
    uri = f'/v2/replication/object-relationships/{relationship_id}/status'

    return request.rest_request(conninfo, credentials, method, uri)


@request.request
def replicate_object_relationship(conninfo, credentials, relationship_id):
    method = 'POST'
    uri = f'/v2/replication/object-relationships/{relationship_id}/replicate'

    return request.rest_request(conninfo, credentials, method, uri)
