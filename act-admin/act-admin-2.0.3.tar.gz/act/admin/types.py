#!/usr/bin/env python3

""" Manage ACT types """

import argparse
import json
import sys
from logging import critical, warning
from typing import Any, Dict, List

import act.api
from act.api import (DEFAULT_FACT_VALIDATOR, DEFAULT_METAFACT_VALIDATOR,
                     DEFAULT_OBJECT_VALIDATOR)
from act.api.libs import cli
from act.types.types import (default_fact_types, default_meta_fact_types,
                             default_object_types, load_types)


class TypeLoadError(Exception):
    pass


def parseargs() -> argparse.Namespace:
    """Parse arguments"""
    parser = cli.parseargs("ACT Type utilities")
    parser.add_argument("--list", action="store_true", help="List types")
    parser.add_argument("--add", action="store_true", help="Add types")
    parser.add_argument(
        "--default-object-types", action="store_true", help="Default object types"
    )
    parser.add_argument(
        "--default-fact-types", action="store_true", help="Default fact types"
    )
    parser.add_argument(
        "--default-meta-fact-types", action="store_true", help="Default meta fact types"
    )
    parser.add_argument("--object-types-file", help="Object type definitions (json)")
    parser.add_argument("--fact-types-file", help="Fact type definitions (json)")
    parser.add_argument(
        "--meta-fact-types-file", help="Meta Fact type definitions (json)"
    )

    return parser


def print_json(o: Any) -> None:
    "Print dict as sorted, indented json object"
    print(json.dumps(o, indent=4, sort_keys=True))


def create_object_types(client: act.api.Act, object_types: List[Dict]) -> None:
    """
    Create object types
    """

    existing_object_types = [
        object_type.name for object_type in client.get_object_types()
    ]

    # Create all objects
    for object_type in object_types:
        name = object_type["name"]
        validator = object_type.get("validator", DEFAULT_OBJECT_VALIDATOR)

        if name in existing_object_types:
            warning("Object type %s already exists" % name)
            continue

        client.object_type(name=name, validator_parameter=validator).add()


def create_fact_types(client: act.api.Act, fact_types: List[Dict]) -> None:
    """
    Create fact type with allowed bindings to ALL objects
    We want to change this later, but keep it like this to make it simpler
    when evaluating the data model
    """

    for fact_type in fact_types:
        name = fact_type["name"]
        validator = fact_type.get("validator", DEFAULT_FACT_VALIDATOR)
        object_bindings = fact_type.get("objectBindings", [])

        if not object_bindings:
            client.create_fact_type_all_bindings(name, validator_parameter=validator)

        else:
            client.create_fact_type(
                name, validator=validator, object_bindings=object_bindings
            )


def create_meta_fact_types(client: act.api.Act, meta_fact_types: List[Dict]) -> None:
    """
    Create fact type with allowed bindings to ALL objects
    We want to change this later, but keep it like this to make it simpler
    when evaluating the data model
    """

    for meta_fact_type in meta_fact_types:
        name = meta_fact_type["name"]
        validator = meta_fact_type.get("validator", DEFAULT_METAFACT_VALIDATOR)
        fact_bindings = meta_fact_type.get("factBindings", [])

        if not fact_bindings:
            client.create_meta_fact_type_all_bindings(
                name, validator_parameter=validator
            )

        else:
            client.create_meta_fact_type(
                name, fact_bindings=fact_bindings, validator=validator
            )


def main() -> None:
    "Main function"

    args = cli.handle_args(parseargs())

    if not (args.list or args.add):
        cli.fatal("Specify either --list, --add")

    if args.list:
        if not (
            args.default_object_types
            or args.default_fact_types
            or args.default_meta_fact_types
            or args.object_types_file
            or args.fact_types_file
            or args.meta_fact_types_file
        ):
            critical("Specify what types to show using --default-* or a file")
            sys.exit(1)

        try:
            if args.default_object_types:
                print_json(default_object_types())

            if args.default_fact_types:
                print_json(default_fact_types())

            if args.default_meta_fact_types:
                print_json(default_meta_fact_types())

            if args.object_types_file:
                print_json(load_types(args.object_types_file))

            if args.fact_types_file:
                print_json(load_types(args.fact_types_file))

            if args.meta_fact_types_file:
                print_json(load_types(args.meta_fact_types_file))
        except TypeLoadError as e:
            critical(str(e))
            sys.exit(1)

        sys.exit(0)

    elif args.add:
        client = cli.init_act(args)

        if not (args.act_baseurl):
            cli.fatal("--act-baseurl must be specified")

        try:
            if args.default_object_types:
                create_object_types(client, default_object_types())

            if args.default_fact_types:
                create_fact_types(client, default_fact_types())

            if args.default_meta_fact_types:
                create_meta_fact_types(client, default_meta_fact_types())

            if args.object_types_file:
                create_object_types(client, load_types(args.object_types_file))

            if args.fact_types_file:
                create_fact_types(client, load_types(args.fact_types_file))

            if args.meta_fact_types_file:
                create_meta_fact_types(client, load_types(args.meta_fact_types_file))
        except TypeLoadError as e:
            critical(str(e))
            sys.exit(1)


if __name__ == "__main__":
    main()
