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

import argparse

from typing import Optional

import qumulo.lib.opts
import qumulo.rest.shutdown as shutdown

from qumulo.lib.auth import Credentials
from qumulo.lib.request import Connection


def ask_for_shutdown(command: str, target: str) -> bool:
    message = f'Are you sure you want to {command} the {target}'
    return qumulo.lib.opts.ask(command, message)


class RestartCommand(qumulo.lib.opts.Subcommand):
    NAME = 'restart'
    SYNOPSIS = 'Restart the entire machine'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument('--force', action='store_true', dest='force', help='Do not prompt')

    @staticmethod
    def main(
        conninfo: Connection, credentials: Optional[Credentials], args: argparse.Namespace
    ) -> None:
        if args.force or ask_for_shutdown('restart', 'machine'):
            shutdown.restart(conninfo, credentials)
            print('The machine is restarting.')


class HaltCommand(qumulo.lib.opts.Subcommand):
    NAME = 'halt'
    SYNOPSIS = 'Halt the server'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument('--force', action='store_true', dest='force', help='Do not prompt')

    @staticmethod
    def main(
        conninfo: Connection, credentials: Optional[Credentials], args: argparse.Namespace
    ) -> None:
        if args.force or ask_for_shutdown('halt', 'server'):
            shutdown.halt(conninfo, credentials)
            print('The server is halting.')


class RestartClusterCommand(qumulo.lib.opts.Subcommand):
    NAME = 'restart_cluster'
    SYNOPSIS = 'Restart the cluster'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument('--force', action='store_true', dest='force', help='Do not prompt')

    @staticmethod
    def main(
        conninfo: Connection, credentials: Optional[Credentials], args: argparse.Namespace
    ) -> None:
        if args.force or ask_for_shutdown('restart', 'cluster'):
            shutdown.restart_cluster(conninfo, credentials)
            print('The cluster is restarting.')


class HaltClusterCommand(qumulo.lib.opts.Subcommand):
    NAME = 'halt_cluster'
    SYNOPSIS = 'Halt the cluster'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument('--force', action='store_true', dest='force', help='Do not prompt')

    @staticmethod
    def main(
        conninfo: Connection, credentials: Optional[Credentials], args: argparse.Namespace
    ) -> None:
        if args.force or ask_for_shutdown('halt', 'cluster'):
            shutdown.halt_cluster(conninfo, credentials)
            print('The cluster is halting.')
