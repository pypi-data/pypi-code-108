import argparse
from typing import Optional

import annoworkcli
import annoworkcli.actual_working_time.delete_actual_working_time
import annoworkcli.actual_working_time.list_actual_working_hours_daily
import annoworkcli.actual_working_time.list_actual_working_hours_daily_groupby_tag
import annoworkcli.actual_working_time.list_actual_working_time


def parse_args(parser: argparse.ArgumentParser):

    subparsers = parser.add_subparsers(dest="subcommand_name")

    # サブコマンドの定義
    # 実績作業時間の削除は間違って削除してしまったときの影響が大きいので、有効にしない。
    # annoworkcli.actual_working_time.delete_actual_working_time.add_parser(subparsers)
    annoworkcli.actual_working_time.list_actual_working_time.add_parser(subparsers)
    annoworkcli.actual_working_time.list_actual_working_hours_daily.add_parser(subparsers)
    annoworkcli.actual_working_time.list_actual_working_hours_daily_groupby_tag.add_parser(subparsers)


def add_parser(subparsers: Optional[argparse._SubParsersAction] = None) -> argparse.ArgumentParser:
    subcommand_name = "actual_working_time"
    subcommand_help = "実績作業時間関係のサブコマンド"

    parser = annoworkcli.common.cli.add_parser(
        subparsers, subcommand_name, subcommand_help, description=subcommand_help, is_subcommand=False
    )
    parse_args(parser)
    return parser
