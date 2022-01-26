import argparse
import logging
import sys

import argcomplete
from logging_actions import log_level_action

from ._public_vm_ip import public_ip

logger = logging.getLogger(__name__)

PUBLIC_VM_IP = "public-vm-ip"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-l", "--log-level", action=log_level_action(logger), default="info"
    )
    subparsers = parser.add_subparsers(required=True, dest="subcommand")

    public_ip_subcommand = subparsers.add_parser(PUBLIC_VM_IP)
    public_ip_subcommand.add_argument(
        "--override-command",
        help="Override the default `az vm list-ip-addresses` for e.g caching. Must output JSON in the same format",
        nargs="+",
        default=None,
    )

    argcomplete.autocomplete(parser)
    args = parser.parse_args()
    logger.debug(f"{args=}")

    return (
        public_ip(command=args.override_command)
        if args.subcommand == PUBLIC_VM_IP
        else 1
    )


def _main():
    sys.exit(main())
