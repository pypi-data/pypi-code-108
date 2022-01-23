from argparse import ArgumentParser
from dataclasses import dataclass
from typing import (
    Dict,
    List,
)

from begin.constants import DEFAULT_REGISTRY_NAME


class Request:
    def __init__(self, target_identifier: str) -> None:
        target_name, _, registry_namespace = target_identifier.partition('@')
        self._target_name = target_name
        self._registry_namespace = registry_namespace or DEFAULT_REGISTRY_NAME
        self._options: Dict[str, str] = {}

    def add_option(self, param_identifier: str) -> None:
        key, _, value = param_identifier.partition(':')
        self._options[key] = value

    @property
    def target_name(self) -> str:
        return self._target_name

    @property
    def registry_namespace(self) -> str:
        return self._registry_namespace

    @property
    def options(self) -> Dict[str, str]:
        return self._options


@dataclass
class OptionalArg:
    short: str
    long: str
    default: str
    help: str


OPTIONAL_ARGS = [
        OptionalArg(
            short='-e',
            long='--extension',
            default='*targets.py',  # TODO get this from settings
            help='The suffix to match target file patterns against.',
        ),
        OptionalArg(
            short='-g',
            long='--global-dir',
            default='~/.begin',  # TODO get this from settings
            help='The location of the directory holding global targets files.',
        ),
    ]


@dataclass
class ParsedCommand:
    extension: str
    global_dir: str
    requests: List[Request]


def _parse_requests(args: List[str]) -> List[Request]:
    requests = []
    request = None
    for arg in args:
        if ':' not in arg:
            # Not a key:value argument pair, must be either target or target@namespace
            if request is not None:
                requests.append(request)
            request = Request(arg)
        else:
            request.add_option(arg)
    requests.append(request)
    return requests


def parse_command():
    parser = ArgumentParser(description='A utility for running targets in a targets.py file.')

    for optional_arg in OPTIONAL_ARGS:
        parser.add_argument(
            optional_arg.short,
            optional_arg.long,
            default=optional_arg.default,
            help=optional_arg.help,
        )

    optional_args, request_args = parser.parse_known_args()
    requests = _parse_requests(request_args)
    return ParsedCommand(
            extension=optional_args.extension,
            global_dir=optional_args.global_dir,
            requests=requests,
        )
