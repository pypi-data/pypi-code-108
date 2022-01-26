import argparse
import json
import logging
from argparse import FileType, Namespace

import yaml
from cliff.columns import FormattableColumn
from keystoneauth1.exceptions import HttpError
from osc_lib import utils as osc_utils
from osc_lib.command import command

LOG = logging.getLogger(__name__)  # Get the logger of this module


class OutputFormat:
    columns = (
        "uuid",
        "name",
        "project_id",
        "hardware_type",
        "properties",
    )


class YamlColumn(FormattableColumn):
    def human_readable(self):
        return yaml.dump(self._value)


class HardwareSerializer(object):
    def serialize_hardware(self, hw_dict: "dict", columns: "list[str]"):
        return osc_utils.get_dict_properties(
            hw_dict,
            columns,
            formatters={
                "properties": YamlColumn,
                "workers": YamlColumn,
            },
        )


class GroupedAction(argparse.Action):
    """Set property based on dest.key."""

    def __call__(self, parser, namespace, values, option_string=None):
        group, dest = self.dest.split(".", 2)

        try:
            group_dict = getattr(namespace, group)
        except AttributeError:
            group_dict = {}
        group_dict.update({dest: values})
        setattr(namespace, group, group_dict)


class BaseParser(command.Command):
    """Base Parser for use with Doni commands.

    Behavior is to take arguments in the following forms, with later ones
    overriding earlier.
    - argparse "default" values
    - cli args
    - serialized json string (or json file for bulk)
    """

    needs_uuid = False

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument("-d", "--dry-run", "--dry_run", action="store_true")
        parser.add_argument(
            "--json",
            default={},
            type=json.loads,
            help="Take args as json string. Values are overridden by other args.",
        )
        if self.needs_uuid:
            parser.add_argument(
                dest="uuid",
                metavar="<uuid>",
                help=("unique ID of hardware item"),
            )

        return parser

    def take_action(self, parsed_args: Namespace):
        """This allows setting arbitrary args via json input."""

        # Get dict of args without json string
        args_dict = vars(parsed_args)
        try:
            # convert json input to dict, remove from namespace
            json_dict = args_dict.get("json", {})
            # override parsed_args with json values
            args_dict.update(json_dict)
        except AttributeError:
            pass


class HardwarePatchCommand(BaseParser, HardwareSerializer):
    def get_patch(self, parsed_args):
        return []

    def take_action(self, parsed_args):
        hw_client = self.app.client_manager.inventory
        hw_uuid = parsed_args.uuid

        patch = self.get_patch(parsed_args)

        if parsed_args.dry_run:
            LOG.warn(patch)
            return None

        if patch:
            try:
                LOG.debug(f"PATCH_BODY:{patch}")
                res = hw_client.update(hw_uuid, patch)
            except HttpError as ex:
                LOG.error(ex.response.text)
                raise ex
            else:
                return self.serialize_hardware(res.json(), list(OutputFormat.columns))
        else:
            LOG.info("No updates to send")
