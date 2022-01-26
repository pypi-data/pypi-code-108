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
from gidapptools.general_helper.conversion import bytes2human

import PySide6
from PySide6 import (QtCore, QtGui, QtWidgets, Qt3DAnimation, Qt3DCore, Qt3DExtras, Qt3DInput, Qt3DLogic, Qt3DRender, QtAxContainer, QtBluetooth,
                     QtCharts, QtConcurrent, QtDataVisualization, QtDesigner, QtHelp, QtMultimedia, QtMultimediaWidgets, QtNetwork, QtNetworkAuth,
                     QtOpenGL, QtOpenGLWidgets, QtPositioning, QtPrintSupport, QtQml, QtQuick, QtQuickControls2, QtQuickWidgets, QtRemoteObjects,
                     QtScxml, QtSensors, QtSerialPort, QtSql, QtStateMachine, QtSvg, QtSvgWidgets, QtTest, QtUiTools, QtWebChannel, QtWebEngineCore,
                     QtWebEngineQuick, QtWebEngineWidgets, QtWebSockets, QtXml)

from PySide6.QtCore import (QByteArray, QTimer, qInstallMessageHandler, qWarning, QFileSystemWatcher, QCoreApplication, QDate, QDateTime, QEvent, QLocale, QMetaObject, QModelIndex, QModelRoleData, QMutex,
                            QMutexLocker, QObject, QPoint, QRect, QRecursiveMutex, QRunnable, QSettings, QSize, QThread, QThreadPool, QTime, QUrl,
                            QWaitCondition, Qt, QAbstractItemModel, QAbstractListModel, QAbstractTableModel, Signal, Slot)

from PySide6.QtGui import (QAction, QBrush, QSyntaxHighlighter, QTextCharFormat, QColor, QConicalGradient, QCursor, QFont, QFontDatabase, QFontMetrics, QGradient, QIcon, QImage,
                           QKeySequence, QLinearGradient, QPainter, QPalette, QPixmap, QRadialGradient, QTransform)

from PySide6.QtWidgets import (QApplication, QBoxLayout, QCheckBox, QColorDialog, QColumnView, QComboBox, QDateTimeEdit, QDialogButtonBox,
                               QDockWidget, QDoubleSpinBox, QFontComboBox, QFormLayout, QFrame, QGridLayout, QGroupBox, QHBoxLayout, QHeaderView,
                               QLCDNumber, QLabel, QLayout, QLineEdit, QListView, QListWidget, QMainWindow, QMenu, QMenuBar, QMessageBox,
                               QProgressBar, QProgressDialog, QPushButton, QSizePolicy, QSpacerItem, QSpinBox, QStackedLayout, QStackedWidget,
                               QStatusBar, QStyledItemDelegate, QSystemTrayIcon, QTabWidget, QTableView, QTextEdit, QTimeEdit, QToolBox, QTreeView,
                               QVBoxLayout, QWidget, QAbstractItemDelegate, QAbstractItemView, QAbstractScrollArea, QRadioButton, QFileDialog, QButtonGroup)

from pyparsing.exceptions import ParseBaseException
from gidapptools.gid_parsing.py_log_parsing import GeneralGrammar, LogLevelToken
# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]


THIS_FILE_DIR = Path(__file__).parent.absolute()


# endregion[Constants]


class AppLogHighlighter(QSyntaxHighlighter):
    grammar = GeneralGrammar()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.formats: dict[str, QTextCharFormat] = {}
        self.setup_formats()

    def setup_formats(self):
        self.base_format = QTextCharFormat()

        date_format = QTextCharFormat()
        date_format.setForeground(QColor(0, 0, 0, 255))
        date_format.setTextOutline(QColor(255, 255, 255, 50))
        date_format.setFontWeight(1000)
        self.formats["time_stamp"] = date_format

        line_number_format = QTextCharFormat()
        line_number_format.setForeground(QColor(0, 0, 0, 255))
        line_number_format.setTextOutline(QColor(255, 255, 255, 50))
        line_number_format.setFontWeight(1000)
        self.formats["line_number"] = line_number_format

        level_format = QTextCharFormat()
        level_format.setFontWeight(1000)
        level_format.setFontUnderline(True)
        self.formats["level"] = level_format

        debug_format = QTextCharFormat()
        debug_format.setBackground(QColor(144, 238, 144, 75))
        self.formats["debug"] = debug_format

        info_format = QTextCharFormat()
        info_format.setBackground(QColor(173, 216, 230, 75))
        self.formats["info"] = info_format

        critical_format = QTextCharFormat()
        critical_format.setBackground(QColor(255, 165, 0, 75))
        self.formats["critical"] = critical_format

        error_format = QTextCharFormat()
        error_format.setBackground(QColor(220, 20, 60, 100))
        self.formats["error"] = error_format

        message_format = QTextCharFormat()
        message_format.setFontWeight(1000)
        self.formats["message"] = message_format

        thread_format = QTextCharFormat()
        self.formats["thread"] = thread_format

        module_format = QTextCharFormat()
        self.formats["module"] = module_format

        function_format = QTextCharFormat()
        self.formats["function"] = function_format

    def highlightBlock(self, text: str) -> None:

        try:
            tokens = self.grammar(text)
            background_fmt = self.formats[tokens["level"].log_level.casefold()]
            self.setFormat(0, len(text), background_fmt)
            for name, token in tokens.items():
                fmt = self.formats.get(name, self.base_format)
                fmt.setBackground(background_fmt.background())
                self.setFormat(token.start, token.span, fmt)

        except ParseBaseException:
            pass

    # def highlightBlock(self, text: str) -> None:
    #     try:
    #         backgrounds = {"debug": QColor(0, 200, 0, 50),
    #                        "info": QColor(0, 0, 255, 50),
    #                        "critical": QColor(255, 200, 0, 50),
    #                        "error": QColor(255, 0, 0, 100)}
    #         if not text.strip():
    #             return
    #         parts = text.split("|")

    #         level_part = parts[2]

    #         start = text.find(level_part)
    #         background = backgrounds.get(level_part.strip().casefold(), QColor(0, 0, 0, 0))
    #         format_item = QTextCharFormat()
    #         format_item.setBackground(background)
    #         self.setFormat(0, text.find("||-->"), format_item)

    #         date_part = parts[0].strip()
    #         start = text.find(date_part)
    #         fmt = self.formats["date"]
    #         fmt.setBackground(background)
    #         self.setFormat(start, len(date_part), fmt)

    #         line_number_part = parts[1].strip()
    #         start = text.find(line_number_part)
    #         fmt = self.formats["line_number"]
    #         fmt.setBackground(background)
    #         self.setFormat(start, len(line_number_part), fmt)

    #         message_start = text.find("||--> ") + 6
    #         self.setFormat(message_start, len(text) - message_start, self.formats["message"])
    #     except IndexError:
    #         pass


class MetaBox(QGroupBox):

    def __init__(self, log_file: Path, parent=None):
        super().__init__(parent=parent)
        self.log_file = log_file
        self.setLayout(QFormLayout())
        qWarning("something")

        self.setTitle("Meta Data")
        self.widgets = {}

        self.setup()

    def _gather_meta_data(self) -> dict[str, str]:
        data = {}
        data["Name"] = self.log_file.name
        data["Path"] = self.log_file.as_posix()
        data["Size"] = bytes2human(self.log_file.stat().st_size)
        data["Lines"] = len(self.log_file.read_text(encoding='utf-8', errors='ignore').splitlines())

        return data

    def setup(self):
        for k, v in self._gather_meta_data().items():
            value_widget = QLabel()
            value_widget.setText(str(v))
            self.layout.addRow(k, value_widget)
            self.widgets[k] = value_widget

    @property
    def layout(self) -> QFormLayout:
        return super().layout()

    def update_size(self):
        size_widget = self.widgets["Size"]
        size_widget.setText(bytes2human(self.log_file.stat().st_size))
        size_widget.repaint()

        line_amount_widget = self.widgets["Lines"]
        line_amount_widget.setText(str(len(self.log_file.read_text(encoding='utf-8', errors='ignore').splitlines())))
        line_amount_widget.repaint()


class AppLogViewer(QWidget):

    def __init__(self, log_file: Path, parent=None) -> None:
        super().__init__(parent=parent)
        self.log_file = Path(log_file).resolve()
        self.file_size = None
        self.timer_id = None

    def setup(self) -> "AppLogViewer":
        self.setLayout(QGridLayout())
        self.setWindowTitle("Application Log")

        self.setup_widgets()
        self.set_content()
        # self.file_watcher = QFileSystemWatcher(self)
        # self.file_watcher.addPath(str(self.log_file))
        # self.file_watcher.fileChanged.connect(self.set_content)
        # self.file_watcher.fileChanged.connect(self.set_content)
        self.timer_id = self.startTimer(500, Qt.CoarseTimer)
        return self

    def setup_widgets(self):
        self.meta_box = MetaBox(self.log_file)
        self.layout.addWidget(self.meta_box)

        self.text_widget = QTextEdit(self)
        self.text_widget.setReadOnly(True)
        self.text_widget.setLineWrapMode(QTextEdit.NoWrap)
        font: QFont = self.text_widget.font()
        font.setStyleHint(QFont.Monospace)
        font.setFamily("Consolas")
        self.text_widget.setFont(font)

        self.layout.addWidget(self.text_widget)
        self.highlighter = AppLogHighlighter()
        self.highlighter.setDocument(self.text_widget.document())

    def set_content(self):
        self.file_size = self.log_file.stat().st_size
        content = self.log_file.read_text(encoding='utf-8', errors='ignore')
        self.text_widget.setPlainText(content)
        self.resize_to_content()
        self.text_widget.verticalScrollBar().setValue(self.text_widget.verticalScrollBar().maximum())
        self.text_widget.update()
        self.text_widget.repaint()

    def resize_to_content(self):
        height = self.size().height()
        width = min(2000, self.text_widget.document().size().toSize().width())
        self.resize(width, height)

    def check_file(self):
        if self.log_file.stat().st_size != self.file_size:
            self.set_content()
            self.meta_box.update_size()

    def timerEvent(self, event: PySide6.QtCore.QTimerEvent) -> None:
        self.check_file()
        return super().timerEvent(event)

    @property
    def layout(self) -> QGridLayout:
        return super().layout()

    def closeEvent(self, event: PySide6.QtGui.QCloseEvent) -> None:
        if self.timer_id is not None:
            self.killTimer(self.timer_id)
        event.accept()
# region[Main_Exec]


if __name__ == '__main__':
    pass

# endregion[Main_Exec]
