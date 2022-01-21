import click
import logging
import json
import datetime as dt
from rich.emoji import Emoji
from rich.text import Text
from rich.syntax import Syntax
from rich.logging import RichHandler

from pydragonfly import Dragonfly

json_flag_option = [
    click.option(
        "-j",
        "--json",
        "as_json",
        is_flag=True,
        help="output as raw JSON",
    ),
]


class ClickContext(click.Context):
    #: ``Dragonfly`` instance
    obj: Dragonfly


def get_status_text(status: str, as_text=True):
    styles = {
        # evalutation
        "clean": ("#73D216", ""),
        "suspicious": ("#CE5C00", ""),
        "malicious": ("#CC0000", ""),
        # statuses
        "queued": ("#CE5C00", str(Emoji("gear"))),
        "pending": ("#CE5C00", str(Emoji("gear"))),
        "running": ("#CE5C00", str(Emoji("gear"))),
        "analyzed": ("#73D216", str(Emoji("heavy_check_mark"))),
        "failed": ("#CC0000", str(Emoji("cross_mark"))),
        "revoked": ("#CC0000", str(Emoji("cross_mark"))),
    }
    color, emoji = styles[status.lower()]
    return (
        Text(status + " " + emoji, style=color)
        if as_text
        else f"[{color}]{status} {emoji}[/]"
    )


def get_success_text(success: str, as_text=True):
    color, emoji = (
        ("#73D216", str(Emoji("heavy_check_mark")))
        if str(success) == "True"
        else ("#CC0000", str(Emoji("cross_mark")))
    )
    return Text(emoji, style=color) if as_text else f"[{color}]{emoji}[/]"


def get_weight_text(weight: int, as_text=True):
    color = "#73D216"
    if weight >= 100:
        color = "#CC0000"
    elif weight >= 50:
        color = "#CE5C00"
    return Text(str(weight), style=color) if as_text else f"[{color}]{weight}[/]"


def get_json_syntax(obj):
    return Syntax(
        json.dumps(obj, indent=2),
        "json",
        theme="ansi_dark",
        word_wrap=True,
        tab_size=2,
    )


def get_datetime_text(str_date: str) -> str:
    return dt.datetime.strptime(str_date, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y-%m-%d")


def get_logger(level: str = "INFO"):
    fmt = "%(message)s"
    logging.basicConfig(
        level=level, format=fmt, datefmt="[%X]", handlers=[RichHandler(markup=True)]
    )
    logger = logging.getLogger("rich")
    return logger


def get_version_number() -> str:
    from ..version import VERSION

    return VERSION


def add_options(options):
    def _add_options(func):
        for option in reversed(options):
            func = option(func)
        return func

    return _add_options
