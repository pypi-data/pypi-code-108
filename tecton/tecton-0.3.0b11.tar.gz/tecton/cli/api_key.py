import sys
from dataclasses import dataclass
from typing import Callable

import tecton
from tecton._internals import metadata_service
from tecton.cli import printer
from tecton_proto.metadataservice.metadata_service_pb2 import CreateApiKeyRequest
from tecton_proto.metadataservice.metadata_service_pb2 import DeleteApiKeyRequest
from tecton_proto.metadataservice.metadata_service_pb2 import ListApiKeysRequest
from tecton_spark.id_helper import IdHelper


@dataclass
class ApiKeyCommand:
    command: str
    description: str
    handler: Callable


def api_key_create(args):
    request = CreateApiKeyRequest()
    request.description = args.description
    request.is_admin = args.is_admin
    response = metadata_service.instance().CreateApiKey(request)
    printer.safe_print("Save this key - you will not be able to get it again.", file=sys.stderr)
    printer.safe_print(response.key)


def api_key_delete(args):
    request = DeleteApiKeyRequest()
    try:
        id_proto = IdHelper.from_string(args.id)
    except:
        printer.safe_print("Invalid format for ID")
        sys.exit(1)
    request.id.CopyFrom(id_proto)
    try:
        response = metadata_service.instance().DeleteApiKey(request)
    except tecton._internals.tecton_errors.TectonAPIValidationError as e:
        printer.safe_print(
            f"API key with ID {args.id} not found. Check `tecton api-key list` to find the IDs of currently active API keys. The key's ID is different from the key's secret value."
        )
        sys.exit(1)
    printer.safe_print("Success")


def api_key_list(args):
    request = ListApiKeysRequest()
    response = metadata_service.instance().ListApiKeys(request)
    for k in response.api_keys:
        printer.safe_print(f"API Key ID: {IdHelper.to_string(k.id)}")
        printer.safe_print(f"Secret Key: {k.obscured_key}")
        printer.safe_print(f"Description: {k.description}")
        printer.safe_print(f"Created by:{k.created_by}")
        printer.safe_print()


COMMANDS = [
    ApiKeyCommand("create", description="Create a new API key.", handler=lambda args: api_key_create(args)),
    ApiKeyCommand("delete", description="Deactivate an API key by its ID.", handler=lambda args: api_key_delete(args)),
    ApiKeyCommand("list", description="List active API keys.", handler=lambda args: api_key_list(args)),
]


def run_api_key_command(args):
    for command in COMMANDS:
        if args.api_key_command == command.command:
            command.handler(args)
            break
    else:
        printer.safe_print(args)
        printer.safe_print("Unknown command", args.command.strip(), file=sys.stderr)
        sys.exit(1)


def build_parser(root_parser):
    api_key_parsers = root_parser.add_subparsers(dest="api_key_command", help="List of API key commands")
    api_key_parsers.required = True

    for c in COMMANDS:
        p = api_key_parsers.add_parser(c.command, help=c.description)
        if c.command == "create":
            p.add_argument(
                "--description", default="", type=str, help="An optional, human readable description for this API key."
            )
            p.add_argument(
                "--is-admin",
                action="store_true",
                default=False,
                help="Whether the API key has admin permissions, generally corresponding to write permissions. Defaults to false.",
            )
        if c.command == "delete":
            p.add_argument("id", help="ID of the API key to delete (not the actual key value).")
