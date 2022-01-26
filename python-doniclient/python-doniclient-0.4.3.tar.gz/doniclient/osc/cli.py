"""Implements Doni command line interface."""

import argparse
import json
import logging
from argparse import FileType, Namespace

from keystoneauth1.exceptions import Conflict, HttpError
from keystoneauth1.exceptions.http import BadRequest
from osc_lib import utils as oscutils
from osc_lib.command import command

from doniclient.osc.common import (
    BaseParser,
    GroupedAction,
    HardwarePatchCommand,
    HardwareSerializer,
    OutputFormat,
)
from doniclient.v1 import resource_fields as res_fields

LOG = logging.getLogger(__name__)  # Get the logger of this module


class ListHardware(BaseParser, command.Lister):
    """List all hardware in the Doni database."""

    log = logging.getLogger(__name__ + ".ListHardware")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "--all",
            help="List hardware from all owners. Requires admin rights.",
            action="store_true",
        )
        return parser

    def take_action(self, parsed_args):
        """List all hw items in Doni."""
        columns = res_fields.HARDWARE_RESOURCE.fields
        labels = res_fields.HARDWARE_RESOURCE.labels

        hw_client = self.app.client_manager.inventory

        if parsed_args.all:
            data = hw_client.export()
        else:
            data = hw_client.list()

        return (
            labels,
            (
                oscutils.get_dict_properties(
                    s, columns, formatters={"Properties": oscutils.format_dict}
                )
                for s in data
            ),
        )


class GetHardware(BaseParser, command.ShowOne):
    """List specific hardware item in Doni."""

    needs_uuid = True

    def take_action(self, parsed_args):
        """List all hw items in Doni."""
        hw_client = self.app.client_manager.inventory
        try:
            data = hw_client.get_by_uuid(parsed_args.uuid)
        except HttpError as ex:
            LOG.error(ex.response.text)
            raise ex

        return self.dict2columns(data)


class DeleteHardware(BaseParser):
    """Delete specific hardware item in Doni."""

    needs_uuid = True

    def take_action(self, parsed_args):
        hw_client = self.app.client_manager.inventory
        try:
            hw_client.delete(parsed_args.uuid)
        except HttpError as ex:
            LOG.error(ex.response.text)
            raise ex


class SyncHardware(BaseParser):
    """Sync specific hardware item in Doni."""

    needs_uuid = True

    def take_action(self, parsed_args):
        hw_client = self.app.client_manager.inventory
        try:
            hw_client.sync(parsed_args.uuid)
        except HttpError as ex:
            LOG.error(ex.response.text)
            raise ex


class CreateOrUpdateParser(BaseParser):

    needs_uuid = True

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "--name",
            help=(
                "Name of the hardware object. Best practice is to use a "
                "universally unique identifier, such has serial number or chassis ID. "
                "This will aid in disambiguating systems."
            ),
        )
        parser.add_argument(
            "--hardware_type",
            default="baremetal",
            help=("hardware_type of item"),
        )

        properties = parser.add_argument_group("properties")

        properties.add_argument(
            "--mgmt_addr",
            metavar="<mgmt_addr>",
            dest="properties.mgmt_addr",
            action=GroupedAction,
        )
        properties.add_argument(
            "--ipmi_username",
            metavar="<ipmi_username>",
            dest="properties.ipmi_username",
            action=GroupedAction,
        )
        properties.add_argument(
            "--ipmi_password",
            metavar="<ipmi_password>",
            dest="properties.ipmi_password",
            action=GroupedAction,
        )
        properties.add_argument(
            "--ipmi_terminal_port",
            metavar="<ipmi_terminal_port>",
            dest="properties.ipmi_terminal_port",
            action=GroupedAction,
            type=int,
        )
        properties.add_argument(
            "--deploy_kernel",
            metavar="<deploy_kernel>",
            dest="properties.baremetal_deploy_kernel_image",
            action=GroupedAction,
        )
        properties.add_argument(
            "--deploy_ramdisk",
            metavar="<deploy_ramdisk>",
            dest="properties.baremetal_deploy_ramdisk_image",
            action=GroupedAction,
        )
        properties.add_argument(
            "--ironic_driver",
            metavar="<ironic_driver>",
            dest="properties.baremetal_driver",
            action=GroupedAction,
        )
        properties.add_argument(
            "--resource_class",
            metavar="<resource_class>",
            default="baremetal",
            dest="properties.baremetal_resource_class",
            action=GroupedAction,
        )
        properties.add_argument(
            "--cpu_arch",
            metavar="<cpu_arch>",
            default="x86_64",
            dest="properties.cpu_arch",
            action=GroupedAction,
        )
        properties.add_argument(
            "--blazar_node_type",
            metavar="<blazar_node_type>",
            dest="properties.node_type",
            action=GroupedAction,
        )
        properties.add_argument(
            "--blazar_su_factor",
            metavar="<blazar_su_factor>",
            dest="properties.su_factor",
            type=float,
            default=1.0,
            action=GroupedAction,
        )
        properties.add_argument(
            "--placement",
            metavar="<placement>",
            dest="properties.placement",
            action=GroupedAction,
            type=json.loads,
        )
        properties.add_argument(
            "--capabilities",
            metavar="<capabilities>",
            dest="properties.baremetal_capabilities",
            action=GroupedAction,
            type=json.loads,
        )

        properties.add_argument(
            "--interfaces",
            default={},
            dest="properties.interfaces",
            type=json.loads,
            help="specify interfaces directly as json dict",
            action=GroupedAction,
        )

        # interfaces = parser.add_argument_group("interfaces")

        # interfaces.add_argument("--iface_mac")
        # interfaces.add_argument("--iface_name")
        # interfaces.add_argument("--switch_id")
        # interfaces.add_argument("--switch_info")
        # interfaces.add_argument("--switch_port_id")

        return parser


class CreateHardware(CreateOrUpdateParser):
    """Create a Hardware Object in Doni."""

    def get_parser(self, prog_name):
        return super().get_parser(prog_name)

    def take_action(self, parsed_args: Namespace):
        """Create new HW item."""
        # Call superclass action to parse input json
        super().take_action(parsed_args)

        hw_client = self.app.client_manager.inventory

        body = {
            "name": parsed_args.name,
            "hardware_type": parsed_args.hardware_type,
            "properties": parsed_args.properties,
        }

        if parsed_args.dry_run:
            LOG.warn(parsed_args)
            LOG.warn(body)
            return

        try:
            data = hw_client.create(body)
        except HttpError as ex:
            LOG.error(ex.response.text)
            raise ex


class UpdateHardware(CreateOrUpdateParser, HardwarePatchCommand):
    """Update properties of existing hardware item."""

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)

        args_to_default = ("name", "hardware_type", "properties")
        # Unset all defaults to avoid accidental changes
        for arg in parser._get_optional_actions():
            if arg.dest in args_to_default:
                arg.default = argparse.SUPPRESS

        return parser

    def get_patch(self, parsed_args):
        patch = []

        field_map = {
            "name": "name",
            "hardware_type": "hardware_type",
        }

        for key, val in field_map.items():
            arg = getattr(parsed_args, key, None)
            if arg:
                patch.append({"op": "add", "path": f"/{val}", "value": arg})

        try:
            for key, val in parsed_args.properties.items():
                patch.append({"op": "add", "path": f"/properties/{key}", "value": val})
        except AttributeError:
            pass

        return patch


class ImportHardware(BaseParser):
    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "--skip_existing",
            help="continue if an item already exists, rather than exiting",
            action="store_true",
        )
        parser.add_argument("-f", "--file", help="JSON input file", type=FileType("r"))
        return parser

    def take_action(self, parsed_args):
        hw_client = self.app.client_manager.inventory
        with parsed_args.file as f:
            for item in json.load(f):
                if parsed_args.dry_run:
                    LOG.warn(item)
                else:
                    try:
                        data = hw_client.create(item)
                    except Conflict as ex:
                        LOG.error(ex.response.text)
                        if parsed_args.skip_existing:
                            continue
                        else:
                            raise ex
                    else:
                        LOG.debug(data)
