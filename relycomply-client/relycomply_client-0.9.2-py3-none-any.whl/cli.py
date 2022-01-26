import argparse
from base64 import b64encode
import json
import logging
import sys
import textwrap
from dataclasses import dataclass
from json.decoder import JSONDecodeError
from typing import Any, Dict

import toml
import yaml
from gql.transport.exceptions import TransportQueryError
from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexers import JsonLexer, TOMLLexer, YamlLexer

# from pygments_graphql import GraphqlLexer
from tabulate import tabulate
from termcolor import cprint

from relycomply_client.helpers import uppercase_dict

from . import RelyComplyGQLClient, cleartoml
from .exceptions import RelyComplyCliException, RelyComplyClientException


@dataclass
class CliArguments:
    type: str
    action: str
    # explain: bool
    debug: bool
    output_format: str
    variables: Dict[str, Any]


class RelyComplyCLI:
    def __init__(self, **credentials):        
        self._gql = None
        self.credentials = credentials

    @property
    def gql(self):
        if not self._gql:
            self._gql = RelyComplyGQLClient(**self.credentials)
        return self._gql

    def run_command(self, args):
        try:
            cli_args = self.parse_args(args)
            if cli_args.debug:
                logging.root.setLevel(logging.DEBUG)
                logging.root.addHandler(logging.StreamHandler())
            result = self.execute_from_args(args)
            formatted_output = self.format_output(cli_args, result)
            print(formatted_output)
        except RelyComplyClientException as e:
            self.print_error(str(e))
        except TransportQueryError as e:
            self.print_error(e.errors[0]["message"])

    def execute_from_args(self, args):
        cli_args = self.parse_args(args)
        return self.execute(cli_args.type, cli_args.action, cli_args.variables)

    def get_argument_parser(self):
        parser = argparse.ArgumentParser(
            prog="rely",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description="A command line interface for the RelyComply platform",
            epilog=textwrap.dedent(
                """
                Additional keyword arguments can be passed through to the RelyComply platform 
                in the form '--key=value'. These values can be json encoded objects.

                If the final argument is a file path it will attempt to load the file as a 
                TOML file. The additional keyword arguments are merged with the values of 
                the input TOML file. The command line arguments will take precedence.

                For more information please see https://docs.relycomply.com.
                """
            ),
        )
        parser.add_argument("type", help="the type of object to perform an action on")
        parser.add_argument("action", help="the action to perform")

        parser.add_argument(
            "--debug",
            action="store_true",
            help="Show the debug logger",
        )

        # # Explain the graphql instructions
        # parser.add_argument(
        #     "--explain",
        #     action="store_true",
        #     help="print out an explanation of the GraphQL commands executed",
        # )

        group = parser.add_mutually_exclusive_group()
        group.add_argument(
            "--toml",
            action="store_const",
            const="toml",
            dest="output_format",
            help="Output the results as toml or a formatted table (default)",
        )
        group.add_argument(
            "--json",
            action="store_const",
            const="json",
            dest="output_format",
            help="Output the results as json",
        )
        group.add_argument(
            "--yaml",
            action="store_const",
            const="yaml",
            dest="output_format",
            help="Output the results as yaml",
        )
        return parser

    def is_base64_field(self, type, action, field):

        base_64_fields = uppercase_dict(self.gql.templates["Base64Fields"])

        return field in base_64_fields.get(type.upper(), {}).get(
            action.upper(), []
        )
        
    def parse_args(self, args):
        parser = self.get_argument_parser()
        set_args, other_args = parser.parse_known_args(args)
        output_format = set_args.output_format or "toml"

        raw_kwargs = [part for part in other_args if part.startswith("--")]

        try:
            raw_kwargs = dict(part[2:].split("=", 1) for part in raw_kwargs)
        except ValueError:
            raise RelyComplyCliException(
                "Keyword arguments must be of the form '--<key>=<value>'."
            )

        kwargs = {}
        
        for key, value in raw_kwargs.items():
            if key.startswith("@"):
                # This is a file reference we load the file and maybe base64 encode it
                new_key = key[1:]
                if self.is_base64_field(set_args.type, set_args.action, new_key):
                    with open(value, "rb") as f:
                        new_value = b64encode(f.read()).decode("ascii")
                else:
                    with open(value, "r") as f:
                        new_value = f.read()
                        
                kwargs[new_key] = new_value
            else:
                # We check if the value is json encoded, and decode it, otherwise it is just a string
                try:
                    value = json.loads(value)
                    kwargs[key] = value
                except JSONDecodeError as e:
                    kwargs[key] = value

        straight_args = [part for part in other_args if not part.startswith("--")]

        if not straight_args:
            filename = None
        elif len(straight_args) == 1:
            filename = straight_args[0]
        else:
            raise RelyComplyCliException("Too many input filename arguments")

        if filename:
            if filename.endswith(".toml"):
                with open(filename) as f:
                    file_kwargs = toml.load(f)
            elif filename.endswith(".json"):
                with open(filename) as f:
                    file_kwargs = json.load(f)
            elif filename.endswith(".yaml"):
                with open(filename) as f:
                    file_kwargs = yaml.load(f)
            else:
                raise RelyComplyCliException(
                    "Unknown config file format: File must be toml, yaml, or json "
                )
            variables = {**file_kwargs, **kwargs}
        else:
            variables = kwargs

        return CliArguments(
            type=set_args.type,
            action=set_args.action,
            # explain=set_args.explain,
            debug=set_args.debug,
            output_format=output_format,
            variables=variables,
        )

    def execute(self, type, action, variables):
        field_type, field = self.get_graphql_field(type, action)
        if field_type == "mutation":
            return self.gql.execute_mutation(field, variables)
        elif field_type == "query":
            if action == "list":
                result = self.gql.execute_query_for_table(field, variables)
                return result
            elif action == "retrieve":
                result = self.gql.execute_query(field, variables, _only=True)
                if not result:
                    raise RelyComplyCliException("No matching items")

                return result

    def get_graphql_field(self, type, action):
        alias_mappings = self.gql.templates["aliases"]
        aliases = [
            *(
                (alias_action + alias_type, mutation_name, "mutation")
                for alias_type, alias_actions in alias_mappings.items()
                for alias_action, mutation_name in alias_actions.items()
            ),
            *((field, field, "mutation") for field in self.gql.mutation_fields),
            *((field, field, "query") for field in self.gql.query_fields),
        ]
        if action in ("list", "retrieve"):
            approximate_name = type + "s"
        else:
            approximate_name = action + type

        for alias, field, field_type in aliases:
            if alias.lower() == approximate_name.lower():
                return field_type, field

        # Find all the possible mutations
        possible_actions = [
            field[: -len(type.lower())]
            for field, _, _ in aliases
            if field.lower().endswith(type.lower())
        ]

        possible_query = [
            field
            for field, _, field_type in aliases
            if (type + "s").lower() == field.lower() and field_type == "query"
        ]

        # See if maybe it can be queried
        if possible_query:
            possible_actions.extend(["retrieve", "list"])

        if possible_actions:
            message = f"Action '{action}' not recognised for type '{type}', possible actions are:\n"
            raise RelyComplyCliException(
                message + "\n".join([f"  - {action}" for action in possible_actions])
            )
        else:
            raise RelyComplyCliException(f"Type '{type}' is not recognised")

    def format_output(self, cli_args, value):
        if cli_args.action == "list":
            return self.format_table_for_terminal(cli_args.output_format, value)
        else:
            return self.format_for_terminal(cli_args.output_format, value)

    def cell_output_for_table(self, value):
        if isinstance(value, dict):
            return json.dumps(value, indent=2)
        elif isinstance(value, list):
            return "\n".join(
                ["- " + self.cell_output_for_table(child) for child in value]
            )
        elif value is None:
            return ""
        else:
            return "\n".join(textwrap.wrap(str(value), 40))

    def format_table_for_terminal(self, output_format, nodes):

        if output_format in ("json", "yaml"):
            return self.format_for_terminal(output_format, list(nodes))
        else:
            # TODO make this page correctly
            nodes = list(nodes)
            if nodes:
                columns = nodes[0].keys()
                headers = [key.replace(".", "\n") for key in columns]
                rows = [
                    [self.cell_output_for_table(node.get(key)) for key in columns]
                    for node in nodes
                ]
                return tabulate(rows, headers=headers, tablefmt="fancy_grid")

            else:
                raise RelyComplyCliException(f"No matching items")

    def format_for_terminal(self, output_format, value):

        if output_format == "json":
            code = json.dumps(value, indent=2)
            lexer = JsonLexer()
        elif output_format == "yaml":
            lexer = YamlLexer()
            code = yaml.dump(value)
        elif output_format == "toml":
            lexer = TOMLLexer()
            code = cleartoml.dumps(value)
        else:
            raise RelyComplyCliException(f"Unknown format '{output_format}'.")

        if sys.stdout.isatty():
            return highlight(code, lexer, TerminalFormatter())
        else:
            return code

    def print_error(self, message):
        cprint(message, "red", file=sys.stderr)


def main():
    cli = RelyComplyCLI()
    cli.run_command(sys.argv[1:])
