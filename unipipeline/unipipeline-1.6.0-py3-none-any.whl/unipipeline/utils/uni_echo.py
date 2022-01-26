import logging
import sys
from typing import IO, Union, Optional

from unipipeline.utils.uni_util_color import UniUtilColor

SUPPORTED_LVL = {logging.INFO, logging.DEBUG, logging.WARNING, logging.ERROR}


def get_lvl(lvl: Union[str, int]) -> int:
    if isinstance(lvl, str):
        lvl = lvl.strip().lower()
        if lvl == 'info':
            return logging.INFO
        if lvl == 'debug':
            return logging.DEBUG
        if lvl == 'error':
            return logging.ERROR
        if lvl == 'warning':
            return logging.WARNING
        raise ValueError('invalid value of level')
    assert lvl in SUPPORTED_LVL
    return lvl


class UniEcho:
    def __init__(self, name: str, colors: UniUtilColor, prefix: str = '', level: Optional[Union[int, str]] = None) -> None:
        self._level_set = level is not None
        self._name = name
        self._level = get_lvl(level if level is not None else 'info')
        self._colors = colors

        prefix = f'{f"{prefix} | " if prefix else ""}{self._name}'
        self._debug_prefix = self._colors.color_it(self._colors.COLOR_GRAY, f'{prefix} | DEBUG   :: ')
        self._info_prefix = self._colors.color_it(self._colors.COLOR_CYAN, f'{prefix} | INFO    :: ')
        self._warn_prefix = self._colors.color_it(self._colors.COLOR_YELLOW, f'{prefix} | WARNING :: ')
        self._err_prefix = self._colors.color_it(self._colors.COLOR_RED, f'{prefix} | ERROR   :: ')
        self._success_prefix = self._colors.color_it(self._colors.COLOR_GREEN, f'{prefix} :: ')

        self._prefix = prefix

    def mk_child(self, name: str) -> 'UniEcho':
        e = UniEcho(name, colors=self._colors, prefix=self._prefix, level=self._level)
        return e

    @property
    def level(self) -> int:
        return self._level

    @level.setter
    def level(self, value: Union[int, str]) -> None:
        if self._level_set:
            return
        self._level = get_lvl(value)

    def echo(self, msg: str, stream: IO[str] = sys.stdout) -> None:
        stream.write(f'{msg}\n')

    def log_debug(self, msg: str) -> None:
        if logging.DEBUG >= self._level:
            self.echo(f'{self._debug_prefix}{msg}')

    def log_info(self, msg: str) -> None:
        if logging.INFO >= self._level:
            self.echo(f'{self._info_prefix}{msg}')

    def log_warning(self, msg: str) -> None:
        if logging.WARNING >= self._level:
            self.echo(f'{self._warn_prefix}{msg}', stream=sys.stderr)

    def log_error(self, msg: str) -> None:
        if logging.ERROR >= self._level:
            self.echo(f'{self._err_prefix}{msg}', stream=sys.stderr)

    def exit_with_error(self, msg: str) -> None:
        self.echo(f'{self._err_prefix}{msg}', stream=sys.stderr)
        exit(1)

    def success(self, msg: str) -> None:
        self.echo(f'{self._success_prefix}{self._colors.color_it(self._colors.COLOR_GREEN, msg)}')
