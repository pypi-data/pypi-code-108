from logging import FileHandler
from enum import Enum
from contextlib import contextmanager

from pybrary.func import caller


class Verbosity(Enum):
    quiet = 0
    normal = 1
    verbose = 2


class Logger:
    def __init__(self, logger, verbosity=None):
        self.logger = logger
        self.verbosity = verbosity or Verbosity.normal

    @contextmanager
    def quiet(self):
        back = self.verbosity
        self.verbosity = Verbosity.quiet
        try:
            yield
        finally:
            self.verbosity = back

    def debug(self, *a):
        if len(a)>1:
            self.logger.debug(*a)
        else:
            self.logger.debug(f'{caller()} -> {a[0]}')

    def info(self, *a):
        if self.verbosity.value < Verbosity.normal.value:
            self.debug(*a)
        else:
            self.logger.info(*a)

    def error(self, *a):
        self.logger.error(*a)

    def exception(self, *a):
        self.logger.exception(*a)

    def logs(self, level='info'):
        for h in self.logger.handlers:
            if isinstance(h, FileHandler):
                if h.get_name()==level:
                    return h.baseFilename

    def __str__(self):
        return str(self.logger)


class Deploy:
    g = "\x1b[32;1m"
    y = "\x1b[33;1m"
    r = "\x1b[31;1m"
    z = "\x1b[0m"

    def __init__(self, logger, setux):
        self.setux = setux
        self.logger = logger
        self.tab = 0

    def info(self, col, msg):
        self.setux.info(msg)
        msg = f'{" "*4*self.tab}{col}{msg[3:]}{self.z}'
        self.logger.info(msg)

    def green(self, msg):
        self.info(self.g, msg)

    @contextmanager
    def yellow(self, msg):
        self.info(self.y, msg)
        self.tab+=1
        yield
        self.tab-=1

    @contextmanager
    def silent(self, msg):
        self.logger.debug(msg)
        self.tab+=1
        yield
        self.tab-=1

    def red(self, msg):
        self.info(self.r, msg)

    def __str__(self):
        return str(self.logger)
