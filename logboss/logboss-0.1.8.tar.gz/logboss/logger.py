import json
from typing import List, Callable, Any, Union, Tuple
import atexit
import sys
import dis
import traceback
import inspect
from datetime import datetime
import simplejson  # Required in case of PyInstaller
import jsonpickle
import re
import threading
from pathlib import Path
from contextlib import contextmanager
from functools import wraps
from logboss.config import LogTagBase, DefaultLogTags
from logboss.generators import HtmlLogGenerator


class _LogThread:
    def __init__(self, depth: int = -1, blacklist_function: callable = None,
                 mode: str = 'all', blacklist_log_tag: 'LogTagBase' = None):
        self.depth = depth
        self._mode = mode
        self.persistence_enabled = mode in {'all', 'persistence'}
        self.console_enabled = mode in {'all', 'console'}
        self.blacklist_function = None
        self.blacklist_function = blacklist_function
        self.blacklist_log_tag = blacklist_log_tag

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, value: str):
        if value == 'current':
            return
        elif value not in (values := {'all', 'persistence', 'console'}):
            raise ValueError(f'Cannot set mode to "{value}" because it is invalid.\n'
                             f'Valid modes are {values}')
        self._mode = value
        self.persistence_enabled = value in {'all', 'persistence'}
        self.console_enabled = value in {'all', 'console'}

    def blacklisted(self, log_tag: 'LogTagBase'):
        if not isinstance(self.blacklist_function, Callable):
            return False, False
        result = self.blacklist_function(log_tag)
        if isinstance(result, tuple):
            console_blacklisted, persistence_blacklisted = result
        elif isinstance(result, bool):
            console_blacklisted, persistence_blacklisted = [result] * 2
        else:
            raise ValueError(
                'A blacklist function must return either a single boolean (for blacklisting both '
                'console and persistence) or a tuple of booleans of size two (blacklist on console, '
                'blacklist on persistence).'
            )
        return console_blacklisted, persistence_blacklisted


class _Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class _LoggerPickler(jsonpickle.pickler.Pickler):
    MASKED_REGEXES = []
    LOCK = threading.Lock()

    def _flatten_key_value_pair(self, k, v, data):
        if self.MASKED_REGEXES and isinstance(k, jsonpickle.pickler.string_types):
            pattern = "(" + ")|(".join(self.MASKED_REGEXES) + ")"
            if re.match(pattern=pattern, string=str(k), flags=re.IGNORECASE):
                v = "********"
        return super()._flatten_key_value_pair(k, v, data)


class Logger(metaclass=_Singleton):
    """
    Creates a singleton instance of the logger.

    Set these properties prior to starting the logger if the default is undesired.

        * ``default_log_tag`` (default: INFO): LogTagType to use in ``log()`` when the log_tag isn't specified.
        * ``default_exception_tag`` (default: CRITICAL): LogTagType that will be called in ``log_exception()``.
        * ``date_format`` (default: `%Y/%m/%d %H:%M:%S`): String compatible with Python's strftime.
        * ``default_rule`` (default: ``lambda x: (False, False)``): Callable function that returns one or two booleans.
          If one boolean, then both console and persistence apply that value. Otherwise return a boolean in the order
          of (do not send to console, do not persist).
        * ``redirect`` (default: None): String path to the text file to create. The path is created if it doesn't exist.
        * ``add_log_tags()``: Call this method to add custom log tags prior to starting the logger.
    """

    CONSOLE_LOCK = threading.Lock()
    LOG_LOCK = threading.Lock()
    OP_LOCK = threading.Lock()

    def __init__(self):
        self.default_log_tags = DefaultLogTags()
        self.default_log_tag = self.default_log_tags.info
        self.default_exception_tag = self.default_log_tags.critical
        self._default_rule = lambda x: (False, False)

        self._disabled = True
        self._date_format = '%Y/%m/%d %H:%M:%S'
        self._timestamp = lambda: datetime.now().strftime(self._date_format)
        self._other_log_tags = []
        self._persistent_logging = False
        self._main_thread = threading.current_thread()
        self._threads = {self._main_thread.ident: _LogThread(depth=0)}
        self._jsonpickle = jsonpickle
        self._jsonpickle.pickler.Pickler = _LoggerPickler
        self._jsonpickle.set_encoder_options(simplejson.__name__, sort_keys=True, indent=4)
        self._redirect = None
        self._redirect_stream = None
        self._log_tags_locked = False
        self.__logs = {}
        self.__loaded_logs = {}

    @property
    def log_tags(self) -> List[LogTagBase]:
        log_tags = [self.default_log_tags] + self._other_log_tags
        return [v for y in log_tags for k, v in vars(y).items() if isinstance(v, LogTagBase)]

    def add_log_tags(self, value):
        """
        Appends the log tags to the list of custom log tags. This will fail after the logger has been started.
        The log tags must be stored in a class like this:

        .. code-block:: python

            class LogTags:
                some_tag = LogTagTypes.Info(name='Some Tag')

            logger.add_log_tags(LogTags)

        Args:
            value: A class of Log
        """
        if self._log_tags_locked and value not in self._other_log_tags:
            raise AssertionError(f'Log tags cannot be added to the logger after '
                                 f'the logger has been started.')
        self._other_log_tags.append(value)

    @property
    def default_rule(self):
        return self._default_rule

    @default_rule.setter
    def default_rule(self, value: Callable[[str, str], bool]):
        self._default_rule = value
        self._set_rule(reset=True, why=False)

    @staticmethod
    def add_cleanup(func, *args, **kwargs):
        """
        Add a cleanup action using Python's ``atexit`` module.

        Args:
            func: Callable function.
            *args: Function arguments.
            **kwargs: Function keyword arguments.
        """
        atexit.register(func, *args, **kwargs)

    @property
    def date_format(self):
        return self._date_format

    @date_format.setter
    def date_format(self, format: str):
        self._date_format = format

    def get_logs(self):
        """
        Use this to get the logs to pass to the HtmlLogGenerator parser. Not required
        if you are using the ``logger.generate()`` context manager.

        Returns: A dictionary with the log tags, entries, and main thread id.
        """
        if self.__loaded_logs:
            return self.__loaded_logs
        log_tags = [{
            'id': log_tag.__tag_id__,
            'name': log_tag.name,
            'alias': log_tag.alias,
            'value': log_tag.value,
            'color': log_tag.color
        } for log_tag in self.log_tags]

        return {
            'log_tags': log_tags,
            'log_entries': self.__logs,
            'main_thread_id': str(self._main_thread.ident)
        }

    @property
    def redirect(self):
        return self._redirect

    @redirect.setter
    def redirect(self, value: str):
        if self._redirect_stream is not None:
            self._redirect_stream.close()
        path = Path(value)
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
        self._redirect = value
        self._redirect_stream = open(value, 'a+')

    def clear_logs(self):
        """
        Clears the log entries.
        """
        self.__logs = {}

    @contextmanager
    def disabled(self, log_tag: Union[LogTagBase, str] = None, why: str = ''):
        """
        WARNING! This disables all logging in a context. This trumps all rules and modes as no logs
        will be processed or printed to the console. Use carefully. Upon exit of the context the logger
        will reset to the original state. Upon exit the logger will raise an error if any exceptions were
        raised in the context and the original state of the logger was enabled. In other words, if the
        logger was never started with ``start()``, then it will not log the exceptions.

        .. code-block:: python

            logger = Logger(...)

            with logger.disabled(log_tag=log_tags.default, why='Suppressing redundant logs...'):
                for i in range(5000):
                    logger.info('I will not be logged at all. Period.')
            logger.info('I am logged!')

        Args:
            log_tag: The LogTagBase object or one of 'debug', 'info', 'warning', 'error', or 'critical'.
            why: A description of why logging is being disabled.
        """
        if isinstance(log_tag, str):
            log_tag = self.default_log_tags[log_tag]
        else:
            log_tag = log_tag or self.default_log_tag
        num_prev_callers = 2
        orig_state = self._disabled
        try:
            self.log(msg=f'Disabling logging. {why}', log_tag=log_tag, num_prev_callers=num_prev_callers)
            self._disabled = True
            yield
        except:
            self._disabled = orig_state
            self.log(msg=f'Re-enabling logging. {why}', log_tag=log_tag, num_prev_callers=num_prev_callers)
            raise
        self._disabled = orig_state
        self.log(msg=f'Re-enabling logging. {why}', log_tag=log_tag, num_prev_callers=num_prev_callers)

    def dump(self, path: Union[Path, str]):
        """
        Dump the logs to ``path``. This option is still under development. Its intent is to dump
        logs to a file on disk to free memory. Currently memory isn't freed by default, so use only
        if you know what you are doing.

        Args:
            path: Path to the JSON file to dump the logs.
        """
        path = Path(path) if not isinstance(path, Path) else path
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('w') as f:
            json.dump(self.get_logs(), f)

    def load(self, json_file):
        """
        Loads logs from a JSON file, which would come from ``dump()``. This feature is still
        under development, so only use if you know what you are doing.

        Args:
            json_file: Path to the JSON file.
        """
        path = Path(json_file) if not isinstance(json_file, Path) else json_file
        if not path.exists():
            raise FileNotFoundError(f'Could load logs because the path "{path}" was not found.')
        with path.open('r') as f:
            self.__loaded_logs = json.load(f)

    @contextmanager
    def generate(self, format_generator: Union[str, Callable], log_file: Union[Path, str],
                 persist: bool = True, **kwargs):
        """
        A context manager that generates a log file from the logs persisted in the context using a format
        generator. The ``format_generator`` currently only supports HTML, but a custom one could be built.

        A custom log generator must be a class whose __init__ accepts the logs from ``get_logs()`` and
        must have a ``generate()`` method that accepts the log file path and kwargs. For example

        .. code-block:: python

            class CustomLogGenerator:
                def __init__(self, logs: dict):
                    self._log_tags = logs['log_tags']
                    self._log_entries = logs['log_entries']
                    self._main_thread_id = logs['main_thread_id']

                def generate(log_file: str, **kwargs):
                    # Define the generation logic here.
                    pass

        Args:
            format_generator: If a string type then only 'html' is supported, which uses the HtmlLogGenerator
                              class. Otherwise a custom callable object can be used to generate the logs.
            log_file: The path to the log file. It is created if it doesn't already exist.
            persist: If ``True`` then the data is persisted and the output is generated. Otherwise the generator
                     does not run.
        """
        if self._disabled:
            self.start(persist=persist)
        if self._persistent_logging:
            if isinstance(format_generator, str):
                generators = {
                    'html': HtmlLogGenerator
                }
                generator_class = generators[format_generator]
            else:
                generator_class = format_generator
            try:
                yield
            except:
                self.log_exception()
                raise
            finally:
                generator = generator_class(logs=self.get_logs())
                generator.generate(log_file=str(log_file), **kwargs)
        else:
            try:
                yield
            except:
                self.log_exception()

    def debug(self, msg: Any, num_prev_callers: int = 0):
        """
        Logs a message with the default DEBUG log tag.

        Args:
            msg: Log message.
            num_prev_callers: Number of previous calls in the call stack that identifies the
                originator of the log message. This should rarely, if ever, be set, but is
                configurable should a a previous caller be tied to the log message.
        """
        self.log(msg=msg, log_tag=self.default_log_tags.debug, num_prev_callers=num_prev_callers + 1)

    def info(self, msg: Any, num_prev_callers: int = 0):
        """
        Logs a message with the default INFO log tag.

        Args:
            msg: Log message.
            num_prev_callers: Number of previous calls in the call stack that identifies the
                originator of the log message. This should rarely, if ever, be set, but is
                configurable should a a previous caller be tied to the log message.
        """
        self.log(msg=msg, log_tag=self.default_log_tags.info, num_prev_callers=num_prev_callers + 1)

    def warning(self, msg: Any, num_prev_callers: int = 0):
        """
        Logs a message with the default WARNING log tag.

        Args:
            msg: Log message.
            num_prev_callers: Number of previous calls in the call stack that identifies the
                originator of the log message. This should rarely, if ever, be set, but is
                configurable should a a previous caller be tied to the log message.
        """
        self.log(msg=msg, log_tag=self.default_log_tags.warning, num_prev_callers=num_prev_callers + 1)

    def error(self, msg: Any, num_prev_callers: int = 0):
        """
        Logs a message with the default ERROR log tag.

        Args:
            msg: Log message.
            num_prev_callers: Number of previous calls in the call stack that identifies the
                originator of the log message. This should rarely, if ever, be set, but is
                configurable should a a previous caller be tied to the log message.
        """
        self.log(msg=msg, log_tag=self.default_log_tags.error, num_prev_callers=num_prev_callers + 1)

    def critical(self, msg: Any, num_prev_callers: int = 0):
        """
        Logs a message with the default CRITICAL log tag.

        Args:
            msg: Log message.
            num_prev_callers: Number of previous calls in the call stack that identifies the
                originator of the log message. This should rarely, if ever, be set, but is
                configurable should a a previous caller be tied to the log message.
        """
        self.log(msg=msg, log_tag=self.default_log_tags.critical, num_prev_callers=num_prev_callers + 1)

    def log(self, msg: Any, log_tag: Union[LogTagBase, str] = None, num_prev_callers: int = 0):
        """
        Logs a message with the ``log_tag`` log tag if given, else the ``default_log_tag``, which, if
        not explicitly set, defaults to the INFO log tag.

        Args:
            msg: Log message.
            log_tag: The LogTagBase object or one of 'debug', 'info', 'warning', 'error', or 'critical'.
            num_prev_callers: Number of previous calls in the call stack that identifies the
                originator of the log message. This should rarely, if ever, be set, but is
                configurable should a a previous caller be tied to the log message.
        """
        if self._disabled:
            return

        if isinstance(log_tag, str):
            log_tag = self.default_log_tags[log_tag]
        else:
            log_tag = log_tag or self.default_log_tag
        thread = threading.current_thread()
        if lt := self._threads.get(thread.ident):
            no_console, no_persistence = lt.blacklisted(log_tag)
            if no_console and no_persistence:
                return
        else:
            no_console, no_persistence = [False] * 2
        func, file_path, line_num = self._get_log_info(num_prev_callers=num_prev_callers)
        self._commit_log(msg=msg, log_tag=log_tag, file_path=file_path, line_num=line_num, func=func,
                         no_console=no_console, no_persistence=no_persistence)

    def log_exception(self, log_tag: Union[LogTagBase, str] = None):
        """
        Logs an exception using `traceback.format_exc()` with the ``log_tag`` log tag if given, else
        the ``default_exception_tag``, which, if not explicitly set, defaults to the CRITICAL log tag.

        Args:
           log_tag: The LogTagBase object or one of 'debug', 'info', 'warning', 'error', or 'critical'.
                    The ``default_exception_tag`` is used by default.
        """
        if self._disabled:
            return
        if isinstance(log_tag, str):
            log_tag = self.default_log_tags[log_tag]
        else:
            log_tag = log_tag or self.default_exception_tag
        with self.OP_LOCK:
            tb = sys.exc_info()[2]

        while True:
            if tb.tb_next is None:
                break
            tb = tb.tb_next
        frame = tb.tb_frame
        outer_frames = inspect.getouterframes(frame)[0]
        if outer_frames.function == '<module>':
            func = inspect.getmodulename(outer_frames.filename)
        else:
            if (class_name := outer_frames[0].f_locals.get('self')) is not None:
                func = f'{class_name.__class__.__qualname__}.{outer_frames.function}'
            else:
                func = outer_frames.function
        msg = traceback.format_exc()
        self._commit_log(msg=msg, log_tag=log_tag, file_path=outer_frames[1], line_num=outer_frames[2],
                         func=func)

    def log_method(self, func: callable, msg: Any, log_tag: Union[LogTagBase, str] = None, returning: bool = False):
        """
        Logs a call or exit of a method or function with the name of the callable and the given ``msg``
        with the ``log_tag`` log tag if given, else the ``default_log_tag``, which, if not explicitly set,
        defaults to the INFO log tag. This is generally not needed and should only be used by ``wrap_func()``.

        Args:
            func: A callable object.
            msg: The log message.
            log_tag: The LogTagBase object or one of 'debug', 'info', 'warning', 'error', or 'critical'.
            returning: If ``True`` gets the last line number of the function instead of the first for the log.
        """
        if self._disabled:
            return
        if isinstance(log_tag, str):
            log_tag = self.default_log_tags[log_tag]
        else:
            log_tag = log_tag or self.default_log_tag
        thread = threading.current_thread()
        if lt := self._threads.get(thread.ident):
            no_console, no_persistence = lt.blacklisted(log_tag)
            if no_console and no_persistence:
                return
        else:
            no_console, no_persistence = [False] * 2

        self._commit_log(
            msg=msg,
            log_tag=log_tag,
            file_path=func.__code__.co_filename,
            line_num=list(dis.findlinestarts(func.__code__))[-1][-1] if returning else func.__code__.co_firstlineno,
            func=func.__qualname__,
            no_console=no_console,
            no_persistence=no_persistence
        )

    @contextmanager
    def rule(self, log_tag: Union[LogTagBase, str] = None, min_level: str = None,
             blacklist_function: Callable[[LogTagBase], Tuple[bool, bool]] = None, why: str = ''):
        """
        The context manager equivalent of ``set_rule()``. When the context exits the ``default_log_rule``
        is applied, which if unset defaults to ``lambda x: (False, False)``, which means there are no
        restrictions enforced by the rules.

        Args:
            log_tag: The LogTagBase object or one of 'debug', 'info', 'warning', 'error', or 'critical'.
            min_level: If a string, must be one of 'debug', 'info', 'warning', 'error', or 'critical', from
                       which the value of the respective default log tag type is used as a minimum threshold
                       for a log event to occur. Otherwise it must be an integer.
            blacklist_function: A custom callable that accepts a single argument (the log tag) and returns
                       either a single boolean (which applies to both console and persistent modes) or a tuple
                       of booleans where the first applies to the console and the second to persistence. A
                       value of ``True`` means the log event will be ignored (hence blacklisted).
            why: The reason why the rule is being created, which is logged using the ``log_tag``.
        """
        self._set_rule(log_tag=log_tag, min_level=min_level, blacklist_function=blacklist_function,
                       why=why, num_prev_callers=2)
        yield
        self._set_rule(log_tag=log_tag, reset=True, num_prev_callers=2)

    def set_mode(self, mode: str, log_tag: Union[LogTagBase, str] = None, why: str = ''):
        """
        The log mode can be used to change where the logs are recorded. This is useful for simply
        reducing noise in the log output.

        There are four modes: current, console, persistence, and all.

            * current: Do not change the mode. Default.
            * console: Change the mode to log to the console only.
            * persistence: Change the mode to log to the SQLite DB file only.
            * all: Change the mode to use both console and persistent logging.

        Args:
            mode: One of 'current', 'console', 'persistence', or 'all'. Default is 'current'. Case sensitive.
            log_tag: The LogTagBase object or one of 'debug', 'info', 'warning', 'error', or 'critical'.
            why: A description of why the mode is being set.
        """
        if self._disabled:
            return

        thread = threading.current_thread()
        if isinstance(log_tag, str):
            log_tag = self.default_log_tags[log_tag]
        else:
            log_tag = log_tag or self.default_log_tag
        msg = f'Setting log mode to "{mode}". '
        if why:
            msg += f" => {why}"
        if thread.ident == self._main_thread.ident:
            for t in self._threads.values():
                t.mode = mode
        elif lt := self._threads.get(thread.ident):
            lt.mode = mode
        else:
            self._threads[thread.ident] = _LogThread(
                depth=self._threads[self._main_thread.ident].depth,
                blacklist_function=self._threads[self._main_thread.ident].blacklist_function,
                mode=mode
            )

        func, file_path, line_num = self._get_log_info(num_prev_callers=0)
        self._commit_log(msg=msg, log_tag=log_tag, file_path=file_path, line_num=line_num, func=func,
                         force=True)

    def set_rule(self, log_tag: Union[LogTagBase, str] = None, min_level: str = None,
                 blacklist_function: Callable[[LogTagBase], Tuple[bool, bool]] = None,
                 reset: bool = False, why: str = ''):
        """
        Sets a rule for blacklisting log messages. This is particularly useful when reducing noise in the
        log output. Only one of ``min_level``, ``blacklist_function``, or ``reset`` can be specified.

        Args:
            log_tag: The LogTagBase object or one of 'debug', 'info', 'warning', 'error', or 'critical'.
            min_level: If a string, must be one of 'debug', 'info', 'warning', 'error', or 'critical', from
                       which the value of the respective default log tag type is used as a minimum threshold
                       for a log event to occur. Otherwise it must be an integer.
            blacklist_function: A custom callable that accepts a single argument (the log tag) and returns
                       either a single boolean (which applies to both console and persistent modes) or a tuple
                       of booleans where the first applies to the console and the second to persistence. A
                       value of ``True`` means the log event will be ignored (hence blacklisted).
            reset: If ``True`` then the ``default_log_rule`` is applied.
            why: The reason why the rule is being created, which is logged using the ``log_tag``.
        """
        return self._set_rule(
            log_tag=log_tag, min_level=min_level, blacklist_function=blacklist_function, reset=reset,
            why=why, num_prev_callers=1
        )

    def start(self, persist: bool = False):
        """
        Starts the logger. If not called, no log events occur. Once the logger is started then the log
        tags cannot be modified. Also, it is wise to NOT modify the ``redirect``, ``default_log_tag``,
        ``default_exception_tag``, ``default_log_rule``, or any of the private variables associated to
        the logger. In general, once the logger is started, then the only calls to the logger should
        be setting rules/modes and logging messages.

        Args:
            persist: If ``True`` the logs will also persist in memory. Otherwise logs are only sent to
                the console or ``redirect`` path.\
        """
        self._disabled = False
        self._log_tags_locked = True
        self._persistent_logging = persist
        self._threads = {
            self._main_thread.ident: _LogThread(
                depth=0,
            )
        }

    def wrap_class(self, log_tag: Union[LogTagBase, str] = None, func_regex_exclude: str = '', mask_input_regexes: List = None,
                   mask_output: bool = False, mask_output_regexes: List = None):
        """
        Applies ``wrap_func()`` to each callable member of a class that does not start with "__" and does not
        match the ``func_regex_exclude``. If a callable member starting with "__" should be wrapped, then it
        must be explicitly wrapped with the ``wrap_func()`` method. The ``mask_input_regexes`` and ``mask_output``
        parameters are passed to the ``wrap_func()`` method.

        Args:
            log_tag: The LogTagBase object or one of 'debug', 'info', 'warning', 'error', or 'critical'.
            func_regex_exclude: A regular expression matching method names that should not be wrapped.
            mask_input_regexes: Passed to ``wrap_func()``.
            mask_output: Passed to ``wrap_func()``.
            mask_output_regexes: Passed to ``wrap_func()``..
        """
        if isinstance(log_tag, str):
            log_tag = self.default_log_tags[log_tag]
        else:
            log_tag = log_tag or self.default_log_tag
        if isinstance(mask_output_regexes, list):
            with _LoggerPickler.LOCK:
                _LoggerPickler.MASKED_REGEXES = list(set(_LoggerPickler.MASKED_REGEXES + mask_output_regexes))

        def _wrap(cls):
            for attr, fn in inspect.getmembers(cls, inspect.isroutine):
                if callable(getattr(cls, attr)) and not fn.__name__.startswith('__'):
                    if func_regex_exclude:
                        matches = re.findall(pattern=func_regex_exclude, string=fn.__name__, flags=re.IGNORECASE)
                        if fn.__name__ in matches:
                            continue
                    if type(cls.__dict__.get(fn.__name__)) is staticmethod:
                        setattr(cls, attr, self.wrap_func(
                            log_tag=log_tag,
                            is_staticmethod=True,
                            mask_input_regexes=mask_input_regexes,
                            mask_output=mask_output
                        )(getattr(cls, attr)))
                    elif type(cls.__dict__.get(fn.__name__)) is classmethod:
                        setattr(cls, attr, self.wrap_func(
                            log_tag=log_tag,
                            is_classmethod=True,
                            mask_input_regexes=mask_input_regexes,
                            mask_output=mask_output
                        )(getattr(cls, attr)))
                    else:
                        setattr(cls, attr, self.wrap_func(
                            log_tag=log_tag,
                            mask_input_regexes=mask_input_regexes,
                            mask_output=mask_output
                        )(getattr(cls, attr)))
            return cls
        return _wrap

    def wrap_func(self, log_tag: Union[LogTagBase, str] = None, mask_input_regexes: List = None, mask_output: bool = False,
                  mask_output_regexes: List = None, is_staticmethod: bool = False, is_classmethod: bool = False):
        """
        Wrapper for a function or method. This wrapper performs a few important steps:
            #. Increases the depth of the call, which controls its relation to all previous and
               subsequent logs in the log hierarchy.
            #. Logs the function's name, inputs, and outputs.
            #. Catches any exceptions raised by the function and logs them.
            #. Decreases the depth of the call to return to the original depth of the call hierarchy.

        The depth is the defining marker for the position of a function in the logged hierarchy. Without it,
        all logs would be flat an hard to parse through.

        .. code-block:: python

            @logger.wrap_func(
                log_tag=Tags.SomeTag,
                mask_input_regexes=['cls', 'password'],
                mask_output_regexes=['.*api.*token.*']
            )
            @classmethod
            def do_something(cls, username, password):
                # Do some stuff
                return {'API Token': 'xyz'}

        * The above example will use the ``Tags.SomeTag`` tag to log the calling and the returning message.
        * The ``cls`` and ``password`` parameters will be masked. The message will show this::

              Called do_something
              Arguments:
              {
                  "cls": "********",
                  "username": "Admin",
                  "password": "********"
              }

        * The output is not masked entirely, but the output will be partially masked like this::

              do_something returned.
              Return Values:
              {
                  "API Token": "********"
              }

        Args:
            log_tag: The LogTagBase object or one of 'debug', 'info', 'warning', 'error', or 'critical'.
            mask_input_regexes: A list of regular expressions matching input variable names.
            mask_output: When ``True`` the entire  output is masked like this: "********".
            mask_output_regexes: A list of regular expressions of keys whose values ought to be masked in the
                                 output. This only applies to return values with key/value pair associations.
                                 Use ``mask_output`` if the output is not a dictionary-like object (such as a string)
            is_classmethod: If ``True`` then the method is intended to be a classmethod.
            is_staticmethod: If ``True`` the the method is intended to be a staticmethod.
        """
        if isinstance(log_tag, str):
            log_tag = self.default_log_tags[log_tag]
        else:
            log_tag = log_tag or self.default_log_tag
        if isinstance(mask_output_regexes, list):
            with _LoggerPickler.LOCK:
                _LoggerPickler.MASKED_REGEXES = list(set(_LoggerPickler.MASKED_REGEXES + mask_output_regexes))

        def __wrap(func):
            @wraps(func)
            def __wrapper(*args, **kwargs):
                if is_classmethod:
                    args = args[1:]
                if self._disabled:
                   return func(*args, **kwargs)

                thread = threading.current_thread()
                # If the current thread hasn't been accounted for, account for it by creating a
                # _LogThread using the main thread's configuration.
                if not self._threads.get(thread.ident):
                    mt = self._threads.get(self._main_thread.ident, _LogThread())
                    self._threads[thread.ident] = _LogThread(
                        depth=mt.depth,
                        blacklist_function=mt.blacklist_function,
                        mode=mt.mode,
                        blacklist_log_tag=mt.blacklist_log_tag
                    )

                # Before the function is called.
                try:
                    params = dict(inspect.signature(func).bind(*args, **kwargs).arguments)  # type: dict
                except TypeError as e:
                    self.log(
                        msg='\n'.join(e.args),
                        log_tag=self.default_exception_tag,
                        num_prev_callers=2
                    )
                    raise TypeError(e)

                before_string = 'Called ' + func.__qualname__
                if params:
                    if mask_input_regexes:
                        in_regexes = "(" + ")|(".join(mask_input_regexes) + ")"
                        for key in params.keys():
                            if re.match(pattern=in_regexes, string=key, flags=re.IGNORECASE):
                                params[key] = '********'
                    before_string += '\nArguments:\n' + self._jsonpickle.dumps(params, max_depth=3, unpicklable=False)
                self.log_method(func=func, msg=before_string, log_tag=log_tag, returning=False)
                self._threads[thread.ident].depth += 1
                try:
                    result = func(*args, **kwargs)

                    # After the function returns.
                    after_string = f'{func.__qualname__} returned.'
                    if result is not None:
                        if mask_output:
                            after_string += ' Output is masked.'
                        else:
                            ret_vals = self._jsonpickle.dumps(result, max_depth=3, unpicklable=False)
                            after_string += f'\nReturn Values: {ret_vals}'
                    self.log_method(func=func, msg=after_string, log_tag=log_tag, returning=True)

                    return result
                except:
                    self.log_exception()
                    raise
                finally:
                    self._threads[thread.ident].depth -= 1

            if is_classmethod:
                return classmethod(__wrapper)
            if is_staticmethod:
                return staticmethod(__wrapper)
            return __wrapper
        return __wrap

    def _commit_log(self, msg: Any, log_tag: LogTagBase, file_path: str, line_num: int, func: str = None,
                    force: bool = False, no_console: bool = False, no_persistence: bool = False):
        """
        Commits the log transaction to the console (or redirect stream) and to memory..

        Args:
            msg: Log message.
            log_tag: The LogTagBase object.
            file_path: Absolute path to the file in relation to the log message.
            line_num: Line number in the ``file_path``.
            func: Optional. The qualified name of the function in relation to the ``line_num``.
            force: Optional. If ``True``, then the log thread settings are ignored and the message is logged to
                   the console and, if ``persistent logging==True``, then the message is persisted.
            no_console: Optional. If ``True``, console output will be suppressed unless ```force`` is ``True``.
            no_persistence: Optional. If ``True``, persistence will be suppressed unless ```force`` is ``True``.
        """
        thread = threading.current_thread()
        # If the current thread hasn't been accounted for, account for it by creating a
        # _LogThread using the main thread's configuration.
        if (mt := self._threads.get(thread.ident)) is None:
            mt = self._threads.get(self._main_thread.ident, _LogThread())
            self._threads[thread.ident] = _LogThread(
                depth=mt.depth,
                blacklist_function=mt.blacklist_function,
                mode=mt.mode,
                blacklist_log_tag=mt.blacklist_log_tag
            )

        if (mt.console_enabled and not no_console) or force:
            with self.CONSOLE_LOCK:
                print(f'[{log_tag.name}] {self._timestamp()}: {msg}', file=self._redirect_stream, flush=True)

        if self._persistent_logging and ((mt.persistence_enabled and not no_persistence) or force):
            key = str(thread.ident)
            with self.LOG_LOCK:
                if key not in self.__logs:
                    self.__logs[key] = []
                self.__logs[key].append(dict(
                    file_path=file_path,
                    function_name=func,
                    line_num=line_num,
                    msg=str(msg),
                    tag_id=log_tag.__tag_id__,
                    depth=self._threads[thread.ident].depth,
                    thread_id=thread.ident,
                    thread_name=thread.name,
                    is_main_thread=(thread.ident == self._main_thread.ident),
                    timestamp=datetime.utcnow().timestamp()
                ))

    def _get_log_info(self, num_prev_callers: int):
        with self.OP_LOCK:
            frame = inspect.currentframe()
        # Add two because this should only be called once internally.
        outer_frames = inspect.getouterframes(frame)[num_prev_callers + 2]
        if outer_frames.function == '<module>':
            func = inspect.getmodulename(outer_frames.filename)
        else:
            if (class_name := outer_frames[0].f_locals.get('self')) is not None:
                func = f'{class_name.__class__.__qualname__}.{outer_frames.function}'
            else:
                func = outer_frames.function
        return func, outer_frames[1], outer_frames[2]

    def _set_rule(self, log_tag: Union[LogTagBase, str] = None, min_level: Union[LogTagBase, str] = None,
                  blacklist_function: Callable[[LogTagBase], Tuple[bool, bool]] = None,
                  reset: bool = False, why: Union[str, bool] = '', num_prev_callers: int = 0):
        if self._disabled:
            return

        if isinstance(log_tag, str):
            log_tag = self.default_log_tags[log_tag]
        else:
            log_tag = log_tag or self.default_log_tag
        thread = threading.current_thread()
        if lt := self._threads.get(thread.ident):
            if lt.blacklist_log_tag and log_tag.value < lt.blacklist_log_tag.value:
                return

        blacklist_log_tag = log_tag
        if min_level:
            if isinstance(min_level, int):
                level = min_level
            elif isinstance(min_level, str):
                level = self.default_log_tags[min_level].value
            elif isinstance(min_level, LogTagBase):
                level = min_level.value
            else:
                raise ValueError('min_level must be one of "debug", "info", "warning", "error" or '
                                 '"critical", or an integer.')
            msg = f'Only log tags with values greater than or equal to {level} will be logged.'
            blacklist_function = lambda x: x.value < level
            blacklist_log_tag = None
        elif blacklist_function:
            msg = f'A function has been defined to decide what is logged.'
        elif reset:
            blacklist_function = self.default_rule
            blacklist_log_tag = None
            if not self._default_rule:
                msg = f'Resetting rule. There are no restrictions to logging in this rule.'
            else:
                msg = f'Resetting rule to the default rule.'
            why = f'{msg} => {why}' if why else msg
        else:
            blacklist_function = self.default_rule
            blacklist_log_tag = None
            msg = f'No rule defined. There are no restrictions to logging in this rule.'

        if why is not False:
            func, file_path, line_num = self._get_log_info(num_prev_callers=num_prev_callers)
            why = why or msg
            self._commit_log(msg=why, log_tag=log_tag, file_path=file_path, line_num=line_num, func=func)

        if thread.ident == self._main_thread.ident:
            for thread in self._threads.values():
                thread.blacklist_function = blacklist_function
                thread.blacklist_log_tag = blacklist_log_tag
        elif lt := self._threads.get(thread.ident):
            lt.blacklist_function = blacklist_function
            lt.blacklist_log_tag = blacklist_log_tag
        else:
            self._threads[thread.ident] = _LogThread(
                depth=self._threads[self._main_thread.ident].depth,
                blacklist_function=blacklist_function,
                mode=self._threads[self._main_thread.ident].mode,
                blacklist_log_tag=blacklist_log_tag
            )
