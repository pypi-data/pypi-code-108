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

import argparse

from typing import Mapping, Optional, Sequence

import qumulo.lib.opts
import qumulo.rest.fs as fs
import qumulo.rest.tree_delete as tree_delete

from qumulo.lib.auth import Credentials
from qumulo.lib.request import Connection
from qumulo.lib.util import humanize, tabulate


def make_table(jobs: Sequence[Mapping[str, object]]) -> str:
    headers = ['id', 'initial_capacity', 'remaining_capacity', 'create_time', 'initial_path']
    rows = [[job[header] for header in headers] for job in jobs]
    return tabulate(rows, headers)


class ListCommand(qumulo.lib.opts.Subcommand):
    NAME = 'tree_delete_list'
    SYNOPSIS = 'Get information about all tree delete jobs'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument('--json', action='store_true', help='Output JSON instead of table.')

    @staticmethod
    def main(
        conninfo: Connection, credentials: Optional[Credentials], args: argparse.Namespace
    ) -> None:
        results = tree_delete.list_jobs(conninfo, credentials)
        if args.json:
            print(results)
        else:
            print(make_table(results.data['jobs']))


class CreateCommand(qumulo.lib.opts.Subcommand):
    NAME = 'tree_delete_create'
    SYNOPSIS = 'Create delete job'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument('id', help='Directory id or path')
        parser.add_argument(
            '--force',
            '-f',
            action='store_true',
            help=(
                'Bypass path confirmation. WARNING! Tree delete can be canceled with '
                'tree_delete_cancel, but already deleted items cannot be recovered.'
            ),
        )

    @staticmethod
    def main(
        conninfo: Connection, credentials: Optional[Credentials], args: argparse.Namespace
    ) -> None:
        dir_path: Optional[str] = None
        dir_id: str

        if args.id.startswith('/'):
            dir_path = args.id
            dir_id = fs.get_file_attr(conninfo, credentials, path=args.id).data['id']
        else:
            dir_id = args.id

        if not args.force:
            if not dir_path:
                dir_path = fs.get_file_attr(conninfo, credentials, id_=dir_id).data['path']

            aggregates = fs.read_dir_aggregates(conninfo, credentials, id_=dir_id).data
            num_files = aggregates['total_files']
            total_capacity = humanize(int(aggregates['total_capacity']))

            message = (
                f'WARNING! Are you sure that you want to delete all {num_files} '
                f'files (total size: {total_capacity}) in "{dir_path}"?'
            )

            if not qumulo.lib.opts.ask(CreateCommand.NAME, message):
                return

        tree_delete.create_job(conninfo, credentials, dir_id)


class GetCommand(qumulo.lib.opts.Subcommand):
    NAME = 'tree_delete_get'
    SYNOPSIS = 'Get information about one delete job'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument('id', help='Directory id')
        parser.add_argument('--json', action='store_true', help='Output JSON instead of table.')

    @staticmethod
    def main(
        conninfo: Connection, credentials: Optional[Credentials], args: argparse.Namespace
    ) -> None:
        results = tree_delete.get_job(conninfo, credentials, args.id)
        if args.json:
            print(results)
        else:
            print(make_table([results.data]))


class CancelCommand(qumulo.lib.opts.Subcommand):
    NAME = 'tree_delete_cancel'
    SYNOPSIS = 'Cancel delete job'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument('id', help='Directory id')

    @staticmethod
    def main(
        conninfo: Connection, credentials: Optional[Credentials], args: argparse.Namespace
    ) -> None:
        tree_delete.cancel_job(conninfo, credentials, args.id)
