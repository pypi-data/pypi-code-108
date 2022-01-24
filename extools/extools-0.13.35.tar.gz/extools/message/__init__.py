import traceback
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

try:
    from accpac import *
except ImportError as e:
    # This happens when the tools are imported outside of the Extender env.
    # We can pass to let the tool do its work (likely sphinx making docs).
    pass

from extools.error_stack import consume_errors

__exm_loggers = {}

def logger_for_module(module_name, level=None, box=None, **kwargs):
    global __exm_loggers
    filestem = module_name.split(".")[0]

    log_path = Path(getOrgPath(), "{}.log".format(filestem))
    log_debug_path = Path(getOrgPath(), "{}.debug".format(filestem))

    if not level:
        level = ExMessages.INFO
        if log_debug_path.exists():
            level = ExMessages.DEBUG
    
    if filestem not in __exm_loggers:
        __exm_loggers[filestem] = ExMessages(
                module_name, level=level, log_path=str(log_path), 
                box=box, **kwargs)
    else:
        return  ExMessages(module_name, level=level, box=box, 
                    handler=__exm_loggers[filestem].handler, **kwargs)
    return __exm_loggers[filestem]

class ExMessages(object):
    """A logger like object for writing messages for the user.

    The ExtenderMessageWriter acts like a logger, allowing a developer
    to add messages that are only displayed to the user if the current
    level is greater than or equal to the message level being called.

    Messages at debug and below, as well as those at error or above,
    support displaying the last exception traceback to make debugging
    easier.

    :param name: the name to log under.
    :type name: str
    :param level: the level at and below which to display messages.
    :type level: int
    :param log_path: the path of a log file to write to.
    :type log_path: str
    :param programs: the list of programs for which to display
        messages.  For example, if programs were ["OE1100", ] then messages
        will only be displayed if the Order Entry program is currently
        running.
    :type programs: list
    :param box: indicates whether to show a message box, add a message to the
        Sage message stack, or suppress UI messages. Defaults to True.
    :type box: True (showMessageBox), False (message stack), None (suppress)
    :param disabled: disable all messages and logging.
        Defaults to False.
    :type disabled: bool
    """

    """Supported Levels"""
    PANIC       = 0
    CRITICAL    = 1
    ERROR       = 5
    WARNING     = 10
    INFO        = 15
    DEBUG       = 20
    RAW         = 25

    LEVELS = (
            PANIC,
            CRITICAL,
            ERROR,
            WARNING,
            INFO,
            DEBUG,
            RAW,
            )
    """Supported log levels in decreasing order of severity."""

    # Level names and log method lookup
    _LEVEL_INFO= {
            PANIC: ("Panic", "critical", ),
            CRITICAL: ("Critical", "critical", ),
            ERROR: ("Error", "error", ),
            WARNING: ("Warning", "warning", ),
            INFO: ("Info", "info", ),
            DEBUG: ("Debug", "debug", ),
            RAW: ("Raw", "debug", ),
            }

    YES_NO_DIALOG = 0x04
    YES_NO_DIALOG_YES = 6
    YES_NO_DIALOG_NO  = 7

    def __init__(self, name, level=None, log_path=None, programs=[], box=True,
                 disabled=False, key="", handler=None):
        """Get a new ExMessages instance."""
        if not level:
            level = self.INFO
        self.level = level
        self.level_info = self._LEVEL_INFO[level]
        self.level_name = self.level_info[0]

        self.name = name
        self.disabled = disabled
        self.programs = programs
        self.box = box
        self.key = key

        self.handler = handler

        self.log = None
        self.log_path = log_path
        self.log_level = getattr(logging, self.level_info[1].upper())
        if self.log_path or self.handler:
            self._setup_log()

    def _setup_log(self):
        self.log = logging.getLogger(self.name)
        if not self.handler:
            self.handler = RotatingFileHandler(
                    filename=str(self.log_path),
                    backupCount=1,
                    maxBytes=10*1024*1024)
            self.handler.setFormatter(logging.Formatter(
                    fmt='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%dT%H:%M:%S',))

        self.log.addHandler(self.handler)
        self.log.setLevel(self.log_level)

    def _write(self, level, msg):
        if self.disabled or (self.programs and program not in self.programs):
            return None

        name = self.name
        if self.key:
            name =  "{}.{}".format(name, self.key)
        msg_w_name = "{}\n\n{}".format(name, msg)
        if level <= self.level:
            if level == self.DEBUG:
                msg_w_name  = "DEBUG {}\n\n{}".format(rotoID, msg_w_name)

            if self.box:
                showMessageBox(msg_w_name)
            elif self.box is not None:
                if level <= self.ERROR:
                    error(msg_w_name)
                elif level <= self.WARNING:
                    warning(msg_w_name)
                else:
                    message(msg_w_name)

        if self.log:
            log_func = getattr(self.log, self._LEVEL_INFO[level][1])
            log_func("{} {}".format(self.key, msg))

        return msg

    def panic(self, msg, exc_info=None):
        """Display and log a panic message.

        :param msg: message to write.
        :type msg: str
        :param exc_info: include last exception backtrace?
        :type exc_info: bool

        :rtype: None
        """
        if exc_info:
            msg = "\n".join([msg, traceback.format_exc(), ])
        self._write(self.PANIC, msg)

    def crit(self, msg, exc_info=None):
        """Display and log a critical message.

        :param msg: message to write.
        :type msg: str
        :param exc_info: include last exception backtrace?
        :type exc_info: bool
        :rtype: None
        """
        if exc_info:
            msg = "\n".join([msg, traceback.format_exc(), ])
        self._write(self.CRITICAL, msg)

    def error(self, msg, exc_info=None):
        """Display and log an error message.

        :param msg: message to write.
        :type msg: str
        :param exc_info: include last exception backtrace?
        :type exc_info: bool
        :rtype: None
        """
        if exc_info:
            msg = "\n".join([msg, traceback.format_exc(), ])
        self._write(self.ERROR, msg)

    def warn(self, msg):
        """Display and log a warning message.

        :param msg: message to write.
        :type msg: str
        :rtype: None
        """
        self._write(self.WARNING, msg)

    def info(self, msg):
        """Display and log an info message.

        :param msg: message to write.
        :type msg: str
        :rtype: None
        """
        self._write(self.INFO, msg)

    def debug(self, msg, exc_info=False):
        """Display and log a debug message.

        :param msg: message to write.
        :type msg: str
        :param exc_info: include last exception backtrace?
        :type exc_info: bool
        :rtype: None
        """
        if exc_info:
            msg = "\n".join([msg, traceback.format_exc(), ])
        self._write(self.DEBUG, msg)

    def raw(self, msg, exc_info=False):
        """Display and log raw output.

        :param msg: message to write.
        :type msg: str
        :param exc_info: include last exception backtrace?
        :type exc_info: bool
        :rtype: None
        """
        msg = "RAW {}\n---------\n{}".format(rotoID, msg)
        if exc_info:
            msg = "\n".join([msg, traceback.format_exc(), ])
        self._write(self.RAW, msg)

    @classmethod
    def prompt(self, title, message):
        """Display a Yes/No dialog prompt.

        :param title: The message box title.
        :type title: str
        :param message: The prompt to display.
        :type message: str
        :returns: True if User selects Yes, else No
        :rtype: bool
        """
        answer = ask(message, title, self.YES_NO_DIALOG)
        if answer == self.YES_NO_DIALOG_YES:
            return True
        return False

    def debug_error_stack(self):
        """Write the contents of the error stack to log as debug messages
        and clear the stack."""
        for priority, message in consume_errors():
            self.debug("Error Stack {}: {}".format(priority, message))
        return True
