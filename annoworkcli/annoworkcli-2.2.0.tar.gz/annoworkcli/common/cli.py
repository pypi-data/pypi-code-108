"""
Command Line Interfaceの共通部分
"""
import argparse
import getpass
import json
import logging
from enum import Enum
from typing import Any, List, Optional, Tuple

import annoworkapi
from annoworkapi.api import DEFAULT_ENDPOINT_URL
from annoworkapi.exceptions import AnnoworkApiException
from more_itertools import first_true

from annoworkcli.common.utils import get_file_scheme_path, read_lines_except_blank_line

logger = logging.getLogger(__name__)

COMMAND_LINE_ERROR_STATUS_CODE = 2


class OutputFormat(Enum):
    CSV = "csv"
    JSON = "json"


class PrettyHelpFormatter(argparse.RawTextHelpFormatter, argparse.ArgumentDefaultsHelpFormatter):
    def _format_action(self, action: argparse.Action) -> str:
        return super()._format_action(action) + "\n"

    def _get_help_string(self, action):
        """引数説明用のメッセージを生成する。
        不要なデフォルト値（--debug や オプショナルな引数）を表示させないようにする.
        `argparse.ArgumentDefaultsHelpFormatter._get_help_string` をオーバライドしている。

        Args:
            action ([type]): [description]

        Returns:
            [type]: [description]
        """
        # ArgumentDefaultsHelpFormatter._get_help_string の中身を、そのまま持ってきた。
        # https://qiita.com/yuji38kwmt/items/c7c4d487e3188afd781e 参照

        # 必須な引数には、引数の説明の後ろに"(required)"を付ける
        help = action.help  # pylint: disable=redefined-builtin
        if action.required:
            help += " (required)"

        if "%(default)" not in action.help:
            if action.default is not argparse.SUPPRESS:
                defaulting_nargs = [argparse.OPTIONAL, argparse.ZERO_OR_MORE]
                if action.option_strings or action.nargs in defaulting_nargs:
                    # 以下の条件だけ、annofabcli独自の設定
                    if action.default is not None and not action.const:
                        help += " (default: %(default)s)"
        return help


def add_parser(
    subparsers: Optional[argparse._SubParsersAction],
    command_name: str,
    command_help: str,
    description: Optional[str] = None,
    is_subcommand: bool = True,
    epilog: Optional[str] = None,
) -> argparse.ArgumentParser:
    """
    サブコマンド用にparserを追加する

    Args:
        subparsers: Noneの場合はsubparserを生成します。
        command_name:
        command_help: 1階層上のコマンドヘルプに表示される コマンドの説明（簡易的な説明）
        description: ヘルプ出力に表示される説明（詳細な説明）
        is_subcommand: サブコマンドかどうか. `annoworkcli job`はコマンド、`annoworkcli job list`はサブコマンドとみなす。
        epilog: ヘルプ出力後に表示される内容。デフォルトはNoneです。

    Returns:
        サブコマンドのparser

    """
    GLOBAL_OPTIONAL_ARGUMENTS_TITLE = "global optional arguments"

    def create_parent_parser() -> argparse.ArgumentParser:
        """
        共通の引数セットを生成する。
        """
        parent_parser = argparse.ArgumentParser(add_help=False)
        group = parent_parser.add_argument_group(GLOBAL_OPTIONAL_ARGUMENTS_TITLE)
        group.add_argument("--debug", action="store_true", help="HTTPリクエストの内容やレスポンスのステータスコードなど、デバッグ用のログが出力されます。")
        group.add_argument(
            "--endpoint_url",
            type=str,
            help=f"AnnoWork WebAPIのエンドポイントを指定します。指定しない場合は ``{DEFAULT_ENDPOINT_URL}`` です。",
        )

        return parent_parser

    if subparsers is None:
        # ヘルプページにコマンドラインオプションを表示する`sphinx-argparse`ライブラリが実行するときは、subparsersがNoneになる。
        subparsers = argparse.ArgumentParser().add_subparsers()
    parents = [create_parent_parser()] if is_subcommand else []

    parser = subparsers.add_parser(
        command_name,
        parents=parents,
        description=description if description is not None else command_help,
        help=command_help,
        epilog=epilog,
        formatter_class=PrettyHelpFormatter,
    )
    parser.set_defaults(command_help=parser.print_help)

    # 引数グループに"global optional group"がある場合は、"--help"オプションをデフォルトの"optional"グループから、"global optional arguments"グループに移動する
    # https://ja.stackoverflow.com/a/57313/19524
    global_optional_argument_group = first_true(
        parser._action_groups, pred=lambda e: e.title == GLOBAL_OPTIONAL_ARGUMENTS_TITLE
    )
    if global_optional_argument_group is not None:
        # optional グループの 0番目が help なので取り出す
        help_action = parser._optionals._group_actions.pop(0)
        assert help_action.dest == "help"
        # global optional group の 先頭にhelpを追加
        global_optional_argument_group._group_actions.insert(0, help_action)

    return parser


def get_list_from_args(str_list: Optional[List[str]] = None) -> Optional[List[str]]:
    """
    文字列のListのサイズが1で、プレフィックスが`file://`ならば、ファイルパスとしてファイルを読み込み、行をListとして返す。
    そうでなければ、引数の値をそのまま返す。

    Args:
        str_list: コマンドライン引数で指定されたリスト、またはfileスキームのURL

    Returns:
        コマンドライン引数で指定されたリスト。
    """
    if str_list is None or len(str_list) == 0:
        return None

    if len(str_list) > 1:
        return str_list

    str_value = str_list[0]
    path = get_file_scheme_path(str_value)
    if path is not None:
        return read_lines_except_blank_line(path)
    else:
        return str_list


def get_json_from_args(target: Optional[str] = None) -> Any:
    """
    JSON形式をPythonオブジェクトに変換する。
    プレフィックスが`file://`ならば、ファイルパスとしてファイルを読み込み、Pythonオブジェクトを返す。
    """

    if target is None:
        return None

    path = get_file_scheme_path(target)
    if path is not None:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    else:
        return json.loads(target)


def prompt_yesno(msg: str) -> bool:
    """
    標準入力で yes, noを選択できるようにする。
    Args:
        msg: 確認メッセージ

    Returns:
        True: Yes, False: No

    """
    while True:
        choice = input(f"{msg} [y/N] : ")
        if choice == "y":
            return True

        elif choice == "N":
            return False


def prompt_yesnoall(msg: str) -> Tuple[bool, bool]:
    """
    標準入力で yes, no, all(すべてyes)を選択できるようにする。
    Args:
        msg: 確認メッセージ

    Returns:
        Tuple[yesno, allflag]. yesno:Trueならyes. allflag: Trueならall.

    """
    while True:
        choice = input(f"{msg} [y/N/ALL] : ")
        if choice == "y":
            return True, False

        elif choice == "N":
            return False, False

        elif choice == "ALL":
            return True, True


def build_annoworkapi(args: argparse.Namespace) -> annoworkapi.resource.Resource:
    endpoint_url = annoworkapi.api.DEFAULT_ENDPOINT_URL
    if args.endpoint_url is not None:
        endpoint_url = args.endpoint_url

    if endpoint_url != annoworkapi.api.DEFAULT_ENDPOINT_URL:
        logger.info(f"endpoint_url= '{endpoint_url}' ")

    try:
        return annoworkapi.build(endpoint_url=endpoint_url)
    except AnnoworkApiException:
        # 環境変数, netrcフィアルに認証情報が設定されていなかったので、標準入力から認証情報を入力させる。
        login_user_id = ""
        while login_user_id == "":
            login_user_id = input("Enter AnnoWork User ID: ")

        login_password = ""
        while login_password == "":
            login_password = getpass.getpass("Enter AnnoWork Password: ")

        return annoworkapi.resource.Resource(
            endpoint_url=endpoint_url, login_user_id=login_user_id, login_password=login_password
        )
