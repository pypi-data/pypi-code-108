import copy
import datetime
import json
import logging.config
import pkgutil
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, TypeVar

import isodate
import pandas
import yaml

DEFAULT_CSV_FORMAT = {"encoding": "utf_8_sig", "index": False}
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"

logger = logging.getLogger(__name__)

T = TypeVar("T")  # Can be anything


def read_lines(filepath: str) -> List[str]:
    """ファイルを行単位で読み込む。改行コードを除く"""
    with open(filepath, encoding="utf-8") as f:
        lines = f.readlines()
    return [e.rstrip("\r\n") for e in lines]


def read_lines_except_blank_line(filepath: str) -> List[str]:
    """ファイルを行単位で読み込む。ただし、改行コード、空行を除く"""
    lines = read_lines(filepath)
    return [line for line in lines if line != ""]


def output_string(target: str, output: Optional[Path] = None) -> None:
    """
    文字列を出力する。

    Args:
        target: 出力対象の文字列
        output: 出力先。Noneなら標準出力に出力する。
    """
    if output is None:
        print(target)
    else:
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open(mode="w", encoding="utf_8") as f:
            f.write(target)
            logger.info(f"{output} に出力しました。")


def print_json(target: Any, is_pretty: bool = False, output: Optional[Path] = None) -> None:
    """
    JSONを出力する。

    Args:
        target: 出力対象のJSON
        is_pretty: 人が見やすいJSONを出力するか
        output: 出力先。Noneなら標準出力に出力する。

    """
    if is_pretty:
        output_string(json.dumps(target, indent=2, ensure_ascii=False), output)
    else:
        output_string(json.dumps(target, ensure_ascii=False), output)


def print_csv(
    df: pandas.DataFrame,
    output: Optional[Path] = None,
    to_csv_kwargs: Optional[Dict[str, Any]] = None,
):
    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)

    path_or_buf = sys.stdout if output is None else str(output)

    kwargs = copy.deepcopy(DEFAULT_CSV_FORMAT)
    if to_csv_kwargs is None:
        df.to_csv(path_or_buf, **kwargs)
    else:
        kwargs.update(to_csv_kwargs)
        df.to_csv(path_or_buf, **kwargs)

    if output is not None:
        logger.info(f"{output} に出力しました。")


def is_file_scheme(str_value: str) -> bool:
    """
    file schemaかどうか

    """
    return str_value.startswith("file://")


def get_file_scheme_path(str_value: str) -> Optional[str]:
    """
    file schemaのパスを取得する。file schemeでない場合は、Noneを返す

    """
    if is_file_scheme(str_value):
        return str_value[len("file://") :]
    else:
        return None


def isoduration_to_hour(duration) -> float:
    """
    ISO 8601 duration を 時間に変換する
    Args:
        duration (str): ISO 8601 Durationの文字

    Returns:
        変換後の時間。

    """
    return isodate.parse_duration(duration).total_seconds() / 3600


def to_iso8601_string(dt: datetime.datetime) -> str:
    return dt.astimezone(datetime.timezone.utc).strftime(DATETIME_FORMAT)


def set_default_logger(is_debug_mode: bool = False):
    """
    デフォルトのロガーを設定する。パッケージ内のlogging.yamlを読み込む。
    """
    # 事前にログ出力先のディレクトリを作成する。
    Path(".log").mkdir(exist_ok=True, parents=True)
    data = pkgutil.get_data("annoworkcli", "data/logging.yaml")
    if data is None:
        logger.warning("annoworkcli/data/logging.yaml の読み込みに失敗しました。")
        raise RuntimeError("annoworkcli/data/logging.yaml の読み込みに失敗しました。")

    logging_config = yaml.safe_load(data.decode("utf-8"))

    if is_debug_mode:
        logging_config["loggers"]["annofabapi"]["level"] = "DEBUG"
        logging_config["loggers"]["annoworkapi"]["level"] = "DEBUG"

    logging.config.dictConfig(logging_config)
