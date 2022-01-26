"""
WiP.

Soon.
"""

# region [Imports]

import os
import re
import sys
import json
import queue
import math
import base64
import pickle
import random
import shelve
import dataclasses
import shutil
import asyncio
import logging
import sqlite3
import platform
import importlib
import subprocess
import inspect
from threading import Thread
from time import sleep, process_time, process_time_ns, perf_counter, perf_counter_ns
from io import BytesIO, StringIO
from abc import ABC, ABCMeta, abstractmethod
from copy import copy, deepcopy
from enum import Enum, Flag, auto, unique
from time import time, sleep
from pprint import pprint, pformat
from pathlib import Path
from string import Formatter, digits, printable, whitespace, punctuation, ascii_letters, ascii_lowercase, ascii_uppercase
from timeit import Timer
from typing import TYPE_CHECKING, Union, Callable, Iterable, Optional, Mapping, Any, IO, TextIO, BinaryIO, Hashable, Generator, Literal, TypeVar, TypedDict, AnyStr
from zipfile import ZipFile, ZIP_LZMA
from datetime import datetime, timezone, timedelta
from tempfile import TemporaryDirectory
from textwrap import TextWrapper, fill, wrap, dedent, indent, shorten
from functools import wraps, partial, lru_cache, singledispatch, total_ordering, cached_property
from importlib import import_module, invalidate_caches
from contextlib import contextmanager, asynccontextmanager, nullcontext, closing, ExitStack, suppress
from statistics import mean, mode, stdev, median, variance, pvariance, harmonic_mean, median_grouped
from collections import Counter, ChainMap, deque, namedtuple, defaultdict
from urllib.parse import urlparse
from importlib.util import find_spec, module_from_spec, spec_from_file_location
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from importlib.machinery import SourceFileLoader


from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QFont, QSyntaxHighlighter, QTextCharFormat, QColor


from PySide6.QtWidgets import QApplication, QFrame, QGridLayout, QLabel, QTextEdit, QWidget

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class StreamCaptureSignaler(QObject):
    flushed_text = Signal(str)
    flushed_items = Signal(tuple)


class BaseStdStreamCapturer:
    signaler: "StreamCaptureSignaler" = None
    separator: str = '\n' + ("═" * 150) + '\n'

    def __init__(self, pass_through: bool = True) -> None:
        self.pass_through = pass_through
        if self.__class__.signaler is None:
            self.__class__.signaler = StreamCaptureSignaler()
        self.original_stream = None
        self.text_cache: str = ""
        self.text_items: list[str] = []

    @property
    def flushed_text(self) -> Signal:
        return self.signaler.flushed_text

    @property
    def flushed_items(self) -> Signal:
        return self.signaler.flushed_items

    def isatty(self) -> bool:
        return False

    def write(self, text: str):
        self.text_cache += text
        if self.original_stream and self.pass_through:
            self.original_stream.write(text)

    def flush(self):
        self.text_items.append(self.text_cache.rstrip() + self.separator)

        self.text_cache = ""
        if self.signaler:
            try:
                self.signaler.flushed_items.emit(self.get_items())
                self.signaler.flushed_text.emit(self.get_text())
            except RuntimeError:
                pass
        if self.original_stream and self.pass_through:
            self.original_stream.flush()

    def get_text(self) -> str:
        return ''.join(self.text_items)

    def get_items(self) -> tuple[str]:
        return tuple(self.text_items)

    def clear(self):
        self.text_items.clear()


class LimitedStdStreamCapturer(BaseStdStreamCapturer):

    def __init__(self, max_len: int = 50) -> None:
        super().__init__()
        self.text_items = deque(maxlen=max_len)


class ErrorHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.rules: dict[re.Pattern, QTextCharFormat] = {}
        self.setup_rules()

    def setup_rules(self):
        sep_pattern = re.compile(r"═+")
        sep_format = QTextCharFormat()
        sep_format.setFontWeight(100)
        sep_format.setBackground(QColor(150, 150, 150, 50))
        self.rules[sep_pattern] = sep_format

        string_pattern = re.compile(r'(?<=\").*(?=\")')
        string_format = QTextCharFormat()
        string_format.setFontItalic(True)
        string_format.setFontUnderline(True)
        string_format.setForeground(QColor(0, 150, 0, 255))
        self.rules[string_pattern] = string_format

        quotes_pattern = re.compile(r'\"')
        quotes_format = QTextCharFormat()
        quotes_format.setForeground(QColor(150, 150, 0, 255))
        self.rules[quotes_pattern] = quotes_format

        self_pattern = re.compile(r"(?<=\b)self(?=\b)")
        self_format = QTextCharFormat()
        self_format.setForeground(QColor(255, 100, 0, 255))
        self.rules[self_pattern] = self_format

        method_pattern = re.compile(r"(?<=\.)\w+(?=\()")
        method_format = QTextCharFormat()
        method_format.setForeground(QColor(0, 0, 200, 255))
        method_format.setFontItalic(True)
        self.rules[method_pattern] = method_format

        error_name_pattern = re.compile(r"\w+Error")
        error_name_format = QTextCharFormat()
        error_name_format.setForeground(QColor(150, 0, 0, 255))
        error_name_format.setTextOutline(QColor(0, 0, 0, 100))
        error_name_format.setFontWeight(1000)
        error_name_format.setFontUnderline(True)
        self.rules[error_name_pattern] = error_name_format

        traceback_title_pattern = re.compile(re.escape(r"Traceback (most recent call last):"))
        traceback_title_format = QTextCharFormat()
        traceback_title_format.setFontUnderline(True)
        traceback_title_format.setBackground(QColor(200, 200, 0, 50))
        self.rules[traceback_title_pattern] = traceback_title_format

    def highlightBlock(self, text: str) -> None:

        for pattern, text_format in self.rules.items():
            for match in pattern.finditer(text):

                start, end = match.span()
                self.setFormat(start, end - start, text_format)


class StdStreamWidget(QWidget):

    def __init__(self, stream_capturer: "BaseStdStreamCapturer", parent: Optional[QWidget] = None) -> None:
        super().__init__(parent=parent)
        self.stream_capturer = stream_capturer

        self.setLayout(QGridLayout())
        self.text_view: QTextEdit = None

    def setup(self) -> "StdStreamWidget":
        self.resize(1500, 500)
        self.highlighter = ErrorHighlighter()
        self.text_view = QTextEdit(self)
        self.highlighter.setDocument(self.text_view.document())
        self.text_view.setReadOnly(True)
        self.text_view.setLineWrapMode(QTextEdit.NoWrap)
        font: QFont = self.text_view.font()
        font.setStyleHint(QFont.Monospace)
        font.setFamily("Consolas")
        font.setPointSize(11)
        self.text_view.setFont(font)
        self.layout.addWidget(self.text_view)
        self.text_view.setPlainText(self.stream_capturer.get_text())
        self.stream_capturer.flushed_text.connect(self.set_text)

        return self

    def set_text(self, text: str):
        self.text_view.setPlainText(text)
        self.text_view.verticalScrollBar().setValue(self.text_view.verticalScrollBar().maximum())

    @property
    def layout(self) -> QGridLayout:
        return super().layout()

    def show(self) -> None:
        self.text_view.verticalScrollBar().setValue(self.text_view.verticalScrollBar().maximum())
        return super().show()


# region[Main_Exec]
if __name__ == '__main__':
    pass

# endregion[Main_Exec]
