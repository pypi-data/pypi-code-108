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

# XXX: Please add types to the functions in this file. Static type checking in
# Python prevents bugs!
# mypy: ignore-errors


"""
Share commands
"""

import re
import sys
import textwrap

from argparse import Action, ArgumentParser, Namespace

import qumulo.lib.opts
import qumulo.rest.fs as fs
import qumulo.rest.smb as smb

from qumulo.lib.acl_util import AceTranslator, AclEditor
from qumulo.lib.auth import Credentials
from qumulo.lib.opts import str_decode
from qumulo.lib.request import Connection
from qumulo.lib.util import bool_from_string, tabulate

#     _    ____ _
#    / \  / ___| |
#   / _ \| |   | |
#  / ___ \ |___| |___
# /_/   \_\____|_____|_             _       _   _
# |  \/  | __ _ _ __ (_)_ __  _   _| | __ _| |_(_) ___  _ __
# | |\/| |/ _` | '_ \| | '_ \| | | | |/ _` | __| |/ _ \| '_ \
# | |  | | (_| | | | | | |_) | |_| | | (_| | |_| | (_) | | | |
# |_|  |_|\__,_|_| |_|_| .__/ \__,_|_|\__,_|\__|_|\___/|_| |_|
#                      |_|
# FIGLET: ACL Manipulation

NO_ACCESS = 'NONE'
READ_ACCESS = 'READ'
WRITE_ACCESS = 'WRITE'
CHANGE_PERMISSIONS_ACCESS = 'CHANGE_PERMISSIONS'
ALL_ACCESS = 'ALL'
ALL_RIGHTS = (NO_ACCESS, READ_ACCESS, WRITE_ACCESS, CHANGE_PERMISSIONS_ACCESS, ALL_ACCESS)

ALLOWED_TYPE = 'ALLOWED'
DENIED_TYPE = 'DENIED'

LOCAL_DOMAIN = 'LOCAL'
WORLD_DOMAIN = 'WORLD'
POSIX_USER_DOMAIN = 'POSIX_USER'
POSIX_GROUP_DOMAIN = 'POSIX_GROUP'
AD_DOMAIN = 'ACTIVE_DIRECTORY'

EVERYONE_NAME = 'Everyone'
GUEST_NAME = 'Guest'

# A SID starts with S, followed by hyphen separated version, authority, and at
# least one sub-authority
SID_REGEXP = re.compile(r'S-[0-9]+-[0-9]+(?:-[0-9]+)+$')

VALID_DOMAIN_TYPES = ('local', 'world', 'ldap_user', 'ldap_group', 'ad')
VALID_TRUSTEE_TYPES = VALID_DOMAIN_TYPES + ('name', 'sid', 'uid', 'gid', 'auth_id')


class ShareAceTranslator(AceTranslator):
    def _parse_rights(self, rights):
        api_rights = [r.upper().replace(' ', '_') for r in rights]
        assert all(r in ALL_RIGHTS for r in api_rights)
        return api_rights

    def parse_rights(self, rights, ace):
        ace['rights'] = self._parse_rights(rights)

    def pretty_rights(self, ace):
        # Replace the _ in CHANGE_PERMISSIONS:
        rights = [r.replace('_', ' ') for r in ace['rights']]
        rights = [r.capitalize() for r in rights]
        return ', '.join(rights)

    def ace_rights_equal(self, ace, rights):
        return set(ace['rights']) == set(self._parse_rights(rights))

    @property
    def has_flags(self):
        return False

    # Keeps pylint happy:
    def parse_flags(self, flags, ace):
        raise TypeError('SMB share aces do not have flags.')

    def pretty_flags(self, ace):
        raise TypeError('SMB share aces do not have flags.')

    def ace_flags_equal(self, ace, flags):
        raise TypeError('SMB share aces do not have flags.')


class NetworkAceTranslator(ShareAceTranslator):
    def parse_trustee(self, trustee, ace):
        if trustee == ['*']:
            ace['address_ranges'] = []
        else:
            ace['address_ranges'] = trustee

    def pretty_trustee(self, ace):
        if not ace['address_ranges']:
            return '*'
        else:
            return ', '.join(ace['address_ranges'])

    def ace_trustee_equal(self, ace, trustee):
        return self.parse_trustee(trustee, ace) == ace['address_ranges']


def pretty_share_list(shares):
    headers = ['ID', 'Name', 'Path', 'Description']
    rows = [[row['id'], row['share_name'], row['fs_path'], row['description']] for row in shares]
    return tabulate(rows, headers)


#  _     _     _     ____  _
# | |   (_)___| |_  / ___|| |__   __ _ _ __ ___  ___
# | |   | / __| __| \___ \| '_ \ / _` | '__/ _ \/ __|
# | |___| \__ \ |_   ___) | | | | (_| | | |  __/\__ \
# |_____|_|___/\__| |____/|_| |_|\__,_|_|  \___||___/
# FIGLET: List Shares


class SMBListSharesCommand(qumulo.lib.opts.Subcommand):
    NAME = 'smb_list_shares'
    SYNOPSIS = 'List all SMB shares'

    @staticmethod
    def options(parser: ArgumentParser) -> None:
        parser.add_argument(
            '--json', action='store_true', help='Print JSON representation of shares.'
        )

    @staticmethod
    def main(conninfo: Connection, credentials: Credentials, args: Namespace) -> None:
        res = smb.smb_list_shares(conninfo, credentials)
        if args.json:
            print(res)
        else:
            print(pretty_share_list(res.data))


def _print_share(response, json_fmt, outfile):
    if json_fmt:
        outfile.write(f'{response}\n')
    else:
        body, _etag = response
        outfile.write(
            'ID: {id}\n'
            'Name: {share_name}\n'
            'Path: {fs_path}\n'
            'Description: {description}\n'
            'Access Based Enumeration: '
            '{access_based_enumeration_enabled}\n'
            'Encryption Required: {require_encryption}\n'
            'Default File Create Mode: {default_file_create_mode}\n'
            'Default Directory Create Mode: '
            '{default_directory_create_mode}\n'.format(**body)
        )
        outfile.write('\n')
        outfile.write(
            'Permissions:\n{}\n'.format(
                AclEditor(ShareAceTranslator(), body['permissions']).pretty_str()
            )
        )
        # Network permissions are a niche feature, so don't distract people
        # by telling them all hosts are allowed all access:
        if body['network_permissions'] != smb.ALLOW_ALL_NETWORK_PERMISSIONS:
            net_editor = AclEditor(NetworkAceTranslator(), body['network_permissions'])
            outfile.write(f'\nNetwork Permissions:\n{net_editor.pretty_str()}\n')


class SMBListShareCommand(qumulo.lib.opts.Subcommand):
    NAME = 'smb_list_share'
    SYNOPSIS = 'List a share'

    @staticmethod
    def options(parser: ArgumentParser) -> None:
        share = parser.add_mutually_exclusive_group(required=True)
        share.add_argument('--id', type=int, default=None, help='ID of share to list')
        share.add_argument('--name', type=str_decode, default=None, help='Name of share to list')

        parser.add_argument(
            '--json', action='store_true', default=False, help='Print the raw JSON response.'
        )

    @staticmethod
    def main(conninfo: Connection, credentials: Credentials, args: Namespace) -> None:
        _print_share(
            smb.smb_list_share(conninfo, credentials, args.id, args.name), args.json, sys.stdout
        )


#     _       _     _   ____  _
#    / \   __| | __| | / ___|| |__   __ _ _ __ ___
#   / _ \ / _` |/ _` | \___ \| '_ \ / _` | '__/ _ \
#  / ___ \ (_| | (_| |  ___) | | | | (_| | | |  __/
# /_/   \_\__,_|\__,_| |____/|_| |_|\__,_|_|  \___|
# FIGLET: Add Share


def _add_initial_acl_args(parser):
    # Permissions options:
    exclusive_perms = parser.add_mutually_exclusive_group()
    exclusive_perms.add_argument(
        '--no-access', action='store_true', default=False, help='Grant no access.'
    )
    exclusive_perms.add_argument(
        '--read-only',
        action='store_true',
        default=False,
        help='Grant everyone except guest read-only access.',
    )
    exclusive_perms.add_argument(
        '--all-access',
        action='store_true',
        default=False,
        help='Grant everyone except guest full access.',
    )

    # These are all exclusive with read-only or no-access, but not with
    # all-access or each other, which argparse can't express:
    parser.add_argument(
        '--grant-read-access',
        type=str_decode,
        nargs='+',
        metavar='TRUSTEE',
        help=(
            'Grant read access to these trustees.  e.g. Everyone, '
            'uid:1000, gid:1001, sid:S-1-5-2-3-4, or auth_id:500'
        ),
    )
    parser.add_argument(
        '--grant-read-write-access',
        type=str_decode,
        nargs='+',
        metavar='TRUSTEE',
        help='Grant read-write access to these trustees.',
    )
    parser.add_argument(
        '--grant-all-access',
        type=str_decode,
        nargs='+',
        metavar='TRUSTEE',
        help='Grant all access to these trustees.',
    )
    parser.add_argument(
        '--deny-access',
        type=str_decode,
        nargs='+',
        metavar='TRUSTEE',
        help='Deny all access to these trustees.',
    )


def _create_new_acl(args):
    have_grants = any(
        [
            args.all_access,
            args.grant_read_access,
            args.grant_read_write_access,
            args.grant_all_access,
        ]
    )
    if args.no_access and have_grants:
        raise ValueError('Cannot specify --no-access and grant other access.')
    if args.read_only and have_grants:
        raise ValueError('Cannot specify --read-only and grant other access.')
    if not any([args.no_access, args.read_only, args.deny_access, have_grants]):
        raise ValueError(
            'Must specify initial permissions (--no-access, '
            '--read-only, --all-access, --grant-read-access, etc.)'
        )

    acl = AclEditor(ShareAceTranslator())

    # Note that order shouldn't matter, the AclEditor should always put
    # these ACEs at the beginning, so they will override any grants
    if args.deny_access:
        acl.deny(args.deny_access, [ALL_ACCESS])

    if args.read_only:
        acl.grant([EVERYONE_NAME], [READ_ACCESS])
    if args.all_access:
        acl.grant([EVERYONE_NAME], [ALL_ACCESS])
    if args.grant_read_access:
        acl.grant(args.grant_read_access, [READ_ACCESS])
    if args.grant_read_write_access:
        acl.grant(args.grant_read_write_access, [READ_ACCESS, WRITE_ACCESS])
    if args.grant_all_access:
        acl.grant(args.grant_all_access, [ALL_ACCESS])

    return acl.acl


def _add_network_permissions_args(parser):
    net_group = parser.add_argument_group(
        'Network Permissions',
        'Options for controlling share access by client address. '
        'By default, all hosts are permitted whatever rights are granted by '
        'both share and file permissions.',
    )
    net_group.add_argument(
        '--full-control-hosts',
        type=str_decode,
        nargs='+',
        default=None,
        metavar='RANGE',
        help=(
            'Address ranges which should be permitted all access that '
            'is also granted by share permissions and file permissions. '
            'May be individual IP addresses, CIDR masks (e.g. 10.1.2.0/24), '
            'or ranges (e.g. 10.2.3.23-47, fd00::42:1fff-c000).'
        ),
    )
    net_group.add_argument(
        '--read-only-hosts',
        type=str_decode,
        nargs='+',
        default=None,
        metavar='RANGE',
        help='Address ranges which should be permitted read-only access at most.',
    )
    net_group.add_argument(
        '--deny-hosts',
        type=str_decode,
        nargs='+',
        default=None,
        metavar='RANGE',
        help=(
            'Address ranges which should be denied access to this '
            'share, regardless of other permissions.'
        ),
    )
    net_group.add_argument(
        '--deny-all-hosts',
        default=False,
        action='store_true',
        help='Deny all access to this share.',
    )


def _net_permissions_from_args(args, default):
    have_hosts = (None, None, None) != (
        args.full_control_hosts,
        args.read_only_hosts,
        args.deny_hosts,
    )
    if args.deny_all_hosts:
        if have_hosts:
            raise ValueError('Cannot specify --deny-all-hosts with other host access options')
        return smb.DENY_ALL_NETWORK_PERMISSIONS
    if not have_hosts:
        return default

    editor = AclEditor(NetworkAceTranslator(), [])
    if args.deny_hosts:
        editor.deny([args.deny_hosts], ['All'])
    if args.read_only_hosts:
        # If there are full_control hosts, insert a deny to make sure read_only
        # hosts don't pick up more rights from the full_control ace.
        if args.full_control_hosts:
            editor.deny([args.read_only_hosts], ['Write', 'Change permissions'])
        editor.grant([args.read_only_hosts], ['Read'])
    if args.full_control_hosts:
        editor.grant([args.full_control_hosts], ['All'])
    return editor.acl


class SMBAddShareCommand(qumulo.lib.opts.Subcommand):
    NAME = 'smb_add_share'
    SYNOPSIS = 'Add a new SMB share'

    @staticmethod
    def options(parser: ArgumentParser) -> None:
        parser.add_argument(
            '--name', type=str_decode, default=None, required=True, help='Name of share'
        )
        parser.add_argument(
            '--fs-path', type=str_decode, default=None, required=True, help='File system path'
        )
        parser.add_argument(
            '--description', type=str_decode, default='', help='Description of this share'
        )
        parser.add_argument(
            '--access-based-enumeration-enabled',
            type=bool_from_string,
            default=False,
            metavar='{true,false}',
            help='Enable Access-based Enumeration on this share',
        )
        parser.add_argument(
            '--create-fs-path',
            action='store_true',
            help='Creates the specified file system path if it does not exist',
        )
        parser.add_argument(
            '--default-file-create-mode',
            type=str_decode,
            default=None,
            help=(
                'Default POSIX file create mode bits on this SMB share (octal, 0644 will be used '
                'if not provided)'
            ),
        )
        parser.add_argument(
            '--default-directory-create-mode',
            type=str_decode,
            default=None,
            help=(
                'Default POSIX directory create mode bits on this SMB share (octal, 0755 will be '
                'used if not provided)'
            ),
        )

        parser.add_argument(
            '--require-encryption',
            type=bool_from_string,
            default=False,
            metavar='{true,false}',
            help=(
                'Require all traffic for this share to be encrypted. If true, clients without '
                'encryption capabilities will not be able to connect.'
            ),
        )
        parser.add_argument(
            '--json', action='store_true', default=False, help='Print the raw JSON response.'
        )

        _add_initial_acl_args(parser)
        _add_network_permissions_args(parser)

    @staticmethod
    def main(conninfo, credentials, args, outfile=sys.stdout, smb_mod=smb):
        acl = _create_new_acl(args)
        net_acl = _net_permissions_from_args(args, default=smb.ALLOW_ALL_NETWORK_PERMISSIONS)

        result = smb_mod.smb_add_share(
            conninfo,
            credentials,
            args.name,
            args.fs_path,
            args.description,
            permissions=acl,
            allow_fs_path_create=args.create_fs_path,
            access_based_enumeration_enabled=args.access_based_enumeration_enabled,
            default_file_create_mode=args.default_file_create_mode,
            default_directory_create_mode=args.default_directory_create_mode,
            require_encryption=args.require_encryption,
            network_permissions=net_acl,
        )

        _print_share(result, args.json, outfile)


#  ____       _      _         ____  _
# |  _ \  ___| | ___| |_ ___  / ___|| |__   __ _ _ __ ___
# | | | |/ _ \ |/ _ \ __/ _ \ \___ \| '_ \ / _` | '__/ _ \
# | |_| |  __/ |  __/ ||  __/  ___) | | | | (_| | | |  __/
# |____/ \___|_|\___|\__\___| |____/|_| |_|\__,_|_|  \___|
# FIGLET: Delete Share


class SMBDeleteShareCommand(qumulo.lib.opts.Subcommand):
    NAME = 'smb_delete_share'
    SYNOPSIS = 'Delete a share'

    @staticmethod
    def options(parser: ArgumentParser) -> None:
        share = parser.add_mutually_exclusive_group(required=True)
        share.add_argument('--id', type=int, default=None, help='ID of share to delete')
        share.add_argument('--name', type=str_decode, default=None, help='Name of share to delete')

    @staticmethod
    def main(conninfo, credentials, args, outfile=sys.stdout, smb_mod=smb):
        smb_mod.smb_delete_share(conninfo, credentials, args.id, args.name)
        outfile.write(
            'Share {} has been deleted.\n'.format(args.id if args.id else f'"{args.name}"')
        )


#  __  __           _ _  __         ____  _
# |  \/  | ___   __| (_)/ _|_   _  / ___|| |__   __ _ _ __ ___
# | |\/| |/ _ \ / _` | | |_| | | | \___ \| '_ \ / _` | '__/ _ \
# | |  | | (_) | (_| | |  _| |_| |  ___) | | | | (_| | | |  __/
# |_|  |_|\___/ \__,_|_|_|  \__, | |____/|_| |_|\__,_|_|  \___|
#                           |___/
# FIGLET: Modify Share


class SMBModShareCommand(qumulo.lib.opts.Subcommand):
    NAME = 'smb_mod_share'
    SYNOPSIS = 'Modify a share'

    @staticmethod
    def options(parser: ArgumentParser) -> None:
        share = parser.add_mutually_exclusive_group(required=True)
        share.add_argument('--id', type=int, default=None, help='ID of share to modify')
        share.add_argument('--name', type=str_decode, default=None, help='Name of share to modify')

        parser.add_argument('--new-name', default=None, help='Change SMB share name')
        parser.add_argument(
            '--fs-path', type=str_decode, default=None, help='Change file system path'
        )
        parser.add_argument(
            '--description', type=str_decode, default=None, help='Change description of this share'
        )
        parser.add_argument(
            '--access-based-enumeration-enabled',
            type=bool_from_string,
            default=None,
            metavar='{true,false}',
            help='Change if Access-based Enumeration is enabled on this share',
        )
        parser.add_argument(
            '--create-fs-path',
            action='store_true',
            help='Creates the specified file system path if it does not exist',
        )
        parser.add_argument(
            '--default-file-create-mode',
            type=str_decode,
            default=None,
            help='Change default POSIX file create mode bits (octal) on this SMB share',
        )
        parser.add_argument(
            '--default-directory-create-mode',
            type=str_decode,
            default=None,
            help='Change default POSIX directory create mode bits (octal) on this SMB share',
        )
        parser.add_argument(
            '--require-encryption',
            type=bool_from_string,
            default=False,
            metavar='{true,false}',
            help=(
                'Require all traffic for this share to be encrypted. If true, clients without '
                'encryption capabilities will not be able to connect.'
            ),
        )
        parser.add_argument(
            '--json', action='store_true', default=False, help='Print the raw JSON response.'
        )

        _add_network_permissions_args(parser)

    @staticmethod
    def main(conninfo, credentials, args, outfile=sys.stdout, smb_mod=smb):
        # N.B. Strictly one of args.id and args.name is allowed to be None
        share_info = {'id_': args.id, 'old_name': args.name}

        if args.create_fs_path is True:
            share_info['allow_fs_path_create'] = True

        if args.new_name is not None:
            share_info['share_name'] = args.new_name
        if args.fs_path is not None:
            share_info['fs_path'] = args.fs_path
        if args.description is not None:
            share_info['description'] = args.description
        if args.access_based_enumeration_enabled is not None:
            share_info['access_based_enumeration_enabled'] = args.access_based_enumeration_enabled
        if args.default_file_create_mode is not None:
            share_info['default_file_create_mode'] = args.default_file_create_mode
        if args.default_directory_create_mode is not None:
            share_info['default_directory_create_mode'] = args.default_directory_create_mode
        if args.require_encryption is not None:
            share_info['require_encryption'] = args.require_encryption

        net_acl = _net_permissions_from_args(args, default=None)
        if net_acl is not None:
            share_info['network_permissions'] = net_acl

        _print_share(
            smb_mod.smb_modify_share(conninfo, credentials, **share_info), args.json, outfile
        )


#  __  __           _ _  __
# |  \/  | ___   __| (_)/ _|_   _
# | |\/| |/ _ \ / _` | | |_| | | |
# | |  | | (_) | (_| | |  _| |_| |
# |_|  |_|\___/ \__,_|_|_|  \__, |
#  ___                      |___/     _
# |  _ \ ___ _ __ _ __ ___ (_)___ ___(_) ___  _ __  ___
# | |_) / _ \ '__| '_ ` _ \| / __/ __| |/ _ \| '_ \/ __|
# |  __/  __/ |  | | | | | | \__ \__ \ | (_) | | | \__ \
# |_|   \___|_|  |_| |_| |_|_|___/___/_|\___/|_| |_|___/
# FIGLET: Modify Permissions

TYPE_CHOICES = [t.capitalize() for t in [ALLOWED_TYPE, DENIED_TYPE]]
RIGHT_CHOICES = [t.replace('_', ' ').capitalize() for t in ALL_RIGHTS]


def _put_new_acl(smb_mod, conninfo, creds, share, new_acl, etag, print_json):
    result = smb_mod.smb_modify_share(
        conninfo, creds, id_=share['id'], permissions=new_acl, if_match=etag
    )

    if print_json:
        return str(result)
    else:
        body, etag = result
        return 'New permissions:\n{}'.format(
            AclEditor(ShareAceTranslator(), body['permissions']).pretty_str()
        )


def _get_share(smb_mod, conninfo, creds, _id, name):
    return smb_mod.smb_list_share(conninfo, creds, _id, name)


def do_add_entry(smb_mod, conninfo, creds, args):
    share, etag = _get_share(smb_mod, conninfo, creds, args.id, args.name)

    # Modify:
    translator = ShareAceTranslator()
    acl = AclEditor(translator, share['permissions'])
    ace_type = translator.parse_type_enum_value(args.type)
    if ace_type == ALLOWED_TYPE:
        acl.grant([args.trustee], args.rights)
    else:
        assert ace_type == DENIED_TYPE
        acl.deny([args.trustee], args.rights)

    if args.dry_run:
        return f'New permissions would be:\n{acl.pretty_str()}'

    return _put_new_acl(smb_mod, conninfo, creds, share, acl.acl, etag, args.json)


def do_remove_entry(smb_mod, conninfo, creds, args):
    share, etag = _get_share(smb_mod, conninfo, creds, args.id, args.name)

    # Remove:
    acl = AclEditor(ShareAceTranslator(), share['permissions'])
    acl.remove(
        position=args.position,
        trustee=args.trustee,
        ace_type=args.type,
        rights=args.rights,
        allow_multiple=args.all_matching,
    )

    if args.dry_run:
        return f'New permissions would be:\n{acl.pretty_str()}'

    return _put_new_acl(smb_mod, conninfo, creds, share, acl.acl, etag, args.json)


def do_modify_entry(smb_mod, conninfo, creds, args):
    share, etag = _get_share(smb_mod, conninfo, creds, args.id, args.name)

    acl = AclEditor(ShareAceTranslator(), share['permissions'])
    acl.modify(
        args.position,
        args.old_trustee,
        args.old_type,
        args.old_rights,
        None,
        args.new_trustee,
        args.new_type,
        args.new_rights,
        None,
        args.all_matching,
    )

    if args.dry_run:
        return f'New permissions would be:\n{acl.pretty_str()}'

    return _put_new_acl(smb_mod, conninfo, creds, share, acl.acl, etag, args.json)


def do_replace(smb_mod, conninfo, creds, args):
    share, etag = _get_share(smb_mod, conninfo, creds, args.id, args.name)
    acl = _create_new_acl(args)

    if args.dry_run:
        return 'New permissions would be:\n{}'.format(
            AclEditor(ShareAceTranslator(), acl).pretty_str()
        )

    return _put_new_acl(smb_mod, conninfo, creds, share, acl, etag, args.json)


# This is separate from smb_mode_share because argparse doesn't allow
# sub-commands to be optional.
class SMBModShareAclCommand(qumulo.lib.opts.Subcommand):
    NAME = 'smb_mod_share_permissions'
    SYNOPSIS = "Modify a share's permissions"

    @staticmethod
    def options(parser: ArgumentParser) -> None:
        share = parser.add_mutually_exclusive_group(required=True)
        share.add_argument('--id', type=int, default=None, help='ID of share to modify')
        share.add_argument('--name', type=str_decode, default=None, help='Name of share to modify')

        parser.add_argument(
            '--json', action='store_true', default=False, help='Print the raw JSON response.'
        )

        subparsers = parser.add_subparsers(dest='command')
        subparsers.required = True

        add_entry = subparsers.add_parser(
            'add_entry', help="Add an entry to the share's permissions."
        )
        add_entry.set_defaults(command=do_add_entry)
        add_entry.add_argument(
            '-t',
            '--trustee',
            type=str_decode,
            required=True,
            help=(
                'The trustee to add.  e.g. Everyone, uid:1000, gid:1001, '
                'sid:S-1-5-2-3-4, or auth_id:500'
            ),
        )
        add_entry.add_argument(
            '-y',
            '--type',
            type=str_decode,
            required=True,
            choices=TYPE_CHOICES,
            help='Whether the trustee should be allowed or denied the given rights',
        )
        add_entry.add_argument(
            '-r',
            '--rights',
            type=str_decode,
            nargs='+',
            required=True,
            metavar='RIGHT',
            choices=RIGHT_CHOICES,
            help='The rights that should be allowed or denied.  Choices: '
            + ', '.join(RIGHT_CHOICES),
        )
        add_entry.add_argument(
            '-d',
            '--dry-run',
            action='store_true',
            default=False,
            help='Do nothing; display what the result of the change would be.',
        )

        remove_entry = subparsers.add_parser(
            'remove_entry', help="Remove an entry from the share's permissions"
        )
        remove_entry.set_defaults(command=do_remove_entry)
        remove_entry.add_argument(
            '-p', '--position', type=int, help='The position of the entry to remove.'
        )
        remove_entry.add_argument(
            '-t',
            '--trustee',
            type=str_decode,
            help=(
                'Remove an entry with this trustee.  e.g. Everyone, '
                'uid:1000, gid:1001, sid:S-1-5-2-3-4, or auth_id:500'
            ),
        )
        remove_entry.add_argument(
            '-y',
            '--type',
            type=str_decode,
            choices=TYPE_CHOICES,
            help='Remove an entry of this type',
        )
        remove_entry.add_argument(
            '-r',
            '--rights',
            type=str_decode,
            nargs='+',
            metavar='RIGHT',
            choices=RIGHT_CHOICES,
            help='Remove an entry with these rights.  Choices: ' + ', '.join(RIGHT_CHOICES),
        )
        remove_entry.add_argument(
            '-a',
            '--all-matching',
            action='store_true',
            default=False,
            help='If multiple entries match the arguments, remove all of them',
        )
        remove_entry.add_argument(
            '-d',
            '--dry-run',
            action='store_true',
            default=False,
            help='Do nothing; display what the result of the change would be.',
        )

        modify_entry = subparsers.add_parser(
            'modify_entry', help='Modify an existing permission entry in place'
        )
        modify_entry.set_defaults(command=do_modify_entry)
        modify_entry.add_argument(
            '-p', '--position', type=int, help='The position of the entry to modify.'
        )
        modify_entry.add_argument(
            '--old-trustee',
            type=str_decode,
            help=(
                'Modify an entry with this trustee.  e.g. Everyone, '
                'uid:1000, gid:1001, sid:S-1-5-2-3-4, or auth_id:500'
            ),
        )
        modify_entry.add_argument(
            '--old-type', type=str_decode, choices=TYPE_CHOICES, help='Modify an entry of this type'
        )
        modify_entry.add_argument(
            '--old-rights',
            type=str_decode,
            nargs='+',
            metavar='RIGHT',
            choices=RIGHT_CHOICES,
            help='Modify an entry with these rights.  Choices: ' + ', '.join(RIGHT_CHOICES),
        )
        modify_entry.add_argument(
            '--new-trustee',
            type=str_decode,
            help=(
                'Set the entry to have this trustee.  e.g. Everyone, '
                'uid:1000, gid:1001, sid:S-1-5-2-3-4, or auth_id:500'
            ),
        )
        modify_entry.add_argument(
            '--new-type', type=str_decode, choices=TYPE_CHOICES, help='Set the type of the entry.'
        )
        modify_entry.add_argument(
            '--new-rights',
            type=str_decode,
            nargs='+',
            metavar='RIGHT',
            choices=RIGHT_CHOICES,
            help='Set the rights of the entry.  Choices: ' + ', '.join(RIGHT_CHOICES),
        )
        modify_entry.add_argument(
            '-a',
            '--all-matching',
            action='store_true',
            default=False,
            help='If multiple entries match the arguments, modify all of them',
        )
        modify_entry.add_argument(
            '-d',
            '--dry-run',
            action='store_true',
            default=False,
            help='Do nothing; display what the result of the change would be.',
        )

        replace = subparsers.add_parser(
            'replace',
            help=(
                'Replace any existing share permissions with new permissions. '
                'If no new permissions are specified, all access will be '
                'denied.'
            ),
        )
        replace.add_argument(
            '-d',
            '--dry-run',
            action='store_true',
            default=False,
            help='Do nothing; display what the result of the change would be.',
        )
        _add_initial_acl_args(replace)
        replace.set_defaults(command=do_replace)

    @staticmethod
    def main(conninfo, credentials, args, outfile=sys.stdout, smb_mod=smb):
        outfile.write(f'{args.command(smb_mod, conninfo, credentials, args)}\n')


#                _                 _   _   _
#  ___ _ __ ___ | |__     ___  ___| |_| |_(_)_ __   __ _ ___
# / __| '_ ` _ \| '_ \   / __|/ _ \ __| __| | '_ \ / _` / __|
# \__ \ | | | | | |_) |  \__ \  __/ |_| |_| | | | | (_| \__ \
# |___/_| |_| |_|_.__/___|___/\___|\__|\__|_|_| |_|\__, |___/
#                   |_____|                        |___/
#  FIGLET: smb_settings
#


class SMBModifySettingsCommand(qumulo.lib.opts.Subcommand):
    NAME = 'smb_modify_settings'
    SYNOPSIS = 'Set SMB server settings'

    @staticmethod
    def options(parser: ArgumentParser) -> None:
        parser.add_argument(
            '-e',
            '--encryption-mode',
            help='Server encryption mode to set',
            choices=('NONE', 'PREFERRED', 'REQUIRED'),
            metavar='{none,preferred,required}',
            type=lambda s: s.upper(),
        )

        available_dialects = [
            'SMB2_DIALECT_2_002',
            'SMB2_DIALECT_2_1',
            'SMB2_DIALECT_3_0',
            'SMB2_DIALECT_3_11',
        ]

        class DialectAction(Action):
            def __call__(self, parser, namespace, values, option_strings=None):
                cur_values = getattr(namespace, self.dest)
                if cur_values is None:
                    cur_values = []

                if 'ALL' in values:
                    if len(values) == 1:
                        cur_values = available_dialects
                    else:
                        raise ValueError('The "ALL" supported dialect option must be used alone.')
                else:
                    for val in values:
                        if val in cur_values:
                            raise ValueError('Duplicate dialect "%s".' % val)
                        if val != '':
                            cur_values.append(val)
                setattr(namespace, self.dest, cur_values)

        pretty_available_dialects = ', '.join(available_dialects).lower()
        parser.add_argument(
            '-d',
            '--supported-dialects',
            action=DialectAction,
            type=lambda s: s.upper(),
            choices=available_dialects + ['ALL', ''],
            metavar=('dialect_1', 'dialect_2'),
            nargs='+',
            help=(
                'Space separated set of SMB dialects to allow clients to negotiate. '
                'Specify no dialects (eg. -d "") to turn off SMB for the cluster. Choose '
                f'from the following: {pretty_available_dialects}, or use -d ALL to '
                'allow all supported dialects.'
            ),
        )

        parser.add_argument(
            '--hide-shares-from-unauthorized-hosts',
            type=bool_from_string,
            metavar='{true,false}',
            default=None,
            help=(
                'Share listing will omit shares that the requesting host is '
                'not authorized to connect to.'
            ),
        )
        parser.add_argument(
            '--hide-shares-from-unauthorized-users',
            type=bool_from_string,
            metavar='{true,false}',
            default=None,
            help=(
                'Share listing will omit shares that the requesting user is '
                'not authorized to connect to. Caution: clients that are not '
                'configured for passwordless authentication typically list '
                'shares using guest privileges; this option will typically '
                'hide all shares from such clients.'
            ),
        )
        parser.add_argument(
            '--snapshot-directory-mode',
            choices=['visible', 'hidden', 'disabled'],
            default=None,
            help=(
                'If "visible", a special .snapshot directory will appear in '
                'directory listings at the root of shares, and be accessible '
                'by name in any directory.  If "hidden", the .snapshot '
                'directory will not appear in directory listings, but will '
                'still be accessible by name.  If "disabled", .snapshot '
                'directories will not be accessible, and snapshots will only '
                'be available via e.g. the Restore Previous Versions dialog '
                'on Windows.'
            ),
        )
        parser.add_argument(
            '--bypass-traverse-checking',
            type=bool_from_string,
            metavar='{true,false}',
            default=None,
            help=(
                'Bypass traverse checking for all users and all directories. In '
                'other words, a user trying to access /foo/bar who has permissions to '
                'bar but no permissions to foo can still access bar. Users still need '
                'permissions on foo to see the contents of that directory.'
            ),
        )
        parser.add_argument(
            '--signing-required',
            type=bool_from_string,
            metavar='{true,false}',
            default=None,
            help=(
                'Require that messages must be signed if the user is not guest. '
                'Applies to all SMB shares.'
            ),
        )

    @staticmethod
    def main(conninfo: Connection, credentials: Credentials, args: Namespace) -> None:
        settings_json = {}

        if args.encryption_mode is not None:
            settings_json['session_encryption'] = args.encryption_mode
        if args.supported_dialects is not None:
            settings_json['supported_dialects'] = args.supported_dialects
        if args.hide_shares_from_unauthorized_hosts is not None:
            settings_json[
                'hide_shares_from_unauthorized_hosts'
            ] = args.hide_shares_from_unauthorized_hosts
        if args.hide_shares_from_unauthorized_users is not None:
            settings_json[
                'hide_shares_from_unauthorized_users'
            ] = args.hide_shares_from_unauthorized_users
        if args.snapshot_directory_mode is not None:
            settings_json['snapshot_directory_mode'] = args.snapshot_directory_mode.upper()
        if args.bypass_traverse_checking is not None:
            settings_json['bypass_traverse_checking'] = args.bypass_traverse_checking
        if args.signing_required is not None:
            settings_json['signing_required'] = args.signing_required

        if len(settings_json) == 0:
            raise ValueError('Choose one or more settings to modify')

        print(smb.patch_smb_settings(conninfo, credentials, settings_json))


class SMBGetSettingsCommand(qumulo.lib.opts.Subcommand):
    NAME = 'smb_get_settings'
    SYNOPSIS = 'Get SMB settings'

    @staticmethod
    def main(conninfo: Connection, credentials: Credentials, _args: Namespace) -> None:
        print(smb.get_smb_settings(conninfo, credentials))


class SMBListFileHandlesCommand(qumulo.lib.opts.Subcommand):
    NAME = 'smb_list_file_handles'
    SYNOPSIS = 'List SMB open file handles'

    @staticmethod
    def options(parser: ArgumentParser) -> None:
        parser.add_argument('--page-size', type=int, help='Max files to return per request')
        parser.add_argument(
            '--file-number',
            type=int,
            default=None,
            required=False,
            help=(
                'Limits results to the specified file, as returned from a command '
                'like fs_file_get_attr or fs_read_dir.'
            ),
        )
        parser.add_argument(
            '-p',
            '--resolve-paths',
            action='store_true',
            help='Returns the primary path of the opened file',
        )
        parser.add_argument('--path', help='Path to file', type=str_decode)

    @staticmethod
    def main(conninfo: Connection, credentials: Credentials, args: Namespace) -> None:
        if args.page_size is not None and args.page_size < 1:
            raise ValueError('Page size must be greater than 0')

        file_number = args.file_number
        if args.path:
            file_attr = fs.get_file_attr(conninfo, credentials, path=args.path)
            file_number = file_attr.lookup('file_number')

        resolve_paths = args.resolve_paths or False
        for f in smb.list_file_handles(
            conninfo,
            credentials,
            file_number=file_number,
            limit=args.page_size,
            resolve_paths=resolve_paths,
        ):
            print(f)


class SMBCloseFileHandleCommand(qumulo.lib.opts.Subcommand):
    NAME = 'smb_close_file_handle'
    SYNOPSIS = 'Force close a specified SMB file handle'
    DESCRIPTION = SYNOPSIS + textwrap.dedent(
        """\n
        NOTE: This will prevent the client from sending any new requests for
        this file handle, releasing all locks and forcing the client to reopen
        the file. The client will not be given the opportunity to flush cached
        writes. Proceed with caution!
    """
    )

    @staticmethod
    def options(parser: ArgumentParser) -> None:
        parser.add_argument(
            '--location',
            type=str,
            default=None,
            required=True,
            help='The location of the file handle to close as returned from smb_list_file_handles',
        )

    @staticmethod
    def main(conninfo: Connection, credentials: Credentials, args: Namespace) -> None:
        if type(args.location) is not str:
            raise ValueError('location must be a string')
        message = (
            'Are you sure you want to force close this file? '
            "The client's cached writes will be lost."
        )
        if not qumulo.lib.opts.ask(SMBCloseFileHandleCommand.NAME, message):
            return
        smb.close_smb_file(conninfo, credentials, location=args.location)


class SMBListSessionsCommand(qumulo.lib.opts.Subcommand):
    NAME = 'smb_list_sessions'
    SYNOPSIS = 'List SMB open sessions'

    @staticmethod
    def options(parser: ArgumentParser) -> None:
        parser.add_argument('--page-size', type=int, help='Max sessions to return per request')
        parser.add_argument(
            '--identity',
            type=str,
            default=None,
            required=False,
            help=(
                "List only sessions matching this user's identity in the "
                'form of: [1] A name or a SID optionally qualified with a '
                'domain prefix (e.g "local:name", "S-1-1-0", "name", '
                '"world:Everyone", "ldap_user:name", or "ad:name"), or [2] An '
                'ID type (e.g. "uid:1001", "auth_id:513", "SID:S-1-1-0").'
            ),
        )

    @staticmethod
    def main(conninfo: Connection, credentials: Credentials, args: Namespace) -> None:
        if args.page_size is not None and args.page_size < 1:
            raise ValueError('Page size must be greater than 0')
        for f in smb.list_smb_sessions(
            conninfo, credentials, limit=args.page_size, identity=args.identity
        ):
            print(f)


class SMBCloseSessionsCommand(qumulo.lib.opts.Subcommand):
    NAME = 'smb_close_sessions'
    SYNOPSIS = 'Force close SMB sessions matching one or more of a set of filters.'
    DESCRIPTION = SYNOPSIS + textwrap.dedent(
        """\n
        NOTE: This will prevent the client from sending any new requests for
        this session, releasing all locks and forcing the client to
        reauthenticate. The client will not be given the opportunity to flush
        cached writes. Proceed with caution!
    """
    )
    BATCH_SIZE = 100

    @staticmethod
    def options(parser: ArgumentParser) -> None:
        parser.add_argument(
            '--identity',
            type=str,
            default=None,
            required=False,
            help=(
                "Close only sessions matching this user's identity in the "
                'form of: [1] A name or a SID optionally qualified with a '
                'domain prefix (e.g "local:name", "S-1-1-0", "name", '
                '"world:Everyone", "ldap_user:name", or "ad:name"), or [2] An '
                'ID type (e.g. "uid:1001", "auth_id:513", "SID:S-1-1-0").'
            ),
        )
        parser.add_argument(
            '--location',
            type=str,
            default=None,
            required=False,
            help=(
                'Close only the session with this location, as provided by '
                'an enumeration from smb_list_sessions.'
            ),
        )
        parser.add_argument(
            '--ip',
            type=str,
            default=None,
            required=False,
            help='Close only sessions originating from this ip.',
        )

    @staticmethod
    def main(conninfo, credentials, args, smb_mod=smb, opts_mod=qumulo.lib.opts):
        if all(a is None for a in (args.identity, args.location, args.ip)):
            raise ValueError('One of identity location or ip must be provided')

        sessions = []
        for f in smb_mod.list_smb_sessions(conninfo, credentials, identity=args.identity):
            sessions.extend(f.lookup('session_infos'))

        if args.ip is not None:
            sessions = [i for i in sessions if args.ip == i['originator']]
        if args.location is not None:
            sessions = [i for i in sessions if args.location == i['location']]
        if not sessions:
            raise ValueError('No sessions found to close')

        message = (
            'About to force close (%d) sessions. Client-side cached writes will be lost. Proceed?'
            % len(sessions)
        )
        if not opts_mod.ask(SMBCloseSessionsCommand.NAME, message):
            return

        # We had a customer who had 340k orphaned smb guest sessions. That
        # caused the API to fail because the request's json size was too large.
        # This simple batching of 100 sessions at a time closed all 340k within
        # a few seconds.
        batch_size = SMBCloseSessionsCommand.BATCH_SIZE
        session_batches = [
            sessions[x : x + batch_size] for x in range(0, len(sessions), batch_size)
        ]
        for batch in session_batches:
            smb_mod.close_smb_sessions(conninfo, credentials, batch)
