import argparse
import logging
import sys
from typing import Optional, Sequence

import annoworkcli
import annoworkcli.account.subcommand
import annoworkcli.actual_working_time.subcommand
import annoworkcli.annofab.subcommand
import annoworkcli.expected_working_time.subcommand
import annoworkcli.job.subcommand
import annoworkcli.my.subcommand
import annoworkcli.organization.subcommand
import annoworkcli.organization_member.subcommand
import annoworkcli.organization_tag.subcommand
import annoworkcli.schedule.subcommand
from annoworkcli.common.cli import PrettyHelpFormatter
from annoworkcli.common.utils import set_default_logger

logger = logging.getLogger(__name__)


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Command Line Interface for AnnoFab",
        formatter_class=PrettyHelpFormatter,
    )
    parser.add_argument("--version", action="version", version=f"annoworkcli {annoworkcli.__version__}")
    parser.set_defaults(command_help=parser.print_help)

    subparsers = parser.add_subparsers(dest="command_name")

    annoworkcli.account.subcommand.add_parser(subparsers)
    annoworkcli.actual_working_time.subcommand.add_parser(subparsers)
    annoworkcli.annofab.subcommand.add_parser(subparsers)
    annoworkcli.expected_working_time.subcommand.add_parser(subparsers)
    annoworkcli.job.subcommand.add_parser(subparsers)
    annoworkcli.my.subcommand.add_parser(subparsers)
    annoworkcli.organization.subcommand.add_parser(subparsers)
    annoworkcli.organization_member.subcommand.add_parser(subparsers)
    annoworkcli.organization_tag.subcommand.add_parser(subparsers)
    annoworkcli.schedule.subcommand.add_parser(subparsers)

    return parser


def main(arguments: Optional[Sequence[str]] = None):
    """
    annoworkcli コマンドのメイン処理

    Args:
        arguments: コマンドライン引数。テストコード用

    """
    parser = create_parser()
    if arguments is None:
        args = parser.parse_args()
    else:
        args = parser.parse_args(arguments)

    if hasattr(args, "subcommand_func"):
        try:
            set_default_logger(is_debug_mode=args.debug)
            logger.info(f"{sys.argv=}")
            args.subcommand_func(args)
        except Exception as e:
            logger.exception(e)
            raise e

    else:
        # 未知のサブコマンドの場合はヘルプを表示
        args.command_help()


if __name__ == "__main__":
    main()
