import os
import json
import logging
import argparse
from akeneo_cli.client import AkeneoClient


def main():
    parser = getArgParser()
    args = parser.parse_args()
    if not args.mode:
        parser.print_help()
        exit(1)

    log_level_id = logging.WARNING
    if args.verbose == 1:
        log_level_id = logging.INFO
    elif args.verbose >= 2:
        log_level_id = logging.DEBUG
    if args.quiet:
        log_level_id = logging.ERROR
    logging.basicConfig(
        format="%(asctime)s %(levelname)s: %(message)s",
        level=log_level_id,
        filename=args.log_file,
    )

    with AkeneoClient(
        os.getenv("AKENEO_URL"),
        os.getenv("AKENEO_CLIENT_ID"),
        os.getenv("AKENEO_CLIENT_SECRET"),
    ).login(os.getenv("AKENEO_USERNAME"), os.getenv("AKENEO_PASSWORD")) as client:
        if args.object == "product":
            if args.mode == "get":
                result = client.get(
                    "products",
                    args.code,
                    filters=dict(page=args.page, limit=args.per_page),
                )
    print(json.dumps(result, indent=4))


def getArgParser():
    objects = prepareObjectsParserDefinitions()
    optional = prepareOptionalArgsDefinitions()
    main = argparse.ArgumentParser(
        prog="akeneo",
        description="Akeneo client.",
        allow_abbrev=False,
    )
    mode = main.add_subparsers(dest="mode", help="mode help")
    mode_get = mode.add_parser(
        "get",
        help="Get",
        parents=[objects, optional],
    )

    mode_get.add_argument(
        "-c",
        "--code",
        dest="code",
        type=str,
        default=None,
        help="Use this to work on a specific product.",
    )

    return main


def prepareOptionalArgsDefinitions():
    parser = argparse.ArgumentParser(allow_abbrev=False, add_help=False)
    parser.add_argument(
        "-v",
        dest="verbose",
        action="count",
        default=0,
        help="Verbose logs output. -v for Info level and -vv for Debug level.",
    )
    parser.add_argument(
        "-l",
        "--log-file",
        dest="log_file",
        type=str,
        default=os.getenv("SAB_ENGINE_LOG_FILE", None),
        help="The file to write the logs into. Alternatively can be set via AKENEO_LOG_FILE env var. If not specified, the logs will be writen in the standard output.",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        dest="quiet",
        action="store_true",
        default=False,
        help="If used, logs will be silenced except for Errors.",
    )
    return parser


def prepareObjectsParserDefinitions():
    optional = prepareOptionalArgsDefinitions()
    object_parser = prepareObjectParserDefinitions()
    parser = argparse.ArgumentParser(allow_abbrev=False, add_help=False)
    obj = parser.add_subparsers(dest="object", help="mode help")
    obj_product = obj.add_parser(
        "product",
        help="Get",
        parents=[object_parser, optional],
    )
    return parser


def prepareObjectParserDefinitions():
    parser = argparse.ArgumentParser(allow_abbrev=False, add_help=False)
    parser.add_argument(
        "-p",
        "--page",
        dest="page",
        type=int,
        default=1,
        metavar="PAGE",
    )
    parser.add_argument(
        "-n",
        "--per-page",
        dest="per_page",
        type=int,
        default=20,
        metavar="PER_PAGE",
    )
    return parser


if "__main__" == __name__:
    main()
