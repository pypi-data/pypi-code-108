import sys

import click

from sotooncli import param_types
from sotooncli.core.command import ExecutableCommand, GroupCommand
from sotooncli.core.param import SotoonArgument, SotoonBooleanFlag, SotoonOption
from sotooncli.param_types import LIST, ChoiceParamType
from sotooncli.sotoon.cache import cache
from sotooncli.sotoon.config import config
from sotooncli.sotoon.options import get_version_option

sotoon_commands = [config, cache]
sotoon_options = [get_version_option()]


class CliRepo:
    def __init__(self, data):
        self.data = data

    def get_cli(self):
        sotoon = self._get_group(self.data)
        sotoon.params += sotoon_options
        for cmd in sotoon_commands:
            sotoon.add_command(cmd)
        return sotoon

    @staticmethod
    def _get_group(data, parent=None):
        args, opts = CliRepo._get_param(data)
        group = GroupCommand(
            data["name"], data["description"], data["capsule"], args, opts, parent
        )
        for subcommand_data in data["commands"]:
            if subcommand_data["is_group"]:
                subcommand = CliRepo._get_group(subcommand_data, group)
            else:
                subcommand = CliRepo._get_command(subcommand_data, group)
            group.add_command(subcommand)
        return group

    @staticmethod
    def _get_command(data, parent):
        args, opts = CliRepo._get_param(data)
        cmd = ExecutableCommand(
            data["name"], data["description"], data["capsule"], args, opts, parent
        )
        return cmd

    @staticmethod
    def _get_param(data):
        args = []
        opts = []
        for param_data in data["args"]:
            param_type = CliRepo._get_param_type(
                param_data["type"], param_data["choices"]
            )
            if param_data["is_positional"]:
                if param_type == LIST:
                    arg = SotoonArgument(
                        name=param_data["name"],
                        placeholder=param_data["placeholder"],
                        description=param_data["description"],
                        is_required=param_data["is_required"],
                        default_value=param_data["default"],
                        param_type=param_type,
                    )
                else:
                    arg = SotoonArgument(
                        name=param_data["name"],
                        placeholder=param_data["placeholder"],
                        description=param_data["description"],
                        is_required=param_data["is_required"],
                        default_value=param_data["default"],
                        param_type=param_type,
                    )
                args.append(arg)
            else:
                if param_type == click.BOOL:
                    opt = SotoonBooleanFlag(
                        name=param_data["name"],
                        placeholder=param_data["placeholder"],
                        description=param_data["description"],
                        is_required=param_data["is_required"],
                        default_value=param_data["default"],
                        short_name=param_data["short_name"],
                    )
                else:
                    opt = SotoonOption(
                        name=param_data["name"],
                        placeholder=param_data["placeholder"],
                        description=param_data["description"],
                        is_required=param_data["is_required"],
                        default_value=param_data["default"],
                        param_type=param_type,
                        short_name=param_data["short_name"],
                    )
                opts.append(opt)
        return args, opts

    @staticmethod
    def _get_param_type(type_str, choices):
        if choices:
            return ChoiceParamType(
                CliRepo._get_param_type(type_str, None), choices=choices
            )
        elif type_str == "int":
            return click.INT
        elif type_str == "string":
            return click.STRING
        elif type_str == "bool":
            return click.BOOL
        elif type_str == "map":
            return param_types.MAP
        elif type_str == "slice":
            return param_types.LIST
        elif type_str == "float":
            return click.FLOAT
        elif type_str == "textFile":
            return param_types.FILE
        else:
            click.echo(
                f'CLI doesn\'t support type "{type_str}", you need to upgrade your CLI.'
            )
            sys.exit(1)
