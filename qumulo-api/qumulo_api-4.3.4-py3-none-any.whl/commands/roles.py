# Copyright (c) 2019 Qumulo, Inc.
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

import re
import sys
import textwrap

from argparse import ArgumentParser, Namespace

import qumulo.lib.opts
import qumulo.rest.roles as roles

from qumulo.lib.auth import Credentials
from qumulo.lib.identity_util import Identity
from qumulo.lib.opts import str_decode
from qumulo.lib.request import Connection, pretty_json
from qumulo.lib.util import TextAligner


class ListRolesCommand(qumulo.lib.opts.Subcommand):
    NAME = 'auth_list_roles'
    SYNOPSIS = 'List all of the roles.'

    @staticmethod
    def print_roles(auth_roles, all_members, aligner):
        for role_name, role in sorted(auth_roles.items()):
            aligner.add_line(role_name)
            with aligner.indented():
                ListRoleCommand.print_role(role, all_members[role_name], aligner)
            aligner.add_line('')

    @staticmethod
    def options(parser: ArgumentParser) -> None:
        parser.add_argument(
            '--json', action='store_true', help='Print JSON representation of auth roles.'
        )

    @staticmethod
    def main(conninfo: Connection, credentials: Credentials, args: Namespace) -> None:
        auth_roles = roles.list_roles(conninfo, credentials)

        if args.json:
            print(auth_roles)
        else:
            aligner = TextAligner()
            role_members = {
                role: roles.list_members(conninfo, credentials, role).data['members']
                for role in auth_roles.data
            }
            ListRolesCommand.print_roles(auth_roles.data, role_members, aligner)
            aligner.write(sys.stdout)


class ListRoleCommand(qumulo.lib.opts.Subcommand):
    NAME = 'auth_list_role'
    SYNOPSIS = 'List a role.'

    @staticmethod
    def _filter_member_info(info):
        return info[0] not in ['domain', 'name'] and info[1] is not None

    @staticmethod
    def print_role(role, members, aligner):
        aligner.add_line(role['description'])
        aligner.add_line('Members:')
        with aligner.indented():
            for member in members.values():
                name = member['name']
                if name is None or name == '':
                    name = 'auth_id:{}'.format(member['auth_id'])
                aligner.add_line(name)
                with aligner.indented():
                    aligner.add_wrapped_table(
                        sorted(filter(ListRoleCommand._filter_member_info, member.items()))
                    )

    @staticmethod
    def options(parser: ArgumentParser) -> None:
        parser.add_argument(
            '-r', '--role', type=str_decode, required=True, help='Name of the role to lookup'
        )
        parser.add_argument(
            '--json', action='store_true', help='Print JSON representation of auth role.'
        )

    @staticmethod
    def main(conninfo: Connection, credentials: Credentials, args: Namespace) -> None:
        role = roles.list_role(conninfo, credentials, args.role).data
        members = roles.list_members(conninfo, credentials, args.role).data['members']
        if args.json:
            # There is no separate command to get members so show both json
            # results for this command.
            print(pretty_json([role, members]))
        else:
            aligner = TextAligner()
            ListRoleCommand.print_role(role, members, aligner)
            aligner.write(sys.stdout)


class CreateRoleCommand(qumulo.lib.opts.Subcommand):
    NAME = 'auth_create_role'
    SYNOPSIS = 'Create a custom role.'

    @staticmethod
    def options(parser: ArgumentParser) -> None:
        parser.add_argument(
            '-r', '--role', type=str_decode, required=True, help='Name of the role to create'
        )
        parser.add_argument(
            '-d',
            '--description',
            type=str_decode,
            default='No description',
            help='Description of the new role',
        )
        parser.add_argument(
            '-p',
            '--privileges-file',
            type=str_decode,
            help='File with privileges for the role (see auth_list_privileges)',
        )

    @staticmethod
    def main(conninfo: Connection, credentials: Credentials, args: Namespace) -> None:
        privileges = []
        if args.privileges_file:
            all_privileges = frozenset(roles.list_privileges(conninfo, credentials).data)
            with open(args.privileges_file, 'rb') as f:
                privileges = ListPrivilegesCommand.parse(all_privileges, f)

        roles.create_role(conninfo, credentials, args.role, args.description, privileges)


class ModifyRoleCommand(qumulo.lib.opts.Subcommand):
    NAME = 'auth_modify_role'
    SYNOPSIS = 'Modify a custom role.'

    @staticmethod
    def options(parser: ArgumentParser) -> None:
        parser.add_argument(
            '-r', '--role', type=str_decode, required=True, help='Name of the role to modify'
        )
        parser.add_argument(
            '-d', '--description', type=str_decode, help='New description of the role'
        )

        privilege_args = parser.add_argument_group('Privileges')
        privilege_args.add_argument(
            '-p',
            '--privileges-file',
            type=str_decode,
            help=(
                "Overwrite the role's privileges with output from "
                'auth_list_privileges, cannot be used with -G or -R'
            ),
        )
        privilege_args.add_argument(
            '-G',
            '--grant',
            metavar='PRIVILEGE',
            nargs='+',
            type=str_decode,
            default=[],
            help='Privilege to add to this role (may be repeated)',
        )
        privilege_args.add_argument(
            '-R',
            '--revoke',
            metavar='PRIVILEGE',
            nargs='+',
            type=str_decode,
            default=[],
            help='Privilege to remove from this role (may be repeated)',
        )

    @staticmethod
    def compute_new_privileges(all_privileges, initial_privileges, grant, revoke):
        granted = frozenset(grant)
        revoked = frozenset(revoke)
        if not (granted or revoked):
            return []

        assert not (granted & revoked), 'Privileges cannot be both granted and revoked {}'.format(
            granted & revoked
        )

        ListPrivilegesCommand.validate_privileges(all_privileges, granted | revoked)

        already_revoked = revoked & (all_privileges - initial_privileges)
        if already_revoked:
            print('Skipping already revoked privilege: {}'.format(', '.join(already_revoked)))

        already_granted = granted & initial_privileges
        if already_granted:
            print('Skipping already granted privilege: {}'.format(', '.join(already_granted)))

        return (initial_privileges | granted) - revoked

    @staticmethod
    def main(conninfo: Connection, credentials: Credentials, args: Namespace) -> None:
        all_privileges = frozenset(roles.list_privileges(conninfo, credentials).data)
        etag = None
        final_privileges = None
        if args.privileges_file:
            assert not args.grant, '--grant is illegal with --privileges-file'
            assert not args.revoke, '--revoke is illegal with --privileges-file'
            with open(args.privileges_file, 'rb') as f:
                final_privileges = ListPrivilegesCommand.parse(all_privileges, f)
        elif args.grant or args.revoke:
            initial_role = roles.list_role(conninfo, credentials, args.role)
            etag = initial_role.etag
            initial_privileges = frozenset(initial_role.data['privileges'])
            final_privileges = ModifyRoleCommand.compute_new_privileges(
                all_privileges, initial_privileges, args.grant, args.revoke
            )

        roles.modify_role(
            conninfo, credentials, args.role, args.description, final_privileges, etag
        )


class DeleteRoleCommand(qumulo.lib.opts.Subcommand):
    NAME = 'auth_delete_role'
    SYNOPSIS = 'Delete a custom role.'

    @staticmethod
    def options(parser: ArgumentParser) -> None:
        parser.add_argument(
            '-r', '--role', type=str_decode, required=True, help='Name of the role to delete'
        )

    @staticmethod
    def main(conninfo: Connection, credentials: Credentials, args: Namespace) -> None:
        roles.delete_role(conninfo, credentials, args.role)


def get_api_id_from_trustee(trustee):
    return Identity(trustee).dictionary()


class AssignRoleCommand(qumulo.lib.opts.Subcommand):
    NAME = 'auth_assign_role'
    SYNOPSIS = 'Assign a user to a role'

    @staticmethod
    def options(parser: ArgumentParser) -> None:
        parser.add_argument(
            '-r', '--role', type=str_decode, required=True, help='Name of the role to assign'
        )
        parser.add_argument(
            '-t',
            '--trustee',
            type=str_decode,
            required=True,
            help=(
                'Assign the role to this trustee.  e.g. Everyone, '
                'uid:1000, gid:1001, sid:S-1-5-2-3-4, or auth_id:500'
            ),
        )

    @staticmethod
    def main(conninfo: Connection, credentials: Credentials, args: Namespace) -> None:
        api_id = get_api_id_from_trustee(args.trustee)
        roles.add_member(conninfo, credentials, args.role, **api_id)


class UnassignRoleCommand(qumulo.lib.opts.Subcommand):
    NAME = 'auth_unassign_role'
    SYNOPSIS = 'Unassign a user from a role'

    @staticmethod
    def options(parser: ArgumentParser) -> None:
        parser.add_argument(
            '-r', '--role', type=str_decode, required=True, help='Name of the role to unassign'
        )
        parser.add_argument(
            '-t',
            '--trustee',
            type=str_decode,
            required=True,
            help=(
                'Unassign the role from this trustee.  e.g. Everyone, '
                'uid:1000, gid:1001, sid:S-1-5-2-3-4, or auth_id:500'
            ),
        )

    @staticmethod
    def main(conninfo: Connection, credentials: Credentials, args: Namespace) -> None:
        api_id = get_api_id_from_trustee(args.trustee)
        roles.remove_member(conninfo, credentials, args.role, **api_id)


class ListPrivilegesCommand(qumulo.lib.opts.Subcommand):
    NAME = 'auth_list_privileges'
    SYNOPSIS = 'List all privileges or privileges associated with a role.'
    DESCRIPTION = textwrap.dedent(
        """\
        List all privileges or privileges associated with a role.  Redirect to a file
        for use with auth_create_role or auth_modify_role. To start from privileges on
        an existing role, specify --role and --verbose.
    """
    )

    @staticmethod
    def print_privileges(privileges, json, denied=()):
        if json:
            print(pretty_json(privileges))
            return
        for privilege_name, description in sorted(privileges.items()):
            prefix = '# Deny ' if privilege_name in denied else ''
            print(f'{prefix}{privilege_name}: {description}')

    @staticmethod
    def validate_privileges(all_privileges, questionable_privileges):
        invalid_privileges = set(questionable_privileges) - set(all_privileges)
        assert not invalid_privileges, 'Unknown privilege {}'.format(', '.join(invalid_privileges))

    @staticmethod
    def parse(all_privileges, privileges_file):
        result = []
        for lineno, line in enumerate(privileges_file.readlines()):
            line = line.decode('utf-8')
            if len(line.strip()) == 0 or line[0] == '#':
                continue
            privilege_match = re.match(r'^PRIVILEGE_[A-Z_]+(\b|$)', line)
            assert privilege_match, (
                'Ambiguous line {} in privileges file. Each line must '
                "start with a '#' or an ALL CAPS privilege".format(lineno)
            )
            result.append(line[: privilege_match.end()])
        ListPrivilegesCommand.validate_privileges(all_privileges, result)
        return result

    @staticmethod
    def options(parser: ArgumentParser) -> None:
        parser.add_argument(
            '-r', '--role', type=str_decode, help='List privileges associated with a role.'
        )
        parser.add_argument(
            '-v',
            '--verbose',
            action='store_true',
            help='Show granted and denied privileges with --role.',
        )
        parser.add_argument(
            '--json', action='store_true', help='Print JSON representation of the privileges.'
        )

    @staticmethod
    def main(conninfo: Connection, credentials: Credentials, args: Namespace) -> None:
        privileges = roles.list_privileges(conninfo, credentials).data
        if not args.role:
            assert not args.verbose, '--verbose requires --role'
            ListPrivilegesCommand.print_privileges(privileges, args.json)
            return

        role = roles.list_role(conninfo, credentials, args.role).data
        granted = {p: privileges[p] for p in role['privileges']}
        denied = [p for p in privileges if p not in granted]

        assert not (args.verbose and args.json), '--verbose is meaningless with --json'
        shown_privileges = privileges if args.verbose else granted
        ListPrivilegesCommand.print_privileges(shown_privileges, args.json, denied)
