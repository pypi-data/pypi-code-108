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

from qumulo.lib.uri import UriBuilder


@request.request
def replicate(conninfo, credentials, relationship):
    method = 'POST'
    uri = f'/v2/replication/source-relationships/{relationship}/replicate'
    return request.rest_request(conninfo, credentials, method, str(uri))


@request.request
def create_source_relationship(
    conninfo,
    credentials,
    target_path,
    address,
    source_id=None,
    source_path=None,
    source_root_read_only=None,
    map_local_ids_to_nfs_ids=None,
    replication_enabled=None,
    target_port=None,
    replication_mode=None,
    snapshot_policies=None,
):

    body = {'target_root_path': target_path, 'target_address': address}

    if source_id is not None:
        body['source_root_id'] = source_id

    if source_path is not None:
        body['source_root_path'] = source_path

    if source_root_read_only is not None:
        body['source_root_read_only'] = source_root_read_only

    if target_port is not None:
        body['target_port'] = target_port

    if map_local_ids_to_nfs_ids is not None:
        body['map_local_ids_to_nfs_ids'] = map_local_ids_to_nfs_ids

    if replication_enabled is not None:
        body['replication_enabled'] = replication_enabled

    if replication_mode is not None:
        body['replication_mode'] = replication_mode

    if snapshot_policies is not None:
        body['snapshot_policies'] = snapshot_policies

    method = 'POST'
    uri = '/v2/replication/source-relationships/'
    return request.rest_request(conninfo, credentials, method, uri, body=body)


@request.request
def list_source_relationships(conninfo, credentials):
    method = 'GET'
    uri = '/v2/replication/source-relationships/'
    return request.rest_request(conninfo, credentials, method, uri)


@request.request
def get_source_relationship(conninfo, credentials, relationship_id):
    method = 'GET'
    uri = '/v2/replication/source-relationships/{}'
    return request.rest_request(conninfo, credentials, method, uri.format(relationship_id))


@request.request
def delete_source_relationship(conninfo, credentials, relationship_id, if_match=None):
    method = 'DELETE'
    uri = f'/v2/replication/source-relationships/{relationship_id}'
    return request.rest_request(conninfo, credentials, method, uri, if_match=if_match)


@request.request
def delete_target_relationship(conninfo, credentials, relationship_id):
    method = 'POST'
    uri = '/v2/replication/target-relationships/{}/delete'
    return request.rest_request(conninfo, credentials, method, uri.format(relationship_id))


@request.request
def modify_source_relationship(
    conninfo,
    credentials,
    relationship_id,
    new_target_address=None,
    new_target_port=None,
    source_root_read_only=None,
    map_local_ids_to_nfs_ids=None,
    replication_enabled=None,
    blackout_windows=None,
    blackout_window_timezone=None,
    replication_mode=None,
    snapshot_policies=None,
    if_match=None,
):

    method = 'PATCH'
    uri = f'/v2/replication/source-relationships/{relationship_id}'

    body = {}
    if new_target_address is not None:
        body['target_address'] = new_target_address
    if new_target_port is not None:
        body['target_port'] = new_target_port
    if source_root_read_only is not None:
        body['source_root_read_only'] = source_root_read_only
    if map_local_ids_to_nfs_ids is not None:
        body['map_local_ids_to_nfs_ids'] = map_local_ids_to_nfs_ids
    if replication_enabled is not None:
        body['replication_enabled'] = replication_enabled
    if blackout_windows is not None:
        body['blackout_windows'] = blackout_windows
    if blackout_window_timezone is not None:
        body['blackout_window_timezone'] = blackout_window_timezone
    if replication_mode is not None:
        body['replication_mode'] = replication_mode
    if snapshot_policies is not None:
        body['snapshot_policies'] = snapshot_policies

    return request.rest_request(conninfo, credentials, method, uri, body=body, if_match=if_match)


@request.request
def list_source_relationship_statuses(conninfo, credentials):
    method = 'GET'
    uri = '/v2/replication/source-relationships/status/'
    return request.rest_request(conninfo, credentials, method, uri)


@request.request
def list_target_relationship_statuses(conninfo, credentials):
    method = 'GET'
    uri = '/v2/replication/target-relationships/status/'
    return request.rest_request(conninfo, credentials, method, uri)


@request.request
def get_source_relationship_status(conninfo, credentials, relationship_id):
    method = 'GET'
    uri = '/v2/replication/source-relationships/{}/status'
    return request.rest_request(conninfo, credentials, method, uri.format(relationship_id))


@request.request
def get_target_relationship_status(conninfo, credentials, relationship_id):
    method = 'GET'
    uri = '/v2/replication/target-relationships/{}/status'
    return request.rest_request(conninfo, credentials, method, uri.format(relationship_id))


@request.request
def authorize(
    conninfo,
    credentials,
    relationship_id,
    allow_non_empty_directory=None,
    allow_fs_path_create=None,
):
    method = 'POST'

    uri = UriBuilder(path=f'/v2/replication/target-relationships/{relationship_id}/authorize')

    if allow_non_empty_directory is not None:
        uri.add_query_param(
            'allow-non-empty-directory', 'true' if allow_non_empty_directory else 'false'
        )
    if allow_fs_path_create is not None:
        uri.add_query_param('allow-fs-path-create', 'true' if allow_fs_path_create else 'false')

    return request.rest_request(conninfo, credentials, method, str(uri))


@request.request
def reconnect_target_relationship(conninfo, credentials, relationship_id):
    method = 'POST'
    uri = '/v2/replication/target-relationships/{}/reconnect'
    return request.rest_request(conninfo, credentials, method, uri.format(relationship_id))


@request.request
def abort_replication(conninfo, credentials, relationship_id, skip_active_policy_snapshot=None):
    method = 'POST'

    uri = UriBuilder(
        path=f'/v2/replication/source-relationships/{relationship_id}/abort-replication'
    )

    if skip_active_policy_snapshot is not None:
        uri.add_query_param(
            'skip-active-policy-snapshot', 'true' if skip_active_policy_snapshot else 'false'
        )

    return request.rest_request(conninfo, credentials, method, str(uri))


@request.request
def make_target_writable(conninfo, credentials, relationship_id):
    method = 'POST'
    uri = '/v2/replication/target-relationships/{}/make-writable'
    return request.rest_request(conninfo, credentials, method, uri.format(relationship_id))


@request.request
def reverse_target_relationship(
    conninfo, credentials, relationship_id, source_address, source_port=None
):
    method = 'POST'
    uri = '/v2/replication/source-relationships/reverse-target-relationship'

    body = {'target_relationship_id': relationship_id, 'source_address': source_address}
    if source_port is not None:
        body['source_port'] = source_port

    return request.rest_request(conninfo, credentials, method, uri, body=body)


@request.request
def dismiss_source_relationship_error(conninfo, credentials, relationship_id):
    method = 'POST'
    uri = '/v2/replication/source-relationships/{}/dismiss-error'
    return request.rest_request(conninfo, credentials, method, uri.format(relationship_id))


@request.request
def dismiss_target_relationship_error(conninfo, credentials, relationship_id):
    method = 'POST'
    uri = '/v2/replication/target-relationships/{}/dismiss-error'
    return request.rest_request(conninfo, credentials, method, uri.format(relationship_id))


@request.request
def list_queued_snapshots(conninfo, credentials, relationship_id):
    method = 'GET'
    uri = '/v2/replication/source-relationships/{}/queued-snapshots/'
    return request.rest_request(conninfo, credentials, method, uri.format(relationship_id))


@request.request
def release_queued_snapshot(conninfo, credentials, relationship_id, snapshot_id):
    method = 'DELETE'
    uri = '/v2/replication/source-relationships/{}/queued-snapshots/{}'
    return request.rest_request(
        conninfo, credentials, method, uri.format(relationship_id, snapshot_id)
    )
