# Copyright (c) 2013 Qumulo, Inc.
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

import qumulo.lib.auth
import qumulo.lib.opts
import qumulo.lib.util
import qumulo.rest.analytics as analytics

from qumulo.lib.auth import Credentials
from qumulo.lib.opts import str_decode
from qumulo.lib.request import Connection


class GetTimeSeriesCommand(qumulo.lib.opts.Subcommand):
    NAME = 'time_series_get'
    SYNOPSIS = 'Get specified time series data.'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            '-b',
            '--begin-time',
            default=0,
            help='Begin time for time series intervals, in epoch seconds',
        )

    @staticmethod
    def main(
        conninfo: Connection, credentials: Optional[Credentials], args: argparse.Namespace
    ) -> None:
        print(analytics.time_series_get(conninfo, credentials, args.begin_time))


class GetCurrentActivityCommand(qumulo.lib.opts.Subcommand):
    NAME = 'current_activity_get'
    SYNOPSIS = 'Get the current sampled IOP and throughput rates'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            '-t',
            '--type',
            type=str_decode,
            default=None,
            choices=[
                'file-iops-read',
                'file-iops-write',
                'metadata-iops-read',
                'metadata-iops-write',
                'file-throughput-read',
                'file-throughput-write',
            ],
            help='The specific type of throughput to get',
        )

    @staticmethod
    def main(
        conninfo: Connection, credentials: Optional[Credentials], args: argparse.Namespace
    ) -> None:
        print(analytics.current_activity_get(conninfo, credentials, args.type))


class GetCapacityHistoryCommand(qumulo.lib.opts.Subcommand):
    NAME = 'capacity_history_get'
    SYNOPSIS = 'Get capacity history data.'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            '--begin-time',
            type=int,
            required=True,
            help='Lower bound on history returned, in epoch seconds.',
        )
        parser.add_argument(
            '--end-time',
            type=int,
            required=False,
            help=(
                'Upper bound on history returned, in epoch seconds. '
                'Defaults to the most recent period for which data is '
                'available.'
            ),
        )
        parser.add_argument(
            '--interval',
            type=str_decode,
            default='hourly',
            choices=['hourly', 'daily', 'weekly'],
            help='The interval at which to sample',
        )

    @staticmethod
    def main(
        conninfo: Connection, credentials: Optional[Credentials], args: argparse.Namespace
    ) -> None:
        print(
            analytics.capacity_history_get(
                conninfo, credentials, args.interval, args.begin_time, args.end_time
            )
        )


class GetCapacityHistoryFilesCommand(qumulo.lib.opts.Subcommand):
    NAME = 'capacity_history_files_get'
    SYNOPSIS = 'Get historical largest file data.'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            '--timestamp',
            type=int,
            required=True,
            help='Time period to retrieve, in epoch seconds.',
        )

    @staticmethod
    def main(
        conninfo: Connection, credentials: Optional[Credentials], args: argparse.Namespace
    ) -> None:
        print(analytics.capacity_history_files_get(conninfo, credentials, args.timestamp))
