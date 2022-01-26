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


from PySide6.QtCore import Qt

from PySide6.QtGui import (QDesktopServices, QPalette, QMouseEvent)

from PySide6.QtWidgets import (QApplication, QLabel, QWidget)


# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class HyperlinkLabel(QLabel):

    def __init__(self, link: str = None, validate: bool = False, parent=None):
        super().__init__(parent=parent)
        self.validate = validate
        self.link: str = None
        if link:
            self.set_link(link)
        self._set_link_color()

    def _validate_link(self, link: str):
        pass

    def _modify_link(self, link: str) -> str:
        return link

    def set_link(self, link: str):
        link = self._modify_link(link)
        if self.validate is True:
            self._validate_link(link)
        self.link = link
        self.setText(link)

    def _set_link_color(self):
        link_color = QApplication.instance().palette().color(QPalette.Button.Link)
        r = link_color.red()
        g = link_color.green()
        b = link_color.blue()
        self.setStyleSheet(f"color: rgb({', '.join(str(i) for i in [r,g,b])})")
        self.setCursor(Qt.PointingHandCursor)

    def _open_link(self):
        QDesktopServices.openUrl(self.link)

    def mousePressEvent(self, ev: QMouseEvent) -> None:
        if ev.button() == Qt.LeftButton:
            self._open_link()
        else:
            super().mousePressEvent(ev)
# region[Main_Exec]


if __name__ == '__main__':
    pass

# endregion[Main_Exec]
