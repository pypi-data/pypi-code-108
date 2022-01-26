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

import PySide6
from PySide6 import (QtCore, QtGui, QtWidgets, Qt3DAnimation, Qt3DCore, Qt3DExtras, Qt3DInput, Qt3DLogic, Qt3DRender, QtAxContainer, QtBluetooth,
                     QtCharts, QtConcurrent, QtDataVisualization, QtDesigner, QtHelp, QtMultimedia, QtMultimediaWidgets, QtNetwork, QtNetworkAuth,
                     QtOpenGL, QtOpenGLWidgets, QtPositioning, QtPrintSupport, QtQml, QtQuick, QtQuickControls2, QtQuickWidgets, QtRemoteObjects,
                     QtScxml, QtSensors, QtSerialPort, QtSql, QtStateMachine, QtSvg, QtSvgWidgets, QtTest, QtUiTools, QtWebChannel, QtWebEngineCore,
                     QtWebEngineQuick, QtWebEngineWidgets, QtWebSockets, QtXml)

from PySide6.QtCore import (QByteArray, QCoreApplication, QDate, QDateTime, QEvent, QLocale, QMetaObject, QModelIndex, QModelRoleData, QMutex,
                            QMutexLocker, QObject, QPoint, QRect, QRecursiveMutex, QRunnable, QSettings, QSize, QThread, QThreadPool, QTime, QUrl,
                            QWaitCondition, Qt, QAbstractItemModel, QAbstractListModel, QAbstractTableModel, Signal, Slot)

from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient, QCursor, QFont, QFontDatabase, QFontMetrics, QGradient, QIcon, QImage,
                           QKeySequence, QLinearGradient, QPainter, QPalette, QPixmap, QRadialGradient, QTransform)

from PySide6.QtWidgets import (QApplication, QBoxLayout, QCheckBox, QColorDialog, QColumnView, QComboBox, QDateTimeEdit, QDialogButtonBox,
                               QDockWidget, QDoubleSpinBox, QFontComboBox, QFormLayout, QFrame, QGridLayout, QGroupBox, QHBoxLayout, QHeaderView,
                               QLCDNumber, QLabel, QLayout, QLineEdit, QListView, QListWidget, QMainWindow, QMenu, QMenuBar, QMessageBox,
                               QProgressBar, QProgressDialog, QPushButton, QSizePolicy, QSpacerItem, QSpinBox, QStackedLayout, QStackedWidget,
                               QStatusBar, QStyledItemDelegate, QSystemTrayIcon, QTabWidget, QTableView, QTextEdit, QTimeEdit, QToolBox, QTreeView,
                               QVBoxLayout, QWidget, QAbstractItemDelegate, QAbstractItemView, QAbstractScrollArea, QRadioButton, QFileDialog, QButtonGroup)


# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class ImageTextButton(QPushButton):

    def __init__(self, icon: QPixmap = None, text: str = None, direction: Union[type[Qt.Vertical], type[Qt.Horizontal]] = Qt.Vertical, parent=None):
        super().__init__(parent=parent)
        layout = QVBoxLayout() if direction == Qt.Vertical else QHBoxLayout()
        self.setLayout(layout)
        self.text_label = QLabel()
        self.text_label.setAlignment(Qt.AlignCenter)
        self.set_text(text)
        self.layout.addWidget(self.text_label)

        self.icon_label = QLabel()
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.set_icon(icon)
        self.layout.addWidget(self.icon_label)

    @property
    def direction(self):
        if isinstance(self.layout, QVBoxLayout):
            return Qt.Vertical
        return Qt.Horizontal

    @property
    def text(self) -> Optional[str]:
        return self.text_label.text()

    @property
    def icon(self) -> Optional[QIcon]:
        return QIcon(self.icon_label.pixmap())

    def _get_correct_image_size(self) -> QSize:
        if not self.text:
            print("self.text is None")
            return self.sizeHint()

        fm = self.text_label.fontMetrics()
        widths = []
        heights = []
        for line in self.text.splitlines():
            br = fm.boundingRect(line)
            widths.append(br.width())
            heights.append(br.height())
        # if self.direction == Qt.Vertical:
        #     return QSize(max(widths), max(heights))
        # else:
        #     return QSize(max(widths), sum(heights))
        return QSize(max(widths), sum(heights))

    def set_text(self, text: str):
        if text is None:
            self.text_label.clear()
            return

        self.text_label.setText(text)

    def set_icon(self, icon: Union[QIcon, QPixmap]):
        if icon is None:
            self.icon_label.clear()
            return

        if isinstance(icon, QIcon):
            icon = icon.pixmap(self._get_correct_image_size(), QIcon.Normal, QIcon.On)
        elif isinstance(icon, QPixmap):
            icon = icon.scaled(self._get_correct_image_size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        self.icon_label.setPixmap(icon)

    def sizeHint(self) -> PySide6.QtCore.QSize:
        return self.layout.sizeHint()

    @property
    def layout(self) -> QBoxLayout:
        return super().layout()
# region[Main_Exec]


if __name__ == '__main__':
    app = QApplication()
    w = ImageTextButton(icon=QPixmap(r"D:\Dropbox\hobby\Modding\Programs\Github\My_Repos\GidAppTools\gidapptools\data\images\placeholder.png"), text="this is a test" + ('\n' + "this is a test") * 10, direction=Qt.Vertical)
    w.show()
    sys.exit(app.exec())

# endregion[Main_Exec]
