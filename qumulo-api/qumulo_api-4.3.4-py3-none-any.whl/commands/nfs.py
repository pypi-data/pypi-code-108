# Copyright (c) 2015 Qumulo, Inc.
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
NFS export commands
"""

import argparse
import json

from typing import Any, cast, Dict, Optional, Sequence

from typing_extensions import TypedDict

import qumulo.lib.util as util
import qumulo.rest.nfs as nfs

from qumulo.lib.auth import Credentials
from qumulo.lib.opts import str_decode, Subcommand
from qumulo.lib.request import Connection, RestResponse
from qumulo.rest.nfs import NFSExportRestriction

NFSExportRestrictions = Sequence[NFSExportRestriction]


# XXX Steven: these API JSON type definitions belong in rest.nfs, but that file needs to have type
# hinting written first, which I'm not going to do right now. At least here they can help people
# touching this brittle command file.
class JSONMapToUserOrGroup(TypedDict):
    id_type: Optional[str]
    id_value: Optional[str]


class JSONRestriction(TypedDict):
    read_only: Optional[bool]
    require_privileged_port: Optional[bool]
    host_restrictions: Optional[Sequence[str]]
    user_mapping: Optional[str]
    map_to_user: Optional[JSONMapToUserOrGroup]
    map_to_group: Optional[JSONMapToUserOrGroup]


JSONRestrictions = Sequence[JSONRestriction]


class JSONExport(TypedDict):
    id: str
    export_path: str
    fs_path: str
    description: str
    restrictions: NFSExportRestrictions
    present_64_bit_fields_as_32_bit: bool
    fields_to_present_as_32_bit: str


def convert_nfs_user_mapping(name: str) -> str:
    convert = {
        'none': 'NFS_MAP_NONE',
        'root': 'NFS_MAP_ROOT',
        'all': 'NFS_MAP_ALL',
        'nfs_map_none': 'NFS_MAP_NONE',
        'nfs_map_root': 'NFS_MAP_ROOT',
        'nfs_map_all': 'NFS_MAP_ALL',
    }

    if name.lower() not in convert:
        raise ValueError('%s is not one of none, root, or all' % (name))
    return convert[name.lower()]


# __     ______     ____                                          _
# \ \   / /___ \   / ___|___  _ __ ___  _ __ ___   __ _ _ __   __| |___
#  \ \ / /  __) | | |   / _ \| '_ ` _ \| '_ ` _ \ / _` | '_ \ / _` / __|
#   \ V /  / __/  | |__| (_) | | | | | | | | | | | (_| | | | | (_| \__ \
#    \_/  |_____|  \____\___/|_| |_| |_|_| |_| |_|\__,_|_| |_|\__,_|___/
# Figlet: v2 commands

ADD_MODIFY_RESTRICTION_HELP = """
    Path to local file containing the restrictions in JSON format.
    user_mapping can be "none"|"root"|"all".
    map_to_user may be "{ "id_type": "LOCAL_USER", "id_value": "<integer_id>" }"
     or "{ "id_type": "NFS_UID", "id_value": "<integer_id>" }".
    map_to_group may be "{ "id_type": "NFS_GID", "id_value": "<integer_id>".
    If user_mapping is not "none", then either specify map_to_user as a
    local user or specify both map_to_user and map_to_group as NFS user/group.
    Example JSON:
    { "restrictions" : [
        {
            "read_only" : true,
            "host_restrictions" : [ "1.2.3.1", "1.2.3.2" ],
            "user_mapping" : "root",
            "map_to_user": {
                "id_type" : "LOCAL_USER",
                "id_value" : "500"
            }
        },
        {
            "read_only" : true,
            "host_restrictions" : [],
            "user_mapping" : "all",
            "map_to_user" :{
                "id_type" : "NFS_UID",
                "id_value" : "500"
            },
            "map_to_group": {
                "id_type" : "NFS_GID",
                "id_value" : "501"
            }
        } ]
    } """


def parse_nfs_export_restrictions_file(path: str) -> NFSExportRestrictions:
    with open(path) as f:
        contents = f.read()
        try:
            restrictions = json.loads(contents)
        except ValueError as ex:
            raise ValueError(
                f'Error parsing JSON restrictions file {path}; file content: {contents}'
            ) from ex
    return parse_nfs_export_restrictions(restrictions['restrictions'])


def parse_nfs_export_restrictions(restrictions: JSONRestrictions) -> NFSExportRestrictions:
    nfs_export_restrictions = list()
    for r in restrictions:
        read_only = r.get('read_only', False)
        require_privileged_port = r.get('require_privileged_port', False)

        host_restrictions = r.get('host_restrictions', [])

        try:
            user_mapping = convert_nfs_user_mapping(cast(str, r.get('user_mapping', 'none')))

            restriction = NFSExportRestriction(
                {
                    'read_only': read_only,
                    'host_restrictions': host_restrictions,
                    'user_mapping': user_mapping,
                    'require_privileged_port': require_privileged_port,
                }
            )

            if user_mapping == 'NFS_MAP_NONE':
                nfs_export_restrictions.append(restriction)
                continue

            user = r.get('map_to_user')
            group = r.get('map_to_group')

            neither_provided = user is None and group is None
            bad_combination = (user is not None and user.get('id_type') == 'NFS_UID') ^ (
                group is not None
            )

            if neither_provided or bad_combination:
                raise ValueError(
                    'Restriction should either specify map_to_user '
                    'with an NFS uid and map_to_group with an NFS gid, or specify '
                    'map_to_user with a local user id.'
                )

            def get_user_or_group_restriction(mapping: JSONMapToUserOrGroup) -> Dict[str, str]:
                id_type = mapping.get('id_type')
                id_value = mapping.get('id_value')
                if id_type is None or id_value is None:
                    raise ValueError('Mappings must include an id_map and an id_type.')
                return {'id_type': id_type, 'id_value': id_value}

            if user is not None:
                restriction['map_to_user'] = get_user_or_group_restriction(user)

            if group is not None:
                restriction['map_to_group'] = get_user_or_group_restriction(group)

        except ValueError as ex:
            raise ValueError(
                f'When trying to process the following restriction: {r}, this error was thrown: '
                f'{ex}'
            ) from ex

        nfs_export_restrictions.append(restriction)

    return nfs_export_restrictions


class NFSListExportsCommand(Subcommand):
    NAME = 'nfs_list_exports'
    SYNOPSIS = 'List all NFS exports'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            '--json', default=False, action='store_true', help='Print raw response JSON.'
        )

    @staticmethod
    def main(
        conninfo: Connection, credentials: Optional[Credentials], args: argparse.Namespace
    ) -> None:
        response = nfs.nfs_list_exports(conninfo, credentials)
        if args.json:
            print(response)
            return

        print(
            util.tabulate(
                [
                    [export['id'], export['export_path'], export['fs_path'], export['description']]
                    for export in response.data
                ],
                ['ID', 'Export Path', 'FS Path', 'Description'],
            )
        )


def nfs_restriction_to_etc_exports_opts(restriction: NFSExportRestriction) -> Sequence[str]:
    opts = list()
    opts.append('ro' if restriction['read_only'] else 'rw')
    opts.append('secure' if restriction['require_privileged_port'] else 'insecure')
    have_map_to = False
    if restriction['user_mapping'] == 'NFS_MAP_NONE':
        opts.append('no_root_squash')
    elif restriction['user_mapping'] == 'NFS_MAP_ROOT':
        opts.append('root_squash')
        have_map_to = True
    else:
        assert (
            restriction['user_mapping'] == 'NFS_MAP_ALL'
        ), 'Unexpected user mapping type: {}'.format(restriction['user_mapping'])
        opts.append('all_squash')
        have_map_to = True

    if have_map_to and restriction['map_to_user']['id_type'] == 'LOCAL_USER':
        # If mapping to a local user, there is no map_to_group (instead the
        # user's primary group is used).  There's no direct equivalent in
        # /etc/exports, so make up a stylistically-similar one:
        opts.append('anonlocal={}'.format(restriction['map_to_user']['id_value']))
    elif have_map_to and restriction['map_to_user']['id_type'] == 'NFS_UID':
        opts.append('anonuid={}'.format(restriction['map_to_user']['id_value']))
        opts.append('anongid={}'.format(restriction['map_to_group']['id_value']))
    else:
        assert not have_map_to, 'Unexpected map_to_user type: {}'.format(
            restriction['map_to_user']['id_type']
        )

    return opts


def pretty_print_export(export: JSONExport, print_json: bool) -> None:
    if print_json:
        print(json.dumps(export, indent=4))
        return

    print('ID:          {}'.format(export['id']))
    print('Export Path: {}'.format(export['export_path']))
    print('FS Path:     {}'.format(export['fs_path']))
    print('Description: {}'.format(export['description']))
    fields = export['fields_to_present_as_32_bit']
    print('32bit-mapped fields: {}'.format(', '.join(fields) if fields else 'None'))
    print('Host Access:')
    access_table = []
    for i, r in enumerate(export['restrictions'], start=1):
        access_table.append(
            [
                i,
                ', '.join(r['host_restrictions']) if r['host_restrictions'] else '*',
                ', '.join(nfs_restriction_to_etc_exports_opts(r)),
            ]
        )
    print(util.tabulate(access_table, ['ID', 'Hosts', 'Access Options']))


class NFSGetExportCommand(Subcommand):
    NAME = 'nfs_get_export'
    SYNOPSIS = 'Get an export'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        export = parser.add_mutually_exclusive_group(required=True)
        export.add_argument('--id', type=str_decode, dest='ref', help='ID of export to list')
        export.add_argument(
            '--export-path', type=str_decode, dest='ref', help='Path of export to list'
        )

        parser.add_argument(
            '--json', default=False, action='store_true', help='Print raw response JSON.'
        )

    @staticmethod
    def main(
        conninfo: Connection, credentials: Optional[Credentials], args: argparse.Namespace
    ) -> None:
        response = nfs.nfs_get_export(conninfo, credentials, args.ref)
        pretty_print_export(response.data, args.json)


PRESENT_32B_CHOICES = ['FILE_IDS', 'FILE_SIZES', 'FS_SIZE', 'NONE']
PRESENT_32B_HELP = (
    'Fields that should be forced to fit in 32 bits for this '
    'export, to support legacy clients and applications. FILE_IDS will hash '
    'file IDs (inode numbers), which can be observed by "stat", and is also '
    'necessary for some deprecated linux system calls (e.g. to list a '
    'directory) to work. FS_SIZE saturates the available, used, and total '
    'capacity reported to tools like "df" to 4GiB. FILE_SIZES saturates the '
    'reported size of individual files to 4GiB, and should be used with '
    'caution as it could cause application misbehavior in the handling of '
    'larger files.  NONE explicitly specifies no 32 bit mapping.'
)


class NFSAddExportCommand(Subcommand):
    NAME = 'nfs_add_export'
    SYNOPSIS = 'Add a new NFS export'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            '--export-path', type=str_decode, default=None, required=True, help='NFS Export path'
        )
        parser.add_argument(
            '--fs-path', type=str_decode, default=None, required=True, help='File system path'
        )
        parser.add_argument(
            '--description', type=str_decode, default='', help='Description of this export'
        )

        restriction_arg = parser.add_mutually_exclusive_group(required=True)
        restriction_arg.add_argument(
            '--no-restrictions',
            action='store_true',
            default=False,
            help='Specify no restrictions for this export.',
        )
        restriction_arg.add_argument(
            '--restrictions',
            type=str_decode,
            default=None,
            metavar='JSON_FILE_PATH',
            required=False,
            help=ADD_MODIFY_RESTRICTION_HELP,
        )
        parser.add_argument(
            '--create-fs-path',
            action='store_true',
            help='Creates the specified file system path if it does not exist',
        )
        parser.add_argument(
            '--fields-to-present-as-32-bit',
            choices=PRESENT_32B_CHOICES,
            metavar='FIELD',
            nargs='+',
            required=False,
            help=PRESENT_32B_HELP,
        )

    @staticmethod
    def main(
        conninfo: Connection, credentials: Optional[Credentials], args: argparse.Namespace
    ) -> None:
        if args.restrictions:
            restrictions = parse_nfs_export_restrictions_file(args.restrictions)
        else:
            restrictions = [NFSExportRestriction.create_default()]

        print(
            nfs.nfs_add_export(
                conninfo,
                credentials,
                args.export_path,
                args.fs_path,
                args.description,
                restrictions,
                allow_fs_path_create=args.create_fs_path,
                fields_to_present_as_32_bit=args.fields_to_present_as_32_bit,
            )
        )


class NFSModExportCommand(Subcommand):
    NAME = 'nfs_mod_export'
    SYNOPSIS = 'Modify an export'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        export = parser.add_mutually_exclusive_group(required=True)
        export.add_argument('--id', type=str_decode, dest='ref', help='ID of export to modify')
        export.add_argument(
            '--export-path', type=str_decode, dest='ref', help='Path of export to modify'
        )

        parser.add_argument(
            '--new-export-path', type=str_decode, default=None, help='Change NFS export path'
        )
        parser.add_argument(
            '--fs-path', type=str_decode, default=None, help='Change file system path'
        )
        parser.add_argument(
            '--description', type=str_decode, default=None, help='Description of this export'
        )
        # Do not require a restrictions argument, it will preserve the existing
        # ones.
        restriction_arg = parser.add_mutually_exclusive_group(required=False)
        restriction_arg.add_argument(
            '--no-restrictions',
            action='store_true',
            default=False,
            help='Specify no restrictions for this export.',
        )
        restriction_arg.add_argument(
            '--restrictions',
            type=str_decode,
            default=None,
            metavar='JSON_FILE_PATH',
            required=False,
            help=ADD_MODIFY_RESTRICTION_HELP,
        )
        parser.add_argument(
            '--create-fs-path',
            action='store_true',
            help='Creates the specified file system path if it does not exist',
        )
        parser.add_argument(
            '--fields-to-present-as-32-bit',
            choices=PRESENT_32B_CHOICES,
            metavar='FIELD',
            nargs='+',
            required=False,
            help=PRESENT_32B_HELP,
        )

    @staticmethod
    def main(
        conninfo: Connection, credentials: Optional[Credentials], args: argparse.Namespace
    ) -> None:
        response = nfs.nfs_get_export(conninfo, credentials, args.ref)

        export_info: Dict[str, Any] = response.data
        export_info['if_match'] = response.etag

        export_info['id_'] = export_info['id']
        del export_info['id']

        export_info['allow_fs_path_create'] = args.create_fs_path
        if args.fields_to_present_as_32_bit is not None:
            export_info['fields_to_present_as_32_bit'] = args.fields_to_present_as_32_bit
            # don't contradict ourselves with the previous value:
            del export_info['present_64_bit_fields_as_32_bit']

        if args.new_export_path is not None:
            export_info['export_path'] = args.new_export_path

        if args.fs_path is not None:
            export_info['fs_path'] = args.fs_path

        if args.description is not None:
            export_info['description'] = args.description

        if args.restrictions:
            export_info['restrictions'] = parse_nfs_export_restrictions_file(args.restrictions)
        elif args.no_restrictions:
            export_info['restrictions'] = [NFSExportRestriction.create_default()]
        else:
            export_info['restrictions'] = [
                NFSExportRestriction(r) for r in export_info['restrictions']
            ]

        print(nfs.nfs_modify_export(conninfo, credentials, **export_info))


def add_user_mapping_from_args(
    entry: NFSExportRestriction, args: argparse.Namespace, must_set: Optional[bool] = True
) -> None:
    """
    @p must_set indicates whether it is mandatory that a user mapping be
        set.  This would be False when modifying an entry that already has
        squashing enabled, in which case the anon user is already set and it is
        not necessary to change it.
    """
    if must_set and not (args.anon_local or (args.anon_uid is not None)):
        raise ValueError('Must specify an anonymous identity when enabling squashing.')

    if args.anon_local and (args.anon_gid is not None):
        raise ValueError('Cannot specify both --anon-local and --anon-gid.')

    if args.anon_local:
        entry.map_to_user = {'id_type': 'LOCAL_USER', 'id_value': args.anon_local}
        if 'map_to_group' in entry.dictionary():
            del entry.map_to_group

    elif args.anon_uid is not None:
        if args.anon_gid is None:
            raise ValueError('Must provide --anon-gid when --anon-uid is given.')
        entry.map_to_user = {'id_type': 'NFS_UID', 'id_value': str(args.anon_uid)}
        entry.map_to_group = {'id_type': 'NFS_GID', 'id_value': str(args.anon_gid)}


def modify_restrictions(
    conninfo: Connection,
    creds: Optional[Credentials],
    old_export: JSONExport,
    etag: Optional[str],
    restrictions: NFSExportRestrictions,
) -> RestResponse:
    return nfs.nfs_modify_export(
        conninfo,
        creds,
        old_export['id'],
        old_export['export_path'],
        old_export['fs_path'],
        old_export['description'],
        restrictions,
        present_64_bit_fields_as_32_bit=old_export['present_64_bit_fields_as_32_bit'],
        if_match=etag,
    )


def do_add_entry(
    conninfo: Connection, creds: Optional[Credentials], args: argparse.Namespace
) -> RestResponse:
    entry = NFSExportRestriction(
        {
            'host_restrictions': args.hosts if args.hosts != ['*'] else [],
            'require_privileged_port': bool(args.secure),
            'read_only': bool(args.ro),
        }
    )

    if args.root_squash:
        entry.user_mapping = 'NFS_MAP_ROOT'
        add_user_mapping_from_args(entry, args)
    elif args.all_squash:
        entry.user_mapping = 'NFS_MAP_ALL'
        add_user_mapping_from_args(entry, args)
    elif any([args.anon_local, args.anon_uid, args.anon_gid]):
        raise ValueError('Anonymous identity cannot be given if squashing is disabled.')
    else:
        entry.user_mapping = 'NFS_MAP_NONE'

    resp = nfs.nfs_get_export(conninfo, creds, args.ref)

    restrictions = [NFSExportRestriction(r) for r in resp.data['restrictions']]
    # NB: list.insert inserts before, but the host entry list is 1-indexed, so
    # passing position to list.insert unchanged will insert after that position.
    restrictions.insert(
        len(restrictions) if args.insert_after is None else args.insert_after, entry
    )

    return modify_restrictions(conninfo, creds, resp.data, resp.etag, restrictions)


def validate_position(restrictions: NFSExportRestrictions, position: int) -> None:
    if position < 1:
        raise ValueError('Position must be 1 or greater')
    if position > len(restrictions):
        raise ValueError(f'Position {position} is greater than the maximum of {len(restrictions)}')


def do_modify_entry(
    conninfo: Connection, creds: Optional[Credentials], args: argparse.Namespace
) -> RestResponse:
    resp = nfs.nfs_get_export(conninfo, creds, args.ref)
    validate_position(resp.data['restrictions'], args.position)
    restrictions = [NFSExportRestriction(r) for r in resp.data['restrictions']]

    entry = restrictions[args.position - 1]

    if args.hosts is not None:
        entry.host_restrictions = args.hosts if args.hosts != ['*'] else []

    if args.secure is not None:
        entry.require_privileged_port = args.secure

    if args.ro is not None:
        entry.read_only = args.ro

    if args.no_root_squash:
        entry.user_mapping = 'NFS_MAP_NONE'
        entry.map_to_user = None
        entry.map_to_group = None

    if args.root_squash:
        entry.user_mapping = 'NFS_MAP_ROOT'
        add_user_mapping_from_args(entry, args, must_set='map_to_user' not in entry.dictionary())

    if args.all_squash:
        entry.user_mapping = 'NFS_MAP_ALL'
        add_user_mapping_from_args(entry, args, must_set='map_to_user' not in entry.dictionary())

    if any([args.anon_local, args.anon_uid is not None, args.anon_gid is not None]):
        # Note that this must be ordered after setting the map mode above in
        # order for this check to be correct:
        if entry.user_mapping == 'NFS_MAP_NONE':
            raise ValueError('Cannot set anonymous identity on a --no-root-squash export.')

        add_user_mapping_from_args(entry, args)

    return modify_restrictions(conninfo, creds, resp.data, resp.etag, restrictions)


def do_remove_entry(
    conninfo: Connection, creds: Optional[Credentials], args: argparse.Namespace
) -> RestResponse:
    resp = nfs.nfs_get_export(conninfo, creds, args.ref)
    validate_position(resp.data['restrictions'], args.position)

    restrictions = [
        NFSExportRestriction(r)
        for i, r in enumerate(resp.data['restrictions'])
        if i != (args.position - 1)
    ]

    return modify_restrictions(conninfo, creds, resp.data, resp.etag, restrictions)


def add_common_export_args(subparser: argparse.ArgumentParser) -> None:
    """
    Add options to parse the "secure", "ro", "no_root_sqush", "root_squash",
    "all_squash", "anon_local", "anon_uid", and "anon_gid" args.  In the case
    of "secure" and "ro", the value is None when unspecified, which allows
    modify_entry to determine whether those flags are to be changed.
    """

    port = subparser.add_mutually_exclusive_group(required=False)
    # Set up flags to set "secure" either True or False, with the default
    # of None, which means insecure is the default but it is possible to
    # distinguish whether a value was explicitly specified.
    port.add_argument(
        '--insecure',
        action='store_false',
        dest='secure',
        default=None,
        help='Hosts may use any source port to access this export. This is the default option.',
    )
    port.add_argument(
        '--secure',
        action='store_true',
        default=None,
        help=(
            'Require hosts to use privileged ports. Note that this will '
            'deny access to OSX clients that use default mount options.'
        ),
    )
    rw = subparser.add_mutually_exclusive_group(required=False)
    rw.add_argument(
        '--rw',
        action='store_false',
        dest='ro',
        default=None,
        help='Export allows both read and write access. This is the default option.',
    )
    rw.add_argument('--ro', action='store_true', default=None, help='Export is read-only.')
    squash = subparser.add_mutually_exclusive_group(required=False)
    squash.add_argument(
        '--no-root-squash',
        action='store_true',
        help="Don't map any users.  This is the default option.",
    )
    squash.add_argument(
        '--root-squash', action='store_true', help='Map access by root to the anonymous user.'
    )
    squash.add_argument(
        '--all-squash', action='store_true', help='Map all access to the anonymous user.'
    )
    # If a squash option is provided, either --anon-local or both
    # --anon-uid and --anon-gid must be provided (unfortunately it
    # argparse can't validate this completely)
    anon = subparser.add_mutually_exclusive_group(required=False)
    anon.add_argument(
        '--anon-local', type=str_decode, help='The name of a local user to squash to.'
    )
    anon.add_argument('--anon-uid', type=int, help='The NFS UID to squash to.')
    # Unfortunately argparse can't express "these two args must be provided
    # together or not at all, exclusive with this other arg."
    subparser.add_argument(
        '--anon-gid', type=int, help='The NFS GID to squash to, when --anon-uid is given.'
    )


class NFSModExportHostAccessCommand(Subcommand):
    NAME = 'nfs_mod_export_host_access'
    SYNOPSIS = 'Modify the access hosts are granted to an export'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        export = parser.add_mutually_exclusive_group(required=True)
        export.add_argument('--id', type=str_decode, dest='ref', help='ID of export to modify')
        export.add_argument(
            '--export-path', type=str_decode, dest='ref', help='Path of export to modify'
        )
        export.add_argument('--json', action='store_true', help='Print raw response JSON')

        subparsers = parser.add_subparsers(dest='command')
        subparsers.required = True

        # Note that the arg names here are a bit odd because they've been
        # chosen to correspond with equivalent options in /etc/exports
        add_entry = subparsers.add_parser('add_entry', help='Add a new host access entry.')
        add_entry.set_defaults(command=do_add_entry)
        add_entry.add_argument(
            '--hosts',
            '-o',
            type=str_decode,
            required=False,
            nargs='+',
            default=['*'],
            help=(
                "Hosts to grant access to.  '*' matches all.  May be "
                'individual IP addresses, CIDR masks (e.g. 10.1.2.0/24), or '
                'ranges (e.g. 10.2.3.23-47, fd00::42:1fff-c000).  Export will '
                'match all by default.'
            ),
        )
        add_entry.add_argument(
            '--insert-after',
            '-a',
            type=int,
            default=None,
            help=(
                'Insert the new entry after the given position.  By default, '
                'the new entry will be added to the end of the host list.'
            ),
        )
        add_common_export_args(add_entry)

        mod_entry = subparsers.add_parser('modify_entry', help='Modify a host access entry.')
        mod_entry.set_defaults(command=do_modify_entry)
        mod_entry.add_argument(
            '--position',
            '-p',
            required=True,
            type=int,
            help='The position of the entry to be removed.',
        )
        mod_entry.add_argument(
            '--hosts',
            '-o',
            type=str_decode,
            required=False,
            nargs='+',
            default=None,
            help=(
                "Change the hosts granted access.  '*' matches all.  May be "
                'individual IP addresses, CIDR masks (e.g. 10.1.2.0/24), or '
                'ranges (e.g. 10.2.3.23-47, fd00::42:1fff-c000).'
            ),
        )
        add_common_export_args(mod_entry)

        remove_entry = subparsers.add_parser('remove_entry', help='Remove a host access entry.')
        remove_entry.set_defaults(command=do_remove_entry)
        remove_entry.add_argument(
            '--position',
            '-p',
            required=True,
            type=int,
            help='The position of the entry to be removed.',
        )

    @staticmethod
    def main(
        conninfo: Connection, credentials: Optional[Credentials], args: argparse.Namespace
    ) -> None:
        response = args.command(conninfo, credentials, args)
        pretty_print_export(response.data, args.json)


class NFSDeleteExportCommand(Subcommand):
    NAME = 'nfs_delete_export'
    SYNOPSIS = 'Delete an export'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        export = parser.add_mutually_exclusive_group(required=True)
        export.add_argument('--id', type=str_decode, dest='ref', help='ID of export to delete')
        export.add_argument(
            '--export-path', type=str_decode, dest='ref', help='Path of export to delete'
        )

    @staticmethod
    def main(
        conninfo: Connection, credentials: Optional[Credentials], args: argparse.Namespace
    ) -> None:
        nfs.nfs_delete_export(conninfo, credentials, args.ref)
        formatted_ref = f'"{args.ref}"' if args.ref.startswith('/') else args.ref
        print(f'Export {formatted_ref} has been deleted.')


class NFSGetSettingsCommand(Subcommand):
    NAME = 'nfs_get_settings'
    SYNOPSIS = 'Retrieve current NFS server configuration.'

    @staticmethod
    def main(
        conninfo: Connection, credentials: Optional[Credentials], _args: argparse.Namespace
    ) -> None:
        print(nfs.get_nfs_config(conninfo, credentials))


class NFSModifySettingsCommand(Subcommand):
    NAME = 'nfs_modify_settings'
    SYNOPSIS = 'Modify current NFS server configuration.'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument('--enable-v4', action='store_true', dest='v4_enabled')
        group.add_argument('--disable-v4', action='store_false', dest='v4_enabled')

    @staticmethod
    def main(
        conninfo: Connection, credentials: Optional[Credentials], args: argparse.Namespace
    ) -> None:
        settings = {'v4_enabled': args.v4_enabled}
        print(nfs.set_nfs_config(conninfo, credentials, settings))
