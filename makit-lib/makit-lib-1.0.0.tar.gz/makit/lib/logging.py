#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@author: LiangChao
@email：liangchao@noboauto.com
@desc: 
"""
import atexit
import os
import sys
import threading
import time
import traceback
from datetime import datetime

from colorama import Fore

from . import fn, ospath
from .const import DEFAULT_TIME_FORMAT
from .ospath import Path

_loggers = []


def safe_exit():
    for _logger in _loggers:
        _logger.exit()


atexit.register(safe_exit)  # 保证python主进程退出时释放所有文件流


class Record(dict):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.time = datetime.now()

    def __getattr__(self, item):
        try:
            return super().__getattribute__(item)
        except AttributeError:
            return self.get(item)


class Level:
    def __init__(self, name, value, color=None):
        self.name = name
        self.code = value
        self.color = color
        self.instance = None
        self.disabled = False

    def disable(self):
        self.disabled = True
        return self

    def __set__(self, instance, value):
        raise LoggingError('Can not change level!')

    def __get__(self, instance, owner):
        self.instance = instance
        return self

    def __call__(self, message, *args, **kwargs):
        if self.code <= 0:
            raise LoggingError(f'Level {self.name} is not callable!')  # TODO return?
        if self.instance.is_enabled_for(self):
            self.instance.log(self, message, *args, **kwargs)

    def __repr__(self):
        return f'<Level {self.name}>'


class Logger:
    notset = Level(name='NOTSET', value=0)
    debug = Level(name='DEBUG', value=10, color=Fore.CYAN)
    info = Level(name='INFO', value=20, color=Fore.GREEN)
    warning = Level(name='WARNING', value=30, color=Fore.YELLOW)
    error = Level(name='ERROR', value=40, color=Fore.RED)
    critical = Level(name='CRITICAL', value=50, color=Fore.RED)

    def __init__(self, level=None):
        self.level = level or self.notset
        self._handlers = []
        self._lock = None
        self.disabled = False
        self._extra_info = {}
        _loggers.append(self)

    @property
    def lock(self):
        if not self._lock:
            self._lock = threading.RLock()
        return self._lock

    def log(self, level, message, *args, include_stack=False, invoked_file=None, **kwargs):
        if self.disabled:
            return
        c = fn.parse_caller(invoked_file=invoked_file or __file__)
        filename, func, lno = c.filename, c.func_name, c.lineno
        if args or kwargs:
            message = message.format(*args, **kwargs)
        record = Record(
            msg=message,
            level=level,
            filename=filename,
            lineno=lno,
            func_name=func,
            **self._extra_info
        )
        if include_stack:
            record['stack_info'] = c.get_stack()
        self._handle_record(record)

    def _handle_record(self, record):
        for handler in self._handlers:
            if record.level.code >= handler.level.code:
                handler.handle(record)
        if len(self._handlers) == 0:  # 如果没有任何日志处理器，则使用默认的控制台输出
            console.handle(record)

    def add_handler(self, handler):
        """
        添加handler
        """
        with self.lock:
            if handler not in self._handlers:
                self._handlers.append(handler)

    def remove_handler(self, handler):
        """
        移除handler
        """
        with self.lock:
            if handler in self._handlers:
                self._handlers.remove(handler)

    def write_file(self, filename, level=None, mode='a', encoding='utf-8', max_size=None, backup_count=10, fmt=None):
        """

        :param level: 级别
        :param filename: 日志文件
        :param mode: 写入模式
        :param encoding: 编码
        :param max_size: 文件最大mb数
        :param backup_count: 最多保留备份数
        :param fmt: 日志格式
        :return:
        """
        if not filename.endswith('.log'):
            filename += '.log'
        filename = os.path.abspath(filename)
        Path(filename).parent.mkdirs(exist_ok=True)
        if not level:
            level = Logger.notset
        if isinstance(level, str):
            level = getattr(logger, level)
        if max_size:
            handler = RotatingFileHandler(
                level, filename, mode,
                max_bytes=max_size * 1024 * 1024,
                encoding=encoding,
                backup_count=backup_count
            )
        else:
            handler = FileHandler(level, filename, mode=mode, encoding=encoding)
        self.add_handler(handler)
        return self

    def send_socket(self, ip, port):
        """

        :param ip:
        :param port:
        :return:
        """

    def http_post(self, url, auth=None):
        """

        :param url:
        :param auth:
        :return:
        """

    def extra(self, **kwargs):
        """
        添加附加信息，配合格式化字符串可以统一追加信息
        :param kwargs:
        :return:
        """
        self._extra_info.update(**kwargs)

    def is_enabled_for(self, level):
        if self.disabled:
            return False
        return level.code >= self.level.code

    def exit(self):
        for handler in self._handlers:
            handler.close()

    def __repr__(self):
        return f'<{self.__class__.__name__} ({self.level.name})>'


class Handler:
    """"""
    FORMAT = None
    TIME_FORMAT = DEFAULT_TIME_FORMAT

    def __init__(self, level):
        self.lock = threading.RLock()
        self.level: Level = level

    def _filter(self, record):
        return True

    def handle(self, record):
        """
        处理日志记录
        :param record:
        :return:
        """
        try:
            if not self._filter(record):
                return
            with self.lock:
                self._handle(record)
        except Exception:
            self._handle_error(record)

    def _handle(self, record):
        raise NotImplementedError

    def _serialize_record(self, record):
        return dict(
            message=record.msg,
            level=record.level.name,
            short_level=record.level.name[0].upper(),
            filename=os.path.basename(record.filename),
            func_name=record.func_name,
            lineno=record.lineno,
            time=record.time.strftime(self.TIME_FORMAT),
            color=record.level.color
        )

    def format(self, record):
        data = self._serialize_record(record)
        return self.FORMAT.format(**data)

    def _handle_error(self, record):
        print(traceback.format_exc())
        pass

    def close(self):
        raise NotImplementedError

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.level.name}>'


class StreamHandler(Handler):
    """"""
    terminator = '\n'

    def __init__(self, level, stream):
        super().__init__(level)
        self._stream = stream

    def flush(self):
        """
        Flushes the stream.
        """
        with self.lock:
            if not self._stream:
                return
            if hasattr(self._stream, "flush"):
                self._stream.flush()

    def _handle(self, record):
        try:
            msg = self.format(record)
            self._stream.write(msg + self.terminator)
            self.flush()
        except RecursionError:
            raise
        except Exception:
            self._handle_error(record)

    def close(self):
        with self.lock:
            if self._stream and hasattr(self._stream, 'close'):
                self._stream.close()
                self._stream = None


class TerminalHandler(StreamHandler):
    """用于控制台终端输出"""
    FORMAT = '{color}[{short_level} {time} {filename}:{lineno}]{color} {message}'

    def __init__(self, level=Logger.notset):
        super().__init__(level, sys.stderr)


console = TerminalHandler()


class FileHandler(StreamHandler):
    """"""
    FORMAT = '[{short_level} {time} {filename}:{lineno}] {message}'

    def __init__(self, level, filename, mode='a', encoding='utf-8'):
        super().__init__(level, None)
        self.filename = filename
        self.mode = mode
        self.encoding = encoding

    def _handle(self, record):
        if self._stream is None:
            self._stream = self.__open_file()
        super()._handle(record)

    def __open_file(self):
        return open(self.filename, self.mode, encoding=self.encoding)


class RotatingFileHandler(FileHandler):
    """"""

    def __init__(self, level, filename, mode='a', encoding='utf-8', max_bytes=None, backup_count=None):
        super().__init__(level, filename, mode, encoding)
        self.max_bytes = max_bytes
        self.backup_count = backup_count

    def _rotate(self, source, dest):
        if os.path.exists(source):
            if os.path.exists(dest):
                os.remove(dest)
            os.rename(source, dest)

    def rollover(self):
        self.close()
        if self.backup_count > 0:
            ospath.delete(f'{self.filename}.{self.backup_count}')
            for i in range(self.backup_count - 1, 0, -1):
                sfn = f'{self.filename}.{i}'
                dfn = f'{self.filename}.{i + 1}'
                self._rotate(sfn, dfn)
            self._rotate(self.filename, f'{self.filename}.1')

    def _should_rollover(self, record):
        if self.max_bytes > 0:
            msg = f"{record}\n"
            self._stream.seek(0, 2)  # due to non-posix-compliant Windows feature
            if self._stream.tell() + len(msg) >= self.max_bytes:
                return True
        return False

    def _handle(self, record):
        if self._should_rollover(record):
            self.rollover()
        super()._handle(record)


class HttpHandler(Handler):
    """"""


class SocketHandler(Handler):
    """"""


class LoggingError(Exception):
    pass


logger = Logger()
