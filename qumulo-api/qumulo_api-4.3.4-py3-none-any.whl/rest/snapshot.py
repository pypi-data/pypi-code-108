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

from typing import Dict, Optional, Sequence

import qumulo.lib.request as request
import qumulo.rest.fs

from qumulo.lib.auth import Credentials
from qumulo.lib.uri import UriBuilder


@request.request
def create_snapshot(
    conninfo: request.Connection,
    credentials: Optional[Credentials],
    name: Optional[str] = None,
    expiration: Optional[str] = None,
    time_to_live: Optional[str] = None,
    path: Optional[str] = None,
    id_: Optional[str] = None,
) -> request.RestResponse:
    method = 'POST'
    uri = '/v2/snapshots/'
    snapshot = {}

    # name is an optional parameter
    if name != None:
        snapshot['name'] = name
    # expiration is an optional parameter
    if expiration != None:
        snapshot['expiration'] = expiration
    # time_to_live is an optional parameter
    if time_to_live is not None:
        uri += '?expiration-time-to-live=' + time_to_live

    assert path == None or id_ == None, 'Cannot specify both path and id'

    # Take a snapshot on a particular path or ID
    if path != None:
        id_ = qumulo.rest.fs.get_file_attr(conninfo, credentials, path=path).lookup('file_number')
    if id_ != None:
        snapshot['source_file_id'] = id_

    return request.rest_request(conninfo, credentials, method, uri, body=snapshot)


@request.request
def modify_snapshot(
    conninfo: request.Connection,
    credentials: Optional[Credentials],
    snapshot_id: int,
    expiration: Optional[str] = None,
    time_to_live: Optional[str] = None,
) -> request.RestResponse:
    method = 'PATCH'
    uri = '/v2/snapshots/{}'
    snapshot = {}

    # expiration is an optional parameter
    if expiration != None:
        snapshot['expiration'] = expiration
    # time_to_live is an optional parameter
    if time_to_live is not None:
        uri += '?expiration-time-to-live=' + time_to_live

    return request.rest_request(
        conninfo, credentials, method, uri.format(snapshot_id), body=snapshot
    )


@request.request
def list_snapshots(
    conninfo: request.Connection,
    credentials: Optional[Credentials],
    include_in_delete: bool = False,
) -> request.RestResponse:
    method = 'GET'
    include_in_delete_ = 'true' if include_in_delete else 'false'
    uri = '/v2/snapshots/?include-in-delete=%s' % include_in_delete_

    return request.rest_request(conninfo, credentials, method, uri)


@request.request
def get_snapshot(
    conninfo: request.Connection, credentials: Optional[Credentials], snapshot_id: int
) -> request.RestResponse:
    method = 'GET'
    uri = '/v2/snapshots/{}'

    return request.rest_request(conninfo, credentials, method, uri.format(snapshot_id))


@request.request
def list_snapshot_statuses(
    conninfo: request.Connection, credentials: Optional[Credentials]
) -> request.RestResponse:
    method = 'GET'
    uri = '/v2/snapshots/status/'

    return request.rest_request(conninfo, credentials, method, uri)


@request.request
def get_snapshot_status(
    conninfo: request.Connection, credentials: Optional[Credentials], snapshot_id: int
) -> request.RestResponse:
    method = 'GET'
    uri = '/v2/snapshots/status/{}'

    return request.rest_request(conninfo, credentials, method, uri.format(snapshot_id))


@request.request
def delete_snapshot(
    conninfo: request.Connection, credentials: Optional[Credentials], snapshot_id: int
) -> request.RestResponse:
    method = 'DELETE'
    uri = '/v2/snapshots/{}'

    return request.rest_request(conninfo, credentials, method, uri.format(snapshot_id))


@request.request
def create_policy(
    conninfo: request.Connection,
    credentials: Optional[Credentials],
    name: str,
    schedule_info: Dict[str, object],
    directory_id: Optional[str] = None,
    enabled: Optional[bool] = None,
) -> request.RestResponse:

    method = 'POST'
    uri = '/v1/snapshots/policies/'

    if directory_id == None:
        directory_id = '2'

    policy = {'name': name, 'schedules': [schedule_info], 'source_file_ids': [directory_id]}

    if enabled is not None:
        policy['enabled'] = enabled

    return request.rest_request(conninfo, credentials, method, uri, body=policy)


@request.request
def modify_policy(
    conninfo: request.Connection,
    credentials: Optional[Credentials],
    policy_id: int,
    name: Optional[str] = None,
    schedule_info: Optional[Dict[str, object]] = None,
    enabled: Optional[bool] = None,
    if_match: Optional[str] = None,
) -> request.RestResponse:

    method = 'PATCH'
    uri = '/v1/snapshots/policies/{}'

    policy: Dict[str, object] = {}
    if name is not None:
        policy.update({'name': name})
    if schedule_info is not None:
        policy.update({'schedules': [schedule_info]})
    if enabled is not None:
        policy['enabled'] = enabled

    return request.rest_request(
        conninfo, credentials, method, uri.format(policy_id), body=policy, if_match=if_match
    )


@request.request
def list_policies(
    conninfo: request.Connection, credentials: Optional[Credentials]
) -> request.RestResponse:
    method = 'GET'
    uri = '/v1/snapshots/policies/'

    return request.rest_request(conninfo, credentials, method, uri)


@request.request
def get_policy(
    conninfo: request.Connection, credentials: Optional[Credentials], policy_id: int
) -> request.RestResponse:
    method = 'GET'
    uri = '/v1/snapshots/policies/{}'

    return request.rest_request(conninfo, credentials, method, uri.format(policy_id))


@request.request
def delete_policy(
    conninfo: request.Connection, credentials: Optional[Credentials], policy_id: int
) -> request.RestResponse:
    method = 'DELETE'
    uri = '/v1/snapshots/policies/{}'

    return request.rest_request(conninfo, credentials, method, uri.format(policy_id))


@request.request
def list_policy_statuses(
    conninfo: request.Connection, credentials: Optional[Credentials]
) -> request.RestResponse:
    method = 'GET'
    uri = '/v1/snapshots/policies/status/'

    return request.rest_request(conninfo, credentials, method, uri)


@request.request
def get_policy_status(
    conninfo: request.Connection, credentials: Optional[Credentials], policy_id: int
) -> request.RestResponse:
    method = 'GET'
    uri = '/v1/snapshots/policies/status/{}'

    return request.rest_request(conninfo, credentials, method, uri.format(policy_id))


@request.request
def get_total_used_capacity(
    conninfo: request.Connection, credentials: Optional[Credentials]
) -> request.RestResponse:
    method = 'GET'
    uri = '/v1/snapshots/total-used-capacity'

    return request.rest_request(conninfo, credentials, method, uri)


@request.request
def calculate_used_capacity(
    conninfo: request.Connection, credentials: Optional[Credentials], ids: Sequence[int]
) -> request.RestResponse:
    method = 'POST'
    uri = '/v1/snapshots/calculate-used-capacity'

    return request.rest_request(conninfo, credentials, method, uri, body=ids)


@request.request
def capacity_used_per_snapshot(
    conninfo: request.Connection, credentials: Optional[Credentials]
) -> request.RestResponse:
    method = 'GET'
    uri = '/v1/snapshots/capacity-used-per-snapshot/'

    return request.rest_request(conninfo, credentials, method, uri)


@request.request
def capacity_used_by_snapshot(
    conninfo: request.Connection, credentials: Optional[Credentials], snapshot_id: int
) -> request.RestResponse:
    method = 'GET'
    uri = '/v1/snapshots/capacity-used-per-snapshot/{}'

    return request.rest_request(conninfo, credentials, method, uri.format(snapshot_id))


@request.request
def get_snapshot_tree_diff(
    conninfo: request.Connection,
    credentials: Optional[Credentials],
    newer_snap: int,
    older_snap: int,
    limit: Optional[int] = None,
    after: Optional[str] = None,
) -> request.RestResponse:
    method = 'GET'
    uri = UriBuilder(path=f'/v2/snapshots/{newer_snap:d}/changes-since/{older_snap:d}')

    if limit is not None:
        uri.add_query_param('limit', limit)

    if after is not None:
        uri.add_query_param('after', after)

    return request.rest_request(conninfo, credentials, method, str(uri))


@request.paging_request
def get_all_snapshot_tree_diff(
    conninfo: request.Connection,
    credentials: Optional[Credentials],
    newer_snap: int,
    older_snap: int,
    limit: Optional[int] = None,
) -> request.PagingIterator:
    uri = UriBuilder(path=f'/v2/snapshots/{newer_snap:d}/changes-since/{older_snap:d}')

    def get_a_snapshot_tree_diff(uri: UriBuilder) -> request.RestResponse:
        return request.rest_request(conninfo, credentials, 'GET', str(uri))

    return request.PagingIterator(str(uri), get_a_snapshot_tree_diff, page_size=limit)


def get_snapshot_file_diff_uri(
    newer_snap: int, older_snap: int, path: Optional[str] = None, file_id: Optional[str] = None
) -> UriBuilder:
    assert (path is not None) ^ (file_id is not None)
    file_ref = str(path if path else file_id)

    return UriBuilder(
        path=f'/v2/snapshots/{newer_snap:d}/changes-since/{older_snap:d}/files'
    ).add_path_component(file_ref)


@request.request
def get_snapshot_file_diff(
    conninfo: request.Connection,
    credentials: Optional[Credentials],
    newer_snap: int,
    older_snap: int,
    path: Optional[str] = None,
    file_id: Optional[str] = None,
    limit: Optional[int] = None,
    after: Optional[str] = None,
) -> request.RestResponse:
    uri = get_snapshot_file_diff_uri(newer_snap, older_snap, path, file_id)
    if limit is not None:
        uri.add_query_param('limit', limit)
    if after is not None:
        uri.add_query_param('after', after)

    return request.rest_request(conninfo, credentials, 'GET', str(uri))


@request.paging_request
def get_all_snapshot_file_diff(
    conninfo: request.Connection,
    credentials: Optional[Credentials],
    newer_snap: int,
    older_snap: int,
    path: Optional[str] = None,
    file_id: Optional[str] = None,
    limit: Optional[int] = None,
) -> request.PagingIterator:
    uri = get_snapshot_file_diff_uri(newer_snap, older_snap, path, file_id)

    def get_a_snapshot_file_diff(uri: UriBuilder) -> request.RestResponse:
        return request.rest_request(conninfo, credentials, 'GET', str(uri))

    return request.PagingIterator(str(uri), get_a_snapshot_file_diff, page_size=limit)
