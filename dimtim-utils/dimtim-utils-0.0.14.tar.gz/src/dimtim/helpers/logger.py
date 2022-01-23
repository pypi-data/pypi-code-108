import logging
from typing import Any, TextIO

from dimtim.utils.terminal import colorize


class Logger:
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR

    def __init__(self, name: str = '', prefix: str = '', stdout: TextIO = None, stdprefix: str = ''):
        self.logger = logging.getLogger(name)
        self.prefix = prefix
        self.stdout = stdout
        self.stdprefix = stdprefix

    def colorize(self, level: int, message: str) -> str:
        color = {self.DEBUG: 'white', self.INFO: 'blue', self.WARNING: 'yellow', self.ERROR: 'red'}.get(level)
        return colorize(message, fg=color)

    def log(self, level: int, message: Any, prefix: str = '', stdprefix: str = '', nolog: bool = False, noout: bool = False, *args, **kwargs):
        if not nolog:
            self.logger.log(level, f'{prefix or self.prefix}{message}', *args, **kwargs)
        if self.stdout and not noout:
            self.stdout.write(self.colorize(level, f'{stdprefix or self.stdprefix}{message}\n'))

    def debug(self, message: Any, prefix: str = '', stdprefix: str = '', nolog: bool = False, noout: bool = False, *args, **kwargs):
        self.log(self.DEBUG, message, prefix, stdprefix, nolog, noout, *args, **kwargs)

    def info(self, message: Any, prefix: str = '', stdprefix: str = '', nolog: bool = False, noout: bool = False, *args, **kwargs):
        self.log(self.INFO, message, prefix, stdprefix, nolog, noout, *args, **kwargs)

    def warning(self, message: Any, prefix: str = '', stdprefix: str = '', nolog: bool = False, noout: bool = False, *args, **kwargs):
        self.log(self.WARNING, message, prefix, stdprefix, nolog, noout, *args, **kwargs)

    def error(self, message: Any, prefix: str = '', stdprefix: str = '', nolog: bool = False, noout: bool = False, *args, **kwargs):
        self.log(self.ERROR, message, prefix, stdprefix, nolog, noout, *args, **kwargs)

    def exception(self, message: Any, prefix: str = '', stdprefix: str = '', nolog: bool = False, noout: bool = False, *args, exc_info: bool = True, **kwargs):
        self.error(message, prefix, stdprefix, nolog, noout, *args, exc_info=exc_info, **kwargs)
