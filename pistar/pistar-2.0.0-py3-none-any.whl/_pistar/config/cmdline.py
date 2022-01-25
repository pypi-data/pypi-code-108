import os
from pluggy import HookimplMarker

from _pistar.config import Config

hookimpl = HookimplMarker("pistar")


class COMMANDS:
    GENERATE = "generate"
    EXECUTE = "run"


@hookimpl(tryfirst=True)
def pistar_add_option(config: Config):
    config.add_option(
        "files_or_dir",
        action="store",
        nargs="+",
        type=str,
        metavar="files_or_dir",
        help="Specify a list or directory of test case files",
    )
    config.add_option(
        "--type",
        action="store",
        type=str,
        default="pistar",
        choices=["pistar", "pytest"],
        required=False,
        help="Specify the type of test case, the default value is pistar",
    )
    config.add_option(
        "-o",
        "--output",
        action="store",
        type=str,
        required=False,
        default=os.curdir,
        metavar="",
        help="Specify the result output directory",
    )
    config.add_option(
        "--debug",
        action="store_true",
        help="Record pistar framework log",
    )
    config.add_option(
        "--collectonly",
        action="store_true",
        help="Record pistar framework log",
    )
    config.add_option(
        "--nocolor",
        action="store_true",
        help="Print info without color"
    )
