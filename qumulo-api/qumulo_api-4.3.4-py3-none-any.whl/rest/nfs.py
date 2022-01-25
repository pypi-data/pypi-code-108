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

# XXX: Please add type parameters to all generics in this file!
# mypy: allow-any-generics

from typing import Dict, Mapping, Optional, Sequence

import qumulo.lib.obj as obj
import qumulo.lib.request as request

from qumulo.lib.auth import Credentials
from qumulo.lib.uri import UriBuilder


class NFSExportRestriction(obj.Object):
    """
    A representation of the restrictions one can place on an individual NFS
    export. Each export must have one or more of these objects.

    A NFSExportRestriction object specifies

      * Whether the export is read_only (otherwise it is read/write).
      * Whether the export can only be mounted by clients coming from a
        privileged port (those less than 1024).
      * What hosts (IP addresses) are allowed to mount the export.
      * Whether to treat certain or all users as ("map" them to) a specific user
        identity.
    """

    @classmethod
    def create_default(cls) -> 'NFSExportRestriction':
        return cls(
            {
                'read_only': False,
                'require_privileged_port': False,
                'host_restrictions': [],
                'user_mapping': 'NFS_MAP_NONE',
                'map_to_user': {'id_type': 'LOCAL_USER', 'id_value': '0'},
            }
        )


@request.request
def nfs_list_exports(
    conninfo: request.Connection, credentials: Optional[Credentials]
) -> request.RestResponse:
    """
    Return all the NFS exports configured in the system.
    """
    method = 'GET'
    uri = '/v2/nfs/exports/'

    return request.rest_request(conninfo, credentials, method, uri)


@request.request
def nfs_add_export(
    conninfo: request.Connection,
    credentials: Optional[Credentials],
    export_path: str,
    fs_path: str,
    description: str,
    restrictions: Sequence[NFSExportRestriction],
    allow_fs_path_create: bool = False,
    present_64_bit_fields_as_32_bit: Optional[bool] = None,
    fields_to_present_as_32_bit: Optional[Sequence] = None,
) -> request.RestResponse:
    """
    Add an NFS export which exports a given filesystem path (fs_path), allowing
    clients to mount that path using the given export_path.

    @param export_path: The path clients will use to specify this export as the
        one to mount. Essentially, the public name of the export.
    @param fs_path: The true path in the Qumulo file system which will then be
        mounted. Clients will not normally be aware of this path when mounting;
        and through the export will not be able to see files/directories outside
        of this path.
    @param description: A description of the export, for administrative
        reference.
    @param restrictions: a list of NFSExportRestriction objects representing
        restrictions on the ways the export can be used (See
        NFSExportRestriction for details).

        The restriction that applies to a given client connection is the first
        one in the list whose "host_restrictions" field includes the client's
        IP address.
    @param allow_fs_path_create: When true, the server will create the fs_path
        directories if they don't exist already.
    @param present_64_bit_fields_as_32_bit: Deprecated in favor of
        @p fields_to_present_as_32_bit.
    @param fields_to_present_as_32_bit a list of field types that should be
        forced to fit in 32bit integers for mounts of this export.  This is
        useful for supporting legacy clients / applictations.  The following
        fields may be given:
        "FILE_IDS" - Hash large file IDs (inode numbers) to fit in 32bits.
            This is known to be necessary for certain deprecated linux system
            calls (e.g. to list a directory) to work. This might break
            applications that try to use inode number to uniquely identify
            files, e.g. rsync hardlink detection.
        "FS_SIZE" - Saturate reported total, used, and free space to 4GiB.
            This is the information that feeds tools like "df".  Note
            that this does not (directly) limit space that is actually available
            to the application.
        "FILE_SIZES" - Saturate size reported for large files to 4GiB.
            This should be used with caution, as it could result in serious
            misbehavior by 64bit applications accessing larger files via this
            export.
    """
    method = 'POST'
    allow_fs_path_create_ = 'true' if allow_fs_path_create else 'false'

    uri = str(
        UriBuilder(path='/v2/nfs/exports/', rstrip_slash=False).add_query_param(
            'allow-fs-path-create', allow_fs_path_create_
        )
    )

    share_info: Dict[str, object] = {
        'export_path': export_path,
        'fs_path': fs_path,
        'description': description,
        'restrictions': [r.dictionary() for r in restrictions],
    }
    if fields_to_present_as_32_bit is not None:
        share_info['fields_to_present_as_32_bit'] = fields_to_present_as_32_bit
    if present_64_bit_fields_as_32_bit is not None:
        assert fields_to_present_as_32_bit is None
        share_info['present_64_bit_fields_as_32_bit'] = present_64_bit_fields_as_32_bit

    return request.rest_request(conninfo, credentials, method, uri, body=share_info)


@request.request
def nfs_get_export(
    conninfo: request.Connection, credentials: Optional[Credentials], ref: str
) -> request.RestResponse:
    """
    Return a specific NFS export, specified by its ID or export-path.
    """

    method = 'GET'
    uri = str(UriBuilder(path='/v2/nfs/exports/').add_path_component(ref))
    return request.rest_request(conninfo, credentials, method, uri)


@request.request
def nfs_modify_export(
    conninfo: request.Connection,
    credentials: Optional[Credentials],
    id_: str,
    export_path: str,
    fs_path: str,
    description: str,
    restrictions: Sequence[NFSExportRestriction],
    allow_fs_path_create: bool = False,
    present_64_bit_fields_as_32_bit: Optional[bool] = None,
    fields_to_present_as_32_bit: Optional[Sequence] = None,
    if_match: Optional[str] = None,
) -> request.RestResponse:
    """
    Set all the aspects of an export, specified by ID, to the values given.
    See @ref nfs_add_export for detailed descriptions of arguments.
    """

    allow_fs_path_create_ = 'true' if allow_fs_path_create else 'false'

    method = 'PUT'
    uri = str(
        UriBuilder(path='/v2/nfs/exports/')
        .add_path_component(id_)
        .add_query_param('allow-fs-path-create', allow_fs_path_create_)
    )

    share_info: Dict[str, object] = {
        'id': id_,
        'export_path': export_path,
        'fs_path': fs_path,
        'description': description,
        'restrictions': [r.dictionary() for r in restrictions],
    }
    if fields_to_present_as_32_bit is not None:
        share_info['fields_to_present_as_32_bit'] = fields_to_present_as_32_bit
    if present_64_bit_fields_as_32_bit is not None:
        share_info['present_64_bit_fields_as_32_bit'] = present_64_bit_fields_as_32_bit

    return request.rest_request(
        conninfo, credentials, method, uri, body=share_info, if_match=if_match
    )


@request.request
def nfs_delete_export(
    conninfo: request.Connection, credentials: Optional[Credentials], ref: str
) -> request.RestResponse:
    """
    Delete an NFS export, specified by its ID or export-path.
    """

    method = 'DELETE'
    uri = str(UriBuilder(path='/v2/nfs/exports/').add_path_component(ref))
    return request.rest_request(conninfo, credentials, method, uri)


@request.request
def get_nfs_config(
    conninfo: request.Connection, credentials: Optional[Credentials]
) -> request.RestResponse:
    """
    Retrieve current NFS server configuration.
    """

    method = 'GET'
    uri = '/v2/nfs/settings'

    return request.rest_request(conninfo, credentials, method, uri)


@request.request
def set_nfs_config(
    conninfo: request.Connection, credentials: Optional[Credentials], config: Mapping[str, bool]
) -> request.RestResponse:
    """
    Modify current NFS server configuration.
    """

    method = 'PATCH'
    uri = '/v2/nfs/settings'

    return request.rest_request(conninfo, credentials, method, uri, body=config)
