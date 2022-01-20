import argparse
from typing import List
import yaml

class Argsy:

    def __init__(self, config_file_name: str = None, config_str: str = None, config_dict: dict = None) -> None:
        self._main_parser = None
        self._sub_parsers = {}

        if config_file_name is not None:
            with open(config_file_name, 'r') as config_file:
                self._arg_def_dict = yaml.load(config_file.read(), Loader=yaml.SafeLoader)
        elif config_str is not None:
            self._arg_def_dict = yaml.load(config_str, Loader=yaml.SafeLoader)
        elif config_dict is not None:
            self._arg_def_dict = config_dict
        else:
            raise Exception('ERROR: No configuration provided.')

        self._build_argparser()

    def _parse_args_dict(self, parser: argparse.ArgumentParser, args: dict):
        for arg_name in args.keys():
            arg = args.get(arg_name)

            if arg.get('cmd_type') == "option":
                name_or_flags=arg.get('flags').split("|")
                parser.add_argument(
                    *name_or_flags,
                    help=arg.get('help'),
                    action=arg.get('action') if arg.get('action') else None,
                    required=arg.get('required'),
                    default=arg.get('default') if arg.get('default') else None,
                )
            elif arg.get('cmd_type') == "position":
                name_or_flags = arg_name
                parser.add_argument(
                    name_or_flags,
                    help=arg.get('help'),
                    metavar=arg.get('metavar') if arg.get('metavar') else None,
                    nargs=arg.get('nargs') if arg.get('nargs') else None,
                )

    def _build_argparser(self):
        program = self._arg_def_dict.get('program')
        self._main_parser = argparse.ArgumentParser(
            prog=program.get('name'),
            description=program.get('description'),
        )

        top_level_args = program.get('args')
        if top_level_args is not None:
            self._parse_args_dict(self._main_parser, top_level_args)

        subcommands = program.get('subcommands')
        subcommand_names = []
        if subcommands is not None:
            subparsers = self._main_parser.add_subparsers(help=subcommands.get('help'))
            subcommands_dict = subcommands.get('cmds')
            if subcommands_dict is not None:
                subcommand_names = list(subcommands_dict.keys())
                for cmd_name in subcommand_names:
                    cmd = subcommands_dict.get(cmd_name)
                    subcommand_parser = subparsers.add_parser(cmd_name, help=cmd.get('help'))
                    self._parse_args_dict(subcommand_parser, cmd.get('args'))
                    self._sub_parsers[cmd_name] = subcommand_parser

    def _parse_args(self, user_args: list):
        # Intersect the user args list and the subcommand names to see what commands were provided
        commands_found = list(set(user_args) & set(self._sub_parsers.keys()))
        user_subcommand = commands_found[0] if len(commands_found) > 0 else None

        return {
            'cmd': user_subcommand,
            'args': self._main_parser.parse_args(user_args).__dict__
        }
        


    def parse_args(self, args: List, print_result = False):
        parse_result = self._parse_args(args)
        if print_result:
            print(parse_result)
        return parse_result

    def show_usage(self, cmd: str = None):
        if cmd is not None:
            parser = self._sub_parsers.get(cmd)
            parser.print_usage()
        else:
            self._main_parser.print_usage()

    def show_help(self, cmd: str = None):
        if cmd is not None:
            parser = self._sub_parsers.get(cmd)
            parser.print_help()
        else:
            self._main_parser.print_help()
            
