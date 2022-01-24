import logging
from collections import namedtuple

default_logger = logging.getLogger('oarepo_model_builder')


# verbosity 1 is the most serious
# verbosity 9 is the least serious


class Log:
    INFO = 0
    ERROR = logging.INFO - logging.ERROR

    LogStackEntry = namedtuple('LogStackEntry', 'verbosity,indent,logger')

    def __init__(self):
        self.stack = [Log.LogStackEntry(verbosity=0, indent=0, logger=default_logger)]

    def enter(self, verbosity, fmt, *args, logger=None, **kwargs):
        if not logger:
            logger = self.stack[-1].logger
        level = self.stack[-1].indent

        if logger.isEnabledFor(logging.INFO - verbosity):
            self(verbosity, fmt, *args, logger=logger, **kwargs)
            level += 1

        self.stack.append(Log.LogStackEntry(verbosity=verbosity, indent=level, logger=logger))

    def leave(self, fmt=None, *args, **kwargs):
        top = self.stack.pop()
        if fmt:
            self(top.verbosity, fmt, *args, logger=top.logger, **kwargs)

    def __call__(self, verbosity, fmt, *args, logger=None, **kwargs):
        if not logger:
            logger = self.stack[-1].logger
        indent = '  ' * (self.stack[-1].indent - 1)
        logger.log(logging.INFO - verbosity, indent + fmt, *args, **kwargs)


log = Log()
