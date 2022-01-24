from ..core import _core  # need to pull in dependent base-types
from ._ui import export as _ui_export, qt_version as _get_ui_qt_version, qt_version_string as _get_ui_qt_version_string, ItemDataProperty, LayoutInfo, LayoutClient, LayoutServer #from ._ui import *
from shyft.energy_market.core import ModelInfo
import json
from shiboken2 import getCppPointer as _getCppPointer
from PySide2 import __version__ as PySideVersion
from PySide2.QtCore import __version__ as PySideQtVersion, qVersion as _get_pyside_qt_runtime_version, QVersionNumber
from PySide2.QtWidgets import QWidget

UiQtVersion = _get_ui_qt_version_string()
QtVersion = _get_pyside_qt_runtime_version()

def versions():
    print(f"PySide2 version {PySideVersion} built with Qt version: {PySideQtVersion}") # PySide2 version and Qt version used to compile PySide2
    print(f"Shyft ui python module built with Qt version: {UiQtVersion}") # Qt version used to compile _ui.pyd
    print(f"Qt version: {QtVersion}") # Qt version of runtime libraries currently used

def export(window: QWidget) -> str:
    ptr = _getCppPointer(window)
    return _ui_export(ptr[0])

def export_print(window: QWidget, pretty: bool = False, indent: int = 2):
    cfg = export(window)
    if pretty:
        print(json.dumps(json.loads(cfg), indent=indent))
    else:
        print(cfg)