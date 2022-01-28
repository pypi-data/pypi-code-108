from enum import Enum
from .Singleton import Singleton
from functools import partial, wraps


class LogLevel(Enum):
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3


class Logger():
    verboseLevel: LogLevel = LogLevel.INFO

    def log(msg, system=None, level=LogLevel.INFO):
        if (system != None):
            msg = "[" + system + "] " + msg

        if (level == LogLevel.WARNING):
            msg = u"\033[33;1;4m%s\033[0m" % (msg)
        if (level == LogLevel.ERROR):
            msg = u"\033[31;1;4m%s\033[0m" % (msg)

        if (Logger.verboseLevel.value <= level.value):
            print(msg)


def classLogger(class_):
    name = class_.__name__

    def log(self, msg, level=LogLevel.INFO):
        Logger.log(msg, name, level)

    def logDebug(self, msg):
        Logger.log(msg, name, level=LogLevel.DEBUG)

    def logWarning(self, msg):
        Logger.log(msg, name, LogLevel.WARNING)

    class_.log = log
    class_.logDebug = logDebug
    class_.logWarning = logWarning
    return class_