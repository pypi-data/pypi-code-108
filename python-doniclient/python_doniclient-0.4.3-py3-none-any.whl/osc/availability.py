# Copyright 2021 University of Chicago
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import logging
from argparse import ArgumentTypeError
from typing import TYPE_CHECKING

from dateutil import parser, tz
from keystoneauth1.exceptions import HttpError
from osc_lib import utils
from osc_lib.command import command

from doniclient.osc.common import HardwarePatchCommand

if TYPE_CHECKING:
    from doniclient.v1.client import Client as DoniClient

LOG = logging.getLogger(__name__)
COLUMNS = ("uuid", "start", "end")


def flexible_datetime(date_str):
    try:
        parsed_dt = parser.parse(date_str)
        dt_with_tz = parsed_dt.replace(tzinfo=parsed_dt.tzinfo or tz.gettz())
        return dt_with_tz
    except ValueError:
        raise ArgumentTypeError(f"Not a valid date: '{date_str}'.")


def _add_date_args(parser, required=True):
    parser.add_argument(
        "--start",
        type=flexible_datetime,
        help=("Date for start of availability window"),
        required=required,
    )
    parser.add_argument(
        "--end",
        type=flexible_datetime,
        help=("Date for end of availability window"),
        required=required,
    )


class ListHardwareAvailability(command.Lister):
    """List all availability windows for a given hardware item."""

    columns = COLUMNS

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            dest="hardware_uuid",
            metavar="<hardware_uuid>",
            help=("unique ID of hardware item"),
        )
        return parser

    def take_action(self, parsed_args):
        """List all hw items in Doni."""
        hw_client: "DoniClient" = self.app.client_manager.inventory
        try:
            items = hw_client.get_availability(parsed_args.hardware_uuid)
        except HttpError as ex:
            LOG.error(ex.response.text)
            raise ex

        items_iterator = (
            utils.get_dict_properties(s, self.columns, formatters={}) for s in items
        )
        return (self.columns, items_iterator)


class AddHardwareAvailability(HardwarePatchCommand):
    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        _add_date_args(parser)
        return parser

    def get_patch(self, parsed_args):
        return [
            {
                "op": "add",
                "path": "/availability/-",
                "value": {
                    "start": parsed_args.start,
                    "end": parsed_args.end,
                },
            }
        ]


class UpdateHardwareAvailability(HardwarePatchCommand):
    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            dest="window_uuid",
            metavar="<window_uuid>",
            help=("unique ID of availability window"),
        )
        _add_date_args(parser, required=False)
        return parser

    def get_patch(self, parsed_args):
        patch = []

        for field in ["start", "end"]:
            value = getattr(parsed_args, field)
            if value:
                patch.append(
                    {
                        "op": "replace",
                        "path": f"/availability/{parsed_args.window_uuid}/{field}",
                        "value": value,
                    }
                )

        return patch


class RemoveHardwareAvailability(HardwarePatchCommand):
    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            dest="window_uuid",
            metavar="<window_uuid>",
            help=("unique ID of availability window"),
        )
        return parser

    def get_patch(self, parsed_args):
        return [
            {
                "op": "remove",
                "path": f"/availability/{parsed_args.window_uuid}",
            },
        ]
