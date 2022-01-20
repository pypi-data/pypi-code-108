import logging
import sys
import socket
import threading

from datetime import date, datetime, time
from json import dumps, JSONEncoder
from logging.config import dictConfig
from typing import Any, Dict, List, Optional, Union
from warnings import warn

from pytz import UTC

from DKCommon.str_utils import decode_bytes

_LOCK = threading.RLock()


class JsonLogEncoder(JSONEncoder):
    """
    Extend JSON encoder and fallback to string casting for unsupported types.

    Including the ability to add additional context to logging messages means there is less control over
    the what is passed TO log messages. This extended encoder ensures log messages can be emited as JSON
    without worrying about crashing (in most cases).

    Date, time and datetime instances are converted to strings in ISO8601 format.
    """

    def default(self, o: Any) -> Union[str, List]:
        if isinstance(o, (date, datetime, time)):
            return o.isoformat()
        elif isinstance(o, tuple):
            return list(o)
        elif isinstance(o, set):
            return sorted(o)  # Sorted returns a list
        elif isinstance(o, bytes):
            try:
                return decode_bytes(o)
            except UnicodeDecodeError:
                return str(o)
        elif isinstance(o, memoryview):
            try:
                return decode_bytes(o.tobytes())
            except UnicodeDecodeError:
                return str(o)
        else:
            try:
                return super().default(o)
            except TypeError:
                return str(o)


class ContextLogRecord(logging.LogRecord):
    """Extended LogRecord with additional context."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set some default values
        self.extra_keys: List[str] = []
        self.hostname = socket.gethostname()

        # TODO: Remove these when mongo logging is completely gone. They are only necessary here
        # because some formatters expect the logrecords __dict__ to have these keys.
        self.mem_usage: Optional[str] = None
        self.disk_used: Optional[str] = None
        self.node: Optional[str] = None

    def __str__(self):
        return f'<ContextLogRecord: {self.name}, {self.levelno}, {self.pathname}, {self.lineno}, "{self.msg}">'

    def add_field(self, *, name: str, value: Any, force: bool = False):
        """Add a field to the log record."""
        if hasattr(self, name) and force is False:
            raise ValueError(f"Cannot overwrite field {name}; already exists.")
        setattr(self, name, value)
        self.extra_keys.append(name)

    @property
    def message_str(self) -> str:
        """Return the message for this LogRecord, decoding from bytes to a string if necessary."""
        if isinstance(self.msg, str):
            return self.msg
        elif isinstance(self.msg, bytes):
            try:
                self.msg = decode_bytes(self.msg)
            except UnicodeDecodeError:
                self.msg = str(self.msg)
            return self.msg
        else:
            self.msg = str(self.msg)
            return self.msg

    def getMessage(self) -> str:
        """
        Return the message for this LogRecord after merging any user-supplied arguments.

        In the case that the log message was arbitrary bytes, we attempt to decode the value as text. NOTE: this
        may not be necessary, but I cannot be sure how the end-users are utilizing this so taking care of the
        decoding is done in case.
        """
        if self.args:
            return self.message_str % self.args
        else:
            return self.message_str


class ExtendedLogger(logging.Logger):
    """An extended logger that adds a trace level and the uses the ContextLogRecord."""

    def trace(self, msg, *args, **kwargs):
        """Log 'msg % args' with severity 'TRACE'."""
        if self.isEnabledFor(5):
            self._log(5, msg, args, **kwargs)

    def _log(self, level, msg, args, exc_info=None, extra=None, stack_info=None, **kwargs):
        """
        Adds extra keyword arguments passed to the `extras` dict.

        If no additional keyword arguments are passed, `extra` remains "None" as expected by the logging system
        upstream. If extra keyword arguments *are* passed then `extra` will be a dict containing the additional
        keyword arguments.
        """
        if kwargs:
            if extra is None:
                extra = {}
            extra.update(kwargs)
        super()._log(level, msg, args, exc_info=exc_info, extra=extra, stack_info=stack_info)

    def makeRecord(
        self, name, level, fn, lno, msg, args, exc_info, func=None, extra=None, sinfo=None
    ) -> ContextLogRecord:
        """
        Factory method for building LogRecord instances.

        The custom LogRecordFactory should be set when logging is initialized, but in the event that
        it is not, make sure to always use the ContextLogRecord.
        """
        record = ContextLogRecord(name, level, fn, lno, msg, args, exc_info, func, sinfo)
        if extra is not None:
            if not isinstance(extra, dict):
                warn(f"Log records were passed extra context that was not a dict instance. Got `{type(extra)}`")
            else:
                for key, value in extra.items():
                    if not hasattr(record, key):
                        record.add_field(name=key, value=value)
                    else:
                        warn(f"Not overwriting log record attribute `{key}` - already exists")
        return record


class JsonLogFormatter(logging.Formatter):
    """
    A log formatter that outputs JSON; useful for logging to ELK or other logging services.

    If given, the order_run_id is included, as well as any extra context passed (if the
    record being formatted is a ContextLogRecord instance).
    """

    KEYLIST = (
        "name",
        "levelname",
        "levelno",
        "pathname",
        "filename",
        "module",
        "lineno",
        "funcName",
        "thread",
        "threadName",
        "processName",
        "process",
    )
    """List of attributes to include as-is (no parsing or modification)."""

    def format(self, record: logging.LogRecord) -> str:
        record_dict = {x: getattr(record, x, None) for x in self.KEYLIST}
        record_dict["timestamp"] = record.created
        naive_dt_obj = datetime.utcfromtimestamp(record.created)
        utc_dt_obj = naive_dt_obj.replace(tzinfo=UTC)
        record_dict["ISO8601"] = utc_dt_obj.isoformat()
        record_dict["message"] = record.getMessage()
        record_dict["asctime"] = self.formatTime(record, self.datefmt)
        record_dict["traceback"] = self.formatException(record.exc_info) if record.exc_info else None
        record_dict["stackinfo"] = self.formatStack(record.stack_info) if record.stack_info else None

        # Update the record dict with extra context but avoid overwriting existing keys
        for key in getattr(record, "extra_keys", []):
            if key in record_dict:
                warn(f"Extra context key `{key}` skipped because this key was already in use.")
            else:
                record_dict[key] = getattr(record, key, None)
        return dumps(record_dict, sort_keys=True, cls=JsonLogEncoder)


class InternalFilter(logging.Filter):
    """Simple filter that excludes log messages with internal=True set."""

    def filter(self, record) -> bool:
        if getattr(record, "internal", False) is True:
            return False
        else:
            return True


def init_logging():
    """Perform initial logging setup so that the Python logging defaults to our extended types."""
    with _LOCK:

        # Add TRACE log level
        logging.addLevelName(5, "TRACE")

        # Set default LoggerClass
        logging.setLoggerClass(ExtendedLogger)
        logging.Logger.manager.setLoggerClass(ExtendedLogger)

        # Setup the default LogRecordFactory to return ContextLogRecord instances
        logging.setLogRecordFactory(ContextLogRecord)
        logging.Logger.manager.setLogRecordFactory(ContextLogRecord)

        # Any existing loggers that aren't ExtendedLogger instances, re-instanciate; update any
        # record factories and record classes
        for name, instance in logging.Logger.manager.loggerDict.items():
            if not isinstance(instance, (ExtendedLogger, logging.PlaceHolder)):
                logging.Logger.manager.loggerDict[name] = ExtendedLogger(instance.name, level=instance.level)

        # Patch out any already created loggers to make sure they're ExtendedLogger instances
        for module in tuple(sys.modules.values()):
            for attr_name in dir(module):
                try:
                    attr = getattr(module, attr_name, None)
                except Exception:
                    continue
                # If it's a Logger instance (but not a custom subclass of any kind), re-initialize
                if isinstance(attr, logging.Logger) and attr.__class__ is logging.Logger:
                    setattr(module, attr_name, ExtendedLogger(attr.name, level=attr.level))


def configure_basic_logging(level: str = "TRACE"):
    """
    A basic logging setup which configures a single console logger.

    Suitable for basic initialization or runs during a test suite.
    """
    init_logging()  # Setup the custom DK logging instances
    BASE_CONFIG: Dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": True,
        "formatters": {"simple": {"format": "%(levelname)8s %(message)s - %(name)s:%(lineno)s"}},
        "handlers": {"console": {"level": level, "class": "logging.StreamHandler", "formatter": "simple"}},
        "loggers": {
            "DKCommon": {"handlers": ["console"], "level": level},
            "DKModules": {"handlers": ["console"], "level": level},
            "DKRestBase": {"handlers": ["console"], "level": level},
            "flask": {"handlers": ["console"], "level": "ERROR"},
            "monitor": {"handlers": ["console"], "level": level},
            "pymongo": {"handlers": ["console"], "level": "ERROR"},
            "RecipeRunner": {"handlers": ["console"], "level": level},
            "repo_rest_api": {"handlers": ["console"], "level": level},
            "server": {"handlers": ["console"], "level": level},
            "service": {"handlers": ["console"], "level": level},
            "urllib3": {"handlers": ["console"], "level": "ERROR"},
        },
    }
    dictConfig(BASE_CONFIG)
